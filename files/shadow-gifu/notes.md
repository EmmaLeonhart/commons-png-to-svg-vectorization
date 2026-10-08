# Shadow picture of Gifu prefecture

- **Target:** [File:Shadow picture of Gifu prefecture.png](https://commons.wikimedia.org/wiki/File:Shadow_picture_of_Gifu_prefecture.png), 337×387,
  silhouette by LERK from Shigenobu Aoki's map data ({{Map of Japan-Shigenobu AOKI}}). Tagged `{{Convert to SVG|locator map}}`.
- **Rebuilt from:** 「国土数値情報（行政区域データ）」（国土交通省） N03-2024, municipalities merged into the
  prefecture and simplified to 0.0005°, plotted in plain lon/lat like the original
  (`tools/n03_prefecture_svg.py`). Terms: Government of Japan Standard Terms of Use 2.0, compatible
  with CC BY 4.0. Release as CC BY 4.0 with that credit.
- **Method:** `python tools/batch_shadow.py Gifu`. Fitted with separate x/y scale (y/x 1.2073, about
  1/cos(latitude)); silhouette IoU against the PNG 0.9737.
- **Text:** none.
