# API Reference

Base URL: `http://localhost:8000`

The examples below assume the API is running locally as described in
[SETUP.md](SETUP.md) (`uvicorn api.main:app --host 127.0.0.1 --port 8000`),
with the database seeded by `make setup`. JWTs are shown as `<token>` and
long response bodies are trimmed with `...`.

## Endpoints

### Health

`GET /health` — Returns service status and dependency health. Responds
`200` when every dependency is healthy and `503` otherwise, with the same
body shape either way.

```bash
curl -i http://localhost:8000/health
```

```text
HTTP/1.1 503 Service Unavailable
...
{"detail":{"status":"unhealthy","dependencies":{"postgres":"unhealthy","redis":"unhealthy","vector_db":"healthy"},"safety_events_last_hour":0,"timestamp":"2026-09-30T04:33:25.545205"}}
```

> On a fresh local setup this currently returns `503` even when the
> `db` and `redis` containers are healthy; that is a separate bug in
> the health checks, not a setup problem.

### Authentication

`POST /auth/register` — Create a new account. Takes a JSON body.

```bash
curl -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"a-strong-password"}'
```

```json
{"access_token":"<token>","token_type":"bearer"}
```

`POST /auth/login` — Obtain a JWT access token. Takes an OAuth2
**form** body: the field is `username` (your email), not `email`.

```bash
curl -X POST http://localhost:8000/auth/login \
  -d 'username=user1@example.com&password=password1'
```

```json
{"access_token":"<token>","token_type":"bearer"}
```

The remaining endpoints require the token from `/auth/login` (or
`/auth/register`) in an `Authorization: Bearer <token>` header.

### Profiles

`POST /profiles` — Create a profile with resume and GitHub username.
Takes multipart form fields; `resume_file` (PDF or Markdown) is optional.

```bash
curl -X POST http://localhost:8000/profiles \
  -H 'Authorization: Bearer <token>' \
  -F github_username=octocat \
  -F portfolio_url=https://example.com/octocat
```

```json
{"id":"f2a08862-4665-4a81-84e8-cd02eb932cb2","user_id":"1173deaa-...","github_username":"octocat","portfolio_url":"https://example.com/octocat","created_at":"2026-09-30T04:33:33.799584Z","resume_filename":null}
```

`GET /profiles/{profile_id}` — Retrieve a profile.

```bash
curl http://localhost:8000/profiles/f2a08862-4665-4a81-84e8-cd02eb932cb2 \
  -H 'Authorization: Bearer <token>'
```

```json
{"id":"f2a08862-4665-4a81-84e8-cd02eb932cb2","user_id":"1173deaa-...","github_username":"octocat", ...}
```

`DELETE /profiles/{profile_id}` — Delete a profile and associated data.
Returns `204 No Content` with an empty body.

```bash
curl -X DELETE http://localhost:8000/profiles/f2a08862-4665-4a81-84e8-cd02eb932cb2 \
  -H 'Authorization: Bearer <token>' -i
```

```text
HTTP/1.1 204 No Content
```

### Reviews

`POST /reviews` — Request a new portfolio review for a profile. Takes a
JSON body with the `profile_id`.

```bash
curl -X POST http://localhost:8000/reviews \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"profile_id":"f2a08862-4665-4a81-84e8-cd02eb932cb2"}'
```

```json
{"id":"f11f0b37-cb22-4749-b5f9-20b96be4a621","profile_id":"f2a08862-...","status":"pending","sections":null,"overall_score":null,"error_message":null, ...}
```

`GET /reviews/{review_id}` — Retrieve a completed review.

```bash
curl http://localhost:8000/reviews/f11f0b37-cb22-4749-b5f9-20b96be4a621 \
  -H 'Authorization: Bearer <token>'
```

```json
{"id":"f11f0b37-...","status":"complete","sections":[{"section_name":"Technical Skills", ...},{"section_name":"Project Experience", ...},{"section_name":"Career Growth", ...}], ...}
```

`GET /reviews` — List reviews for the authenticated user (paginated).

```bash
curl 'http://localhost:8000/reviews?page=1&page_size=20' \
  -H 'Authorization: Bearer <token>'
```

```json
{"items":[ ... ],"total":3,"page":1,"page_size":20}
```

## Interactive Docs

When the API is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
