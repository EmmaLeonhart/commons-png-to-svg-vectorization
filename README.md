# commons-png-to-svg-vectorization

> Started with [cleanvibe](https://github.com/EmmaLeonhart/cleanvibe) on 2026-10-07.

Agentic vectorization of individual PNG files on Wikimedia Commons: each PNG is rebuilt
as an SVG, one file at a time.

Second strand (from 2026-10-15): **coats of arms for the people of the order.life genealogy**.
Every person with arms on Wikidata whose only image is a PNG or JPG gets an SVG, rebuilt from the
blazon with the [Sodacan arms generator](https://github.com/EmmaLeonhart) (Emma's blazon → SVG
generator, used read-only) or from an existing Commons SVG. See `files/arms/README.md`;
`files/arms/person_arms_status.tsv` says where each person's SVG is, and
`files/arms/generator-gaps.md` lists what the generator cannot draw yet.

## Rules

- **Rebuild, don't trace.** Where a PNG was made from a vector source (an existing SVG
  map, chart or diagram), the SVG is rebuilt from that source. Tracing the bitmap is a
  last resort.
- **All text is real `<text>`**, never outlined to paths, so the result works with
  [SVGTranslate](https://svgtranslate.toolforge.org/).

## Layout

- `queue.md`: files still to do (built by `tools/build_queue.py` from the list in
  `data_lake/`).
- `upload/<slug>/`: finished SVGs, ready to upload (every completed file is copied here).
- `files/<slug>/`: one folder per finished file, holding the SVG, the `build.py` that
  generates it, and `notes.md` (source, licence, method).
- `data_lake/`: the input list and downloaded originals (`data_lake/downloads/`).
- `devlog.md`: what has been finished.
- `scratch/`: working files. They are tracked in git so nothing is lost.

## Working on it

Run `cleanvibe` in this folder (or double-click `!runClaude.bat` on Windows) to
open a new Claude session here. Earlier sessions are in `sessions/`.
