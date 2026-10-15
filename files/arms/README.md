# Coats of arms for order.life

Emma's request (inochi-no-michikyo queue, 2026-10-14): "start a session of ... agentic-vectorization to have
it autonomously build coats of arms for our coat of arms thing". See INTENT.md, "Second strand".

- `person_arms_status.tsv`: every order.life person with arms on Wikidata (P94) and where their SVG is
  (`tools/person_arms_status.py`). Status values: svg, vector-exists, rebuilt (path under upload/),
  generator-gap, raster-original, todo.
- `arms.json`: blazon (and crop box) per raster file rebuilt with Emma's Sodacan-arms-svg-generator;
  `tools/build_arms.py` renders them all, checks each against its raster and writes `results.tsv`,
  `<slug>/<slug>.svg` and `<slug>/notes.md`; accepted ones are copied to `upload/arms-<slug>/`.
- `generator-gaps.md`: what the generator could not draw, for its own session to pick up.
- `raster_status.json`: the by-eye triage of the other raster files (raster originals, vectors that exist).
