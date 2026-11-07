fix(rag): let short claims pass the faithfulness overlap check (#59)

## Summary
`FaithfulnessChecker._is_supported()` required two shared non-stop-word tokens and compared tokens with punctuation still attached, so short claims such as "Knows Python" could never be marked supported and comma-separated claims missed their context. This change strips surrounding punctuation from both token sets and also accepts a claim when at least one meaningful token overlaps and the overlap covers at least half of the claim's meaningful tokens. It changes only `_is_supported()`.

## Issue
Closes #59

## Changes
- `rag/evaluator/faithfulness_checker.py`: strip surrounding punctuation from claim and context tokens in `_is_supported()`.
- `rag/evaluator/faithfulness_checker.py`: accept a claim when overlap is at least 2 meaningful tokens, or at least 1 covering half of the claim's meaningful tokens.
- `tests/unit/test_faithfulness_checker.py`: remove the `issue #59` xfail markers from `test_multiple_context_chunks` and `test_multiple_claims_varying_support`, which now pass.
- `tests/unit/test_faithfulness_checker.py`: add `test_short_claim_supported_by_reworded_context` and `test_punctuation_does_not_block_support`.

## Testing
- [ ] **CI is green on this PR (all five jobs)** — required for review
- [x] Unit tests pass (`make test-unit`): 379 passed, 51 xfailed
- [x] Integration tests pass (`make test-integration`): "no tests ran", Path Review has no integration tests yet
- [x] Linter passes (`make lint`): All checks passed!
- [x] Type checker passes (`make typecheck`): Success: no issues found in 76 source files
- [x] New/updated tests cover the changes
- [x] If this fixes a seeded bug: removed its `@pytest.mark.xfail` marker (and any
      matching suppression in `pyproject.toml`) — removed for the two tests this change fixes; see Notes for the one that stays

Before (main) and after (this branch), same repro steps:

```
pytest tests/unit/test_faithfulness_checker.py -v -rx
  before: 18 passed, 4 xfailed
  after:  22 passed, 2 xfailed

pytest tests/unit/test_faithfulness_checker.py --runxfail
  before: 4 failed (3 x #59, 1 x #60), 18 passed
  after:  2 failed (test_partial_support_returns_middle_score, test_none_context_chunk_text), 22 passed

_is_supported("Knows Python", "python expert")
  before: False
  after:  True
_is_supported("Knows Python", "The candidate knows Python")
  before: True
  after:  True
```

`make` is not installed on my machine, so I ran the command each target contains; full output is in my test evidence. I ran this on Windows 11 / Python 3.11.7, not Linux.

## Screenshots / Demo
N/A: no UI change.

## Notes for Reviewers
- **AI use:** I used Claude Code on this change: it helped with the fix and tests, ran the checks, and drafted this description. I reviewed the diff and the pasted output before opening the PR.
- **Left out on purpose:** `test_partial_support_returns_middle_score` keeps its `issue #59` xfail marker. It uses one claim but asserts `0.2 < score < 0.8`, and one claim can only score 0.0 or 1.0, so no change to `_is_supported()` can make it pass. I did not change `check()` or `_extract_claims()` to force it. `test_none_context_chunk_text` is issue #60 and is untouched.
- **Threshold is my proposal:** the "half of the meaningful tokens" rule is untuned. I checked it against the existing "no support" tests (they still pass) but not against tokens like `c++` or `node.js`.
- **Overlap with #90:** PR #90 also rewrites `_is_supported()`, so whichever lands second will conflict. This change is narrower: it does not touch `check()` or `_extract_claims()` and adds no filler-word list.
