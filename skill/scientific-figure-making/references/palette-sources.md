# Palette sources

The registry is local-first and compact. It is not a full mirror of external datasets.

Source families used for design principles:

- ColorBrewer-like qualitative, sequential, and diverging palettes.
- Okabe-Ito / Tol-style colorblind-safe categorical palettes.
- Matplotlib scientific colormap samples such as viridis and cividis.
- CMasher/colorspace/scientific-colormap literature: perceptual uniformity and color-vision-deficiency safety.
- Curated Nature/IEEE-like publication palettes.

Why local-first:

- Online palette websites are often optimized for decorative UI design rather than scientific readability.
- Runtime web scraping is brittle and may fail during figure generation.
- Paper figures need stable semantic color roles across plots.
- Accessibility and print safety matter more than novelty.
