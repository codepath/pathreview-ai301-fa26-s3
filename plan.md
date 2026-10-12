# API request documentation gap

## Diagnosis

`docs/API.md` names `POST /profiles` and `POST /reviews` but does not document
their request content types, fields, or example bodies. This leaves clients
without enough information to construct either request. The checked-out
handlers show that the two endpoints use different formats:

- `POST /profiles` accepts form fields and an optional uploaded file through
  FastAPI `Form()` and `File()` parameters. Its fields are
  `github_username` (string, optional), `portfolio_url` (string, optional),
  and `resume_file` (file, optional). The implementation accepts PDF,
  Markdown, and plain-text MIME types and rejects other file types with 422.
- `POST /reviews` accepts the `ReviewCreate` Pydantic model as a JSON body.
  The model has one required field, `profile_id`, typed as a UUID.

This is a documentation gap, not evidence of a request-handling defect.

## Reproduction evidence

The reported read-only reproduction is:

> “Read `docs/API.md` lines 18–26: both `POST /profiles` and `POST /reviews`
> get a single description line each, then the doc moves on to the next
> section — no field list, content type, or example body for either.”

The handlers and schema corroborate the expected request formats:

> `api/routes/profiles.py`: `github_username: str = Form(default=None)`,
> `portfolio_url: str = Form(default=None)`, and
> `resume_file: UploadFile = File(default=None)`.

> `api/routes/profiles.py`: `if file_mime not in ["application/pdf",
> "text/markdown", "text/plain"]:` followed by an
> `HTTP_422_UNPROCESSABLE_ENTITY` response.

> `api/routes/reviews.py`: `data: ReviewCreate`.

> `api/schemas/review.py`: `class ReviewCreate(BaseModel):` and
> `profile_id: UUID`.

These are source-inspection repro steps; no running server is needed to confirm
the missing API reference details.

## Scope

### Change

- Expand the `POST /profiles` entry in `docs/API.md` with its
  `multipart/form-data` content type, all three optional fields, the accepted
  resume file types and 422 behavior, and a representative multipart request
  example.
- Expand the `POST /reviews` entry with its `application/json` content type,
  required UUID `profile_id` field, and a representative JSON body.
- Keep names, optionality, and constraints aligned with the checked-out route
  handlers and schema.

### Won't change

- Do not change route behavior, schemas, validation, authentication, or
  response formats.
- Do not document unrelated endpoints or redesign the API reference.
- Do not claim that profile fields are required: the handler gives each
  `Form()`/`File()` parameter a `None` default.

## Files to touch

- `docs/API.md` — add request details and examples for the two POST endpoints.
- `plan.md` — record this diagnosis, scope, approach, test plan, risks, and
  post-build deviations.

## Approach

1. Update only the two endpoint descriptions in `docs/API.md`.
2. Describe profile requests as multipart form data, listing
   `github_username` (string, optional), `portfolio_url` (string, optional),
   and `resume_file` (file, optional). State that the implementation accepts
   PDF, Markdown, or plain text and returns 422 for unsupported file types.
3. Describe review requests as JSON with required `profile_id` (UUID), and
   include a valid UUID-shaped example.
4. Compare the edited reference against the route signatures and schema to
   ensure the documentation does not imply required profile fields or JSON
   upload semantics.

## Test plan

Re-run the two source-inspection reproduction checks; these are the relevant
unit-level checks for this documentation-only gap:

1. Inspect the `POST /profiles` and `POST /reviews` sections in
   `docs/API.md`. Before the fix, the quoted repro evidence above says each has
   only a one-line description and no content type, fields, or example. After
   the fix, expect `POST /profiles` to show `multipart/form-data`, all three
   optional fields with types and resume constraints, and a multipart example;
   expect `POST /reviews` to show `application/json`, required `profile_id`
   (UUID), and a JSON example.
2. Re-check `api/routes/profiles.py`, `api/routes/reviews.py`, and
   `api/schemas/review.py` against the documented details. After the fix,
   expect each documented field name, type, optional/required status, accepted
   file type, and request format to match the source. No API server is needed
   for this check.

No runtime API test or build is planned because the intended change is
documentation-only. If the repository has a documentation-specific checker,
run it after editing; otherwise inspect the rendered Markdown structure and
examples manually.

## Risks and unknowns

- The profile route's docstring mentions PDF and Markdown, but the executable
  MIME check also accepts `text/plain`. The API reference should follow the
  executable check and disclose all three accepted types.
- MIME type validation uses the upload's provided content type, falling back
  to a filename-based guess. Actual behavior can therefore depend on the
  uploaded MIME metadata; documenting the accepted MIME types is more precise
  than promising acceptance based only on filename extension.
- Both handlers depend on `get_current_user`; the requested change concerns
  request bodies and content types, so authentication details remain out of
  scope.
- Confirm whether this repository defines a documentation lint/check command
  before choosing any additional validation beyond the two reproduction
  checks.

## Deviations

None. Implemented as planned. claude did everything as planned no deviations happened