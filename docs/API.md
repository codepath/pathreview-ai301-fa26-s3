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

Request body: `multipart/form-data`

| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `github_username` | string | No | GitHub username to associate with the profile. | `octocat` |
| `portfolio_url` | string | No | Portfolio or personal website URL for the profile. | `https://octocat.dev` |
| `resume_file` | file | No | Resume upload. Accepted file types are PDF, Markdown, or plain text. | `resume.pdf` |

Example:

```bash
curl -X POST http://localhost:8000/profiles \
  -H "Authorization: Bearer <token>" \
  -F "github_username=octocat" \
  -F "portfolio_url=https://octocat.dev" \
  -F "resume_file=@resume.pdf"
```

`GET /profiles/{profile_id}` — Retrieve a profile.
`DELETE /profiles/{profile_id}` — Delete a profile and associated data.

### Reviews

`POST /reviews` — Request a new portfolio review for a profile.

Request body: JSON

| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `profile_id` | UUID string | Yes | ID of the profile to review. | `8d1f3d3d-7b1f-4d8f-9f2b-1c2a3b4c5d6e` |

Example:

```json
{
  "profile_id": "8d1f3d3d-7b1f-4d8f-9f2b-1c2a3b4c5d6e"
}
```

`GET /reviews/{review_id}` — Retrieve a completed review.
`GET /reviews` — List reviews for the authenticated user (paginated).

## Interactive Docs

When the API is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
