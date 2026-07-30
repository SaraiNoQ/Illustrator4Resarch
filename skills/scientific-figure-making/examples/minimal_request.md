# Minimal style-first request

Version 0.7 does not require a complete prompt, but it makes unresolved style
choices visible instead of silently applying generic defaults.

```text
/scientific-figure-making

results.csv 是论文主实验结果，Ours 是本文方法。
我还没有决定期刊风格、图类型、配色、字体和版式。
请先读取数据，给出 Style Brief，并针对每个缺失的样式维度推荐方案供我确认。
样式问题之后再列出会影响科学解释的问题；确认前不要正式绘图。
```

If the user wants to delegate everything:

```text
/scientific-figure-making

results.csv 是论文主实验结果，Ours 是本文方法。
全部视觉选择采用你的最佳推荐；如有科学语义不明确再问我。
确认科学含义后生成并检查 PNG、PDF、代码、Figure Spec 和 QA。
```

If a reference image is available:

```text
/scientific-figure-making

把 results.csv 做成论文主图。attached/reference.png 是视觉参考，请先读取它，
沿用可观察的颜色层级、字体方向、图形语法和版式；只询问参考图没有说明的内容。
Ours 是本文方法。
```

Expected incomplete-request behavior:

1. Inspect a designated reference before asking style questions.
2. Create a Style Brief.
3. Ask separately about every unresolved style dimension, with recommendations.
4. Put up to three scientific questions after the style section.
5. Wait until style, chart, and scientific semantics are confirmed.
6. Create a schema 1.1 Figure Spec and runnable script.
7. Render PNG/PDF, run deterministic QA, and inspect original/grayscale output.
8. Revise observed defects before delivery.
