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
- **Completed vectorizations go into `upload/`**, as a rule: user, 2026-10-08, "directory
  should have our completed vectorizations put into it as a rule". One subfolder per file
  (`upload/<slug>/<name>.svg`). `upload/` also holds the user's own material (e.g.
  `upload/inochi-daigengu/` photos); leave that alone.

## Open questions

- Upload: finished SVGs are staged in `upload/`. Whether description pages should be
  drafted alongside them is still open. NEEDS-DECISION (user).
- Licence of rebuilt flag maps: the best vector outlines (Flappiefh's géolocalisation maps)
  are CC BY-SA 4.0, so SVGs built on them can't stay PD like the PNGs. Use them anyway,
  or look for PD outlines first? NEEDS-DECISION (user). Assumption until then: use them
  and record the licence in each notes.md.
- Prefecture "Shadow picture" PNGs (44, Shigenobu Aoki's data, plain lat/lon plots): Aoki's
  vector data is not available. Natural Earth (PD) was too smooth. Chosen source: MLIT
  国土数値情報 N03 administrative areas, merged per prefecture (Tochigi: IoU 0.979, detail
  matches the PNG). Licence: Government of Japan Standard Terms of Use 2.0, compatible with
  CC BY 4.0; credit 「国土数値情報（行政区域データ）」（国土交通省）. Assumption: release
  these SVGs as CC BY 4.0 with that credit. NEEDS-DECISION (user) only if that's not OK.
- Restarting the two jobs Claude Code stopped for low memory (the shadow-picture batch, 31
  prefectures left; the render_match re-check). Both had memory-hungry steps, since bounded.
  BLOCKED-ON-USER-ACTION: the harness says to restart them only when the user asks.
- Script specimens (images of single glyphs or script samples: 1bc1a, ADLaM, Ahom rendering, Bali Ba,
  Bamum King Njoya (4)): `<text>` needs the script's font on Commons; open-font glyph outlines would be
  paths, against the vector-text rule. NEEDS-DECISION (user).
- Hand-drawn geographic symbols (Abkhazia stub, Gunma shadow picture): the correct outline differs from
  the drawn one. Replace with correct geography, or leave? NEEDS-DECISION (user).
- Which wiki the search list was run on: its article titles are on neither en.wikipedia
  nor Commons. Filenames are resolved against Commons instead.

## Confidence

High on the goal and the constraints (stated directly). The queue is settled: 1140 Commons
files; 255 already have a vector version, 299 look like raster originals (photos, paintings,
screenshots; kept for review, not traced), and the rest are worked one by one, flat graphics first.

What works so far (2026-10-08 01:24): rebuilding from the PNG's own stated source SVG (or the
revision of it that existed when the PNG was made), registered against the PNG, with text
re-added as `<text>`. Simple constructions with no source (flags that are a field plus an
inscription, geometric diagrams, family trees) are drawn directly from measured geometry: exact
straight runs from aliased line art, equal-angle sectors, text set in a matching font. That is
construction, not tracing.
Raster-based PNGs (photos, artworks, terrain relief) are marked not rebuildable rather than
traced. Assumption: freeform drawings (woodblock prints, line-art figures, brush calligraphy,
organic crests) also count as tracing-only, even when flat-coloured, so they are marked, not
vectorized. Correct this if line art should be traced after all. Tools must stay memory-bounded: two jobs were stopped by the harness for low memory
caused by unbounded steps (since fixed).

## Log

- Work started 2026-10-07 23:02 PST, on the user's go-ahead. GitHub repo (private):
  EmmaLeonhart/commons-png-to-svg-vectorization.
