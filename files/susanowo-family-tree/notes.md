# Susanowo family tree (スサノオの系図)

- **Target:** [File:Susanowo family tree.png](https://commons.wikimedia.org/wiki/File:Susanowo_family_tree.png),
  444×817, by nnh (2005), "selfmade by MS-Paint". GFDL / CC BY-SA 3.0 migrated / CC BY 2.5.
- **Rebuilt from scratch**, since there is no vector source:
  - Lines: the PNG is aliased 1 px MS Paint art, so every straight run (21 horizontal including the
    double marriage lines, 18 vertical) is taken as an exact segment. The dotted line (x 201: solid,
    1-on/1-off, solid) and the hop where the line from 大山津見神 crosses the 須佐之男命 marriage
    line are drawn as paths.
  - Names: 26 names as vertical `<text writing-mode="tb">`, 16 px, red for female and blue for male
    as in the PNG, bold for 建速須佐之男命, 大年神 and 大国主神. The three names set in two columns
    (布波能母遅久奴須奴神, 深淵之水夜礼花神, 天之都度閇知泥神) are one `<text>` each with two
    `<tspan>` columns, so they translate as one unit. Black notes 禊, 誓約 and （宗像三神） at 12 px.
  - Ink boxes of the names match the PNG within 1 px.
- **Transcription:** read off the image and checked against the Kojiki genealogy of Susanoo.
- **Not yet checked:** librsvg's handling of `writing-mode="tb"` (vertical text) on Commons. If it
  renders poorly there, the fallback is one positioned `<tspan>` per character inside each `<text>`.
- Same licences as the original.
