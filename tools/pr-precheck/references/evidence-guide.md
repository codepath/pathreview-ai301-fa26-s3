## Plan

In a package: the `## Plan` or `## Implementation Plan` section of the bundle file.
In my PR: `plan.md` in the repo root of my fork, on my branch.
Good looks like: numbered steps with file names and function names; a `## Deviations` section if anything changed.

## Diff

In a package: the fenced diff block in the bundle file (lines prefixed `+` or `-`).
In my PR: output of `git diff main...HEAD` run from the repo root on my branch — three dots, covering every committed change relative to `main`.
Good looks like: only the files the plan names are changed; no debug prints, no commented-out code, no unrelated whitespace edits.

## PR title and description

In a package: the `## Title` and `## Description` sections of the bundle file.
In my PR: the first line of `pr_draft.md` (title) and the rest of the file (description, filled from the repo's PR template).
Good looks like: title names the issue type and fix; description has every template section filled; `Closes #N` present; Changes bullets map one-to-one to diff hunks.

## Test evidence

In a package: the `## Test Evidence` or `## Testing` section of the bundle file.
In my PR: `test_evidence.md` — contains output from `make test-unit`, `make test-integration`, `make lint`, `make typecheck`, plus before-repro (on `main`) and after-repro (on my branch) for the issue.
Good looks like: all four `make` commands present with their full output; before shows the bug; after shows it is fixed; a failing check reported with reason is still valid evidence.

## Issue thread

In a package: the `## Issue` section of the bundle file.
In my PR: the GitHub issue thread at the URL in the `Closes #` line, fetched live from the scoped repo.
Good looks like: issue describes the bug with a repro; plan's approach matches the diagnosis in the thread.

## PR template

In a package: the `## Template` section of the bundle file (if present) or inferred from description section headings.
In my PR: `.github/PULL_REQUEST_TEMPLATE.md` fetched live from the scoped repo.
Good looks like: every heading in the template appears in the description; checkboxes ticked only for checks that actually passed; CI box left unticked (CI only runs after the PR is opened).

## AI-use disclosure

In a package: the Notes for Reviewers section of the description.
In my PR: the Notes for Reviewers section of `pr_draft.md`.
Good looks like: at least one sentence saying what AI tools were used and how (e.g., "Used Claude to draft test cases, reviewed and adjusted each one manually").
