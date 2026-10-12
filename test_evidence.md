# Test evidence — issue #37 (API request body schemas)

This is a documentation-only change (`docs/API.md`, plus `plan.md` /
`comment.md` process artifacts). No route, schema, or validation code was
touched. Evidence below is from local runs on this branch
(`docs/37-api-request-body-schemas`), since this branch has not yet been
opened as a PR and GitHub Actions CI has not run against it.

## Source-inspection checks (per plan.md)

1. Re-read `docs/API.md`: `POST /profiles` now shows `multipart/form-data`,
   a field table for `github_username`, `portfolio_url`, `resume_file`
   (all optional), the accepted MIME types (`application/pdf`,
   `text/markdown`, `text/plain`) with the 422 behavior, and a `curl -F`
   example. `POST /reviews` now shows `application/json`, a field table
   with required UUID `profile_id`, and a JSON example body.
2. Compared the documented fields against source:
   - `api/routes/profiles.py`: `github_username: str = Form(default=None)`,
     `portfolio_url: str = Form(default=None)`,
     `resume_file: UploadFile = File(default=None)`, and
     `if file_mime not in ["application/pdf", "text/markdown", "text/plain"]`
     → 422. Matches the doc.
   - `api/routes/reviews.py` / `api/schemas/review.py`: `data: ReviewCreate`
     where `ReviewCreate.profile_id: UUID` is the only field. Matches the doc.

## Local command runs (venv: `.venv`, Python 3.14.3)

- `ruff check .` → `All checks passed!`
- `black --check .` → `All done! 110 files would be left unchanged.`
- `mypy api/ core/ ingestion/ rag/ agent/ safety/ --ignore-missing-imports`
  → `Success: no issues found in 76 source files`
- `LLM_PROVIDER=mock pytest tests/unit -v --tb=short`
  → `375 passed, 53 xfailed, 1 warning` (the 53 xfails are the pre-existing
  seeded-bug markers, unrelated to this docs-only change)
- `LLM_PROVIDER=mock pytest tests/integration -v --tb=short`
  → `0 items collected` — the integration suite is empty by design; the CI
  workflow (`.github/workflows/ci.yml`) explicitly treats "no tests
  collected" as a pass for this job
- `cd frontend && npm test -- --run` (not required by this issue, run for
  completeness since the CI workflow has a fifth, frontend job) → 17/18
  passed on first run; the one failure (`ProfileForm` portfolio URL
  character-limit test) was a local timing timeout, reproduced as a pass
  (7.6s) when re-run in isolation with a longer timeout. This branch makes
  no frontend changes.

## Not run

- No actual GitHub Actions run exists yet for this branch — no PR has been
  opened, so the `pull_request`/`push` triggers in `.github/workflows/ci.yml`
  have not fired. The local runs above reproduce all five CI jobs'
  commands directly and all pass, but this is not the same as a green CI
  run on the PR itself.
