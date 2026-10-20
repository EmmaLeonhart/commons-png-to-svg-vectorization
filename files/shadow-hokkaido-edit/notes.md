# Shadow picture of Hokkaido prefecture edit

- **Target:** [File:Shadow picture of Hokkaido prefecture edit.png](https://commons.wikimedia.org/wiki/File:Shadow_picture_of_Hokkaido_prefecture_edit.png), 550×400.
- **Rebuilt from:** 「国土数値情報（行政区域データ）」（国土交通省） N03-2024, municipalities merged into the
  prefecture and simplified to 0.0003°. Terms: Government of Japan Standard Terms of Use 2.0, compatible with
  CC BY 4.0. Release as CC BY 4.0 with that credit.
- **Method:** `python tools/shadow_rotfit.py hokkaido-edit 1 fit` (scale, aspect 1.37, rotation 11.2°, offset);
  silhouette IoU against the PNG 0.9488. The PNG is drawn rotated 11°, which `tools/batch_shadow.py` (scale and offset only) cannot fit. As the PNG (an edit drawn without the disputed islands), N03's Shikotan, Kunashiri, Etorofu, Shana and Shibetoro districts are left out (`SHADOW_DROP_DISTRICTS`), and so are the Habomai islets east of 145.84°E (`SHADOW_MAX_LON`).
- **Text:** none.
- Comparison: `Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_shadow-hokkaido-edit.png`.
