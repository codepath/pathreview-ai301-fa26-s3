Notify registered webhooks when a review finishes (#35)

## Summary
Clients had no way to find out a review was done except by polling: `POST /webhooks` returned 404, `callback_url` on `POST /reviews` was silently ignored, and `process_review()` ended without any outbound call. This PR adds `POST /webhooks`, which stores a callback URL on the user's account, and makes `process_review()` POST the finished review (the same JSON as `GET /reviews/{id}`) to each of the owner's URLs when a review reaches `complete` or `failed`. The URL is registered on the account rather than per review because, in my repro, the whole pipeline finished in the same second the review was created, so a URL registered after `POST /reviews` would race the review and often miss it.

## Issue
Closes #35

## Changes
- `core/models/webhook.py` (new) and `core/models/__init__.py`: `Webhook` model (`id`, `user_id` FK to users with cascade delete, `url`, `created_at`), unique on `(user_id, url)`.
- `alembic/versions/003_add_webhooks_table.py` (new): creates the `webhooks` table and an index on `user_id`; `down_revision` is 002.
- `api/schemas/webhook.py` (new): `WebhookCreate(url: AnyHttpUrl)` and `WebhookResponse`.
- `api/routes/webhooks.py` (new) and `api/main.py`: authenticated `POST /webhooks`. A non-http(s) URL gets a 422; registering the same URL again returns the existing record.
- `core/services/webhook_service.py` (new): `register_webhook()`, and `notify_review_finished()`, which reloads the review from the DB, skips unfinished reviews, and POSTs the payload to each URL with one attempt and a 5 s timeout. It logs `webhook_delivered` or `webhook_delivery_failed` and never raises.
- `core/services/review_service.py`: the pipeline body moved unchanged into `_process_review()`; `process_review()` now calls it inside `try/finally`, and the `finally` calls `notify_review_finished()`, so every exit path notifies.
- `tests/unit/test_webhook_service.py` (new) and `tests/unit/test_review_service.py`: 10 tests covering delivery of `complete` and `failed` reviews, no delivery for unfinished or missing reviews or users with no webhooks, the DB reload, an unreachable URL and a broken session being logged instead of raised, and `process_review()` notifying on an early return.
- `docs/API.md`: documents `POST /webhooks` and the delivered payload.

## Testing
- [ ] **CI is green on this PR (all five jobs)** — required for review
- [x] Unit tests pass (`make test-unit`)
- [ ] Integration tests pass (`make test-integration`)
- [x] Linter passes (`make lint`)
- [ ] Type checker passes (`make typecheck`)
- [x] New/updated tests cover the changes
- [ ] If this fixes a seeded bug: removed its `@pytest.mark.xfail` marker (and any
      matching suppression in `pyproject.toml`)

Run on Linux, Python 3.12.3, Postgres 16 in Docker, `LLM_PROVIDER=mock`, branch @ `fa8d761`.

Check results:

```
$ make test-unit
================= 385 passed, 53 xfailed, 6 warnings in 11.04s =================

$ make test-integration
collecting ... collected 0 items
============================ no tests ran in 0.14s =============================
make: *** [Makefile:43: test-integration] Error 5

$ make lint
.venv/bin/ruff check .
All checks passed!

$ make typecheck
.venv/bin/mypy api/ core/ ingestion/ rag/ agent/ safety/
.venv/lib/python3.12/site-packages/numpy/__init__.pyi:737: error: Type statement is only supported in Python 3.12 and greater  [syntax]
Found 1 error in 1 file (errors prevented further checking)
make: *** [Makefile:57: typecheck] Error 2

$ .venv/bin/mypy --python-version 3.12 api/ core/ ingestion/ rag/ agent/ safety/
Success: no issues found in 80 source files
```

- **Integration** is unticked because Path Review has no integration tests yet, so the target stops with "no tests ran".
- **Typecheck** is unticked because it fails, and it fails identically on `main`. `pyproject.toml` sets mypy to `python_version = "3.11"`, the numpy stubs installed under Python 3.12 use 3.12-only syntax, and mypy stops there before checking any project file. With `--python-version 3.12` the branch is clean (last command above). I didn't change the mypy config, since it's outside #35.
- **Seeded bug** is unticked because #35 isn't one: `grep -rn "issue #35:" tests` finds no marker.

Before/after: my Unit 2 repro, re-run with the same script, DB, and seed data. Before = server running `main` @ `2f4e82f`; after = this branch.

| Step | Before (`main`) | After (branch) |
|---|---|---|
| `/openapi.json` lists `/webhooks` | no | yes |
| `POST /webhooks {"url": "http://127.0.0.1:9999/hook"}` | 404 | 200, `id` + `url` returned |
| same request again | 404 | 200, same `id`; 1 row in `webhooks` |
| create a review, poll 5 s, wait 5 s | `complete`; listener got **0** requests | `complete`; listener got **exactly 1** POST, `id` and `"status":"complete"` match |
| webhook body vs `GET /reviews/{id}` | no body | identical |
| server log after `review_processing_completed` | nothing | `webhook_delivered ... status_code=200` |
| `POST /webhooks {"url": "not-a-url"}` | 404 | 422 |
| user2 (no webhook) creates a review | 0 requests | 0 requests, no `webhook_*` log line |
| listener stopped, user1 creates a review | `complete` | `complete`, `webhook_delivery_failed error='All connection attempts failed'`, no traceback |

Before (`main`), key output:

```
$ curl -s -w "\n  HTTP %{http_code}\n" -X POST $API/webhooks ... -d '{"url": "http://127.0.0.1:9999/hook"}'
{"detail":"Not Found"}
  HTTP 404

[01:14:25.379] {"review_id":"3458dd8d-...","status":"complete","progress_pct":0}

## Listener after step 6 (0 request(s))
listening on 127.0.0.1:9999

[info] review_processing_completed  overall_score=0.81 review_id=3458dd8d-...
(no further log lines for this review)
```

After (this branch), key output:

```
$ curl -s -w "\n  HTTP %{http_code}\n" -X POST $API/webhooks ... -d '{"url": "http://127.0.0.1:9999/hook"}'
{"id":"56dc199c-6ee7-4f6b-9f65-057cf19c4c10","url":"http://127.0.0.1:9999/hook","created_at":"2026-10-08T06:54:21.779402Z"}
  HTTP 200

[01:14:45.956] {"review_id":"05aaa210-...","status":"complete","progress_pct":0}

## Listener after step 6 (1 request(s))
listening on 127.0.0.1:9999
[2026-10-26T01:14:46.005995+00:00] POST /hook {"id":"05aaa210-f041-4c5a-b5a2-0df4b19995b2","profile_id":"e1bd943f-...","status":"complete","sections":[...],"overall_score":0.81,...}

## Webhook body vs GET /reviews/{id}
identical

[info]    review_processing_completed  overall_score=0.81 review_id=05aaa210-...
[info]    webhook_delivered            review_id=05aaa210-... status_code=200 url=http://127.0.0.1:9999/hook

$ POST /webhooks {"url": "not-a-url"}
  HTTP 422

listener stopped, user1 creates a review:
[info]    review_processing_completed  review_id=6f60aafd-...
[warning] webhook_delivery_failed      error='All connection attempts failed' review_id=6f60aafd-... url=http://127.0.0.1:9999/hook
```

The `created_at` of 2026-10-08 is from my first test run; the DB wasn't reset, so registering the same URL returns that existing row. The POST arrived about 85 ms after the review's stored `updated_at`.

## Screenshots / Demo
N/A: this is an API-only change with no UI. The before/after transcript under Testing shows the behavior a screenshot would.

## Notes for Reviewers
**AI use.** I used Claude (Claude Code) throughout this change: to help draft the plan, write the code and tests, run the checks and the before/after repro, and draft this description. I reviewed every line of the diff, and I checked each claim here against the diff and the run output before posting.

**Changes from my posted plan** (all recorded in my plan's deviation notes):
- `process_review()` wraps a new `_process_review()` instead of re-indenting its ~100-line body inside `try/finally`, so the diff shows a small change. Every exit path is still covered.
- The notifier has three `try` blocks (DB lookup, HTTP client, each URL) instead of one, so one bad URL can't stop delivery to the others, and the log names the stage that failed. It still never raises.
- One `httpx.AsyncClient` is shared across a user's URLs instead of one per URL.
- Migration 003 also adds an index on `webhooks.user_id`, since the notifier looks webhooks up by user on every finished review.
- `register_webhook()` takes `user_id: str`, matching the models' `UUID(as_uuid=False)`; mypy caught the mismatch.
- The notifier reloads the review with `populate_existing=True`. Without it, my first live run sent an `updated_at` that didn't match `GET /reviews/{id}`, because the session doesn't expire objects on commit and returned the cached value. My mocked unit tests couldn't catch this; only the live run did.

**Left out on purpose:** listing or deleting webhooks, `callback_url` on `POST /reviews` (still ignored, as on `main`), retries, payload signing, and a delivery queue. The issue asks only for registration and delivery, and each of these is its own design decision.

**Questions for you:**
- **SSRF.** The server will POST to any http(s) URL a user registers, including loopback and internal addresses. I didn't block private ranges, because my own test relies on `127.0.0.1`. Should that be restricted, here or in a follow-up?
- **Existing timestamp offset, not changed here.** `GET /reviews/{id}` reports `updated_at` four hours ahead of the stored time. The app writes a naive UTC datetime into a `timestamptz` column, and it's read back as local time. It's on `main` too and outside #35; I can open a separate issue if that's useful.
