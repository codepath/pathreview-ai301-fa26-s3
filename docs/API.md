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

Request body (`multipart/form-data`):

| Field | Type | Required | Notes | Example |
|---|---|---|---|---|
| `github_username` | string | optional | max 255 chars | `octocat` |
| `portfolio_url` | string | optional | max 500 chars | `https://octocat.dev` |
| `resume_file` | file | optional | PDF, Markdown, or plain text only — 422 if another type | `resume.pdf` |

`GET /profiles/{profile_id}` — Retrieve a profile.
`DELETE /profiles/{profile_id}` — Delete a profile and associated data.

### Reviews

`POST /reviews` — Request a new portfolio review for a profile.

Request body (`application/json`):

| Field | Type | Required | Notes | Example |
|---|---|---|---|---|
| `profile_id` | UUID | required | ID of the profile to review | `3fa85f64-5717-4562-b3fc-2c963f66afa6` |

`GET /reviews/{review_id}` — Retrieve a completed review.
`GET /reviews` — List reviews for the authenticated user (paginated).

## Interactive Docs

When the API is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
