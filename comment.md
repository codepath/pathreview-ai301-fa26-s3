Reproduced on commit 2f4e82f (Windows 11, Python 3.13.5).

Cause. The regex patterns in _detect_sections() and _strip_markdown() use `^` which only matches at the start of a line with no leading whitespace. When PDF extraction adds indentation, the patterns fail and you get an empty list instead of section names.

Fix. Change the four patterns from `^` to `^\s*` in _detect_sections() at lines 134-135. Same fix in _strip_markdown() around line 98. Remove @pytest.mark.xfail(strict=True) from test_detect_sections, test_parse_single_column_resume_text, test_parse_resume_no_work_experience, test_parse_markdown_resume, and test_strip_markdown_syntax. They're marked strict so a passing test shows as XPASS(strict) which fails CI.

Scope. Only changing resume_parser.py and test_resume_parser.py. Not touching anything else.

Test. Before fix: run the indented snippet from the issue (expect []). After fix: run the same (expect ['Education', 'Skills']). Run unindented snippet both ways (expect ['Education', 'Skills'] either way). Full test suite: expect all 5 tests to pass, no regressions.

Not confirmed. Haven't checked what else calls _detect_sections(). Haven't verified the two markdown tests are truly out of scope. Will check both before changing anything.
