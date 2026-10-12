.venv/bin/pytest tests/unit -v -m unit
.venv/bin/pytest tests/integration -v -m integration
make: .venv/bin/pytest: No such file or directory
make: *** [test-integration] Error 1
.venv/bin/ruff check .
make: .venv/bin/ruff: No such file or directory
make: *** [lint] Error 1
.venv/bin/mypy api/ core/ ingestion/ rag/ agent/ safety/
make: .venv/bin/mypy: No such file or directory
make: *** [typecheck] Error 1
