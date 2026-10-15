I reproduced [#56](https://github.com/codepath/pathreview-ai301-fa26-s3/issues/56).

## Environment

- macOS 15.7.2, Apple Silicon (`arm64`)
- Python 3.14.7
- `tiktoken` 0.14.0
- Commit: `2f4e82f52efbcfcc57d65b3fa5348672163ca088`

## Steps

From the repository root, I created a Python 3.14 virtual environment and installed `pytest` and `tiktoken`.

I then ran:

```python
from ingestion.chunking.structural_chunker import StructuralChunker

chunker = StructuralChunker()

plain = "This is a plain document with no headings at all. " * 20
headed = "# Heading\nThis is content."

print("plain document chars:", len(plain))
print("plain document chunks:", len(chunker.chunk(plain, {"source": "issue-56-repro"})))
print("headed document chunks:", len(chunker.chunk(headed, {"source": "control"})))
```

The output was:

```text
plain document chars: 1000
plain document chunks: 0
headed document chunks: 1
```

I also ran the existing test:

```bash
python -m pytest -q tests/unit/test_structural_chunker.py::TestStructuralChunker::test_document_with_no_headings -rx
```

which reported:

```text
XFAIL ...test_document_with_no_headings - issue #56: structural chunker drops documents with no headings
```

## Result

The heading-less document produces no chunks, while the headed control document produces one chunk. This matches the behavior described in issue #56.

The existing test is marked as an expected failure for this issue. I reproduced the issue locally and will investigate the chunking logic before making the fix.