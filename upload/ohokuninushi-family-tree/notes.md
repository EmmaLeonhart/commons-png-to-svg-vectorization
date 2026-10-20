# Ohokuninushi family tree (大国主の系図)

- **Target:** [File:Ohokuninushi family tree.png](https://commons.wikimedia.org/wiki/File:Ohokuninushi_family_tree.png),
  441×993, by nnh (2005), "selfmade by MS-Paint and OpenOffice.org", after the Kojiki.
  GFDL / CC BY 2.5 (same tags as the original).
- **Rebuilt from scratch** with `python tools/rebuild_tree.py files/ohokuninushi-family-tree/spec.json`:
  - lines: 32 horizontal and 33 vertical exact 1 px segments extracted from the aliased line art (the
    dashed line under 速須佐之男命 is its dashes as segments) and 2 filled dots as circles. Every black
    pixel is explained; black-pixel IoU against the PNG is 0.991;
  - names: 36 vertical `<text>` (red / blue / `#cccc00` as in the PNG, 大国主神 bold), with
    seven two-column names as one `<text>` with two `<tspan>`s. The names are in `spec.json`, read off
    the image and checked against the Kojiki genealogy of Ōkuninushi.
- **Not yet checked:** librsvg's vertical text (`writing-mode="tb"`).
