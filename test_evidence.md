# Test evidence for #59 (branch fix/59-faithfulness-token-overlap)

Environment: Windows 11, Python 3.11.7, fresh venv with `pip install -e ".[dev]"`. `make` is not installed on this machine, so each `make` target below was run as the command its Makefile target contains (named in each heading). The unit 2 repro steps were re-run on `main` (before) and on this branch (after).

## BEFORE (main)
XFAIL tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_partial_support_returns_middle_score - issue #59: faithfulness checker can never mark short claims as supported
XFAIL tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_multiple_context_chunks - issue #59: faithfulness checker can never mark short claims as supported
XFAIL tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_multiple_claims_varying_support - issue #59: faithfulness checker can never mark short claims as supported
XFAIL tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_none_context_chunk_text - issue #60: faithfulness checker crashes when a context chunk has text: None
======================== 18 passed, 4 xfailed in 4.67s ========================
-- --runxfail
FAILED tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_partial_support_returns_middle_score
FAILED tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_multiple_context_chunks
FAILED tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_multiple_claims_varying_support
FAILED tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_none_context_chunk_text
4 failed, 18 passed in 1.90s
-- direct calls
False
True

## AFTER (fix/59-faithfulness-token-overlap)
XFAIL tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_partial_support_returns_middle_score - issue #59: faithfulness checker can never mark short claims as supported
XFAIL tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_none_context_chunk_text - issue #60: faithfulness checker crashes when a context chunk has text: None
======================== 22 passed, 2 xfailed in 2.13s ========================
-- --runxfail
FAILED tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_partial_support_returns_middle_score
FAILED tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_none_context_chunk_text
2 failed, 22 passed in 2.03s
-- direct calls
True
True

## make test-unit (make not installed on this machine; ran its command: pytest tests/unit -v -m unit)
    self._kind = _ParameterKind(kind)
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

tests/unit/test_review_service.py::TestReviewService::test_list_reviews_returns_reviews_list
  C:\Users\Abish\anaconda3\Lib\inspect.py:2330: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    return _signature_fromstr(cls, func, s, skip_bound_arg)
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================ 379 passed, 51 xfailed, 3 warnings in 33.82s =================

## make test-integration (pytest tests/integration -v -m integration)
configfile: pyproject.toml
plugins: anyio-4.15.1, hypothesis-6.169.0, platformdirs-4.13.0, asyncio-1.4.0, benchmark-5.3.0, cov-7.1.0, pytest_httpserver-1.2.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 0 items

============================ no tests ran in 0.88s ============================

## make lint (ruff check .)
All checks passed!

## make typecheck (mypy api/ core/ ingestion/ rag/ agent/ safety/)
Success: no issues found in 76 source files

## Notes
- Both the `make test-unit` and `make test-integration` lines are pasted as run. Integration reports "no tests ran" because Path Review has no integration tests yet.
- `test_partial_support_returns_middle_score` still fails under `--runxfail` and keeps its `issue #59` xfail marker: it feeds one claim but asserts `0.2 < score < 0.8`, which one claim cannot produce. This is recorded under Deviations in plan.md. `test_none_context_chunk_text` (#60) is out of scope and stays xfailed.
- CI has not run: the PR is not open yet.
