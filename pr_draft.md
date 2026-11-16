docs: document request bodies for `POST /profiles` and `POST /reviews`

## Summary

`docs/API.md` listed every endpoint with a one-line description but gave no request bodies, so a reader had no way to learn what to send — including the fact that `POST /profiles` takes `multipart/form-data` while `POST /reviews` takes JSON. This PR adds a "Request body" subsection to each of those two endpoints with a field table (name, type, required, constraints, description, example) and a runnable `curl` example. Every field was cross-checked against the route handlers and Pydantic schemas, and against the live OpenAPI schema. Docs only — no application code or behavior changes.

## Issue

Closes #37

## Changes

- Added a `#### POST /profiles request body` section to `docs/API.md`: states the content type is `multipart/form-data` (**not** JSON) and that an `Authorization: Bearer <token>` header is required.
- Added a field table for `POST /profiles` covering `github_username` (string, max 255), `portfolio_url` (string, max 500) and `resume_file` (file), all optional, with the accepted resume content types (`application/pdf`, `text/markdown`, `text/plain`) and the `422 Resume must be a PDF or Markdown file` failure case.
- Added a `curl` example for `POST /profiles` using `-F` flags, including `;type=application/pdf` on the file part.
- Added a `#### POST /reviews request body` section: content type `application/json`, same auth header, and a field table for `profile_id` (UUID string, required).
- Noted that `POST /reviews` returns immediately with `status: "pending"` and that the caller should poll `GET /reviews/{review_id}`.
- Added a `curl` example for `POST /reviews` with a JSON body.
- Reworded the `POST /profiles` summary line from "Create a profile with resume and GitHub username" to "Create a profile with an optional resume upload and GitHub username", because the old wording implied the fields were required and would have contradicted the table directly beneath it.

## Testing

- [ ] **CI is green on this PR (all five jobs)** — required for review
- [ ] Unit tests pass (`make test-unit`)
- [ ] Integration tests pass (`make test-integration`)
- [ ] Linter passes (`make lint`)
- [ ] Type checker passes (`make typecheck`)
- [ ] New/updated tests cover the changes
- [X] If this fixes a seeded bug: removed its `@pytest.mark.xfail` marker (and any
      matching suppression in `pyproject.toml`)

This is a documentation-only change, so verification was reading the doc against the code and against the API's own generated schema.

**Before** — `docs/API.md` gave one line per endpoint and no request body at all:

```
`POST /profiles` — Create a profile with resume and GitHub username.
`POST /reviews` — Request a new portfolio review for a profile.
```

A reader could not tell what fields either endpoint accepted, which were required, or that the two endpoints use different content types.

**After** — each endpoint has a request-body section with its content type, a field table (type, required, constraints, description, example) and a `curl` example. See the diff on `docs/API.md`.

**Check: documented fields vs. the live OpenAPI schema.** With `.venv` activated and the stack up under Docker, I read the app's generated schema and compared it to the tables:

- `POST /profiles` → content type `multipart/form-data`, request body `required: false`, **zero** required fields; properties `github_username`, `portfolio_url`, `resume_file`.
- `POST /reviews` → content type `application/json`, request body required, required fields `['profile_id']`, `format: uuid`.

Both match what the tables say, including the multipart-vs-JSON split the issue called out and the "all three profile fields are optional" claim.

**Check: auth header format.** `api/middleware/auth.py` uses `OAuth2PasswordBearer(tokenUrl="/auth/login")`, so `Authorization: Bearer <token>` is correct for both examples.

**Check: diff scope.** `git diff --stat` touches only `docs/API.md` (40 insertions, 1 deletion).

**Not verified:** the live `200` and `422` responses from actually running the two `curl` examples, which need a seeded database. The field names, types and the 422 message were read from `api/routes/profiles.py` and `api/schemas/profile.py` instead.

## Screenshots / Demo

N/A — this change is Markdown-only and has no UI surface. The rendered result is visible in the diff on `docs/API.md`.

## Notes for Reviewers

**AI use.** I read all files within `api` modules and understood the bugs. I asked Claude Code to verify by reading the files as well and summarize the request structure/ I then drafted the two field tables and the `curl` examples. I checked each row myself against the source and against the app's generated OpenAPI schema before accepting it, and I edited the wording to match the existing style of `docs/API.md`. The decision about what to document and what to leave out was mine.

**Changed from my plan.** My plan scoped this to adding new subsections only, with no edits to existing text. I also changed one existing line — the `POST /profiles` summary — because "Create a profile with resume and GitHub username" implies those fields are required, which the table directly below it contradicts. One line, and only for accuracy.

**Left out on purpose.** Response schemas and error tables for these two endpoints, and request bodies for every other endpoint (`POST /auth/*`, `PUT /profiles/{id}`), are out of scope for #37. Worth noting that `PUT /profiles/{profile_id}` exists in the code but is not listed in `docs/API.md` at all — that is a separate gap and I did not add it here.

**Question for a maintainer.** I documented what the code does: all three `POST /profiles` fields are optional, so an empty multipart body is accepted. If the intent is that at least one of them must be supplied, that is a code change rather than a doc change, and I am happy to file it separately.
