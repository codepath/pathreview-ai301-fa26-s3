# API Reference

Base URL: `http://localhost:8000`

## Endpoints

### Health

`GET /health` — Returns service status and dependency health.

### Authentication

`POST /auth/register` — Create a new account.
`POST /auth/login` — Obtain a JWT access token.

### Profiles

`POST /profiles` — Create a profile with an optional resume upload and GitHub username.
`GET /profiles/{profile_id}` — Retrieve a profile.
`DELETE /profiles/{profile_id}` — Delete a profile and associated data.

#### `POST /profiles` request body

Content type: `multipart/form-data` (**not** JSON).
Requires an `Authorization: Bearer <token>` header; obtain the token from `POST /auth/login`.

| Field | Type | Required | Description | Example |
| --- | --- | --- | --- | --- |
| `github_username` | string, max 255 chars | No | GitHub account to ingest public repositories from. | `octocat` |
| `portfolio_url` | string, max 500 chars | No | URL of the candidate's portfolio site. | `https://octocat.dev` |
| `resume_file` | file | No | Résumé to parse. Must be PDF or Markdown — accepted content types are `application/pdf`, `text/markdown` and `text/plain`. Any other type returns `422` with detail `Resume must be a PDF or Markdown file`. | `resume.pdf` |

All three fields are optional and may be sent in any combination.

```bash
curl -X POST http://localhost:8000/profiles \
  -H "Authorization: Bearer $TOKEN" \
  -F "github_username=octocat" \
  -F "portfolio_url=https://octocat.dev" \
  -F "resume_file=@resume.pdf;type=application/pdf"
```

### Reviews

`POST /reviews` — Request a new portfolio review for a profile.
`GET /reviews/{review_id}` — Retrieve a completed review.
`GET /reviews` — List reviews for the authenticated user (paginated).

#### `POST /reviews` request body

Content type: `application/json`.
Requires an `Authorization: Bearer <token>` header; obtain the token from `POST /auth/login`.

| Field | Type | Required | Description | Example |
| --- | --- | --- | --- | --- |
| `profile_id` | UUID string | Yes | ID of the profile to review, as returned by `POST /profiles`. | `3fa85f64-5717-4562-b3fc-2c963f66afa6` |

The review is processed in the background, so the response returns immediately with `status` set to `pending`. Poll `GET /reviews/{review_id}` for the result.

```bash
curl -X POST http://localhost:8000/reviews \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}'
```

## Rate limiting

Every request is counted against a rolling one-minute window in two buckets:

| Bucket | Keyed on | Default limit | Applies to |
| --- | --- | --- | --- |
| IP | Client IP address of the connection | 120 requests / minute | Every request, signed in or not |
| User | `sub` claim of the bearer token | 60 requests / minute | Requests that carry a decodable token |

Both buckets must have capacity. An authenticated request therefore counts
against its user budget *and* the budget of the IP it came from, so signing in
does not raise the per-IP ceiling, and several users behind one NAT share that
ceiling.

Limits are configurable through `RATE_LIMIT_PER_IP_PER_MINUTE`,
`RATE_LIMIT_PER_MINUTE` and `RATE_LIMIT_WINDOW_SECONDS`. Set
`RATE_LIMIT_ENABLED=false` to turn rate limiting off during local development.

Exempt from rate limiting: `GET /`, `GET /health`, `/docs`, `/redoc`,
`/openapi.json`, and all `OPTIONS` (CORS preflight) requests.

### Headers

Every rate-limited response carries:

| Header | Meaning |
| --- | --- |
| `X-RateLimit-Limit` | Budget of whichever bucket is closest to exhaustion |
| `X-RateLimit-Remaining` | Requests left in that bucket |
| `X-RateLimit-Window` | Window length in seconds |

### `429 Too Many Requests`

When either bucket is exhausted, the API responds `429` without reaching the
route. The response adds a `Retry-After` header holding the window length in
seconds, and the body names which bucket was hit:

```json
{
  "detail": "Rate limit exceeded: more than 120 requests per 60 seconds from this ip. Retry after 60 seconds.",
  "scope": "ip",
  "request_id": "6f1c2f4e-9a3b-4c2d-8f11-2b7d9a0c5e13"
}
```

`scope` is `ip` or `user`. Quote `request_id` when reporting a limit you believe
is wrong.

If Redis is unavailable, rate limiting fails open — requests are served normally
rather than rejected.

## Interactive Docs

When the API is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
