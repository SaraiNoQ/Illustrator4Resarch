# Minimal guided request

Version 0.6 does not require a complete plotting prompt.

```text
/scientific-figure-making

results.csv 是论文主实验结果，请你决定最合适的论文图。
Ours 是本文方法；没有说明的普通设计要求请使用合理默认值。
生成后检查真实导出图片并修复问题。
```

If data is pasted directly:

```text
/scientific-figure-making

请把下面的实验结果制作成论文主图，图类型、布局、配色和输出细节由你决定。

Datasets: GSM8K, MATH, HotpotQA, WebShop
Metric: Accuracy (%), higher is better
Ours: 72.4, 41.8, 68.2, 58.0
Baseline A: 68.1, 38.7, 64.5, 54.2
Baseline B: 63.0, 34.9, 61.3, 49.8
```

The expected behavior is:

1. Create a Figure Brief.
2. Ask only if scientific semantics are missing.
3. Choose and explain the chart.
4. Use publication-safe defaults for presentation.
5. Save a Figure Spec and runnable script.
6. Render PNG/PDF.
7. Run deterministic QA.
8. Generate and inspect an original/grayscale preview.
9. Revise observed defects before delivery.
