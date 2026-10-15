Here's my plan for this, following up on the repro above.

**Cause:** `_extract_sections` in `ingestion/chunking/structural_chunker.py` only keeps lines once it has seen a heading. The collect check on line 120 and both save checks (lines 94 and 124) all depend on `heading_stack`, so a heading-less document comes back with no sections and `chunk()` returns `[]`.

**Fix:** add a fallback in `chunk()`. When `_extract_sections` returns nothing and the text has no heading line, treat the whole document as one section with `heading_path == ""` and `heading_level == 0`. The existing loop then makes it a single chunk, or sends it to the semantic chunker if it's over 800 tokens. The heading-line check matters because heading-only documents like `"# Title"` also return no sections today, and I don't want the fallback to change those. `_extract_sections` stays as it is, so headed documents chunk exactly as before.

**Tests:** remove the `xfail` marker from `test_document_with_no_headings`, and add tests for the no-heading chunk's metadata, a heading-less document over 800 tokens, and a heading-only document still returning `[]`. After the fix, my repro script should print `plain document chunks: 1`.

**Not in this PR:** while tracing this I noticed that the same check also drops intro text above a document's first heading (`"Intro paragraph.\n# Title\nBody"` returns only `['Body']`). Separately, empty sections between two headings produce an empty `''` chunk. Both change how headed documents chunk, and this issue doesn't ask for that, so I'm leaving them for separate issues.

One open question: heading-less documents will now produce chunks with an empty `heading_path`. I haven't checked yet whether anything downstream expects it to always be set, and I'll do that before opening the PR.

I used Claude Code to help trace the cause and draft this plan. 
