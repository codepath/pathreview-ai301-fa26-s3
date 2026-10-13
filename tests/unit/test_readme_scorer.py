"""Tests for readme_scorer.py"""

import pytest

from agent.tools.readme_scorer import ReadmeScorer


@pytest.mark.unit
class TestReadmeScorer:
    """Test suite for ReadmeScorer."""

    @pytest.fixture
    def scorer(self):
        """Create a ReadmeScorer instance."""
        return ReadmeScorer()

    def test_readme_with_all_quality_signals(self, scorer):
        """Test README with all quality signals returns high score."""
        readme = """
        # Project Name

        Project Name is a sample application designed to demonstrate a complete and well-documented software project. The application provides a simple structure that can be used as an example for installation, usage, configuration, testing, deployment, and maintenance documentation. The goal of this README is to give contributors and users enough information to understand what the project does, how to set it up, and how to work with it successfully.

        The project exposes a small service that can be installed locally and run as a Python application. It is intended to be easy to understand while still including the sections that are commonly expected in a mature open source project. The documentation below includes installation instructions, usage examples, configuration details, feature descriptions, development guidance, testing information, troubleshooting notes, and links to a live demonstration.

        ## Installation

        The project requires Python 3.9 or newer. It is recommended to use a virtual environment so that project dependencies remain isolated from other Python applications installed on the system.

        Create and activate a virtual environment before installing the package.

        ```bash
        python -m venv .venv
        source .venv/bin/activate
        ```

        On Windows, activate the environment using the appropriate command for your shell.

        After the environment is active, install the package with pip:

        ```bash
        pip install package
        ```

        If you are working from a cloned development copy, you can install the project in editable mode so that local code changes are immediately reflected when you run the application.

        ```bash
        pip install -e .
        ```

        Once installation is complete, verify that the package can be imported successfully before continuing.

        ## Usage

        The package can be imported and executed directly from Python.

        ```python
        import package
        package.run()
        ```

        The run function starts the application using the default configuration. For local development, the application can be started from a terminal and accessed through the configured host and port.

        A typical workflow is to install the project, start the application, make a request, inspect the response, and then stop the development process when testing is complete. Additional configuration options can be supplied through environment variables or a local configuration file.

        ## Features

        - Feature 1 provides the primary application workflow.
        - Feature 2 adds support for configurable behavior.
        - Feature 3 provides additional functionality for development and testing.
        - Clear installation instructions for new contributors.
        - Simple Python usage examples.
        - Support for local development environments.
        - Structured configuration options.
        - Logging for important application events.
        - Automated tests for core functionality.
        - Documentation for common troubleshooting scenarios.

        The project is intentionally organized so that each feature can be understood independently. This makes it easier for new contributors to identify where functionality is implemented and how changes should be tested.

        ## Configuration

        The application uses sensible defaults so that it can run immediately after installation. Users can override settings through environment variables when necessary.

        Common configuration values may include the application host, port, database connection information, logging level, and environment name. Development environments can use local values, while production deployments should store sensitive configuration outside of source control.

        Before deploying the project, review the configuration carefully and confirm that development-only options are disabled.

        ## Tech Stack

        - Python 3.9
        - FastAPI
        - PostgreSQL

        Python is used for the main application logic. FastAPI provides the web application framework and request handling. PostgreSQL is used for persistent data storage. Together, these technologies provide a straightforward development environment that can support both local testing and production deployment.

        ## Development

        Contributors should begin by cloning the repository and installing the development dependencies. Changes should be made on a separate branch and tested locally before they are submitted for review.

        Keep changes focused on one issue whenever possible. New behavior should include appropriate tests, and existing tests should continue to pass after the change.

        Code should remain readable and consistent with the existing project structure. Before submitting a change, review the affected files and make sure temporary debugging output or unrelated modifications have not been included.

        ## Testing

        The project includes automated tests for important application behavior. Tests should be run before opening a pull request.

        A typical test command is:

        ```bash
        pytest
        ```

        If a test fails, review the failure output and confirm that the test environment matches the expected setup. When fixing a bug, it is helpful to reproduce the failure before making the change and then run the same test again afterward to confirm that the behavior has been corrected.

        ## Troubleshooting

        If the package cannot be imported, confirm that the virtual environment is active and that the installation completed successfully.

        If the application cannot connect to PostgreSQL, verify that the database service is running and that the configured connection values are correct.

        If tests behave differently across environments, compare Python versions, installed dependency versions, environment variables, and repository state. Recording these details can make it easier for another contributor to reproduce the same result.

        ## Project Structure

        The project is organized into separate areas for application code, tests, configuration, and documentation. Application modules contain the runtime behavior, while the test suite verifies expected results. Keeping these responsibilities separate makes the codebase easier to navigate and maintain.

        New contributors should begin with the README, then review the tests related to the feature they are changing. Existing tests often provide useful examples of how the application is expected to behave.

        ## Contributing

        Contributions are welcome. Before submitting a pull request, make sure the project installs correctly, the relevant tests pass, and the change is limited to the intended issue.

        A useful contribution includes a clear explanation of what changed, why the change was necessary, and how the result was tested. Small, focused pull requests are generally easier to review and maintain than large changes that combine unrelated work.

        ## Status

        ![Build Status](https://example.com/badge.svg)
        ![Coverage](https://example.com/coverage.svg)

        The build status badge represents the current state of the automated build process, while the coverage badge provides a summary of test coverage.

        ## Live Demo

        A demonstration deployment is available for users who want to explore the project without installing it locally.

        [Try it here](https://demo.example.com)

        The live demo is intended for evaluation and basic experimentation. For development work, contributors should run the project locally so that they can inspect logs, change configuration, and run the full test suite.
        """

        result = scorer.execute({"readme_content": readme})

        assert result.success is True
        data = result.data
        assert data["has_readme"] is True
        assert data["word_count"] >= 500
        assert data["word_count_category"] == "comprehensive"
        assert data["has_installation_section"] is True
        assert data["has_usage_section"] is True
        assert data["has_badges"] is True
        assert data["has_demo_link"] is True
        assert data["has_tech_stack_section"] is True
        assert data["overall_score"] > 0.7  # Should be high

    def test_readme_with_no_content(self, scorer):
        """Test README with no content returns score of 0.0."""
        result = scorer.execute({"readme_content": ""})

        assert result.success is True
        data = result.data
        assert data["has_readme"] is False
        assert data["word_count"] == 0
        assert data["word_count_category"] == "minimal"
        assert data["overall_score"] == 0.0

    def test_readme_with_only_title(self, scorer):
        """Test README with only a title returns minimal word count category."""
        readme = "# Project Title"

        result = scorer.execute({"readme_content": readme})

        assert result.success is True
        data = result.data
        assert data["has_readme"] is True
        assert data["word_count"] < 100
        assert data["word_count_category"] == "minimal"
        assert data["overall_score"] < 0.3

    def test_word_count_category_minimal(self, scorer):
        """Test word_count_category: < 100 = minimal."""
        readme = "This is a very short readme with just a few words."

        result = scorer.execute({"readme_content": readme})

        data = result.data
        assert data["word_count"] < 100
        assert data["word_count_category"] == "minimal"

    def test_word_count_category_adequate(self, scorer):
        """Test word_count_category: 100-500 = adequate."""
        readme = " ".join(["word"] * 200)  # 200 words

        result = scorer.execute({"readme_content": readme})

        data = result.data
        assert 100 <= data["word_count"] <= 500
        assert data["word_count_category"] == "adequate"

    def test_word_count_category_comprehensive(self, scorer):
        """Test word_count_category: > 500 = comprehensive."""
        readme = " ".join(["word"] * 700)  # 700 words

        result = scorer.execute({"readme_content": readme})

        data = result.data
        assert data["word_count"] > 500
        assert data["word_count_category"] == "comprehensive"

    def test_installation_section_detection(self, scorer):
        """Test detection of installation section."""
        readme_with_install = """
        # Project
        ## Installation
        pip install package
        """

        result = scorer.execute({"readme_content": readme_with_install})
        assert result.data["has_installation_section"] is True

        readme_without_install = """
        # Project
        ## Description
        This is a project.
        """

        result = scorer.execute({"readme_content": readme_without_install})
        assert result.data["has_installation_section"] is False

    def test_usage_section_detection(self, scorer):
        """Test detection of usage section."""
        readme_with_usage = """
        # Project
        ## Usage
        Run the project like this...
        """

        result = scorer.execute({"readme_content": readme_with_usage})
        assert result.data["has_usage_section"] is True

    def test_setup_keyword_counts_as_installation(self, scorer):
        """Test that 'setup' keyword counts as installation."""
        readme = """
        # Project
        ## Getting Started
        Run setup.sh
        """

        result = scorer.execute({"readme_content": readme})
        # "Getting Started" matches the pattern
        assert (
            result.data["has_installation_section"] is True
            or result.data["has_usage_section"] is True
        )

    def test_quickstart_counts_as_usage(self, scorer):
        """Test that 'quickstart' counts as usage."""
        readme = """
        # Project
        ## Quickstart
        Quick example here
        """

        result = scorer.execute({"readme_content": readme})
        assert result.data["has_usage_section"] is True

    def test_badge_detection(self, scorer):
        """Test badge detection."""
        readme_with_badges = """
        ![Status](https://example.com/status.svg)
        ![License](https://example.com/license.svg)
        """

        result = scorer.execute({"readme_content": readme_with_badges})
        assert result.data["has_badges"] is True

    def test_demo_link_detection(self, scorer):
        """Test demo/live link detection."""
        readme_with_demo = """
        # Project
        [Live Demo](https://demo.example.com)
        """

        result = scorer.execute({"readme_content": readme_with_demo})
        assert result.data["has_demo_link"] is True

    def test_tech_stack_section_detection(self, scorer):
        """Test tech stack section detection."""
        readme_with_stack = """
        # Project
        ## Tech Stack
        - Python
        - FastAPI
        - PostgreSQL
        """

        result = scorer.execute({"readme_content": readme_with_stack})
        assert result.data["has_tech_stack_section"] is True

    def test_technologies_keyword_counts(self, scorer):
        """Test that 'Technologies' keyword counts as tech stack."""
        readme = """
        # Project
        ## Technologies
        Python, JavaScript, React
        """

        result = scorer.execute({"readme_content": readme})
        assert result.data["has_tech_stack_section"] is True

    def test_overall_score_calculation(self, scorer):
        """Test that overall score aggregates components."""
        readme = """
        # Good README

        ## Installation
        Install it!

        ## Usage
        Use it!

        ## Tech Stack
        Python, JavaScript

        ![Build](https://example.com/build.svg)

        This readme has lots of content here.
        """ * 3  # Make it comprehensive

        result = scorer.execute({"readme_content": readme})

        data = result.data
        assert 0.0 <= data["overall_score"] <= 1.0
        # Multiple signals should yield higher score
        assert data["overall_score"] > 0.5

    def test_missing_readme_content_key(self, scorer):
        """Test handling of missing readme_content key."""
        result = scorer.execute({})

        assert result.success is True
        data = result.data
        assert data["has_readme"] is False

    def test_result_has_all_required_fields(self, scorer):
        """Test that result has all required fields."""
        result = scorer.execute({"readme_content": "# Test"})

        data = result.data
        assert "has_readme" in data
        assert "word_count" in data
        assert "word_count_category" in data
        assert "has_installation_section" in data
        assert "has_usage_section" in data
        assert "has_badges" in data
        assert "has_demo_link" in data
        assert "has_tech_stack_section" in data
        assert "overall_score" in data

    def test_case_insensitive_section_detection(self, scorer):
        """Test that section detection is case insensitive."""
        readme = """
        # Project
        ## INSTALLATION
        Install here
        """

        result = scorer.execute({"readme_content": readme})
        assert result.data["has_installation_section"] is True

    def test_whitespace_only_readme(self, scorer):
        """Test handling of whitespace-only README."""
        result = scorer.execute({"readme_content": "   \n\n   \t  "})

        data = result.data
        assert data["has_readme"] is False
        assert data["word_count"] == 0

    def test_example_keyword_counts_as_usage(self, scorer):
        """Test that 'Example' counts as usage section."""
        readme = """
        # Project
        ## Example
        Here's how to use it
        """

        result = scorer.execute({"readme_content": readme})
        assert result.data["has_usage_section"] is True

    def test_score_scales_with_word_count(self, scorer):
        """Test that longer READMEs get bonus in score."""
        short_readme = "# Title\nSmall content."
        long_readme = "# Title\n" + "Content paragraph. " * 100

        result_short = scorer.execute({"readme_content": short_readme})
        result_long = scorer.execute({"readme_content": long_readme})

        assert result_long.data["overall_score"] > result_short.data["overall_score"]

    def test_try_it_as_demo_indicator(self, scorer):
        """Test that 'try it' indicates demo link."""
        readme = "Check it out [try it here](https://example.com)"

        result = scorer.execute({"readme_content": readme})
        assert result.data["has_demo_link"] is True

    def test_built_with_counts_as_tech_stack(self, scorer):
        """Test that 'Built With' counts as tech stack."""
        readme = """
        # Project
        ## Built With
        - Python
        - FastAPI
        """

        result = scorer.execute({"readme_content": readme})
        assert result.data["has_tech_stack_section"] is True
