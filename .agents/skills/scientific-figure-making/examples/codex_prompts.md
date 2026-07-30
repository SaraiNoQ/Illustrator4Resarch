# Codex prompt examples

Use these prompts when calling this repository from Codex.

## 1. Guided main-results request

This is the preferred v0.6 test because it does not preselect a chart or style.

```text
Read AGENTS.md and use skills/scientific-figure-making/SKILL.md.

这些是论文主实验结果，请完成投稿级主图。图类型、布局、配色和输出细节由你根据论文表达需要决定。Fed-SOLO 是本文方法；没有提供的普通视觉要求采用合理默认值。生成后检查真实图片并修复问题。

Data:
Datasets: GSM8K, MATH, HotpotQA, WebShop
Metric: Accuracy / Success Rate (%)
Fed-SOLO: 72.4, 41.8, 68.2, 58.0
FedAvg-LoRA: 68.1, 38.7, 64.5, 54.2
Local LoRA: 63.0, 34.9, 61.3, 49.8
FedReFT: 66.2, 37.1, 63.8, 52.5
```

Expected behavior:

- create a Figure Brief;
- do not ask the user to choose a chart or palette;
- create a Figure Spec;
- render PNG/PDF and a runnable script;
- run deterministic QA;
- create and inspect an original/grayscale preview;
- revise observed defects.

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
range, or another quantity before rendering error bars.

## 4. Refinement mode

```text
Read AGENTS.md and use skills/scientific-figure-making/SKILL.md.

Inspect figures/current.png and scripts/plot_current.py. The legend hides two
curves and the x tick labels overlap. Improve it to submission quality without
changing any values. Preserve the current blue for Ours. Inspect the original
image before editing, then render and compare the revision.
```
