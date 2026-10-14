## Diagnosis
The section detection failure is caused by overly rigid regular expressions. As noted in the repro evidence, `_detect_sections() uses regex patterns anchored at line starts... no sections are detected`. When a resume contains leading whitespace or indentation before a section header, the strictly anchored `^` regex fails to match it, resulting in the parser missing valid sections entirely.

## Scope
* **In Scope:** Modifying the regex compilation patterns within the `_detect_sections()` function to account for optional leading whitespace. Running and passing the three currently failing tests in the test suite. 
* **Out of Scope:** Refactoring the larger parsing logic in the file, altering how extracted sections are stored or processed, or adding support for new resume section types not currently defined.

## Files Touched
* `ingestion/parsers/resume_parser.py`
* `tests/unit/test_resume_parser.py` (only if the tests themselves require minor spacing adjustments to validate the fix)

## Approach
I will locate the regex strings in `_detect_sections()` (e.g., `r'^Education'`) and update them to allow optional leading whitespace by inserting `\s*` after the start-of-line anchor (e.g., `r'^\s*Education'`). This ensures the regex still requires the section name to be the first text on the line, but prevents indentation from breaking the match.

## Test Plan
1. Re-run the reproduction steps from Unit 2 by executing the test suite: `pytest tests/unit/test_resume_parser.py`.
2. Confirm the three named failing tests still fail due to the `_detect_sections()` bug.
3. Apply the regex update in `resume_parser.py`.
4. Re-run `pytest tests/unit/test_resume_parser.py`.
5. **Expected Outcome:** The three previously failing tests will pass, and the rest of the unit test suite will remain green, confirming the regex successfully captures indented sections without introducing regressions.

## Risks and Unknowns
* **Multi-line flags:** If the `re.MULTILINE` flag is not being used properly, `^` might only match the beginning of the entire file rather than the beginning of each line. I need to verify the regex flags in use.
* **Over-matching:** Allowing whitespace might accidentally trigger false positives if a bullet point in the middle of a paragraph happens to line-wrap and start with a section keyword.

## Deviations
