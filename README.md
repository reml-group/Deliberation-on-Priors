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
We use three benchmark datasets in our experiments: **WebQSP**, **ComplexWebQuestions (CWQ)**, and **MetaQA**.

- For **WebQSP** and **CWQ**, we adopt the same preprocessing protocol as previous studies, and directly use the preprocessed datasets released by [RoG](https://arxiv.org/abs/2310.01061). These datasets follow standard subgraph extraction methods established in [prior work](https://github.com/RichardHGL/WSDM2021_NSM/tree/main/preprocessing/Freebase).

  - [RoG-WebQSP](https://huggingface.co/datasets/rmanluo/RoG-webqsp)
  - [RoG-CWQ](https://huggingface.co/datasets/rmanluo/RoG-cwq)

  Please download the datasets and place them under the `data/` directory:

```bash
data/
├── RoG-webqsp/
└── RoG-cwq/
```


