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
| Charges between a fess not drawn | Gules, a fess between six crosses crosslet or | beauchamp-john, beauchamp-bergavenny | |
| 'on the fess a mullet' not parsed; a crescent with an ordinary drawn shield-sized | Gules, a fess between six crosses crosslet or, a crescent sable | beauchamp-john, beauchamp-bergavenny | |
| Fess between two chevrons: chevrons dropped | Or, a fess between two chevrons sable | lisle-john | |
| 'passant' goat drawn rearing; 'bordure embattled' drawn plain | Or, a goat passant sable, a bordure embattled sable | cabrera-viscounts | |
| 'fimbriated' not drawn | Azure, a cross gules fimbriated or between four fleurs-de-lis or | clermont-bishopric | |
| Charge between a beast's horns | (bull's head with a patriarchal cross between the horns) | terter | |
| No drawing for the cross of Toulouse | Gules, a cross clechy voided and pommetty or | toulouse-tripoli | charge-no-drawing: cross clechy, pommetty |
| 'an orle of martlets' drawn as one large martlet | Quarterly, 1st and 4th or, a maunch gules; 2nd and 3rd barry of twelve argent and azure, an orle of martlets gules | hastings-john-2nd, hastings-pembroke | none (silent) |
| Untinctured arms (Swedish medieval seals drawn in grey) have no tincture to blazon | (a lion rampant, untinctured) | COA-Bengt Magnusson, COA-staende lejon, COA-Birger Filipsson, Vingad pil, vingad pilspets | no concept for 'untinctured' |
| Bars embattled on one edge | (PNG: gules, two bars embattled argent) | berg-old | none |

Also seen, minor: 'Gules, three crowns or' leaves thin dark arcs above the two upper crowns.
