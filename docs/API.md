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

Request: `multipart/form-data`

| field | type | required | notes |
|---|---|---|---|
| github_username | string | no | |
| portfolio_url | string | no | |
| resume_file | file | no | must be PDF, Markdown, or plain text; 422 otherwise |

Example:
```
curl -X POST http://localhost:8000/profiles \
  -F "github_username=octocat" \
  -F "portfolio_url=https://example.com" \
  -F "resume_file=@resume.pdf"
```

`GET /profiles/{profile_id}` — Retrieve a profile.
`DELETE /profiles/{profile_id}` — Delete a profile and associated data.

### Reviews

`POST /reviews` — Request a new portfolio review for a profile.

Request: `application/json`

| field | type | required | notes |
|---|---|---|---|
| profile_id | UUID | yes | |

Example:
```json
{ "profile_id": "d1194941-176d-4de7-8b3f-424fa7cc6ec7" }
```

`GET /reviews/{review_id}` — Retrieve a completed review.
`GET /reviews` — List reviews for the authenticated user (paginated).

## Interactive Docs

When the API is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
