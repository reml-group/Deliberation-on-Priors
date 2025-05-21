# Deliberation-on-Priors (DP)

<p align="center">
  <strong>Deliberation on Priors: Trustworthy Reasoning of Large Language Models on Knowledge Graphs</strong>
</p>

<p align="center">
  <img src="images/framework.png" alt="Framework Overview" width="700"/>
</p>


## 🛠️ Project Structure

```bash
Deliberation-on-Priors/
├── config/                      # Configuration files for training or prompting
├── data/
│   ├── metaQA/                  # The MetaQA dataset directly from its original source
│   ├── instance/                # Instantiated reasoning trees
│   ├── PG/                      # Path generation results
│   └── test/                    # Input questions (e.g., CWQ/WebQSP 500 samples)
├── data_process/                # Data preprocessing scripts
│   ├── load_data.py             # Extract ground_paths_with_entity from subgraphs(CWQ/WebQSP)
│   ├── load_metaqa_data.py      # Extract ground_paths_with_entity from subgraphs(MetaQA)
│   ├── load_sft_data.py         # Format SFT data into prompt-response pairs for SFT
│   └── load_kto_data.py         # Generate KTO (positive/negative) training samples
├── images/
│   ├── framework.png            # Framework figure for the paper
│   └── result.png               # Visualization of experimental results
├── reasoning/                   # Core reasoning logic
│   ├── path_generation.py       # Path generation using fine-tuned LLM
│   ├── instantiation.py         # Triplet instantiation for paths(CWQ/WebQSP)
│   ├── instantiation_metaqa.py  # Triplet instantiation for paths(MetaQA)
│   └── introspection.py         # Iterative path selection & constraint checking
├── scripts/                     # Shell scripts for full pipeline execution
│   ├── data_process.sh
│   ├── data_process_metaqa.sh
│   ├── path_generation.sh
│   ├── instantiation.sh
│   ├── instantiation_metaqa.sh
│   └── introspection.sh
├── utils/                        # Utility functions, prompt templates, metrics
├── LICENSE
├── README.md
└── requirements.txt             # Python dependencies
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/reml-group/Deliberation-on-Priors.git
cd Deliberation-on-Priors
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Reasoning on KGs
In this section, we present the overall **Deliberation on Priors (DP)** reasoning workflow.

To simplify experiments and clearly separate modules, we conduct the ***Planning*** and ***Instantiation*** stages of reasoning in an offline manner.

#### a. Planning
In ***Planning*** stage, we use the model fine-tuned during the ***distillation*** stage to generate multi-hop reasoning paths for a given question and topic entities.

> 🔜 Our fine-tuned model will be released on [Hugging Face](https://huggingface.co/) soon.
>
> 📂 Since the model is not yet released, we provide partial path generation results under the `./data/PG/` directory to facilitate quick testing and reproduction.
>
> 📘 For details on how to fine-tune the model used in this stage, please refer to Dataset Preparation and Training section.

We adopt [vLLM](https://github.com/vllm-project/vllm) for fast and efficient decoding during path generation.
vLLM is a high-throughput LLM inference and serving library developed by the Sky Computing Lab at UC Berkeley, now maintained by a broad open-source community.

Install vLLM with `pip` or [from source](https://docs.vllm.ai/en/latest/getting_started/installation/gpu/index.html#build-wheel-from-source):

```bash
pip install vllm
```

After installation, launch the vLLM OpenAI-compatible API server using the following command:
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

Then, run the following script to perform path generation:
```bash
bash scripts/path_generation.sh
```

Before running the script, make sure to fill in the following variables inside `scripts/path_generation.sh`:
```bash
API_KEY="your_api_key_here"
MODEL_NAME_OR_PATH="/path/to/your/fine-tuned_model"
BASE_URL="http://localhost:8000/v1"
```

#### b. Instantiation
The ***Instantiation*** stage takes the generated paths from the previous step as input.
It instantiates each relation path into concrete knowledge graph triplets using a pre-extracted subgraph, and determines which paths are valid (i.e., successfully grounded) and which are not.

For **WebQSP** and **CWQ**, simply run:
```bash
bash scripts/instantiation.sh
```

For **MetaQA**, run:
```bash
bash scripts/instantiation_metaqa.sh
```

> 📦 **Note on Test Sets**
>
> To facilitate quick reproduction and lightweight testing of our reasoning code, we provide two pre-processed test sets under the `data/test/` and `data/PG/` directories:
>
> - `data/test/{cwq,webqsp}_500.jsonl`: A set of 500 test questions, each with at least one valid ground path. We excluded ungroundable questions caused by limitations in RoG’s subgraphs to ensure reliable inference and evaluation.
> - `data/PG/{cwq,webqsp}_500.jsonl`: Corresponding path generation results obtained using our fine-tuned model (already run through the `scripts/path_generation.sh` script).
> - `data/test/metaqa_600.jsonl`, `data/PG/metaqa_600.jsonl`: For MetaQA, we sample 600 test questions in total — 200 from each of the 1-hop, 2-hop, and 3-hop subsets — ensuring coverage across different reasoning depths. Path generation has also been completed in advance for convenience.
>
> These test files allow users to directly run the **Instantiation** and **Introspection** stages **without training or deploying** the full path generation model.
>
> This greatly facilitates faster debugging and exploration of our core reasoning pipeline.
>
> Additionally, using a 500/600-sample subset keeps experiments more economical while preserving representativeness.

#### c. Introspection
The ***Introspection*** stage is the core component of our framework. It performs iterative reasoning by combining large language models with constraint-aware path selection.

Given a set of instantiated candidate paths, the model follows this loop:
1. **Constraint Extraction**: Constraints are extracted once from the question using an LLM.
2. **Path Selection**: The model selects the most promising reasoning path based on current memory and constraints.
3. **Constraint Verification**: The selected path is verified by checking whether it satisfies the extracted constraints.
4. **Feedback and Memory Update**: If verification fails, feedback is recorded and used to inform the next selection round.

This process continues until all constraints are satisfied or no viable paths remain. It simulates a deliberative reasoning process and enables the model to correct itself during inference.

```bash
bash scripts/introspection.sh
```

Before running, please make sure to manually configure the following variables at the top of `scripts/introspection.sh`:

```bash
API_KEY="your_api_key_here"                     # Your OpenAI or vLLM-compatible API key
MODEL="gpt-4.1"                                 # Model name (e.g., gpt-4.1, gpt-4o)
BASE_URL="api server url"                       # Base URL
```

### 4. Dataset Preparation
We use three benchmark datasets in our experiments: **WebQSP**, **ComplexWebQuestions (CWQ)**, and **MetaQA**.

For **WebQSP** and **CWQ**, we adopt the same preprocessing protocol as previous studies, and directly use the preprocessed datasets released by [RoG](https://arxiv.org/abs/2310.01061). These datasets follow standard subgraph extraction methods established in [prior work](https://github.com/RichardHGL/WSDM2021_NSM/tree/main/preprocessing/Freebase). 

  - [RoG-WebQSP](https://huggingface.co/datasets/rmanluo/RoG-webqsp)
  - [RoG-CWQ](https://huggingface.co/datasets/rmanluo/RoG-cwq)

To process the data for both SFT and KTO training, simply run:
```bash
bash scripts/data_process.sh
```
This script performs the following steps for both WebQSP and CWQ:

  - Load and parse the raw subgraph data using the Hugging Face datasets interface
    → implemented in `data_process/load_data.py`(automatically downloads RoG-WebQSP and RoG-CWQ datasets).
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

For **MetaQA**, we load the dataset directly from its original source and apply our own preprocessing. To process the data, simply run:
```bash
bash scripts/metaqa_process.sh
```

### 5. Training
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

### 6. Result

<p align="center">
  <img src="images/result.png" alt="Result" width="700"/>
</p>
