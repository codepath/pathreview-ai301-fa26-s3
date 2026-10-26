# Plan: review-ready webhooks (#35)

Issue: https://github.com/codepath/pathreview-ai301-fa26-s3/issues/35

Repro: https://github.com/codepath/pathreview-ai301-fa26-s3/issues/35#issuecomment-5903806095

Branch: `fix/35-review-webhooks` on my fork, from `main` at `2f4e82f`

## Repro evidence this plan relies on

From my posted repro (Linux, Python 3.12.3, Postgres 16.15, FastAPI
0.142.1, commit `2f4e82f`, `LLM_PROVIDER=mock`):

> - `POST /webhooks` returns 404. The OpenAPI route list has no webhook or callback route.
> - The API accepted `callback_url` without an error and ignored it, because `ReviewCreate` only defines `profile_id`.
> - The server log shows the whole pipeline running in the same second the review was created, ending in `review_processing_completed`. No outbound HTTP call is logged.
> - The listener received 0 requests.
> - `grep -rliE "webhook|callback|notify|notification" api/ core/` matches no files. `process_review()` in `core/services/review_service.py` sets `status="complete"`, commits, logs, and returns, with no notification step.

## Diagnosis

This is a missing feature, not a broken one. The repro shows two gaps,
and both have to be filled for a client to be told a review is done:

1. **Nowhere to register.** `POST /webhooks` is a 404 and no route
   stores a callback URL. `callback_url` on `POST /reviews` is dropped
   by `ReviewCreate`.
2. **Nothing to send.** `process_review()` ends at `commit` + `log` on
   every exit path. No outbound HTTP call is logged, and the listener
   got 0 requests.

The repro also constrains the design. The pipeline finishes "in the
same second the review was created". So a callback registered *after*
`POST /reviews` (for example, a per-review registration route) would
race the review and often lose. I'm registering the callback on the
**account**, before any review starts, so the URL is already stored
when `process_review()` reaches its end.

## Scope

**In**

- `POST /webhooks` (authenticated): stores `{url}` for the current
  user and returns the record. The URL must be `http` or `https`
  (pydantic `AnyHttpUrl`), or the request gets a 422. Registering the
  same URL twice returns the existing record instead of a duplicate.
- When a review reaches a terminal status (`complete` or `failed`),
  POST the review payload to every URL registered by the profile's
  owner. The body is the same JSON as `GET /reviews/{id}`
  (`ReviewResponse`). I'm including `failed` on purpose: a client that
  depends on the webhook would otherwise wait forever on a failed
  review.
- Delivery is one attempt with a 5 s timeout. Success or failure is
  logged. A delivery failure never changes the review's status and
  never raises out of `process_review()`.

**Out** (not touched in this change)

- Listing or deleting webhooks (`GET`/`DELETE /webhooks`). The issue
  only asks to register.
- `callback_url` on `POST /reviews`. It stays ignored, as today.
- Retries/backoff, payload signing (HMAC), and a delivery queue or
  worker. Nothing in `core/services/` exists to extend, and each is its
  own design decision.
- SSRF protection (blocking private or loopback targets). See Risks.
- Frontend UI, progress events, and any change to polling or to the
  review pipeline steps themselves.

## Files

| File | Change |
|---|---|
| `core/models/webhook.py` (new) | `Webhook` model: `id`, `user_id` (FK users, cascade), `url`, `created_at`; unique `(user_id, url)` |
| `core/models/__init__.py` | export `Webhook` |
| `alembic/versions/003_add_webhooks_table.py` (new) | create `webhooks` table; `down_revision` = 002 |
| `api/schemas/webhook.py` (new) | `WebhookCreate(url: AnyHttpUrl)`, `WebhookResponse` |
| `core/services/webhook_service.py` (new) | `register_webhook(db, user_id, url)`; `notify_review_finished(db, review_id)` |
| `api/routes/webhooks.py` (new) | `POST /webhooks` using `get_current_user`, same error-handling shape as `reviews.py` |
| `api/main.py` | `app.include_router(webhooks.router)` |
| `core/services/review_service.py` | wrap `process_review()`'s body in `try/finally`; the `finally` calls `notify_review_finished(db, review_id)` |
| `tests/unit/test_webhook_service.py` (new) | delivery tests (below) |
| `tests/unit/test_review_service.py` | test that `process_review()` calls the notifier on an early-return path |
| `docs/API.md` | document `POST /webhooks` and the delivered payload |

