# Shadow picture of Shiga prefecture

- **Target:** [File:Shadow picture of Shiga prefecture.png](https://commons.wikimedia.org/wiki/File:Shadow_picture_of_Shiga_prefecture.png), 252×392.
- **Rebuilt from:** 「国土数値情報（行政区域データ）」（国土交通省） N03-2024, municipalities merged into the
  prefecture and simplified to 0.0003°. Terms: Government of Japan Standard Terms of Use 2.0, compatible with
  CC BY 4.0. Release as CC BY 4.0 with that credit.
- **Method:** `SHADOW_LAKES_MIN_AREA=0.0005 python tools/shadow_rotfit.py shiga 25 fit` (scale, aspect 1.22, rotation 0.0°, offset);
  silhouette IoU against the PNG 0.9453. `tools/batch_shadow.py`, which fits scale and offset only, had parked it.
- **Lakes:** the PNG shows Lake Biwa as a hole, so lakes of at least 0.0005 square degrees from MLIT 国土数値情報 W09
  (湖沼, same terms) are cut out (IoU 0.82 without).
- **Text:** none.
- Comparison: `Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_shadow-shiga.png`.
