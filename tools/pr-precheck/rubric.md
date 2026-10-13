<!--
Four failure modes from the activity worksheet — every required check covers at least one:
1. Silent drift      — diff does more/less than the plan says; description doesn't match the diff
2. Not tested        — fix is not covered by a test; test evidence is missing or incomplete
3. Unreviewable      — debug noise, commented-out code, unrelated edits pollute the diff
4. Standards wall    — template sections missing, AI-use disclosure absent, Closes # missing
-->

| Check                       | Evidence                                     | Pass condition                                                                                                                                                                                                                                                                                               | Weight    |
| --------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- |
| R1 Diff matches plan        | `plan.md` + `git diff main...HEAD`           | Every changed file/behavior is described in the plan or its `## Deviations`; nothing planned is silently missing from the diff                                                                                                                                                                               | required  |
| R2 Description matches diff | PR description Changes bullets vs diff hunks | Every bullet in the Changes section maps to a real diff hunk; no diff change goes unmentioned in the description                                                                                                                                                                                             | required  |
| R3 Test evidence present    | Testing section / `test_evidence.md`         | Before AND after repro output shown; test results present (any form: pytest output, make test-unit, or equivalent); failures reported with reason count as evidence; in eval mode, accept any test evidence section present and non-empty                                                                    | required  |
| R4 Fix is tested            | `tests/` directory in diff                   | At least one test covers the fixed behavior; any `@pytest.mark.xfail` marker for this issue and its pyproject.toml suppression are removed                                                                                                                                                                   | required  |
| R5 Reviewable diff          | diff                                         | No debug `print` statements, commented-out code, unrelated edits, or formatting churn; diff is scoped to the issue                                                                                                                                                                                           | required  |
| R6 Template complete        | PR description vs repo template              | Every section the repo's template requires is present and filled (or `N/A` with a reason); `Closes #N` or equivalent issue reference present; in eval mode, grade against the template headings visible in the bundle's Repo facts or infer from description headings — do not require a live template fetch | required  |
| R7 AI-use disclosure        | Notes for Reviewers section                  | If the repo's contribution policy requires an AI-use statement, it must be present; if the policy is silent or absent (as in most open-source repos), this check passes automatically                                                                                                                        | required  |
| R8 Branch name              | branch name                                  | Matches `type/NNN-short-desc` pattern (type prefix from: fix, docs, feat, test, refactor, perf, chore); in eval mode, if no branch name is provided in the bundle, grade as pass                                                                                                                             | preferred |

**Verdict rule:** Any `required` check graded `fail` -> **reject**. Any `required` check graded `unclear` (evidence missing or ambiguous) -> **reject**; the summary states what evidence was missing. `preferred` failures are noted but never cause a reject on their own. All `required` checks `pass` -> **accept**. A shortfall the description openly discloses with a reason satisfies R1 and R2 for that shortfall.

Category coverage:

- Silent drift -> R1, R2
- Not tested -> R3, R4
- Unreviewable -> R5
- Standards wall -> R6, R7
