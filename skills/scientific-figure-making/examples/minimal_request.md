# Example skill request

```text
/scientific-figure-making

请根据下面的数据画一张论文主实验 grouped bar：

风格：简洁大气，Nature科研风格，色盲安全。
方法：Fed-SOLO, FedAvg-LoRA, Local LoRA, FedReFT。
数据集：GSM8K, MATH, HotpotQA, WebShop。
指标：Accuracy / Success Rate (%)。
数据：
Fed-SOLO: 72.4, 41.8, 68.2, 58.0
FedAvg-LoRA: 68.1, 38.7, 64.5, 54.2
Local LoRA: 63.0, 34.9, 61.3, 49.8
FedReFT: 66.2, 37.1, 63.8, 52.5

要求：自动选择最合适的 palette，Fed-SOLO 是 proposed，FedAvg-LoRA 是 baseline，导出 PNG 和 PDF。
```
