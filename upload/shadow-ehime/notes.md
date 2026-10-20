# Shadow picture of Ehime prefecture

- **Target:** [File:Shadow picture of Ehime prefecture.png](https://commons.wikimedia.org/wiki/File:Shadow_picture_of_Ehime_prefecture.png), 510×365.
- **Rebuilt from:** 「国土数値情報（行政区域データ）」（国土交通省） N03-2024, municipalities merged into the
  prefecture and simplified to 0.0003°. Terms: Government of Japan Standard Terms of Use 2.0, compatible with
  CC BY 4.0. Release as CC BY 4.0 with that credit.
- **Method:** `python files/shadow-ehime/build.py fit`. Unlike the other shadow pictures, this one is drawn rotated
  (29.4°), which `tools/batch_shadow.py` does not allow for: its fit sheared the shape (IoU 0.52). The direct fit
  with scale, aspect (1.22, about 1/cos(latitude)), rotation and offset reaches silhouette IoU 0.9313. The PNG fills
  in the southwest's ria coast a little more than the real data does.
- **Text:** none.
- Comparison: `Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_shadow-ehime.png`.
