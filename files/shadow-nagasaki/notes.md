# Shadow picture of Nagasaki prefecture

- **Target:** [File:Shadow picture of Nagasaki prefecture.png](https://commons.wikimedia.org/wiki/File:Shadow_picture_of_Nagasaki_prefecture.png), 501×329.
- **Rebuilt from:** 「国土数値情報（行政区域データ）」（国土交通省） N03 of 2000-10-01, municipalities merged and
  simplified to 0.0003°. The 2024 data adds the Isahaya Bay reclamation, which the PNG lacks. Terms: Government of
  Japan Standard Terms of Use 2.0, compatible with CC BY 4.0. Release as CC BY 4.0 with that credit.
- **Method:** `python files/shadow-nagasaki/build.py fit`. The PNG has two framed insets: Tsushima on the left (behind
  a stepped frame line) and Iki in a box at the top. So a single fit fails (`tools/shadow_rotfit.py`: IoU 0.31). The
  rest of the prefecture, Tsushima (上県郡, 下県郡) and Iki (壱岐郡) are each fitted to the ink in their own region with
  scale, aspect, rotation and offset (region IoU 0.86, 0.89, 0.86). The 1 px frame lines are measured, and a 1 px
  outline matches the PNG's slightly bolder silhouettes.
- **Result:** whole-image IoU 0.869. That is below the 0.93 used for single-outline prefectures, but the layout and
  insets are in register. What remains is the PNG's smoothed outlines of this prefecture's hundreds of islets at
  501×329.
- **Text:** none.
- Comparison: `Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_shadow-nagasaki.png`.
