"""Red-team test suite for the prompt injection defense (safety/prompt_defense.py).

Runs a curated corpus of known prompt injection attacks against
PromptDefense.is_injection_attempt and asserts every attack is blocked,
plus a corpus of benign inputs that must not be flagged. Fixtures live in
tests/fixtures/injection_attempts/ as JSON files, one attack category per
file, so the corpus can grow without touching this file.
"""

import json
from pathlib import Path

import pytest

from safety.prompt_defense import PromptDefense

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "injection_attempts"


def _load_cases(filename: str) -> list[dict]:
    path = FIXTURES_DIR / filename
    return json.loads(path.read_text(encoding="utf-8"))


def _case_id(case: dict) -> str:
    return case["id"]


ATTACK_FILES = [
    "role_switching.json",
    "instruction_override.json",
    "template_and_code_injection.json",
]

ATTACK_CASES = [case for filename in ATTACK_FILES for case in _load_cases(filename)]
BENIGN_CASES = _load_cases("benign_inputs.json")
KNOWN_GAP_CASES = _load_cases("known_gaps.json")


@pytest.mark.security
class TestPromptInjectionRedTeam:
    """Every curated attack must be blocked; every benign input must pass through."""

    @pytest.mark.parametrize("case", ATTACK_CASES, ids=_case_id)
    def test_attack_is_blocked(self, case):
        assert PromptDefense.is_injection_attempt(case["text"]) is True, (
            f"{case['id']} ({case['description']}) was not detected as an "
            f"injection attempt: {case['text']!r}"
        )

    @pytest.mark.parametrize("case", BENIGN_CASES, ids=_case_id)
    def test_benign_input_not_blocked(self, case):
        assert PromptDefense.is_injection_attempt(case["text"]) is False, (
            f"{case['id']} ({case['description']}) was a false positive: " f"{case['text']!r}"
        )

    @pytest.mark.parametrize("case", KNOWN_GAP_CASES, ids=_case_id)
    @pytest.mark.xfail(
        strict=True,
        reason="manifest D-04: role-switch regex requires the colon immediately "
        "after the role word, so whitespace-before-colon variants bypass detection",
    )
    def test_known_gap_attack_is_blocked(self, case):
        assert (
            PromptDefense.is_injection_attempt(case["text"]) is True
        ), f"{case['id']} ({case['description']}) was not detected: {case['text']!r}"
