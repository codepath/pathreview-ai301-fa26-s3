"""Tests for scripts/run_evals.py"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import run_evals  # noqa: E402


@pytest.mark.unit
class TestRunEvals:
    """Test suite for the offline eval runner."""

    def test_main_writes_report_for_fixture_profiles(self, tmp_path):
        """Running against the bundled fixture writes a scored eval_results.json."""
        output = tmp_path / "eval_results.json"

        exit_code = run_evals.main(["--output", str(output)])

        assert exit_code == 0
        report = json.loads(output.read_text(encoding="utf-8"))
        assert report["profile_count"] >= 1
        assert report["results"][0]["profile"] == "basic_profile"
        for key in ("relevance_score", "faithfulness_score", "overall_score"):
            assert 0.0 <= report["results"][0][key] <= 1.0

    def test_empty_profiles_dir_exits_nonzero(self, tmp_path):
        """No benchmark profiles is an error, not a silent success."""
        exit_code = run_evals.main(
            ["--profiles-dir", str(tmp_path), "--output", str(tmp_path / "out.json")]
        )

        assert exit_code == 1
