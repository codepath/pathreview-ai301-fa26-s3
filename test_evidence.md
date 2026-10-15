# Test evidence: #56, structural chunker drops documents with no headings

Environment: macOS 15.7.2 arm64, Python 3.14.7, tiktoken 0.14.0, pytest 9.1.1. Docker not running.

- Before = `main` at `2f4e82f52efbcfcc57d65b3fa5348672163ca088`, checked out in a separate worktree, with imports forced to that worktree (`PYTHONPATH`) so the editable install doesn't load the branch's code.
- After = `fix/56-structural-chunker-no-headings` at `edcabe16d881b5bd35bc4383263e7769580fd03d`.

## Repro (from my repro comment on #56)

```python
from ingestion.chunking.structural_chunker import StructuralChunker

chunker = StructuralChunker()

plain = "This is a plain document with no headings at all. " * 20
headed = "# Heading\nThis is content."

print("plain document chars:", len(plain))
print("plain document chunks:", len(chunker.chunk(plain, {"source": "issue-56-repro"})))
print("headed document chunks:", len(chunker.chunk(headed, {"source": "control"})))
```

### Before (main)

```text
plain document chars: 1000
plain document chunks: 0
headed document chunks: 1
```

### After (branch)

```text
plain document chars: 1000
plain document chunks: 1
headed document chunks: 1
```

The heading-less document goes from 0 chunks to 1. The headed control stays at 1.

## Regression tests

Command: `python -m pytest tests/unit/test_structural_chunker.py -q`

### Before (main's chunker, branch's test file)

```text
FAILED tests/unit/test_structural_chunker.py::TestStructuralChunker::test_document_with_no_headings
FAILED tests/unit/test_structural_chunker.py::TestStructuralChunker::test_no_headings_chunk_metadata
FAILED tests/unit/test_structural_chunker.py::TestStructuralChunker::test_large_document_with_no_headings_is_sub_chunked
3 failed, 15 passed in 0.48s
```

`test_heading_only_document_unchanged` passes before and after. It guards the heading-line check, so it isn't a reproduction of the bug.

### After (branch)

```text
18 passed in 0.36s
```

No XFAIL or XPASS: the `xfail` marker for #56 is removed.

## Repo checks (after, on the branch)

- `make test-unit`: `379 passed, 52 xfailed, 1 warning in 18.01s`
- `make lint`: `All checks passed!`
- `make typecheck`: `Success: no issues found in 76 source files`
- `black --check` on both changed files: `2 files would be left unchanged.`
- `make test-integration`: stops with no tests collected (exit code 5). `tests/integration/` only contains `__init__.py`, so this isn't caused by the change.

  ```text
  collecting ... collected 0 items

  ============================ no tests ran in 0.24s =============================
  make: *** [test-integration] Error 5
  ```

- Frontend tests: not run. This PR has no frontend changes.
