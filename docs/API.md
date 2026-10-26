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
`GET /profiles/{profile_id}` — Retrieve a profile.
`DELETE /profiles/{profile_id}` — Delete a profile and associated data.

### Reviews

`POST /reviews` — Request a new portfolio review for a profile.
`GET /reviews/{review_id}` — Retrieve a completed review.
`GET /reviews` — List reviews for the authenticated user (paginated).

### Webhooks

`POST /webhooks` — Register a callback URL for the authenticated user. Body: `{"url": "https://..."}`; the URL must be `http` or `https` (otherwise 422). Registering the same URL again returns the existing webhook.

When any of the user's reviews reaches `complete` or `failed`, each registered URL receives a `POST` whose JSON body is the same as `GET /reviews/{review_id}`. Delivery is one attempt with a 5 second timeout; failures are logged and do not change the review's status.

## Interactive Docs

When the API is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
