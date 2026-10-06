# API Reference

Base URL: `http://localhost:8000`

## Endpoints

### Health

`GET /health` — Returns service status and dependency health.

### Authentication

`POST /auth/register` — Create a new account.
`POST /auth/login` — Obtain a JWT access token.

### Profiles

`POST /profiles` — Create a profile with resume and GitHub username.

Request body: `multipart/form-data`. Send the fields as form data, not
JSON: a JSON body is not read, and the profile is created with every
field empty.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `github_username` | string | No | GitHub username to analyze. | `octocat` |
| `portfolio_url` | string | No | URL of a portfolio site. | `https://example.com` |
| `resume_file` | file | No | Resume upload. Accepted types: `application/pdf`, `text/markdown`, `text/plain`. | `resume.md` |

An upload of any other type returns `422` with
`{"detail": "Resume must be a PDF or Markdown file"}`.

```bash
curl -X POST http://localhost:8000/profiles \
  -H "Authorization: Bearer $TOKEN" \
  -F "github_username=octocat" \
  -F "portfolio_url=https://example.com" \
  -F "resume_file=@resume.md;type=text/markdown"
```

`GET /profiles/{profile_id}` — Retrieve a profile.
`DELETE /profiles/{profile_id}` — Delete a profile and associated data.

### Reviews

`POST /reviews` — Request a new portfolio review for a profile.

Request body: `application/json`.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `profile_id` | UUID | Yes | ID of the profile to review, as returned by `POST /profiles`. | `d1194941-176d-4de7-8b3f-424fa7cc6ec7` |

```bash
curl -X POST http://localhost:8000/reviews \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "d1194941-176d-4de7-8b3f-424fa7cc6ec7"}'
```

`GET /reviews/{review_id}` — Retrieve a completed review.
`GET /reviews` — List reviews for the authenticated user (paginated).

## Interactive Docs

When the API is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
