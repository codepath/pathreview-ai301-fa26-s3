"""Integration tests for GitHubTool against a local pytest-httpserver."""

import json
from pathlib import Path

import pytest
from pytest_httpserver import HTTPServer

from agent.tools.github_tool import GitHubTool


@pytest.mark.integration
class TestGitHubTool:
    """Integration test suite for GitHubTool against a mock GitHub API server."""

    @pytest.fixture
    def github_tool(self, httpserver: HTTPServer) -> GitHubTool:
        """Return a GitHubTool pointed at the local pytest-httpserver.

        Args:
            httpserver: The pytest-httpserver fixture providing a local server.

        Returns:
            A GitHubTool instance with base_url set to the local server.
        """
        tool = GitHubTool()
        tool.base_url = httpserver.url_for("").rstrip("/")
        return tool

    def test_repository_not_found(self, httpserver: HTTPServer, github_tool: GitHubTool) -> None:
        """Test that a 404 repository response maps to a not-found error.

        Args:
            httpserver: The pytest-httpserver fixture providing a local server.
            github_tool: The GitHubTool fixture under test.
        """
        httpserver.expect_request("/repos/octocat/nope", method="GET").respond_with_data(
            "", status=404
        )

        result = github_tool.execute({"github_username": "octocat", "repo_name": "nope"})

        httpserver.check()
        assert result.success is False
        assert result.data == {}
        assert result.error == "Repository not found"
        assert len(httpserver.log) == 1
        request, _ = httpserver.log[0]
        assert request.method == "GET"
        assert request.path == "/repos/octocat/nope"

    def test_rate_limited_or_access_denied(
        self, httpserver: HTTPServer, github_tool: GitHubTool
    ) -> None:
        """Test that a 403 response maps to a rate-limit-or-access-denied error.

        Args:
            httpserver: The pytest-httpserver fixture providing a local server.
            github_tool: The GitHubTool fixture under test.
        """
        httpserver.expect_request("/repos/octocat/limited", method="GET").respond_with_data(
            "", status=403
        )

        result = github_tool.execute({"github_username": "octocat", "repo_name": "limited"})

        httpserver.check()
        assert result.success is False
        assert result.data == {}
        assert result.error == "Rate limited or access denied"
        assert len(httpserver.log) == 1
        request, _ = httpserver.log[0]
        assert request.method == "GET"
        assert request.path == "/repos/octocat/limited"

    def test_fetch_repo_metadata_success_with_readme(
        self, httpserver: HTTPServer, github_tool: GitHubTool
    ) -> None:
        """Test a successful fetch with a README present against fixture data.

        Args:
            httpserver: The pytest-httpserver fixture providing a local server.
            github_tool: The GitHubTool fixture under test.
        """
        fixture_path = Path(__file__).parent.parent / "fixtures" / "github_responses"
        fixture_data = json.loads((fixture_path / "repo_success.json").read_text())
        httpserver.expect_request("/repos/octocat/ok", method="GET").respond_with_json(fixture_data)
        httpserver.expect_request("/repos/octocat/ok/readme", method="HEAD").respond_with_data(
            "", status=200
        )

        result = github_tool.execute({"github_username": "octocat", "repo_name": "ok"})

        httpserver.check()
        assert result.success is True
        assert result.error is None
        assert result.data == {
            "name": "ok",
            "description": "d",
            "primary_language": "Python",
            "star_count": 1,
            "fork_count": 0,
            "open_issues_count": 0,
            "last_commit_date": "2026-01-01T00:00:00Z",
            "has_readme": True,
            "topics": [],
            "homepage": "",
        }
        assert len(httpserver.log) == 2
        first_request, _ = httpserver.log[0]
        second_request, _ = httpserver.log[1]
        assert first_request.method == "GET"
        assert first_request.path == "/repos/octocat/ok"
        assert second_request.method == "HEAD"
        assert second_request.path == "/repos/octocat/ok/readme"
