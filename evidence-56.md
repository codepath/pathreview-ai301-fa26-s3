# Evidence: #56 before and after

Environment: macOS 15.7.2 arm64, Python 3.14.7, tiktoken 0.14.0, pytest 9.1.1.
Base commit: `2f4e82f52efbcfcc57d65b3fa5348672163ca088` on branch `fix/56-structural-chunker-no-headings`.
"Before" = fix in `ingestion/chunking/structural_chunker.py` stashed (new tests and xfail removal still applied). "After" = fix applied.

## Repro script

```python
from ingestion.chunking.structural_chunker import StructuralChunker

chunker = StructuralChunker()

plain = "This is a plain document with no headings at all. " * 20
headed = "# Heading\nThis is content."

print("plain document chars:", len(plain))
print("plain document chunks:", len(chunker.chunk(plain, {"source": "issue-56-repro"})))
print("headed document chunks:", len(chunker.chunk(headed, {"source": "control"})))
```

### Before

```text
plain document chars: 1000
plain document chunks: 0
headed document chunks: 1
```

### After

```text
plain document chars: 1000
plain document chunks: 1
headed document chunks: 1
```

## Structural chunker tests

Command: `python -m pytest tests/unit/test_structural_chunker.py -v`

### Before

```text
TestStructuralChunker::test_empty_input_returns_empty_list PASSED [  5%]
TestStructuralChunker::test_whitespace_only_input PASSED [ 11%]
TestStructuralChunker::test_document_with_no_headings FAILED [ 16%]
TestStructuralChunker::test_no_headings_chunk_metadata FAILED [ 22%]
TestStructuralChunker::test_large_document_with_no_headings_is_sub_chunked FAILED [ 27%]
TestStructuralChunker::test_heading_only_document_unchanged PASSED [ 33%]
TestStructuralChunker::test_document_with_nested_headings PASSED [ 38%]
TestStructuralChunker::test_heading_path_format PASSED [ 44%]
TestStructuralChunker::test_large_section_sub_chunked PASSED [ 50%]
TestStructuralChunker::test_chunk_metadata_includes_heading_level PASSED [ 55%]
TestStructuralChunker::test_chunk_metadata_structure PASSED [ 61%]
TestStructuralChunker::test_preserve_source_metadata PASSED [ 66%]
TestStructuralChunker::test_multiple_h1_headings PASSED [ 72%]
TestStructuralChunker::test_heading_path_breadcrumb PASSED [ 77%]
TestStructuralChunker::test_chunks_have_text_content PASSED [ 83%]
TestStructuralChunker::test_section_extraction_with_multiple_levels PASSED [ 88%]
TestStructuralChunker::test_heading_not_in_middle_of_content PASSED [ 94%]
TestStructuralChunker::test_empty_sections_handled PASSED [100%]
FAILED tests/unit/test_structural_chunker.py::TestStructuralChunker::test_document_with_no_headings
FAILED tests/unit/test_structural_chunker.py::TestStructuralChunker::test_no_headings_chunk_metadata
FAILED tests/unit/test_structural_chunker.py::TestStructuralChunker::test_large_document_with_no_headings_is_sub_chunked
========================= 3 failed, 15 passed in 0.31s =========================
```

### After

```text
TestStructuralChunker::test_empty_input_returns_empty_list PASSED [  5%]
TestStructuralChunker::test_whitespace_only_input PASSED [ 11%]
TestStructuralChunker::test_document_with_no_headings PASSED [ 16%]
TestStructuralChunker::test_no_headings_chunk_metadata PASSED [ 22%]
TestStructuralChunker::test_large_document_with_no_headings_is_sub_chunked PASSED [ 27%]
TestStructuralChunker::test_heading_only_document_unchanged PASSED [ 33%]
TestStructuralChunker::test_document_with_nested_headings PASSED [ 38%]
TestStructuralChunker::test_heading_path_format PASSED [ 44%]
TestStructuralChunker::test_large_section_sub_chunked PASSED [ 50%]
TestStructuralChunker::test_chunk_metadata_includes_heading_level PASSED [ 55%]
TestStructuralChunker::test_chunk_metadata_structure PASSED [ 61%]
TestStructuralChunker::test_preserve_source_metadata PASSED [ 66%]
TestStructuralChunker::test_multiple_h1_headings PASSED [ 72%]
TestStructuralChunker::test_heading_path_breadcrumb PASSED [ 77%]
TestStructuralChunker::test_chunks_have_text_content PASSED [ 83%]
TestStructuralChunker::test_section_extraction_with_multiple_levels PASSED [ 88%]
TestStructuralChunker::test_heading_not_in_middle_of_content PASSED [ 94%]
TestStructuralChunker::test_empty_sections_handled PASSED [100%]
============================== 18 passed in 0.24s ==============================
```

## CI checks (after)

- `make lint`: All checks passed!
- `make typecheck`: Success: no issues found in 76 source files
- `make test-unit`: 379 passed, 52 xfailed
- `black --check` on both changed files: 2 files would be left unchanged
- Not run: `make test-integration` (needs Docker), frontend job (no frontend changes)
