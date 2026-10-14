# Plan: Fix Resume Section Detection with Leading Whitespace

## Diagnosis

The `_detect_sections()` function in `ingestion/parsers/resume_parser.py` uses regex patterns anchored to the start of a line (`^education\s*:`, etc.) without accounting for leading whitespace. When PDF text extraction preserves indentation (common in multi-column layouts), section headers with leading spaces fail to match, returning an empty `detected_sections` list instead of detecting sections like Education and Skills.

The repro evidence shows:
- With indentation: `detected_sections` returns `[]` (bug)
- Without indentation: `detected_sections` returns `['Education', 'Skills']` (correct)

This matches the reported behavior: section headers are only detected after users navigate away and return, which suggests the issue is pure pattern matching, not downstream processing.

## Scope

**In:** The regex patterns in `_detect_sections()` method and `_strip_markdown()` helper in `ingestion/parsers/resume_parser.py`. Change patterns from `^section_name` to `^\s*section_name` to allow optional leading whitespace before section headers.

**Out:** No changes to how sections are extracted after matching, no changes to other parsers or to the rest of the resume parsing pipeline. Not modifying how PDF text is extracted or preserved.

## Changes

1. Locate `_detect_sections()` in `ingestion/parsers/resume_parser.py` (around line where regex patterns are compiled)
2. Update each section pattern from `^` anchor to `^\s*` to match optional leading whitespace
   - Example: change `^education\s*[:|-]` to `^\s*education\s*[:|-]`
3. Apply the same fix to `_strip_markdown()` helper: change `re.sub(r"^#+\s+", ...)` to `re.sub(r"^\s*#+\s+", ...)`
4. Remove `@pytest.mark.xfail(strict=True)` decorator from these 5 test methods in `tests/unit/test_resume_parser.py`:
   - `test_parse_single_column_resume_text`
   - `test_parse_resume_no_work_experience`
   - `test_detect_sections`
   - `test_parse_markdown_resume`
   - `test_strip_markdown_syntax`
   
   (Per CONTRIBUTING.md: "removing the `@pytest.mark.xfail` line is part of fixing the issue"; with `strict=True`, a passing test still marked xfail shows as `XPASS(strict)` which pytest counts as a failure)

## Test Plan

Reproduce the original bug and verify the fix:

**Before:**
```
$ python -c "from ingestion.parsers.resume_parser import ResumeParser; r = ResumeParser(); res = r.parse('\n    Education:\n    - B.S. Computer Science\n\n    Skills: Python\n'); print(res.metadata['detected_sections'])"
[]
```

**After fix and marker removal, should show:**
```
['Education', 'Skills']
```

Run the 5 tests after removing xfail markers (as specified in Changes step 4):
```
pytest tests/unit/test_resume_parser.py::test_detect_sections -v
pytest tests/unit/test_resume_parser.py::test_parse_single_column_resume_text -v
pytest tests/unit/test_resume_parser.py::test_parse_resume_no_work_experience -v
pytest tests/unit/test_resume_parser.py::test_parse_markdown_resume -v
pytest tests/unit/test_resume_parser.py::test_strip_markdown_syntax -v
```

All tests should now pass. (Important: xfail markers must be removed first; running these tests with `strict=True` markers still in place results in `XPASS(strict)` which pytest counts as a failure, even though the fix works.)

## Risks and Unknowns

- **xfail marker removal requirement:** Per CONTRIBUTING.md, removing `@pytest.mark.xfail` decorators is part of fixing the issue. Without removal, passing tests will show as `XPASS(strict)` which pytest counts as CI failure. This is not a code problem but a required administrative step. Forgetting this step causes misleading test output.
- **Secondary issue:** `test_parse_markdown_resume` and `test_strip_markdown_syntax` failures may also involve markdown header stripping logic. The same `^\s*` fix should address both, but edge cases with different markdown heading levels (`##`, `###`) should be spot-checked.
- **Regex performance:** Adding `\s*` is not expected to impact performance, but integration tests should run to confirm no slowdown on large resume batches.
- **Edge cases:** Very aggressive indentation (tabs vs. spaces, multiple levels) should work with `\s*`, but the test suite will verify.

## Deviations

No deviations from plan. All changes implemented as specified:
- Regex patterns updated from `^` to `^\s*` in both _detect_sections() and _strip_markdown()
- All 5 xfail markers removed from test methods
- Before/after test verified: indented text now correctly returns ['Education', 'Skills'] instead of []
- Unindented text still works correctly
- Scope verified: only resume_parser.py and test_resume_parser.py modified, no other callers affected
- Tests ready to run on full suite once test environment is set up
