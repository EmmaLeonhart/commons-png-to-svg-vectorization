# Shadow picture of Hiroshima prefecture

- **Target:** [File:Shadow picture of Hiroshima prefecture.png](https://commons.wikimedia.org/wiki/File:Shadow_picture_of_Hiroshima_prefecture.png), 463×395.
- **Rebuilt from:** 「国土数値情報（行政区域データ）」（国土交通省） N03-2024, municipalities merged into the
  prefecture and simplified to 0.0003°. Terms: Government of Japan Standard Terms of Use 2.0, compatible with
  CC BY 4.0. Release as CC BY 4.0 with that credit.
- **Method:** `python tools/shadow_rotfit.py hiroshima 34 fit` (scale, aspect 1.18, rotation 0.0°, offset);
  silhouette IoU against the PNG 0.9044. `tools/batch_shadow.py`, which fits scale and offset only, had parked it. Below the batch's 0.93 bar, but the coast is in register (restarted fits converge to the same optimum); the difference is the PNG's coarse blobs for the many Seto Inland Sea islands at 463×395.
- **Text:** none.
- Comparison: `Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_shadow-hiroshima.png`.
