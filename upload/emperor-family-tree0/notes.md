# Emperor family tree0 (天皇家系図 神代)

- **Target:** [File:Emperor family tree0.png](https://commons.wikimedia.org/wiki/File:Emperor_family_tree0.png),
  339×860, by nnh (2005), "selfmade by MS-Paint". GFDL / CC BY 2.5 (same tags as the original).
- **Rebuilt from scratch** with `python tools/rebuild_tree.py files/emperor-family-tree0/spec.json`:
  - black lines: 31 horizontal, 33 vertical and 2 diagonal exact segments, plus 2 dotted runs (the
    dotted descent to 大国主神 and the dotted bar of the bracket at 大物主神). Only 3 black pixels are
    left unexplained. The hop over the 須佐之男命 line is a 12 px arc (`extra` in the spec);
  - the grey line dividing 国津神系 / 天津神系 is 7 exact segments, drawn over the black as in the PNG;
  - 23 names as vertical `<text>` (5 in two columns), and the notes 国津神系, 天津神系 (twice each),
    幸魂・奇魂 (vertical) and "1" at 12 px. The names were read off the image and follow the Kojiki
    line from 伊邪那岐神 / 伊邪那美神 to 神武天皇.
- **Not yet checked:** librsvg's vertical text (`writing-mode="tb"`).
