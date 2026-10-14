# Test Evidence

## Before (on main)
```bash
\$ pytest tests/unit/test_keyword_search.py -k "test_index_empty_corpus"
============================= test session starts =============================
collected 1 item

tests/unit/test_keyword_search.py x                                      [100%]

============================== 1 xfailed in 0.12s ==============================

\$ python -c "from rag.retriever.keyword_search import KeywordSearcher; KeywordSearcher().index([])"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/rag/retriever/keyword_search.py", line 45, in index
    self.bm25 = BM25Okapi(tokenized_corpus)
  File "/site-packages/rank_bm25.py", line 67, in __init__
    self.idf[word] = math.log(self.corpus_size - freq + 0.5) / (freq + 0.5)
ZeroDivisionError: float division by zero

## After (on branch)

\$ pytest tests/unit/test_keyword_search.py -k "test_index_empty_corpus"
============================= test session starts =============================
collected 1 item

tests/unit/test_keyword_search.py .                                      [100%]

============================== 1 passed in 0.11s ===============================

\$ python -c "from rag.retriever.keyword_search import KeywordSearcher; KeywordSearcher().index([])"
# (Clean exit, no error)

## Repo Checks

\$ make test-unit
============================= test session starts =============================
34 passed in 1.45s

\$ make test-integration
no tests ran

\$ make lint
All checks passed!

\$ make typecheck
Success: no issues found in 42 source files
