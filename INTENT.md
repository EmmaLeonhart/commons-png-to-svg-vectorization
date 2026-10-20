# What this project is for

_Maintained by Claude: a running read of what the user is trying to do. It is
analysis, not a transcript, and it changes as understanding improves._

## Current understanding

Vectorize individual PNG files from Wikimedia Commons agentically, one file at a
time, producing SVG replacements suitable for upload.

### Second strand: coats of arms for order.life (from 2026-10-15)

Emma's queue item in the inochi-no-michikyo repo (added 2026-10-14, relayed word for word):
"start a session of C:\Users\Emma\Documents\GitHub\agentic-vectorization to have it autonomously
build coats of arms for our coat of arms thing". The coat of arms thing is her
Sodacan-arms-svg-generator (blazon → SVG in Sodacan's Commons style). The arms are for the people of
the order.life genealogy: one unique SVG coat of arms per person (name schema, Emma 2026-10-13: "Coat
of arms | everyone | a unique SVG").

My reading of how this repo serves it (Claude's assumption, 2026-10-15; correct it if wrong):

1. **The people who already have arms.** 1,805 order.life people have a coat of arms on Wikidata
   (P94): 1,576 as SVG already, 230 as raster (110 distinct PNG/GIF files, 75 JPG). The raster ones
   are this repo's job: rebuild each as an SVG. Simple shields are rebuilt **from their blazon with
   Emma's generator** (imported read-only, `tools/generator_render.py`), so the SVG is in the same
   Sodacan style as everything else the generator makes, and checked against the PNG. That is
   rebuilding, not tracing. Where Commons already has an SVG of the same arms, it is recorded, not
   redone. Manuscript paintings, seals and photos are raster originals: marked, not traced.
2. **Coat-of-arms PNGs on Commons in general** (the ~30 under Template:Coat of arms already in the
   queue) are rebuilt the same way after the order.life ones.
3. **The person → arms table** (`data_lake/downloads/order-life-arms/person_arms.tsv`) records who
   has arms and in which file, for whoever links them into order.life later.
4. **Not this repo's job:** inventing new arms for the ~105,000 people with none. That is the
   generator's (its INTENT keeps "existing blazons only" for now) and inochi's queue says it waits for
   the generator. OUT-OF-SCOPE here. Other repositories are read, never edited.

### Third strand: making existing traced SVGs smaller (from 2026-10-19)

Emma, 2026-10-19 (chat), on Category:Vectorized_Tarot_by_Immanuelle: "can you download all of these and run an
attempt at vectorization on these? As I believe they can be made much more efficient. Separate folder and relying
more on trimming down existing ones like merging really close color things and such". Done for all 79 cards
(`tarot/`, 276 MB -> 75 MB, visually identical); `tools/optimize_traced_svg.py` + svgo can be reused on other
auto-traced SVGs she points to.

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

- **(Ended 2026-10-19 20:00.) No vectorizations until 2026-10-19 20:00.** Emma, 2026-10-19 18:28 (chat): "do not do any more vectorizations
  for until 8 p.m. because I'm going to be uploading these." She asked for everything finished, double-checked and
  zipped into the chat. Loop ticks before 20:00 only commit and push.

- **Upload packages are flat and licensed.** Emma, 2026-10-19 (chat): "give it to me with the licenses added as
  comments in the svg files, and all top level. Give me a license all of them can be released under if possible."
  `tools/package_upload.py` does this; the common licence is CC BY-SA 4.0 (every source checked as compatible).

- **Do not edit the other repositories** (inochi-no-michikyo, Sodacan-arms-svg-generator): read
  them, import the generator read-only, write only here (relayed instruction, 2026-10-15).

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
  Bamum King Njoya (4), and the brush-written Siddham Bonji* letters): `<text>` needs the script's font on Commons; open-font glyph outlines would be
  paths, against the vector-text rule. NEEDS-DECISION (user).
- Hand-drawn or generalised geography (Abkhazia stub, Gunma shadow picture, Aomori Tsugaru-block from the
  old ja.wp Japan map.png): the correct outline differs from the drawn one. Replace with correct geography,
  or leave? NEEDS-DECISION (user). A correct-geography build of the Tsugaru map is ready, unstaged.
- Loop rule vs. NEEDS-DECISION (noted 2026-10-19 15:45 PST, cleanvibe v2.0.6): the loop skill says a stuck
  first item gets "make the call yourself and record why"; CLAUDE.md's not-done taxonomy allows a
  NEEDS-DECISION tag, and the update-check skill says CLAUDE.md wins a conflict. Many top queue items are
  tagged NEEDS-DECISION (user), so with "never look past the first item" the loop would stall on item 1.
  Assumption until Emma says otherwise: the tick makes the call on items where an existing user constraint
  points one way (rebuild, don't trace; vector text) and records it in devlog.md; items that are a genuinely
  new question for her (licences, uploading) keep their tag. NEEDS-DECISION (Emma): is that right?
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
vectorized. Correct this if line art should be traced after all. Assumption: straight-edged
pictograms (road signs, simple icons) may have their polygon corners fitted to the colour mask
(`tools/fit_polygons.py`): that recovers the drawing's own vertices rather than following freeform
outlines. Correct this if it counts as tracing for you. Likewise for charts: a chart is rebuilt from its
published data where that can be found (Japan birth/death rates), and otherwise its plotted functions are
recovered as low-order polynomials checked against the source's published values (CompareTropicalYears,
agreeing with Meeus to 5e-6 day). Map rebuilds use public boundary data (MLIT N03, US Census) in a
projection fitted to the PNG, with region membership read from the PNG's colours. Tools must stay memory-bounded: two jobs were stopped by the harness for low memory
caused by unbounded steps (since fixed).

## Log

- 2026-10-15 03:14 PST: new session, started from Emma's inochi-no-michikyo queue item to build
  coats of arms for the generator / order.life. Arms strand added above; worked first.
- 2026-10-15 03:38 PST: every order.life person with arms classified (`files/arms/person_arms_status.tsv`);
  54 rebuilt here, 63 wait on generator gaps (`files/arms/generator-gaps.md`). Next: the Template:Coat of arms
  PNGs in the main queue, same method.
- 2026-10-15 08:41 PST: main queue continued while the arms wait on the generator: 15 more files rebuilt today
  (charts from data or recovered functions, maps from census/N03 boundaries, diagrams and icons by construction),
  and about 35 triaged as not rebuildable, blocked on a missing vector badge, or a decision for the user. Reading
  of the project unchanged.
- 2026-10-19 16:38 PST: new session; loop refreshed to cleanvibe v2.0.6 (first item, then the next, one at a
  time). Under it, items tagged NEEDS-DECISION that an existing constraint settles were decided and logged in
  devlog.md: script specimens become `<text>` in the script's Noto font (1bc1a, ADLaM, Ahom done); hand-drawn
  or generalised geography is replaced by real geography (Abkhazia, Aomori Tsugaru done); hand-drawn curves
  are not fitted (amateur radio coil made regular). Arms: every order.life person is now classified with no
  needs-investigation left (57 rebuilt, 31 vector on Commons, 69 waiting on the generator). Reading of the
  project unchanged.
- 2026-10-20 08:08 PST: the end of the Japanese-named files, now into the digits and A– files. Saigen Jiro's line plans
  (kofun, Heian Palace) are rebuilt by construction. A smooth drawn curve in such a plan is made regular, not fitted:
  for the Danpusan estimated moat line, straight sides tangent to a circle. Dash phases are fitted per piece, since the
  PNGs restart dashes per path. Hand-estimated colour plans with freehand water edges (Hiroshi Nishida's), photographs
  (coins, the lunar calendar's moons) and painted illustrations are set aside. A Commons SVG of the same emblem in a
  different drawing is noted, not used. Reading of the project unchanged.
- 2026-10-20 07:10 PST: into the Japanese-named files at the end of the queue. Kamon are rebuilt by construction when
  they are compass-and-ruler work (井桁に唐花菱: a 井 frame and circle-lobe petals in a square space, one affine map into
  the lozenge); freehand brush strokes and trees are set aside. A PNG that cannot match its stated base (大洋.png) can
  have a generalised base map; real geography replaces it, coloured by the PNG's nearest land. Check strokes at native
  resolution before reading a style from a downscaled preview: 室宮山古墳 復原図.png looked hollow in previews but has
  solid 15 px strokes. Reading of the project unchanged.
- 2026-10-20 06:13 PST: queue through the U–Y files. District locators drawn on Meiji-era districts are built from
  the N03 data of 1920, when those districts still stood (Yamanashi Koma-gun / Yamanashi-gun); the 2000 municipalities
  don't follow the old district edges. Text cut off by a crop edge that cannot be read is not guessed; such files are
  set aside as UNSAFE-TO-GUESS (XinXiu star chart). `tools/fit_text.py` rewrites the tracked
  `scratch/fit_text_tool/line.*` on each run; restore them before committing. Reading of the project unchanged.
- 2026-10-20 04:52 PST: this session's raw transcript, `sessions/2026-10-19_fd7db514.jsonl`, has passed GitHub's
  100 MB file limit (101 MB), so a commit containing it cannot be pushed. That session-log commit was redone with only
  the readable `.md` transcript. The `.jsonl` is left modified in the working tree and kept out of commits by hand; the
  last pushed copy is the 78 MB version. The hourly hook (`.claude/hooks/save_session_log.py`) will try to commit it
  again, and such commits must be redone without it before pushing. NEEDS-DECISION (Emma): how cleanvibe should store
  transcripts over 100 MB: Git LFS, splitting, compressing, or not tracking the raw `.jsonl`.
- 2026-10-20 03:32 PST: queue through the S–T files. Script samples on en.wikipedia Help:Multilingual support take
  their exact text from that page (it shows each image beside the same text). Images cut from a Commons SVG are
  rebuilt from the revision current when the PNG was made (East Timor shield: 2012 revision). A hate-group logo
  (Stormfront) is not vectorised; it is held as NEEDS-DECISION for Emma. Working rule: temporary files of these ticks
  go in `scratch/tmp/`, never under a bare `scratch/` name. Several earlier scratch files are tracked, and
  overwriting or deleting them by name or glob has hit them three times today (each time restored from git).
- 2026-10-20 02:25 PST: every queued prefecture shadow picture is now rebuilt from N03 and staged. Variants handled:
  rotation (`tools/shadow_rotfit.py`), lakes the PNG shows as holes (MLIT W09: Ibaraki, Shiga, Shizuoka, Shimane),
  framed insets fitted per region (Hokkaidō, Nagasaki with N03 2000, Shimane), and island-only views (Okinawa 2,
  bounding box). Two sit below 0.93 with the outline in register (Hiroshima, Nagasaki: coarse islets in small PNGs).
  At 01:5x a wind-down request from Emma arrived, relayed by another session ("pc-manager"): finish, commit, push,
  stop crons. The work was finished and pushed. The cron was kept on, because her standing rule says crons stay on
  and only she stops them directly. This is asked in chat and awaits her word. NEEDS-DECISION (Emma): stop the loop
  cron or not.
- 2026-10-20 00:55 PST: the shadow pictures parked below IoU 0.93 (Ehime, Fukui, Gunma, Hiroshima) were not bad data:
  several PNGs are drawn rotated (5–29°), which `tools/batch_shadow.py` can't fit. `tools/shadow_rotfit.py` (scale,
  aspect, rotation, offset) rebuilds them from N03 at 0.90–0.975, and `tools/shadow_package.py` stages them. The
  remaining queued shadow pictures go through these two tools. Reading of the project unchanged.
- 2026-10-20 00:25 PST: queue through the O–R files. Chart and map rules from these ticks: a chart made by a known
  program from public data (Orion-Sternkarte, pp3) is rebuilt from that program's own data and style file, with what
  the author added by hand (extra constellation lines) read back from the PNG as data. A hand-drawn map that real
  geography can't overlay without losing part of it (Regionen japans) is laid out to the PNG's extent instead. A
  hand-painted range map with no free source stays not rebuildable, and an existing vector range map is noted as the
  alternative. SVGs staged after the 2026-10-19 upload zips are not in them yet. Reading of the project unchanged.
- 2026-10-19 22:57 PST: queue through the N–O files. New rule of thumb from these ticks: a script specimen whose
  text cannot be read reliably (PNG in a non-Noto font, no text in the description: Cross of Herat, Nonotonoto) is set
  aside rather than guessed. Reading of the project unchanged.
- 2026-10-19 21:40 PST: after the 20:00 pause, the queue is moving through the K–M files: script specimens set in their
  Noto fonts (identified by glyph matching where the description doesn't give the text), maps rebuilt from N03 /
  Natural Earth (Japan region maps now via `tools/japan_region_map.py`), line-art plans and crests by construction.
  OFL-licensed originals (font renderings) keep the OFL in upload packages. Reading of the project unchanged.
- 2026-10-19 18:13 PST: three loop ticks on the main queue since. More maps rebuilt from public data (Bohai Sea,
  Greater Macedonia, Eastern Europe locator from the 2011 world SVG), an emblem flag from its source SVG (Indonesian
  Marine Corps), a shrine plan by construction with transcribed text, and every script specimen as Noto `<text>`.
  Working rule from these ticks: an item BLOCKED-ON-EXTERNAL stays in place, is re-checked when reached, and the
  tick moves on; items already triaged not rebuildable are taken off the queue with a devlog line. Reading of the
  project unchanged.
- Work started 2026-10-07 23:02 PST, on the user's go-ahead. GitHub repo (private):
  EmmaLeonhart/commons-png-to-svg-vectorization.
- 2026-10-08 13:20 PST: 40 files finished and staged in upload/; 546 still to vectorize, 256 already
  vectorized on Commons, 299 likely raster originals set aside. Understanding of the goal unchanged;
  the open questions above still need the user.
