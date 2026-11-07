# Plan for issue #59: faithfulness checker scores claims unsupported when the context uses different words

## Diagnosis

`FaithfulnessChecker._is_supported()` in `rag/evaluator/faithfulness_checker.py` decides support by requiring at least 2 shared non-stop-word tokens between the claim and the context (`len(meaningful_overlap) >= 2`). The tokens come from `.lower().split()`, so punctuation stays attached to words.

My unit 2 repro shows two failure paths through that one line:

- Short claims can never pass. Quoting my repro: `_is_supported("Knows Python", "python expert")` returned `False`, while `_is_supported("Knows Python", "The candidate knows Python")` returned `True`. "Same claim, same underlying fact, opposite verdicts depending only on whether the context happens to reuse two or more of the claim's words."
- Punctuation breaks matching. Quoting my repro: `_extract_claims` only strips the trailing `.`/`!`/`?`, so the claim's tokens keep commas (`"python,"`, `"javascript,"`), which do not match the context's comma-free tokens. Only `"docker"` overlaps, "one word short of the `>=2` threshold. Removing the commas by hand (no other change) flips the same call to supported."

Under `--runxfail`, three #59 tests fail: `assert 0.2 < 0.0`, `assert 0.0 > 0.5`, `assert 0.2 < 0.0` (`test_partial_support_returns_middle_score`, `test_multiple_context_chunks`, `test_multiple_claims_varying_support`).

## Scope

In scope:
- Make `_is_supported()` tokenize without attached punctuation.
- Replace the fixed `>= 2` overlap count with a rule that also lets a short claim be supported when most of its meaningful tokens appear in the context.
- Remove the `xfail` markers tagged `issue #59` in `tests/unit/test_faithfulness_checker.py` for tests that pass after the fix, and add regression tests for the two repro calls.

Not in scope:
- `test_none_context_chunk_text` (`TypeError` at `faithfulness_checker.py:38`). It is tagged for issue #60, so it stays xfailed.
- Semantic matching, embeddings, stemming, or synonym handling. The issue is about the overlap rule, not about a new matching approach.
- `check()` and `_extract_claims()` behavior, the 10-claim limit, and any other module.

## Files I will touch

- `rag/evaluator/faithfulness_checker.py`: `_is_supported()` only.
- `tests/unit/test_faithfulness_checker.py`: remove #59 `xfail` markers that now pass; add regression tests.

## Approach

1. In `_is_supported()`, strip surrounding punctuation from each token after `.lower().split()` for both claim and context.
2. Compute `meaningful_claim_tokens = claim_tokens - stop_words` and treat the claim as supported when the overlap is at least 1 token and covers at least half of the claim's meaningful tokens (to be tuned against the existing tests).
3. Run the existing test file and adjust the threshold only as far as the issue's examples and the currently passing tests require.
4. Remove the `xfail(strict=True)` markers for the tests that now pass (a strict xfail that passes is reported as a failure, so they must go in the same change).
5. Add two regression tests: the issue's `"Knows Python"` / `"python expert"` pair, and the comma case from `test_multiple_context_chunks`.

## Test plan

Re-run my unit 2 repro steps after the fix:

1. `pytest tests/unit/test_faithfulness_checker.py -v -rx`. Before: `18 passed, 4 xfailed`. Expected after: the #59 tests pass without xfail markers, and `test_none_context_chunk_text` remains xfailed for #60.
2. `pytest tests/unit/test_faithfulness_checker.py --runxfail`. Before: the three #59 failures above. Expected after: only the #60 `TypeError` failure remains.
3. In a Python shell, `c._is_supported("Knows Python", "python expert")`. Before: `False`. Expected after: `True`.
4. `c._is_supported("Knows Python", "The candidate knows Python")` stays `True`, and the "Rust" no-support test in the file still scores below 0.5.

## Risks and unknowns

- `test_partial_support_returns_middle_score` feeds one sentence and asserts `0.2 < score < 0.8`. With one claim the score can only be 0.0 or 1.0, so I do not yet know whether this test can pass with a change to `_is_supported()` alone. If it cannot, I will leave its marker in place and report that on the issue instead of widening scope.
- The "half of the meaningful tokens" threshold is my proposal, not verified. A looser rule could mark unrelated claims as supported, so I will check it against the "no support" tests before keeping it.
- Stripping punctuation could change how tokens like `c++` or `node.js` match. I have not tested those inputs.
- Prior art on the thread: PR #90 (open, by mohtashim-syed, "judge faithfulness claims on content words") already rewrites `_is_supported()`, `check()` and `_extract_claims()` and adds a filler-word list. Znasif's and mohtashim-syed's plan comments on #59 take a similar route. My change is narrower and touches the same function, so whichever lands first will conflict with the other. Under the Path Review house rules a classmate's plan does not block mine; I will build and test on my own fork branch only and will not push to the shared repo.
- I reproduced on Windows 11 / Python 3.11.7 with structlog 26.1.0, not on the Linux environment the issue may assume.

## Deviations

Mostly the plan held. One part ended differently, which the plan listed as an unknown: `test_partial_support_returns_middle_score` still cannot pass. It has one claim, so the score is 0.0 or 1.0 and the assertion `0.2 < score < 0.8` is unreachable from a change to `_is_supported()`. I left its `issue #59` xfail marker in place and did not change `check()` or `_extract_claims()` to force it. The other two #59 tests (`test_multiple_context_chunks`, `test_multiple_claims_varying_support`) now pass, so I removed their markers. The threshold I built is: overlap of at least 2 meaningful tokens, or at least 1 covering half of the claim's meaningful tokens. I did not test `c++` or `node.js` tokens.