## Approach

1. Add the model and migration. Run `alembic upgrade head` and check
   that `\d webhooks` shows the table and the unique constraint.
2. Add `register_webhook` and the schema and route, and wire the router
   into `api/main.py`. Check that `POST /webhooks` returns 200 (not
   404) and appears in `/openapi.json`.
3. Add `notify_review_finished(db, review_id)`:
   1. Load the review. Return if it's missing or its status isn't
      `complete`/`failed`.
   2. Load the owner's webhooks via `review.profile_id → profiles.user_id`.
   3. Build `ReviewResponse.model_validate(review).model_dump(mode="json")`.
   4. For each URL, `httpx.AsyncClient(timeout=5.0).post(url, json=payload)`.
      Log `webhook_delivered` (url, status_code) or
      `webhook_delivery_failed` (url, error).
   5. The whole function is inside `try/except Exception` and logs
      instead of raising. `httpx` is already a dependency and is unused
      today.
4. Hook it in with a single `try/finally` around `process_review()`'s
   existing body. This one site covers every exit (missing review,
   missing profile, failed safety checks, success, and the outer
   exception) without editing each `return`. The missing-review exit
   notifies nobody, because step 3.1 returns.
5. Write the tests. Then run `make check && make test-unit`.

## Test plan

**Re-run of my Unit 2 repro** (same environment, `LLM_PROVIDER=mock`,
listener on `127.0.0.1:9999` logging each POST with a timestamp):

| Step | Unit 2 result | Expected after the fix |
|---|---|---|
| 1–4: setup, uvicorn + listener, log in as `user1@example.com`, read `profile_id` | as before | unchanged |
| new 4a: `POST /webhooks {"url": "http://127.0.0.1:9999/hook"}` | **404** | **200**, body has an `id` and the URL; `/openapi.json` lists `/webhooks` |
| new 4b: same request again | n/a | 200, same `id` (no duplicate row) |
| 5: `POST /reviews {"profile_id": ...}` | 200, `pending` | unchanged |
| 6: poll status 5 s, wait 5 s | `complete`; listener got **0 requests**; no outbound call in the log | still `complete` by polling; listener gets **exactly 1** POST whose JSON `id` equals the review id and `status` is `"complete"`, received after the review's `updated_at`; server log shows `webhook_delivered` with `status_code=200` |

**Negative and failure checks**

- Log in as `user2@example.com` (no webhook registered) and create a
  review. The listener gets 0 requests, and there's no
  `webhook_delivered` log line.
- `POST /webhooks {"url": "not-a-url"}` returns 422.
- Stop the listener and create a review as `user1`. The review still
  reaches `complete`, and the log shows `webhook_delivery_failed`, not a
  traceback.

**Unit tests** (`tests/unit/test_webhook_service.py`, with
`pytest-httpserver` and the mocked-session style of
`test_review_service.py`):

- A complete review with one registered URL produces exactly one POST,
  with a JSON body whose `id`/`status` match.
- A `failed` review is delivered, with `status == "failed"`.
- A `pending`/`processing` review produces no request.
- A user with no webhooks produces no request.
- An unreachable URL doesn't raise and logs `webhook_delivery_failed`.
- `process_review()` with a missing profile still calls
  `notify_review_finished` once (this proves the `finally` covers early
  returns).

## Risks and unknowns

- **30–90 s reviews are untested.** With `mock`, my repro finished "in
  the same second the review was created". Account-level registration
  avoids depending on timing, but I'm only checking ordering (the POST
  arrives after `updated_at`), not a long review. If time allows, I'll
  add a temporary `asyncio.sleep` in a local-only branch to watch a
  slow review get delivered. That change won't be committed.
- **SSRF.** The server will POST to any URL a user registers, including
  loopback or internal addresses. My own test relies on `127.0.0.1`,
  so blocking private ranges would break it. I'm leaving it out and
  will raise it in the PR as an open question, not decide it here.
- **Session state on the exception path.** `process_review()` reuses
  the request's DB session. If the outer `except` was triggered by a
  DB error, the notifier's query may fail on the same session. It's
  caught and logged, so delivery on that path is best-effort. I'll
  check this in a unit test with a session whose `execute` raises.
- **Slow receivers.** A hanging callback holds the background task for
  up to 5 s per URL. The review's status is already committed and
  visible to polling by then, so this delays nothing a client can see.
  I'll confirm that in the slow-listener check above.
