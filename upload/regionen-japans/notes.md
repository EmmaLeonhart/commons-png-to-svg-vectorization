# File:Regionen japans.png → SVG

Built by `files/regionen-japans/build.py` from Natural Earth 10m admin-1 prefectures (public domain) in a Lambert
conformal conic. Each prefecture is filled with its region's colour, using the PNG's eight colours and the standard
eight regions (Hokkaidō, Tōhoku, Kantō, Chūbu, Kansai, Chūgoku, Shikoku, Kyūshū with Okinawa), with black prefecture
borders. Okinawa Island sits in the PNG's inset, and the inset's grey frame is measured.

The call (as for the other generalised Japan maps): the PNG's outline is hand-drawn and squeezes the west. Overlaid on
real geography it only reaches land IoU 0.58, and that fit pushes Kyūshū off the canvas. So the real map is laid out
to fill the PNG's land extent (the largest scale that fits, centred) rather than traced. Real Japan is wider than the
drawing, so the map comes out a little smaller. Comparison:
`Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_regionen-japans.png`.

Licence: as the PNG, GFDL (Christian Günther, {{GFDL|migration=relicense}}, so also CC BY-SA 3.0). The geography is
Natural Earth (public domain).
