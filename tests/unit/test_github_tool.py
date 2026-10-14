"""Tests for github_tool.py"""

import httpx
import pytest

from agent.tools.github_tool import GitHubTool
from ingestion.parsers.repo_analyzer import RepoAnalyzer


class FakeResponse:
    """Minimal stand-in for an httpx response."""

    def __init__(self, payload=None, status_code=200):
        self._payload = payload or {}
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://api.github.com")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError("error", request=request, response=response)

    def json(self):
        return self._payload


@pytest.mark.unit
class TestGitHubToolFileStructure:
    """Test suite for the file_structure field returned by GitHubTool."""

    @pytest.fixture
    def tool(self):
        """Create a GitHubTool instance."""
        return GitHubTool()

    @pytest.fixture
    def fake_github(self, monkeypatch):
        """Replace GitHub network calls; the tree response can be set per test."""
        responses = {
            "repo": FakeResponse({"name": "demo", "default_branch": "main"}),
            "tree": FakeResponse(
                {
                    "truncated": False,
                    "tree": [
                        {"path": "tests/test_app.py"},
                        {"path": ".github/workflows/ci.yml"},
                        {"path": "README.md"},
                    ],
                }
            ),
        }

        def fake_get(url, **kwargs):
            return responses["tree"] if "/git/trees/" in url else responses["repo"]

        monkeypatch.setattr(httpx, "get", fake_get)
        monkeypatch.setattr(httpx, "head", lambda url, **kwargs: FakeResponse())
        return responses

    def test_file_structure_is_returned(self, tool, fake_github):
        """The tool returns the repository's file paths under file_structure."""
        result = tool.execute({"github_username": "owner", "repo_name": "demo"})

        assert result.success is True
        assert result.data["file_structure"] == [
            "tests/test_app.py",
            ".github/workflows/ci.yml",
            "README.md",
        ]

    def test_analyzer_detects_tests_and_ci_from_tool_output(self, tool, fake_github):
        """Passing the tool's output to RepoAnalyzer sets has_tests and has_ci."""
        result = tool.execute({"github_username": "owner", "repo_name": "demo"})

        analysis = RepoAnalyzer().parse(result.data)

        assert analysis.metadata["has_tests"] is True
        assert analysis.metadata["has_ci"] is True

    def test_failed_tree_request_gives_empty_file_structure(self, tool, fake_github):
        """If the file list cannot be fetched, the tool still succeeds."""
        fake_github["tree"] = FakeResponse(status_code=500)

        result = tool.execute({"github_username": "owner", "repo_name": "demo"})

        assert result.success is True
        assert result.data["file_structure"] == []

    def test_truncated_tree_gives_empty_file_structure(self, tool, fake_github):
        """A truncated file list is not used, because it would be incomplete."""
        fake_github["tree"] = FakeResponse({"truncated": True, "tree": [{"path": "a.py"}]})

        result = tool.execute({"github_username": "owner", "repo_name": "demo"})

        assert result.success is True
        assert result.data["file_structure"] == []
