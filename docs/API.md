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

## Interactive Docs

When the API is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
