# Shadow picture of Niigata prefecture

- **Target:** [File:Shadow picture of Niigata prefecture.png](https://commons.wikimedia.org/wiki/File:Shadow_picture_of_Niigata_prefecture.png), 508×390.
- **Rebuilt from:** 「国土数値情報（行政区域データ）」（国土交通省） N03-2024, municipalities merged into the
  prefecture and simplified to 0.0003°. Terms: Government of Japan Standard Terms of Use 2.0, compatible with
  CC BY 4.0. Release as CC BY 4.0 with that credit.
- **Method:** `python tools/shadow_rotfit.py niigata 15 fit` (scale, aspect 1.25, rotation 13.5°, offset);
  silhouette IoU against the PNG 0.9565. `tools/batch_shadow.py`, which fits scale and offset only, had parked it.
- **Text:** none.
- Comparison: `Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_shadow-niigata.png`.
