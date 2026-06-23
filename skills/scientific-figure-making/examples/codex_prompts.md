# Codex prompt examples

Use these prompts when calling this repository from Codex.

## 1. Generate a main comparison figure

```text
Read AGENTS.md and use skills/scientific-figure-making/SKILL.md.

Task: create a paper-ready grouped bar chart.
Style: 简洁大气，Nature 科研风格，色盲安全。
Semantic roles: Fed-SOLO is proposed; FedAvg-LoRA is baseline; Local LoRA is neutral.
Output: create scripts/plot_main_comparison.py and save figures/main_comparison.png and figures/main_comparison.pdf.
Validation: run python scripts/plot_main_comparison.py. If library code changed, run python -m pytest -q.

Data:
Datasets: GSM8K, MATH, HotpotQA, WebShop
Metric: Accuracy / Success Rate (%)
Fed-SOLO: 72.4, 41.8, 68.2, 58.0
FedAvg-LoRA: 68.1, 38.7, 64.5, 54.2
Local LoRA: 63.0, 34.9, 61.3, 49.8
FedReFT: 66.2, 37.1, 63.8, 52.5
```

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

## 3. Generate an ablation figure

```text
Read AGENTS.md and use skills/scientific-figure-making/SKILL.md.

Task: create an ablation bar chart for a paper.
Style: IEEE 风格，克制，工程感，黑白打印也要可区分。
Semantic roles: Full model is proposed; all w/o variants are ablation; baseline is neutral.
Encoding: use color plus hatch because the figure may be printed in grayscale.
Output: create scripts/plot_ablation.py and save figures/ablation.png and figures/ablation.pdf.
Validation: run the plotting script.

Data:
Methods: Full, w/o routing, w/o SecAgg, w/o DP, Baseline
Accuracy: 78.4, 74.2, 76.0, 75.1, 70.3
```