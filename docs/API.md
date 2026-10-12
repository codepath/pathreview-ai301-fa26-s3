# API Reference

Base URL: `http://localhost:8000`

## Running the examples

The examples below assume the local stack from [SETUP.md](SETUP.md) is running
and the API is served by `uvicorn api.main:app --host 127.0.0.1 --port 8000`.
They are written for a bash shell (Git Bash on Windows, or any Linux or macOS
shell). Replace `<token>` with the `access_token` returned by `POST /auth/login`
or `POST /auth/register`, and replace `<profile_id>` and `<review_id>` with the
`id` values returned by the create calls. The seeded development account is
`user1@example.com` / `password1` (from `scripts/seed_db.py`). Response bodies
are trimmed to their shape; ids, timestamps, and scores differ on every run.

## Endpoints

### Health

`GET /health` — Returns service status and dependency health.

```bash
curl http://localhost:8000/health
# HTTP 503 on a fresh setup: the postgres and redis health checks fail because of
# a known health-check bug that is tracked separately. The rest of the API works.
# {"detail":{"status":"unhealthy","dependencies":{"postgres":"unhealthy","redis":"unhealthy","vector_db":"healthy"}, ...}}
```

### Authentication

`POST /auth/register` — Create a new account.

```bash
curl -X POST http://localhost:8000/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"newuser@example.com","password":"a-strong-password"}'
# JSON body.
# HTTP 200
# {"access_token":"<token>","token_type":"bearer"}
# Running it again with the same email returns HTTP 400 {"detail":"Email already registered"}.
```

`POST /auth/login` — Obtain a JWT access token.

```bash
curl -X POST http://localhost:8000/auth/login -d 'username=user1@example.com&password=password1'
# Form body (OAuth2 password flow): the field is `username`, not `email`, and it is not JSON.
# HTTP 200
# {"access_token":"<token>","token_type":"bearer"}
```

### Profiles

`POST /profiles` — Create a profile with resume and GitHub username.

```bash
curl -X POST http://localhost:8000/profiles -H 'Authorization: Bearer <token>' \
  -F github_username=octocat -F portfolio_url=https://example.com
# Multipart form fields (-F), not JSON.
# HTTP 200
# {"id":"<profile_id>","user_id":"...","github_username":"octocat","portfolio_url":"https://example.com","created_at":"...","resume_filename":null}
```

`GET /profiles/{profile_id}` — Retrieve a profile.

```bash
curl http://localhost:8000/profiles/<profile_id> -H 'Authorization: Bearer <token>'
# HTTP 200
# {"id":"<profile_id>","user_id":"...","github_username":"octocat","portfolio_url":"https://example.com","created_at":"...","resume_filename":null}
```

`DELETE /profiles/{profile_id}` — Delete a profile and associated data.

```bash
curl -X DELETE http://localhost:8000/profiles/<profile_id> -H 'Authorization: Bearer <token>'
# HTTP 204, empty body.
# Deleting a profile also removes its reviews, so run the Reviews examples first if you are walking through this file top to bottom.
```

### Reviews

`POST /reviews` — Request a new portfolio review for a profile.

```bash
curl -X POST http://localhost:8000/reviews -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' -d '{"profile_id":"<profile_id>"}'
# HTTP 200
# {"id":"<review_id>","profile_id":"<profile_id>","status":"pending","sections":null,"overall_score":null,"error_message":null, ...}
```

`GET /reviews/{review_id}` — Retrieve a completed review.

```bash
curl http://localhost:8000/reviews/<review_id> -H 'Authorization: Bearer <token>'
# HTTP 200 once the review has finished
# {"id":"<review_id>","status":"complete","sections":[{"section_name":"Technical Skills", ...}, ...],"overall_score":0.81, ...}
```

`GET /reviews` — List reviews for the authenticated user (paginated).

```bash
curl 'http://localhost:8000/reviews?page=1&page_size=20' -H 'Authorization: Bearer <token>'
# HTTP 200
# {"items":[ ... ],"total":4,"page":1,"page_size":20}
```

## Interactive Docs

When the API is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
