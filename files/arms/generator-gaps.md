# What Emma's arms generator could not draw (found while rebuilding order.life arms)

Written by this repo for the Sodacan-arms-svg-generator session; this repo does not edit that one.
Generator commit 8d8ab870. Each case is a real coat of arms of an order.life person whose only
image on Commons is a PNG. Every blazon below parses fully; the drawing is what falls short.
Pictures (Commons PNG left, generator right):
`Documents\claude-screenshots\agentic-vectorization_2026-10-15\cmp_<slug>.png`.

| Gap | Blazon | Files | Generator note |
|---|---|---|---|
| No drawing for a cross patonce | Gules, a cross patonce argent / vair | vescy-eustace, fortibus-william, deforz | charge-no-drawing: cross patonce |
| No layout for many charges between an ordinary | Gules, a chevron between ten crosses pattee argent | berkeley | charge-no-layout: 10\|between:chevron |
| No layout for six charges between a bend; cotises not drawn | Azure, a bend argent cotised or between six lions rampant or | bohun, bohun-henry | charge-no-layout: 6\|between:bend |
| No drawing for mascles | Gules, seven mascles or | ferrers | charge-no-drawing: mascle |
| 'in pale' ignored (three charges set two and one) | Or, three lions passant in pale sable | carew, giffard-brimpsfield, erik-eriksson | none (silent) |
| 'counterchanged' not applied to charges | Quarterly or and gules, four lions rampant counterchanged | glyndwr | none (silent) |
| Roundels 'in chief' drawn as a scalloped chief | Argent, two bars gules, in chief three torteaux | moels | none (silent) |
| Label of eleven points drawn with three, low on the shield | Or, a fess gules, a label of eleven points azure | quincy-saire | none (silent) |
| Bars embattled on one edge | (PNG: gules, two bars embattled argent) | berg-old | none |

Also seen, minor: 'Gules, three crowns or' leaves thin dark arcs above the two upper crowns.
