# API Reference

Base URL: `http://localhost:8000`

The examples below assume the local server is running as described in
[docs/SETUP.md](SETUP.md). Replace `<token>` with the `access_token`
value returned by `POST /auth/login`. The seeded login is
`user1@example.com` / `password1`.

## Endpoints

### Health

`GET /health` — Returns service status and dependency health.

```bash
curl http://localhost:8000/health
# HTTP 503 (expected on a fresh local setup — the postgres and redis
# health checks report unhealthy while Docker services are still
# initialising; this is a separate known issue and does not affect
# API functionality)
# {"detail":{"status":"unhealthy","dependencies":{"postgres":"unhealthy","redis":"unhealthy","vector_db":"healthy"},...}}
```

### Authentication

`POST /auth/register` — Create a new account.

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"yourpassword"}'
# HTTP 200
# {"access_token":"<token>","token_type":"bearer"}
```

`POST /auth/login` — Obtain a JWT access token.

> **Note:** this endpoint follows the OAuth2 password grant form — the
> body must use `username` (not `email`) and must be form-encoded, not
> JSON.

```bash
curl -X POST http://localhost:8000/auth/login \
  -d "username=user1@example.com&password=password1"
# HTTP 200
# {"access_token":"<token>","token_type":"bearer"}
```

### Profiles

`POST /profiles` — Create a profile with resume and GitHub username.

> **Note:** this endpoint takes multipart form fields, not a JSON body.

```bash
curl -X POST http://localhost:8000/profiles \
  -H "Authorization: Bearer <token>" \
  -F "github_username=your-github-username" \
  -F "portfolio_url=https://example.com"
# HTTP 200
# {"id":"<profile_id>","user_id":"<user_id>","github_username":"your-github-username","portfolio_url":"https://example.com","created_at":"...","resume_filename":null}
```

`GET /profiles/{profile_id}` — Retrieve a profile.

```bash
curl http://localhost:8000/profiles/<profile_id> \
  -H "Authorization: Bearer <token>"
# HTTP 200
# {"id":"<profile_id>","github_username":"your-github-username","portfolio_url":"https://example.com",...}
```

`DELETE /profiles/{profile_id}` — Delete a profile and associated data.

```bash
curl -X DELETE http://localhost:8000/profiles/<profile_id> \
  -H "Authorization: Bearer <token>"
# HTTP 204 (no response body)
```

### Reviews

`POST /reviews` — Request a new portfolio review for a profile.

```bash
curl -X POST http://localhost:8000/reviews \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"profile_id":"<profile_id>"}'
# HTTP 200
# {"id":"<review_id>","profile_id":"<profile_id>","status":"pending",...}
```

`GET /reviews/{review_id}` — Retrieve a completed review.

```bash
curl http://localhost:8000/reviews/<review_id> \
  -H "Authorization: Bearer <token>"
# HTTP 200
# {"id":"<review_id>","status":"complete","sections":[...],"overall_score":0.81,...}
```

`GET /reviews` — List reviews for the authenticated user (paginated).

```bash
curl "http://localhost:8000/reviews?page=1&page_size=5" \
  -H "Authorization: Bearer <token>"
# HTTP 200
# {"items":[...],"total":4,"page":1,"page_size":5}
```

## Interactive Docs

When the API is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
