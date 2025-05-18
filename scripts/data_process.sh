#!/bin/bash

set -e  # 若中途出错自动退出

# List of datasets to process
DATASETS=("cwq" "webqsp")

for NAME in "${DATASETS[@]}"; do
  echo "=============================="
  echo "🔄 Processing dataset: $NAME"
  echo "=============================="

  RAW_INPUT_DIR="./data/datasets/RoG-${NAME}"
  INTERMEDIATE_OUTPUT="./data/train_${NAME}_with_paths.jsonl"
  FINAL_OUTPUT="./data/train_${NAME}_sft.jsonl"

  # Step 1: run load_data.py
  echo "🔍 Step 1: Extracting ground paths..."
  python data_process/load_data.py \
    --dataset_file_path ${RAW_INPUT_DIR} \
    --output_file_path ${INTERMEDIATE_OUTPUT} \
    --split train

  # Step 2: run load_sft_data.py
  echo "✏️ Step 2: Formatting for SFT..."
  python data_process/load_sft_data.py \
    --input_path ${INTERMEDIATE_OUTPUT} \
    --output_path ${FINAL_OUTPUT}

  echo "✅ ${NAME} done! SFT data saved to ${FINAL_OUTPUT}"
  echo
done

echo "🎉 All datasets processed!"