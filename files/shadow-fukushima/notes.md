# Shadow picture of Fukushima prefecture

- **Target:** [File:Shadow picture of Fukushima prefecture.png](https://commons.wikimedia.org/wiki/File:Shadow_picture_of_Fukushima_prefecture.png), 504×401,
  silhouette by LERK from Shigenobu Aoki's map data ({{Map of Japan-Shigenobu AOKI}}). Tagged `{{Convert to SVG|locator map}}`.
- **Rebuilt from:** 「国土数値情報（行政区域データ）」（国土交通省） N03-2024, municipalities merged into the
  prefecture and simplified to 0.0005°, plotted in plain lon/lat like the original
  (`tools/n03_prefecture_svg.py`). Terms: Government of Japan Standard Terms of Use 2.0, compatible
  with CC BY 4.0. Release as CC BY 4.0 with that credit.
- **Method:** `python tools/batch_shadow.py Fukushima`. Fitted with separate x/y scale (y/x 1.2783, about
  1/cos(latitude)); silhouette IoU against the PNG 0.9807.
- **Text:** none.
