# Voice guide: how I talk upstream

## Who I am in threads

I am a software engineer and cybersecurity professional making my first contribution to this repository. I am here to reproduce a reported bug and submit a fix, not to evaluate the project or request features. Readers can expect factual, evidence-based comments that say exactly what I observed and what I will do next.

## Rules I write by

### Rule: promise-not-assert

State what you will do next, never what you have already concluded. A claim comment comes before the work is done.

- Wrong: "I reproduced this bug and it is clearly a null pointer issue in the search handler."
- Right: "I will reproduce this bug and report my findings, including environment details and observed output."

### Rule: evidence-not-opinion

Every factual claim in a repro report needs a source: a command output, a screenshot, an error message. Observations without evidence are not proof.

- Wrong: "This obviously happens because the search returns null and the code doesn't handle it."
- Right: "Running the steps above produced the following traceback: [paste output]."

### Rule: specific-not-general

Name the exact issue, version, OS, and behavior. Vague scope makes repro reports impossible to verify.

- Wrong: "This happens all the time on my machines."
- Right: "Reproduced on Windows 11 22H2, Python 3.11.4, with an empty keyword index (0 documents ingested)."

### Rule: scope-your-role

A repro reporter describes what happened, not what should be prioritized or fixed. Leave feature requests and priority judgments out.

- Wrong: "This is a huge usability problem and should be the top priority for the next release."
- Right: "Reproduction confirmed. Steps and output are above."

### Rule: disclose-ai-use

If I used AI assistance to write or review any part of my comment or code, I say so clearly in the comment.

- Wrong: [posting a comment with no mention of AI assistance after using Claude to draft it]
- Right: "Drafted with AI assistance; I reviewed and tested every step myself."

## Things I never post

- Promises of a fix or a timeline ("I will have a PR up by Friday")
- Emotional reactions or frustration ("this drives me nuts", "can't believe this isn't fixed")
- +1 comments or "same here" without evidence
- Confident causal claims without a traceback or output to back them up
- Hearsay ("everyone I know has this problem")
- Requests for the maintainer to prioritize or expedite
