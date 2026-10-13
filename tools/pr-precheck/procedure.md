## Read order

1. `scope.md` — live mode only: refuse if `Repo:` is a placeholder or the PR is for another repo; skip entirely in eval mode.
2. `rubric.md` — load the checks and verdict rule before reading any evidence.
3. `references/evidence-guide.md` — load the evidence map before collecting evidence.
4. `plan.md` (live: file on disk; eval: plan section of bundle).
5. The diff — live: `git diff main...HEAD` from the working copy root; eval: diff section of bundle.
6. `pr_draft.md` / PR title and description — live: file on disk; eval: description section of bundle.
7. `test_evidence.md` / Testing section — live: file on disk; eval: test evidence section of bundle.
8. Live mode only: fetch `.github/PULL_REQUEST_TEMPLATE.md` and `docs/CONTRIBUTING.md` from the scoped repo; fetch the issue thread.
9. `voice-guide.md` — live mode only: hold PR title and description against every rule; report broken rules by name with a quote.

## Evidence gathering

For each check, collect the cited artifacts side by side before grading:

## Evidence gathering

For each check, collect the cited artifacts side by side before grading:

- R1: list plan steps -> list diff files/functions changed; flag any diff file not in the plan and any plan step with no matching diff hunk.
- R2: list description Changes bullets -> list diff hunks; flag any bullet with no matching hunk and any hunk with no matching bullet.
- R3: locate before repro, after repro, and all four `make` outputs in the evidence file; note any that are missing.
- R4: search `tests/` in the diff for a test that exercises the fixed behavior; search for `xfail` markers referencing this issue.
- R5: scan diff for `print(`, commented blocks, files unrelated to the issue, whitespace-only changes across unrelated files.
- R6: compare description headings against PR template headings one by one; locate `Closes #`; locate CI checkbox state.
- R7: search Notes for Reviewers section for AI-use statement.
- R8: read branch name and parse against `type/NNN-short-desc` pattern.

Record file:line (or bundle section:line) for every finding before moving to check execution.

## Check execution

Run R1 through R8 in order. For each check:

1. State the evidence collected (fact or direct quote, with location).
2. Apply the pass condition from `rubric.md` exactly as written.
3. Assign `pass`, `fail`, or `unclear`.
   - `unclear` when the evidence is present but ambiguous, or when required evidence is entirely absent and cannot be inferred.
   - Never infer evidence that is not shown; missing = `unclear` for that check.

## Verdict assembly

1. Apply the verdict rule from `rubric.md`:
   - Any required check = `fail` or `unclear` -> verdict is `reject`.
   - All required checks = `pass` -> verdict is `accept`.
2. Write a one-line per-check summary (check name, grade, key evidence phrase).
3. If verdict is `reject`, list each failing check and what would need to change to flip it.
4. Emit the JSON block from `SKILL.md` exactly as specified — valid, complete, and last. Nothing follows it.
