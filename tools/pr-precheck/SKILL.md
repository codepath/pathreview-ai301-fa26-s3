---
name: pr-precheck
description: Grade a PR package (a candidate pull request read against the plan it claims to implement and the issue that plan belongs to) and decide whether it is ready to submit. Use when checking your own branch, draft PR title, and description before opening the pull request, or when grading an eval package bundle.
---

# pr-precheck: rubric-driven PR grading

## The question

This tool answers exactly one question about exactly one PR package: **is this PR ready to submit?** A PR package is a candidate pull request — a title, description, diff, and test evidence — read against the plan it claims to implement and the issue that plan belongs to. The tool never grades more than one package per run and never answers from intuition: it executes the components in this directory and produces a binary verdict.

## Inputs and modes

**Live mode** is for checking your own PR before you open it. Inputs are:

- `plan.md` — your Unit 3 plan, including any `## Deviations` section you added
- The diff on your branch, produced by running `git diff main...HEAD` (three dots) from the top of your fork's working copy — every committed change your branch makes relative to `main`
- `pr_draft.md` — your PR title on the first line and your full description below it (filled from the repo's PR template)
- `test_evidence.md` — output from all four repo checks (`make test-unit`, `make test-integration`, `make lint`, `make typecheck`) plus your before and after repro output
- The live issue thread, `.github/PULL_REQUEST_TEMPLATE.md`, and `docs/CONTRIBUTING.md` from the scoped repo, fetched at run time

A house-chain student reads the house plan and the house repro pack wherever these steps say `plan.md` and repro output; the same checks grade the same things.

**Eval mode** is for grading a frozen package bundle. The bundle text is the whole world: nothing is fetched, no files outside the bundle are read, and every check runs with the full verdict rule applied.

## The scope seam (live mode only)

Before reading any other input in live mode, read `scope.md`. It names the repo where the PR must live and the house rules of that environment. If the `Repo:` line still contains an unfilled placeholder (`<ORG>/<PATH-REVIEW-REPO>`), stop immediately without grading and tell the student to replace it with their section's Path Review repo. If the PR being graded is not in the scoped repo, refuse to grade and explain why. Never guess a scope. In eval mode, ignore `scope.md` entirely.

## The voice seam (live mode only)

After reading scope, read `voice-guide.md`. Hold the PR title and description from `pr_draft.md` against every rule in the guide. Report each broken rule by name in the per-check summary, quoting the offending phrase. The voice guide never changes the verdict on its own unless `rubric.md` contains a check that explicitly reads it. In eval mode, ignore `voice-guide.md` entirely.

## Component reads

Read the components in this order: `rubric.md` defines the checks and the verdict rule. `references/evidence-guide.md` maps where each evidence family lives in both a package and a live submission. `procedure.md` defines the operating steps and is executed as written. If `procedure.md` is silent on a step, report the gap and do not improvise. If `rubric.md` or `procedure.md` has no written content (only comment placeholders), refuse to grade and say so — an empty tool that invents checks is worse than no tool.

## Verdict and output

The verdict is binary: `accept` means the PR is ready to submit; `reject` means hold. There is no third option, no "accept with reservations". Reservations belong in the check evidence lines. End every reply with the fenced JSON block below, valid, complete, and last — nothing follows it.

```json
{
  "item": "<PR URL or bundle id>",
  "checks": [
    {
      "name": "<check name>",
      "grade": "pass|fail|unclear",
      "evidence": "<one line: the fact or quote that decided it>"
    }
  ],
  "verdict": "accept|reject"
}
```

## Grading discipline

- **Evidence first.** Name the specific fact or quote that decided every check. "Looks fine" or "seems complete" is not evidence.
- **Grade the thing, not the polish.** A terse complete PR can be ready; a confident detailed one can hide drift. Read the artifact against the plan, the issue, and the stated standards — not against how well it is written.
- **The rubric decides, not the run.** If a check passes by its stated condition but feels wrong, it still passes. Fix the rubric, not the verdict.
- **The procedure decides how, not the run.** Follow `procedure.md` as written. When a step is missing, report the gap rather than inventing a substitute.
- **Unclear defaults to fail.** Where the rubric's verdict rule is silent on `unclear`, treat it as failing. A claim you cannot verify from the package is a claim that is not ready to submit.
