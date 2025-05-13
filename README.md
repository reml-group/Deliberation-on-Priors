# Deliberation-on-Priors (Anonymous Submission)

<p align="center">
  <img src="images/framework.png" alt="Framework Overview" width="700"/>
</p>

This repository contains the source code for our NeurIPS 2025 submission, currently under double-blind review.

## 🛠️ Project Structure


```bash
.
├── images/              # Framework images and figures
├── utils/               # Utility functions
├── models/              # Core model components
├── data/                # Data
├── data_process/        # Data loading and preprocessing
├── scripts/             # Shell scripts for running experiments
├── main.py              # Entry point script (if applicable)
├── requirements.txt     # Dependency list
└── README.md            # This file
```

## 🚀 Getting Started

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Dataset Preparation
We use three benchmark datasets in our experiments: WebQSP, ComplexWebQuestions (CWQ), and MetaQA.

For WebQSP and CWQ, we adopt the same preprocessing protocol as [RoG](https://arxiv.org/abs/2310.01061), and directly use the publicly released datasets: [RoG-WebQSP](https://huggingface.co/datasets/rmanluo/RoG-webqsp "点击查看 HuggingFace 页面") and [RoG-CWQ](https://huggingface.co/datasets/rmanluo/RoG-cwq "点击查看 HuggingFace 页面")

Please download the datasets and place them under the `datasets/` directory:
```bash
datasets/
├── RoG-webqsp/
└── RoG-cwq/
```
