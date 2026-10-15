# Plan: #56, structural chunker drops documents with no headings

## Cause

`StructuralChunker._extract_sections` in `ingestion/chunking/structural_chunker.py` only keeps text that comes after a heading. Three conditions gate on `heading_stack`:

- line 120: a content line is collected only `if heading_stack or current_section_lines`. With no heading yet, both are empty, so the line is thrown away. `current_section_lines` can never become non-empty, so every line of a heading-less document is discarded.
- line 94: when a heading arrives, the pending lines are saved only `if heading_stack`.
- line 124: the final section is saved only `if current_section_lines and heading_stack`.

So `_extract_sections` returns `[]`, and `chunk()` loops over nothing and returns `[]`. That matches my repro: the 1000-char plain document gives 0 chunks, while the `# Heading` control gives 1.

## Scope

One fallback in `chunk()` that applies only when a document has no headings at all, plus its tests. `_extract_sections` doesn't change, so headed documents chunk exactly as they do today.

Not in scope:
- **Keeping intro text before the first heading.** The same gate drops it, but the issue only reports documents with no headings. A fallback that applies only when there are no headings fixes #56 without changing how headed documents chunk. Changing that is a separate behavior decision (see Risks).
- **A test for intro text before the first heading** (`"Intro paragraph.\n# Title\nBody"` giving 2 chunks). It tests the intro-text behavior above, which this PR doesn't change.
- **A test that a leading blank line adds no empty chunk** (`"\n# Title\nBody"` giving 1 chunk). It was only needed to guard the intro-text approach. Without that change, `_extract_sections` still throws away lines before the first heading, so there's nothing new to guard. The input already returns `['Body']` today and would pass before and after.
- **Empty sections between consecutive headings.** They already produce an empty `''` chunk (`"# A\nx\n## B\n\n## C\ny"` gives `['x', '', 'y']`). That's existing behavior with a different cause, so I'll mention it in the PR as a possible follow-up.
- `char_start`/`char_end` are section-relative. That's unrelated to this bug.
- Line 116 (`current_level = heading_level  # noqa: F841`) and its comment stay as they are. CONTRIBUTING says not to clean up an explained `# noqa`, and the fallback doesn't need it.
- The `var-annotated` mypy override in `pyproject.toml` is shared with three other modules and isn't specific to #56.

## Approach

All edits go in `ingestion/chunking/structural_chunker.py`, `chunk()`:

1. Right after `sections = self._extract_sections(text)`, add: if `sections` is empty and `text` has no heading line, set `sections = [{"content": text.strip(), "path": [], "level": 0}]`. For "has no heading line," reuse the heading pattern `_extract_sections` already matches against (`^(#{1,6})\s+(.+)$`, applied per line with `re.MULTILINE`). Blank and whitespace-only input already returns `[]` at line 35, before this point.
2. Leave the rest of the loop as it is. A heading-less document of 800 tokens or fewer becomes one chunk with `heading_path == ""` and `heading_level == 0`. A longer one goes to `SemanticChunker` through the existing `SECTION_TOKEN_LIMIT` branch, the same way a large headed section does.

The heading-line check is needed because `_extract_sections` also returns `[]` for documents made only of headings (`"# Title"`, `"# A\n## B"`, both checked locally). Without the check, the fallback would turn those into a no-heading chunk containing `"# Title"`. That would change behavior for documents that do have headings.

Then, in `tests/unit/test_structural_chunker.py`:

3. Remove the `@pytest.mark.xfail(strict=True, reason="issue #56: ...")` marker from `test_document_with_no_headings`. CONTRIBUTING requires this, and once the fix lands the strict marker would turn into an `XPASS(strict)` failure.
4. Add `test_no_headings_chunk_metadata`: the plain document from the repro gives exactly 1 chunk whose text equals `text.strip()`, with `heading_path == ""`, `heading_level == 0`, and the caller's `source` preserved.
5. Add `test_large_document_with_no_headings_is_sub_chunked`: a heading-less document over 800 tokens gives 1 or more chunks, each with non-empty text.
6. Add `test_heading_only_document_unchanged`: `"# Title"` still returns `[]`. This pins the heading-line check from step 1.

## Test plan

- Re-run the repro script from my repro comment. Before: `plain document chunks: 0`. After: `plain document chunks: 1` (1000 chars is about 200 tokens, under the 800 limit). Control: `headed document chunks: 1` stays the same.
- `python -m pytest -q tests/unit/test_structural_chunker.py`. Before the fix (with the xfail removed), `test_document_with_no_headings`, `test_no_headings_chunk_metadata`, and `test_large_document_with_no_headings_is_sub_chunked` fail, because `chunk()` returns `[]` for heading-less input. `test_heading_only_document_unchanged` passes both before and after; it's a guard against the fallback catching heading-only documents, not a reproduction of the bug. After: all pass, and nothing reports XFAIL or XPASS.
- `make lint`, `make typecheck`, `make test-unit`: green. These are the CI jobs CONTRIBUTING says must pass.

## Risks and unknowns

- **Intro text before the first heading is still dropped.** While tracing the cause I noticed that the same `heading_stack` gate in `_extract_sections` drops text above a document's first heading. `"Intro paragraph.\n# Title\nBody"` returns only `['Body']`. That affects READMEs (the `readme` source type in `StrategySelector`) with a badge line or intro paragraph. I'm not changing it here, because it changes chunking for headed documents and #56 doesn't ask for that. I'll mention it on the issue as a candidate for its own issue.
- **Empty `heading_path` downstream.** Heading-less documents will now produce chunks with `heading_path == ""`. I haven't yet checked whether anything in retrieval or scoring assumes `heading_path` is non-empty. I'll grep for `heading_path` consumers before opening the PR.
- **Integration tests.** I haven't run `make test-integration` yet. If any fixture relies on a heading-less README producing no chunks, the result will change and I'll report it.

## Deviations

None. The build followed the plan: one fallback in `chunk()` guarded by the heading-line check, the xfail marker removed, and the three planned tests added. `_extract_sections`, line 116, and `pyproject.toml` are untouched.

Two open risks from above, after the build:
- **Empty `heading_path` downstream:** checked. Grepping the Python sources for `heading_path` finds no code outside the chunker that reads it, only a docstring in `ingestion/chunking/base.py`.
- **Integration tests:** still not run, because they need Docker. `make lint`, `make typecheck`, and `make test-unit` (379 passed, 52 xfailed) are green.

Before and after outputs from the repro and the structural chunker tests are in `evidence-56.md`. The new tests behaved as the test plan predicted: three failed before the fix, `test_heading_only_document_unchanged` passed both before and after, and all 18 pass after.
