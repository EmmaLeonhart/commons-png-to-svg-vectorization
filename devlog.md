# Devlog

## 2026-10-07

- **File:Kinai-and-Hyuga-Province-in-Japan-RA.png → SVG** (`files/kinai-hyuga/`).
  Rebuilt from File:Provinces of Japan.svg: registered against the PNG, highlighted
  provinces read from it, 19 labels as real `<text>` fitted to within 4 px. Checked
  in Chrome only, not yet in librsvg.
- Built `queue.md` from the user's PNG list: 1140 Commons files, 91 unresolved names.
- **File:Ushu Province.png → SVG** (`files/ushu-province/`). Rebuilt from File:Provinces
  of Japan-Dewa.svg with the new `tools/rebuild_locator.py` (registration plus colour
  reading, generalised from the Kinai job). 100% land/sea agreement; no text.
- `tools/rebuild_locator.py` and `tools/render_svg.py`: a reusable rebuild for locator
  maps made from the "Provinces of Japan" SVG family. Checked against Kinai: it finds the
  same seven provinces and the same transform as the hand-made build.
- `tools/triage.py`: sorted all queued files by route (triage.md).
