"""Tests for github_tool.py."""

import json

import pytest

from agent.tools.github_tool import GitHubTool
from ingestion.parsers.repo_analyzer import RepoAnalyzer


@pytest.mark.unit
def test_file_structure_enables_test_and_ci_detection(monkeypatch):
    """Repository file paths should reach RepoAnalyzer."""

    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self._json_data = json_data
            self.status_code = status_code

        def json(self):
            return self._json_data

        def raise_for_status(self):
            return None

    def mock_get(url, **kwargs):
        if "/git/trees/" in url:
            return MockResponse(
                {
                    "tree": [
                        {"path": "README.md"},
                        {"path": "tests/unit/test_example.py"},
                        {"path": ".github/workflows/ci.yml"},
                        {"path": "pyproject.toml"},
                    ]
                }
            )

        return MockResponse(
            {
                "name": "example-repo",
                "description": "Example repository",
                "language": "Python",
                "stargazers_count": 1,
                "forks_count": 2,
                "open_issues_count": 3,
                "pushed_at": "2026-10-01T00:00:00Z",
                "topics": [],
                "homepage": None,
                "default_branch": "main",
            }
        )

    monkeypatch.setattr("agent.tools.github_tool.httpx.get", mock_get)
    monkeypatch.setattr(
        GitHubTool,
        "_has_readme",
        lambda self, username, repo_name: True,
    )

    result = GitHubTool().execute(
        {
            "github_username": "codepath",
            "repo_name": "example-repo",
        }
    )

    assert result.success is True
    assert "file_structure" in result.data
    assert "tests/unit/test_example.py" in result.data["file_structure"]
    assert ".github/workflows/ci.yml" in result.data["file_structure"]

    analysis = RepoAnalyzer().parse(json.dumps(result.data))

    assert analysis.metadata["has_tests"] is True
    assert analysis.metadata["has_ci"] is True
    assert "Python" in analysis.metadata["tech_stack"]


@pytest.mark.unit
def test_fetch_file_structure_returns_empty_on_api_error(monkeypatch):
    import httpx

    from agent.tools.github_tool import GitHubTool

    def mock_get(*args, **kwargs):
        raise httpx.RequestError("GitHub API unavailable")

    monkeypatch.setattr(httpx, "get", mock_get)

    tool = GitHubTool()
    result = tool._fetch_file_structure("test-user", "test-repo", "main")

    assert result == []