- **Payload shape.** I'm reusing `ReviewResponse` rather than inventing
  an envelope (`{"event": ..., "review": ...}`). If reviewers want an
  event type, it's an additive change.
- **Migration numbering.** I'll confirm 002's revision id before writing
  003's `down_revision`, and run `alembic downgrade -1 && alembic
  upgrade head` once.

## Deviations

<!-- Fill in after the build: what changed from this plan, and why. -->

None of these change what the feature does or what my posted plan
comment says, so I'm not adding a comment on the issue.

1. **`process_review()` is a wrapper, not a re-indented body.** The plan
   said to wrap `process_review()`'s existing body in `try/finally`.
   Doing that would re-indent about 100 lines and hide a three-line
   change in the diff. Instead, the body moved unchanged into
   `_process_review()`, and `process_review()` is now `try: await
   _process_review(...)` / `finally: await notify_review_finished(...)`.
   Every exit path is still covered. The one caller
   (`api/routes/reviews.py`) still calls `process_review`.
2. **Three `try` blocks in the notifier, not one.** The plan put the
   whole of `notify_review_finished()` inside a single `try/except`. The
   build has three: one around the DB lookup (`webhook_lookup_failed`),
   one around the HTTP client (`webhook_client_failed`), and one around
   each URL (`webhook_delivery_failed`). A bad URL can't stop delivery to
   the others, and the log says which stage failed. It still never
   raises.
3. **One `httpx.AsyncClient` for all of a user's URLs**, instead of one
   per URL as step 3.4 implied. The behaviour is the same and it costs
   less.
4. **Index on `webhooks.user_id`.** Migration 003 also creates
   `ix_webhooks_user_id`, which the Files table didn't list. The
   notifier looks up webhooks by user on every finished review.
5. **`register_webhook(user_id)` is typed `str`, not `UUID`.** The models
   use `UUID(as_uuid=False)`, so ids are strings at runtime. mypy caught
   the mismatch, and I fixed it in its own commit (`45a7d48`) together
   with a reused `stmt` variable that mypy also flagged.
6. **`make check` doesn't fully pass, and it doesn't pass on `main`
   either.** Lint and black pass, and `make test-unit` passes (384
   passed, 53 xfailed). `make typecheck` stops with a syntax error inside
   numpy's stub file: `pyproject.toml` sets mypy to Python 3.11, and the
   installed numpy stubs use 3.12-only syntax. I didn't change that
   config. I ran `mypy --python-version 3.12` on the five changed source
   files instead, and they're clean. I'll check whether CI's typecheck
   job passes, and if it fails I'll say so in the PR.
7. **The live re-run found a bug, now fixed.** The first after-run
   passed every row of the test plan table, but the webhook body's
   `updated_at` didn't match `GET /reviews/{id}`:
   `"2026-10-08T02:52:27.401681"` against `"2026-10-08T06:52:27.401681Z"`.
   The plan promises the same JSON. The cause: the session uses
   `expire_on_commit=False`, so the notifier's query returned the cached
   `Review` that still held `process_review()`'s naive `utcnow()`,
   instead of the value Postgres stored. The fix adds
   `execution_options(populate_existing=True)` to that query, plus a unit
   test that asserts the option is set. On the re-run the body is
   identical to `GET`. My unit tests mocked the session, so they couldn't
   catch this; only the live run did.
8. **Step 8 results** (in `evidence/`, kept out of git): I ran the same
   script against `main` @ `2f4e82f` (before) and this branch (after).
   - `POST /webhooks` went from 404 to 200, and re-registering returns
     the same `id` with 1 row.
   - The listener went from 0 requests to exactly 1 POST, whose body is
     identical to `GET`.
   - `webhook_delivered status_code=200` is logged.
   - A bad URL gets a 422.
   - user2 with no webhook gets 0 requests.
   - With the listener stopped, the review is still `complete` and
     `webhook_delivery_failed` is logged with no traceback.
   - The migration round-trip (`downgrade -1`, `upgrade head`) works,
     and `\d webhooks` shows the unique constraint, index, and cascading
     foreign key.

   One test-plan line needs a correction. "Received after the review's
   `updated_at`" holds against the stored value (02:54:21.983 UTC
   stored, delivered 02:54:22.057Z). But `GET` shows that time 4 h
   later. That offset is on `main` too (naive UTC written to a
   `timestamptz` column, read back as local EDT). It's an existing bug
   outside #35, which I'll mention in the PR rather than fix here.
