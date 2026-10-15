fix(ingestion): chunk documents with no headings as a single section

## Summary
`StructuralChunker.chunk()` returned no chunks for any document without a markdown heading, because `_extract_sections` only keeps text that comes after a heading. This PR adds a fallback in `chunk()`: when `_extract_sections` returns nothing and the text has no heading line, the whole document becomes one section with an empty `heading_path` and `heading_level` 0. From there the existing loop handles it, so a document over 800 tokens goes to `SemanticChunker` the same way a large headed section does. `_extract_sections` is unchanged, so headed documents chunk exactly as before.

## Issue
Closes #56

## Changes
- `ingestion/chunking/structural_chunker.py`: add the no-headings fallback in `chunk()`. It only applies when the text has no line matching the heading pattern `_extract_sections` already uses, so heading-only documents like `"# Title"` still return `[]`.
- `tests/unit/test_structural_chunker.py`: remove the `xfail(strict=True)` marker for #56 from `test_document_with_no_headings`.
- `tests/unit/test_structural_chunker.py`: add `test_no_headings_chunk_metadata` (one chunk, text equals `text.strip()`, `heading_path == ""`, `heading_level == 0`, `source` kept), `test_large_document_with_no_headings_is_sub_chunked` (a heading-less document over 800 tokens still produces non-empty chunks), and `test_heading_only_document_unchanged` (`"# Title"` still returns `[]`).

## Testing
- [ ] **CI is green on this PR (all five jobs)** — required for review
- [x] Unit tests pass (`make test-unit`)
- [ ] Integration tests pass (`make test-integration`)
- [x] Linter passes (`make lint`)
- [x] Type checker passes (`make typecheck`)
- [x] New/updated tests cover the changes
- [x] If this fixes a seeded bug: removed its `@pytest.mark.xfail` marker (and any
      matching suppression in `pyproject.toml`)

Repro from my comment on #56, run on `main` and then on this branch:

```text
# main (2f4e82f)
plain document chars: 1000
plain document chunks: 0
headed document chunks: 1

# this branch (edcabe1)
plain document chars: 1000
plain document chunks: 1
headed document chunks: 1
```

`pytest tests/unit/test_structural_chunker.py` against `main`'s chunker: `3 failed, 15 passed` (the three no-heading tests). On this branch: `18 passed`.

- `make test-unit`: 379 passed, 52 xfailed
- `make lint`: All checks passed!
- `make typecheck`: Success: no issues found in 76 source files
- `make test-integration`: `no tests ran` (exit code 5). `tests/integration/` only contains `__init__.py`, so there's nothing to collect. That's why the box is unticked.
- CI hasn't run yet because the PR isn't open, so that box is unticked too.
- `black --check` on both changed files: unchanged. No frontend changes, so the frontend tests weren't run.

## Screenshots / Demo
N/A. This is a backend chunking change with no UI.

## Notes for Reviewers
- Heading-less documents now produce chunks with `heading_path == ""`. I grepped for `heading_path`: nothing outside the chunker reads it, only a docstring in `ingestion/chunking/base.py`.
- Not changed here, possible follow-ups: text above a document's first heading is still dropped (`"Intro paragraph.\n# Title\nBody"` returns only `['Body']`), and an empty section between two headings still produces an empty `''` chunk. Both change how headed documents chunk, which #56 doesn't ask for, so I left them out, as my plan comment said.

Claude Code helped me with making this PR. It wrote the code in the PR, and I reviewed it thoroughly before making commits. It also helped trace the cause, draft the plan, and write this PR description. It also ran the tests and made sure everything was correct before I opened the PR
