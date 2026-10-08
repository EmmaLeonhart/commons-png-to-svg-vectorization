# commons-png-to-svg-vectorization

> Started with [cleanvibe](https://github.com/EmmaLeonhart/cleanvibe) on 2026-10-07.

Agentic vectorization of individual PNG files on Wikimedia Commons: each PNG is rebuilt
as an SVG, one file at a time.

## Rules

- **Rebuild, don't trace.** Where a PNG was made from a vector source (an existing SVG
  map, chart or diagram), the SVG is rebuilt from that source. Tracing the bitmap is a
  last resort.
- **All text is real `<text>`**, never outlined to paths, so the result works with
  [SVGTranslate](https://svgtranslate.toolforge.org/).

## Layout

- `queue.md`: files still to do (built by `tools/build_queue.py` from the list in
  `data_lake/`).
- `files/<slug>/`: one folder per finished file, holding the SVG, the `build.py` that
  generates it, and `notes.md` (source, licence, method).
- `data_lake/`: the input list and downloaded originals (`data_lake/downloads/`).
- `devlog.md`: what has been finished.
- `scratch/`: working files. They are tracked in git so nothing is lost.

## Working on it

Run `cleanvibe` in this folder (or double-click `!runClaude.bat` on Windows) to
open a new Claude session here. Earlier sessions are in `sessions/`.
