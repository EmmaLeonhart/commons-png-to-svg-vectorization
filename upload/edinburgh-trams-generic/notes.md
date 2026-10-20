# EdinburghTramsGeneric

- **Target:** [File:EdinburghTramsGeneric.png](https://commons.wikimedia.org/wiki/File:EdinburghTramsGeneric.png), 1000×909,
  "a symbol intended to represent Edinburgh Trams ... loosely based on the shape and colours of the graphical portion
  of the system's official logo", own work by G-13114, PD-shape.
- **Rebuilt as:** a grey disc (ellipse from the opaque mask's moments; it is practically a circle, r 388) and four
  straight bands, two red and two white. Each band's centre line and half-width come from a PCA fit to its colour
  mask (two-line k-means within each colour, `bands.json`); they are clipped to the disc and stacked as the PNG's
  crossings show (red NW–SE, white SW–NE, white NW–SE, red SW–NE on top).
- **Check:** IoU per colour: disc 0.999, grey 0.968, white 0.952, red 0.924 (the original's bands are hand-drawn
  and taper slightly). PD-shape.
