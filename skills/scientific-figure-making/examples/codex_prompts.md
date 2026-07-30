# Codex prompt examples

Use these prompts when calling this repository from Codex.

## 1. Guided main-results request

This is the preferred v0.9 intake test because it supplies structured data while
leaving visual design undecided.

```text
Read AGENTS.md and use skills/scientific-figure-making/SKILL.md.

这些是论文主实验结果，请完成投稿级主图。Fed-SOLO 是本文方法；我还没有决定投稿风格、图类型、布局、配色和字体。请先给出 Style Brief，对每个缺失维度给出推荐并让我确认；样式问题之后再问科学问题，确认前不要正式绘图。

Data:
Datasets: GSM8K, MATH, HotpotQA, WebShop
Metric: Accuracy / Success Rate (%)
Fed-SOLO: 72.4, 41.8, 68.2, 58.0
FedAvg-LoRA: 68.1, 38.7, 64.5, 54.2
Local LoRA: 63.0, 34.9, 61.3, 49.8
FedReFT: 66.2, 37.1, 63.8, 52.5
```

Expected behavior:

- create a Style Brief before scientific interpretation;
- ask venue, chart/grammar, palette, typography, and layout separately;
- recommend an answer for each style question;
- normalize and audit the input before rendering;
- wait for data, style, and scientific confirmation;
- create a schema 1.2 Figure Spec and render only after confirmation;
- export compact outer bounds and run deterministic plus visual QA.

## 2. Preview palettes only

```text
Read AGENTS.md. Use scientific_figure_skill.auto_palette and suggest_palettes.
For the request "简洁大气，Nature科研风格，适合多方法柱状图", preview the top 6 palette candidates.
Return the selected palette name, hex colors, semantic roles, and a short explanation.
Do not generate a figure.
```

Equivalent command:

```bash
python skills/scientific-figure-making/scripts/preview_palette.py "简洁大气，Nature科研风格" --figure-type grouped_bar --n-colors 5 --top-k 6
```

## 3. Critical uncertainty question

```text
Read AGENTS.md and use skills/scientific-figure-making/SKILL.md.

请把以下消融结果画成论文图：Full 78.4 ± 0.7, w/o routing 74.2 ± 1.1,
w/o SecAgg 76.0 ± 0.8, w/o DP 75.1 ± 0.9, Baseline 70.3 ± 1.4。
Accuracy 越高越好，其他你来决定。
```

Expected behavior: recommend the chart, but ask whether `±` means SD, SE, CI,
range, or another quantity before rendering error bars. Because “其他你来决定”
is explicit delegation, do not ask redundant style questions.

## 4. Refinement mode

```text
Read AGENTS.md and use skills/scientific-figure-making/SKILL.md.

Inspect figures/current.png and scripts/plot_current.py. The legend hides two
curves, the x tick labels overlap, and the left outer margin wastes space.
Improve it to submission quality without changing any values. Preserve the
current blue for Ours. Inspect the original image before editing, then render,
check `outer_whitespace`, and compare the revision.
```

## 5. Designated visual reference

```text
Read AGENTS.md and use skills/scientific-figure-making/SKILL.md.

Use results.csv for the main paper figure. references/target.png is the visual
reference: preserve its color hierarchy, sans-serif direction, open axes, and
top legend. Inspect it before asking questions and ask only about unresolved
style or scientific details.
```

## 6. Table screenshot as data

```text
Read AGENTS.md and use skills/scientific-figure-making/SKILL.md.

attached/results-table.png is a screenshot of my experiment table and is the
primary data source. Inspect it at original resolution, transcribe it into a
normalized CSV, and show the extracted table after the style questions. Do not
render until I confirm the transcription. If the attachment is a chart rather
than a table, ask me for the underlying values instead of digitizing it.
```
