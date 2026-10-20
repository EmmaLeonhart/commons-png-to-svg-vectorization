# Shadow picture of Okinawa prefecture 2

- **Target:** [File:Shadow picture of Okinawa prefecture 2.png](https://commons.wikimedia.org/wiki/File:Shadow_picture_of_Okinawa_prefecture_2.png), 174×237.
- **Rebuilt from:** 「国土数値情報（行政区域データ）」（国土交通省） N03-2024, municipalities merged into the
  prefecture and simplified to 0.0003°. Terms: Government of Japan Standard Terms of Use 2.0, compatible with
  CC BY 4.0. Release as CC BY 4.0 with that credit.
- **Method:** `python tools/shadow_rotfit.py okinawa-2 47 fit` (scale, aspect 1.10, rotation 2.7°, offset);
  silhouette IoU against the PNG 0.8773. `tools/batch_shadow.py`, which fits scale and offset only, had parked it. The PNG shows only the waters around Okinawa Island, so the islands are limited to SHADOW_BBOX=127.1,25.9,128.5,27.2 (Okinawa Island, Iheya-Izena, Iejima, Kerama; without Kume, the Daito and Sakishima Islands). A 1.3 px outline (SHADOW_STROKE) matches the PNG's slightly bolder silhouettes. The score is rendered IoU: below 0.93, but the outline is in register, and what remains is a 1 px rim on a 174×237 image.
- **Text:** none.
- Comparison: `Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_shadow-okinawa-2.png`.
