# Deliberation-on-Priors (Anonymous Submission)

<p align="center">
  <strong>Deliberation on Priors: Trustworthy Reasoning of Large Language Models on Knowledge Graphs</strong>
</p>

<p align="center">
  <img src="images/framework.png" alt="Framework Overview" width="700"/>
</p>

This repository contains the source code for our NeurIPS 2025 submission, currently under double-blind review.

## 🛠️ Project Structure

```bash
.
├── config/                    # Configuration files for training/inference
├── data/                      # Input/output data files (JSONL, results, etc.)
├── data_process/              # Data loading and preprocessing scripts
│   └── load_data.py
├── images/                    # Figures (e.g., framework diagram)
│   └── framework.png
├── reasoning/                 # Main reasoning stage scripts
│   ├── instance.py            # Instantiation stage
│   ├── path_generation.py     # Path generation via vLLM
│   └── reasoning.py           # Introspection stage (path selection & verification)
├── scripts/                   # Main reasoning stage scripts
│   ├── data_process.sh        
│   ├── 
│   └── 
├── utils/                     # Common utility functions
│   ├── common_func.py
│   ├── create_graph.py
│   ├── parse.py
│   ├── prompt_template_list.py
│   ├── statics_caculate.py
│   └── __init__.py
├── LICENSE
├── README.md
└── requirements.txt           # Environment dependencies
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

To process the data for both SFT and KTO training, simply run:
```bash
bash ./scripts/data_process.sh
```
This script performs the following steps for both WebQSP and CWQ:

  - Load and parse the raw subgraph data using the Hugging Face datasets interface
    → implemented in `data_process/load_data.py`.
  - Extract reasoning paths (i.e., ground_paths_with_entity) between topic and answer entities
    → implemented in `data_process/load_data.py`.
  - Format SFT training data by converting paths into prompt-response pairs
    → implemented in `data_process/load_sft_data.py`.
  - Generate KTO training data by constructing positive and negative reasoning path samples. Negative paths are generated via path truncation, entity-path swapping, and relation deletion, as targeted perturbations of the original weak supervision data.
    → implemented in `data_process/load_kto_data.py`.

After completion, the following files will be created under the `data/` directory:
```bash
data/
├── train_webqsp_with_paths.jsonl     # Intermediate output with extracted paths
├── train_webqsp_sft.jsonl            # Prompt-response pairs for SFT training
├── train_webqsp_kto.jsonl            # Positive and negative pairs for KTO
├── train_cwq_with_paths.jsonl
├── train_cwq_sft.jsonl
└── train_cwq_kto.jsonl
```

- For **MetaQA**, we load the dataset directly from its original source and apply our own preprocessing.

### 3. Training
During ***Distillation*** stage, our model is implemented and trained using the [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory)framework — a clean, modular, and extensible framework for fine-tuning large language models.

To reproduce our training setup, first clone and set up LLaMA-Factory and configure the environment as follows:
```bash
git clone --depth 1 https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e ".[torch,metrics]"
```
Then, you can refer to the key configuration we provide under the `config/` directory of this repository:

```bash
./config/dataset_info.json
./config/llama3_lora_sft.yaml
./config/llama3_lora_kto.yaml
```
You can refer to these configuration files to run SFT and [KTO](https://arxiv.org/abs/2402.01306) directly within the LLaMA-Factory framework.
Each file specifies task-related settings such as dataset path, learning rate, batch size, LoRA parameters, etc.

### 4. Reasoning
To simplify experiments and clearly separate modules, we conduct the ***Planning*** and ***Instantiation*** stages of reasoning in an offline manner.
#### a. Planning
In ***Planning*** stage, we use the model fine-tuned during the ***distillation*** stage to generate multi-hop reasoning paths for a given question and topic entities.

🔜 Our fine-tuned model will be released on [Hugging Face](https://huggingface.co/) soon.

We adopt [vLLM](https://github.com/vllm-project/vllm) for fast and efficient decoding during path generation.
vLLM is a high-throughput LLM inference and serving library developed by the Sky Computing Lab at UC Berkeley, now maintained by a broad open-source community.

```bash
CUDA_VISIBLE_DEVICES=0 python -m vllm.entrypoints.openai.api_server \
  --dtype bfloat16 \
  --api-key your_api_key_here \
  --gpu-memory-utilization 0.9 \
  --tensor-parallel-size 1 \
  --trust-remote-code \
  --port 8000 \
  --model /path/to/your/fine-tuned_model
```

Before running the script, make sure to fill in the following variables inside `scripts/run_path_generation.sh`:
```bash
API_KEY="your_api_key_here"
MODEL_NAME_OR_PATH="/path/to/your/fine-tuned_model"
BASE_URL="http://localhost:8000/v1"
```

Then, run the following script to perform path generation:
```bash
bash ./scripts/run_path_generation.sh
```

#### b. Instantiation
The ***Instantiation*** stage takes the generated paths from the previous step as input.
It instantiates each relation path into concrete knowledge graph triplets using a pre-extracted subgraph, and determines which paths are valid (i.e., successfully grounded) and which are not.

```bash
bash ./scripts/instantiation.sh
```

#### c. Introspection
This stage performs iterative path selection and constraint verification.
Constraints are extracted once, and the model repeatedly selects and verifies paths until the constraints are satisfied or no paths remain.

```bash
export API_KEY="sk-xxxx"
```
```bash
python scripts/reasoning.py \
  --model_id "4.1" \
  --api_key ${API_KEY} \
  --base_url "your base url" \
  --input_paths your/input_file/path \
  --output_dir your/output_folder/path \
  --log_prefix "log" \
  --num_repeat 1
```

### 5. Result

<p align="center">
  <img src="images/result.png" alt="Result" width="700"/>
</p>

## 📌 Notes

- This repository is anonymized for double-blind review.  
- All results can be reproduced using the provided scripts and configuration files.  
- Please refer to each stage’s section above for detailed instructions.  
- For any questions during review, clarifications will be made in the rebuttal phase.

