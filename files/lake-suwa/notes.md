# File:Size of Lake Suwa.png → SVG

Rebuilt from public data (`files/lake-suwa/build.py`). The map is plain Web Mercator: the current lake fits the PNG's
dark-blue lake at IoU 0.975, with no rotation.

- **Current lake (759 m):** 諏訪湖 from MLIT 国土数値情報 W09 (湖沼).
- **Land bands:** from the GSI 10 m DEM (地理院タイル dem, zoom 14; tiles in `data_lake/downloads/gsi-dem-suwa/`),
  lightly smoothed. 765–800 m is pale, 800–900 m mid, and above 900 m dark. The thresholds come from sampling the DEM
  under each of the PNG's colours.
- **Lake of ca. 500–1000 CE:** ground below 765 m (the level the description gives), keeping the parts the PNG paints
  as lake. The real 765 m contour adds a side valley at the southeast end that the PNG's hand-estimated outline (from
  *suwazine* vol. 2) leaves out.
- **Rivers:** MLIT 国土数値情報 W05 (河川), keeping the ones the PNG draws: those whose projected course lies mostly on
  its light-blue river pixels.
- **Labels:** all real `<text>` in Bahnschrift, a DIN face like the PNG's, fitted to its lettering. The two shrine
  marks (torii) are drawn as beams and posts in the PNG's red.

Comparison: `Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_lake-suwa.png`.

Licence: CC BY-SA 4.0, as the PNG (Pat457), crediting 「国土数値情報（湖沼・河川データ）」（国土交通省） and
「地理院タイル（標高タイル）」（国土地理院）. Both are under terms compatible with CC BY 4.0.
