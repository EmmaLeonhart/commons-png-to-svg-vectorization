# Shadow picture of Hokkaido prefecture

- **Target:** [File:Shadow picture of Hokkaido prefecture.png](https://commons.wikimedia.org/wiki/File:Shadow_picture_of_Hokkaido_prefecture.png), 550×400.
- **Rebuilt from:** 「国土数値情報（行政区域データ）」（国土交通省） N03-2024, municipalities merged and simplified to
  0.0003°. Terms: Government of Japan Standard Terms of Use 2.0, compatible with CC BY 4.0. Release as CC BY 4.0
  with that credit.
- **Method:** `python files/shadow-hokkaido/build.py fit`.
  - Outside its inset, the PNG is pixel-identical to File:Shadow picture of Hokkaido prefecture edit.png, so the main
    map reuses that rebuild's geometry and fit (rotated 11°; IoU 0.94 there).
  - The inset (top right, behind the PNG's 2 px frame) holds N03's Shikotan, Kunashiri, Etorofu, Shana and Shibetoro
    districts and the Habomai islets, fitted to the inset's ink on their own (IoU 0.67). The islands are thin, so
    edges dominate that score. Shikotan and Habomai sit a few px off, because the PNG's inset was drawn from a
    different source (the Demis map).
  - Whole-image silhouette IoU 0.9315.
- **Text:** none.
- Comparison: `Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_shadow-hokkaido.png`.
