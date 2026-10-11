"""Tests for orchestrator.py"""

import pytest

from agent.memory.session_store import SessionStore
from agent.orchestrator import Orchestrator
from agent.tools.base import BaseTool, ToolResult


class CountingTool(BaseTool):
    """Stub tool that reports how many times it has executed."""

    name = "market_analyzer"
    description = "test tool"

    def __init__(self):
        self.calls = 0

    def execute(self, input_data: dict) -> ToolResult:
        self.calls += 1
        return ToolResult(success=True, data={"call_number": self.calls})


class FakeSessionStore(SessionStore):
    """In-memory stand-in for SessionStore that records call order."""

    def __init__(self, initial: dict | None = None):
        self.data = dict(initial or {})
        self.calls: list[tuple[str, str]] = []

    def get(self, session_id: str) -> dict | None:
        self.calls.append(("get", session_id))
        return self.data.get(session_id)

    def set(self, session_id: str, data: dict, ttl_seconds: int = 3600) -> None:
        self.calls.append(("set", session_id))
        self.data[session_id] = data

    def delete(self, session_id: str) -> None:
        self.calls.append(("delete", session_id))
        self.data.pop(session_id, None)


@pytest.mark.unit
class TestOrchestratorRunIsolation:
    """Each run() must start without state left over from earlier runs."""

    def test_sequential_runs_execute_tool_again(self):
        """Test a second run() on the same instance does not reuse the first run's result."""
        tool = CountingTool()
        orch = Orchestrator(tools={"market_analyzer": tool})

        result1 = orch.run("profile-1", {"resume_text": "irrelevant"})
        result2 = orch.run("profile-2", {"resume_text": "irrelevant"})

        assert tool.calls == 2
        assert result1["tool_results"]["market_analyzer"] == {"call_number": 1}
        assert result2["tool_results"]["market_analyzer"] == {"call_number": 2}

    def test_cached_results_only_cover_current_run(self):
        """Test cached_results holds only the current run's entries."""
        tool = CountingTool()
        orch = Orchestrator(tools={"market_analyzer": tool})

        orch.run("profile-1", {"resume_text": "irrelevant"})
        result2 = orch.run("profile-2", {"resume_text": "irrelevant"})

        cached = list(result2["cached_results"].values())
        assert len(cached) == 1
        assert cached[0].data == {"call_number": 2}

    def test_saved_session_state_is_deleted_before_run(self):
        """Test stale saved state is deleted first and not merged into the new state."""
        store = FakeSessionStore(initial={"profile-2": {"stale_tool": {"old": True}}})
        orch = Orchestrator(tools={"market_analyzer": CountingTool()}, session_store=store)

        orch.run("profile-2", {"resume_text": "irrelevant"})

        assert store.calls[0] == ("delete", "profile-2")
        assert store.calls[-1] == ("set", "profile-2")
        assert "stale_tool" not in store.data["profile-2"]
        assert store.data["profile-2"]["market_analyzer"] == {"call_number": 1}
