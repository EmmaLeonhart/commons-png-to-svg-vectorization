# Nigeria Rivers State map

- **Target:** [File:Nigeria Rivers State map.png](https://commons.wikimedia.org/wiki/File:Nigeria_Rivers_State_map.png),
  777×599, by Himalayan Explorer (2010-02-11), CC BY-SA 3.0.
- **Rebuilt from:** the 2010-02-11 revision of [File:Nigeria location map.svg](https://commons.wikimedia.org/wiki/File:Nigeria_location_map.svg)
  by Uwe Dedering (saved as `data_lake/downloads/nigeria-rivers-state/Nigeria location map (2010-02-11 revision).svg`).
  This is the revision that existed when the PNG was made; its border lines match the PNG at
  0.90 IoU. The current revision (December 2010) redrew the states and matches worse (0.67).
  CC BY-SA 3.0, the same as the original.
- **Method:** `python files/nigeria-rivers-state/build.py`. That revision has no state polygons, only
  border lines. The PNG's red was flood-filled, so it stops at rivers as well as borders. The
  build cuts the land shape along the state lines, the national border and the rivers, keeps
  every piece that is mostly red in the PNG (5 pieces), and inserts their union as one path
  above the land and below the lines. The red area matches the PNG at IoU 0.943.
- **Differences:** creeks inside the red area show the source's blue river lines; in the PNG
  they are pale.
- **Text:** none.
- **Checked:** in Chrome against the PNG.
