# Message-driven chart selection

Choose a chart from the scientific question and data structure. Chart names in
the request are preferences, not a substitute for checking whether the form
communicates the data honestly.

## Decision guide

| Scientific task | Preferred forms | Avoid by default |
| --- | --- | --- |
| Compare methods across a few datasets | grouped dot plot, grouped bar, small multiples | stacked bars |
| Rank many methods on one metric | ordered horizontal bar or dot plot | unsorted vertical bars |
| Show change over rounds/time | line plot with markers and uncertainty band | bars for dense time points |
| Show distributions or raw replicates | box/violin plus points, interval plot | mean-only bars |
| Show two-variable relationship | scatter with fit only when justified | dual-axis line plot |
| Show accuracy/cost trade-off | scatter with Pareto frontier | combining unlike units on one axis |
| Show matrix structure | heatmap with correct sequential/diverging scale | categorical rainbow map |
| Show signed residuals/deltas | zero-centered diverging heatmap or dot plot | sequential colormap |
| Show component contribution | ordered ablation dot/bar, waterfall when additive | pie chart |
| Show composition | stacked bar/area when totals are meaningful | overlapping lines |
| Show multiple linked messages | aligned multi-panel figure | one overloaded axes |

## Chart-specific reasoning

### Bars versus dots

Use bars when a zero baseline and magnitude comparison are meaningful and the
number of groups is modest. Prefer dots or intervals when:

- the axis does not naturally start at zero;
- small differences matter;
- confidence intervals are central;
- the chart contains many methods.

If a non-zero bar baseline is necessary, disclose it prominently and consider a
dot plot instead.

### Lines

Use connecting lines only when the x-axis has an ordered or continuous meaning.
Do not connect unrelated datasets merely to make a method profile unless that
comparison is explicitly intended. Combine color with marker or linestyle when
there are multiple series.

### Heatmaps

Use sequential color for magnitude, diverging color for values centered on a
meaningful reference, and cyclic color for phase or angle. Annotate cells only
when the matrix is small enough for text to remain legible.

### Scatter and trade-offs

Map each quantity to a separate axis with units. Label or otherwise identify
important methods. Draw a Pareto frontier only after confirming the preferred
direction of every axis. Do not imply a regression or causal relationship
without justification.

### Uncertainty

Use raw replicates when available. Otherwise render uncertainty only after its
meaning is known. Captions and legends should distinguish SD, SE, CI, range, and
percentiles.

## Multi-panel decomposition

Use multiple panels when:

- metrics have incompatible units or ranges;
- one panel would need more than one y-axis;
- distribution and aggregate views are both necessary;
- a main result and an ablation support different messages;
- labels or series would become unreadable in one panel.

Give panels a shared visual language, aligned axes when comparable, and panel
labels `(a)`, `(b)`, and so on. Do not share axes across panels with
incompatible units.

## Respecting explicit requests

Honor a user's explicit chart choice when it is scientifically defensible. If
the requested form risks distortion, explain the issue and recommend a safer
alternative before rendering. Do not silently substitute a materially
different story.
