# Shadow picture of Aomori prefecture

- **Target:** [File:Shadow picture of Aomori prefecture.png](https://commons.wikimedia.org/wiki/File:Shadow_picture_of_Aomori_prefecture.png), 420×387,
  silhouette by LERK from Shigenobu Aoki's map data ({{Map of Japan-Shigenobu AOKI}}). Tagged `{{Convert to SVG|locator map}}`.
- **Rebuilt from:** 「国土数値情報（行政区域データ）」（国土交通省） N03-2024, municipalities merged into the
  prefecture and simplified to 0.0005°, plotted in plain lon/lat like the original
  (`tools/n03_prefecture_svg.py`). Terms: Government of Japan Standard Terms of Use 2.0, compatible
  with CC BY 4.0. Release as CC BY 4.0 with that credit.
- **Method:** `python tools/batch_shadow.py Aomori`. Fitted with separate x/y scale (y/x 1.3345, about
  1/cos(latitude)); silhouette IoU against the PNG 0.9537. The original shows Lake Ogawara as a hole; the N03 outline does not (lakes are part of the municipalities).
- **Text:** none.
