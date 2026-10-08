# What this project is for

_Maintained by Claude: a running read of what the user is trying to do. It is
analysis, not a transcript, and it changes as understanding improves._

## Current understanding

Vectorize individual PNG files from Wikimedia Commons agentically, one file at a
time, producing SVG replacements suitable for upload.

## What supports it

- User, 2026-10-07: "the notion here is that we are trying to vectorize individual
  files agentically on wikipedia."
- First file given in chat: File:Kinai-and-Hyuga-Province-in-Japan-RA.png (done:
  `files/kinai-hyuga/`).
- `data_lake/wikipedia-png-search-results.txt` (dropped as Untitled-1.txt): "All of the
  pngs referenced in this file are to be parsed out and have vectorizations attempted
  on them". User: the files are on Commons ("commons lol").
- Folder name chosen by the user: `agentic-vectorization`.

## Constraints from the user

- **Rebuild, don't trace.** "rebuilding is preferred and tracing the png is not desired
  almost all of the time." Rebuild from the file's vector source where one exists.
- **All SVG text is vector text** (real `<text>`, not paths) "so svgtranslate could be
  used for it". Universal rule.
- **Download and save every queued file** ("download and save every queued up one").
- **scratch/ is tracked.** The user removed it from .gitignore ("this is a recipe for
  losing work"). Things may be deleted from scratch/, but only after they are committed
  so history keeps them.
- **Commit and push as work goes**; do not leave work uncommitted.

## Open questions

- Upload: does the user upload the SVGs to Commons, or should that be prepared
  (description pages, `{{Vector version available}}`)? NEEDS-DECISION (user).
- Licence of rebuilt flag maps: the best vector outlines (Flappiefh's géolocalisation maps)
  are CC BY-SA 4.0, so SVGs built on them can't stay PD like the PNGs. Use them anyway,
  or look for PD outlines first? NEEDS-DECISION (user). Assumption until then: use them
  and record the licence in each notes.md.
- Which wiki the search list was run on: its article titles are on neither en.wikipedia
  nor Commons. Filenames are resolved against Commons instead.

## Confidence

High on the goal and the constraints (stated directly). Medium on queue scope until the
list is resolved.

## Log

- Work started 2026-10-07 23:02 PST, on the user's go-ahead. GitHub repo (private):
  EmmaLeonhart/commons-png-to-svg-vectorization.
