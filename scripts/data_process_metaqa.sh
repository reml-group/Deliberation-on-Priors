#!/bin/bash

set -e  # Exit on error

# ===== 参数配置 =====
KB_PATH="./data/metaQA/kb.txt"
DATASET_DIR="./data/metaQA"
OUTPUT_DIR="./data/processed_metaqa"

mkdir -p "${OUTPUT_DIR}"

HOPS=("1-hop" "2-hop" "3-hop")
MAX_PATH_LENS=(1 2 3)

# Step 1: Extract ground paths from KB
echo "🔍 Step 1: Extracting ground paths from KB..."
python data_process/load_metaqa_data.py \
  --kb_path "${KB_PATH}" \
  --dataset_dir "${DATASET_DIR}" \
  --output_dir "${OUTPUT_DIR}"

# Step 2: For each hop, convert to SFT format
echo "✏️ Step 2: Formatting SFT data for each hop..."

for i in "${!HOPS[@]}"; do
  HOP="${HOPS[$i]}"
  MAX_LEN="${MAX_PATH_LENS[$i]}"
  echo "🚀 Processing ${HOP} (max_path_len=${MAX_LEN})"

  INPUT_PATH="${OUTPUT_DIR}/${HOP}/qa_train.jsonl"
  OUTPUT_PATH="./data/train_metaqa_${HOP}_sft.jsonl"

  python data_process/load_sft_data.py \
    --input_path "${INPUT_PATH}" \
    --output_path "${OUTPUT_PATH}" \
    --max_path_len ${MAX_LEN}

  echo "✅ SFT data saved to ${OUTPUT_PATH}"
  echo
done

echo "🎉 All MetaQA hops processed!"