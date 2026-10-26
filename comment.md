Here's my plan, based on my repro above. In that run, `POST /webhooks` returned 404, `callback_url` on `POST /reviews` was silently dropped, and `process_review()` ended with `review_processing_completed` and no outbound call. My listener got 0 requests. So two things are missing: a place to register a callback, and a send when the review finishes.

**Approach.** Register the callback per account, before any review starts. In my repro the whole pipeline ran "in the same second the review was created", so a URL registered after `POST /reviews` would race the review. With account-level registration, the URL is already stored when the review ends. @tanisnus proposed a per-review route and covers the race by delivering from two paths. I'm trying the other trade-off, so the two plans can be compared.

- New `POST /webhooks` (`api/routes/webhooks.py`): stores an `http(s)` URL for the current user, with a `webhooks` table and migration 003. Registering the same URL twice returns the existing record.
- New `core/services/webhook_service.py`: `notify_review_finished()` POSTs the same JSON as `GET /reviews/{id}` to the owner's URLs when the status is `complete` or `failed`. It makes one attempt with a 5 s timeout, and failures are logged, never raised.
- `process_review()` gets a single `try/finally` that calls the notifier, so every exit path is covered without editing each `return`.

**Not in scope:** listing or deleting webhooks, `callback_url` on `POST /reviews`, retries, signing, a delivery queue, frontend, and blocking private/loopback targets. That last one is an SSRF question I'd rather raise in the PR than decide here, since my own test posts to `127.0.0.1`.

**Test plan.** I'll re-run my repro steps with `POST /webhooks` added before step 5. I expect a 200 instead of a 404, then exactly one POST at the listener with the review's `id` and `"status": "complete"`, arriving after its `updated_at`, plus a `webhook_delivered` log line. I'll also check three cases: a user with no webhook gets 0 requests, a bad URL gets a 422, and a stopped listener still leaves the review `complete`, with `webhook_delivery_failed` logged. Unit tests in `tests/unit/test_webhook_service.py` use `pytest-httpserver`.

**Unknowns.** With `LLM_PROVIDER=mock` I can't produce a 30–90 s review, so I'm checking ordering rather than a real long run. On the exception path, delivery reuses a session that may already be broken, so it's best-effort there.

Work will be on `fix/35-review-webhooks` in my fork. I used Claude to help draft this plan; I've checked it against the code and my repro.
