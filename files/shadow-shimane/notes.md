# Shadow picture of Shimane prefecture

- **Target:** [File:Shadow picture of Shimane prefecture.png](https://commons.wikimedia.org/wiki/File:Shadow_picture_of_Shimane_prefecture.png), 504×357.
- **Rebuilt from:** 「国土数値情報（行政区域データ）」（国土交通省） N03-2024, municipalities merged and simplified to
  0.0003°, with lakes from 国土数値情報 W09 (湖沼). Terms: Government of Japan Standard Terms of Use 2.0, compatible
  with CC BY 4.0. Release as CC BY 4.0 with that credit.
- **Method:** `python files/shadow-shimane/build.py fit`.
  - The PNG puts the Oki Islands (隠岐郡) in a framed inset at the top left, and Takeshima in a small box in that
    inset's corner. In N03, Takeshima is part of 隠岐の島町; here it is the part north of 37°N.
  - A single fit fails (IoU 0.895). The rest of the prefecture, Oki and Takeshima are each fitted to the ink in their
    own region with scale, aspect, rotation and offset (region IoU 0.945, 0.850, 0.58 for a speck of a few pixels).
  - The two frames (#202020 and #626262) are measured. Lake Shinji and Nakaumi are cut out (W09 lakes of at least
    0.0005 square degrees), as the PNG shows them as holes.
  - Rendered whole-image IoU 0.9275.
- **Text:** none.
- Comparison: `Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_shadow-shimane.png`.
