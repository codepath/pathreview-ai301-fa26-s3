Fix ZeroDivisionError on empty corpus in KeywordSearcher

## Summary
This pull request prevents a crash when the `KeywordSearcher` tries to index an empty list of documents. I added a guard clause to the `index()` method so it handles empty inputs gracefully without passing them to the rank-bm25 library.

## Issue
Closes #68

## Changes
- Added a check in `rag/retriever/keyword_search.py` to return early if the provided corpus is empty.
- Removed the `@pytest.mark.xfail` marker referencing manifest id H-01 from the covering test in `tests/unit/test_keyword_search.py`.

## Testing
- [x] I have added or updated tests for my changes
- [x] I have run `make test-unit` and `make test-integration`
- [x] I have run `make lint` and `make typecheck`

Test evidence:
(See `test_evidence.md` for full before-and-after terminal output and check results.)

## Screenshots / Demo
N/A because this is a backend logic fix and there are no visual changes to the UI.

## Notes for Reviewers
I used an AI assistant to help identify the correct guard clause syntax to avoid the `ZeroDivisionError` and to draft the layout of this pull request description.
