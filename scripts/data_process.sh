#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# List of datasets to process
DATASETS=("cwq" "webqsp")

for NAME in "${DATASETS[@]}"; do
  echo "=============================="
  echo "🔄 Processing dataset: $NAME"
  echo "=============================="

  HF_DATASET_NAME="rmanluo/RoG-${NAME}"
  INTERMEDIATE_OUTPUT="./data/train_${NAME}_with_paths.jsonl"
  SFT_OUTPUT="./data/train_${NAME}_sft.jsonl"
  KTO_OUTPUT="./data/train_${NAME}_kto.jsonl"

  # Set max_path_len per dataset
  if [ "$NAME" == "cwq" ]; then
    MAX_PATH_LEN=4
  elif [ "$NAME" == "webqsp" ]; then
    MAX_PATH_LEN=2
  else
    echo "❌ Unknown dataset: $NAME"
    exit 1
  fi

  # Step 1: run load_data.py
  echo "🔍 Step 1: Extracting ground paths..."
  python data_process/load_data.py \
    --hf_dataset_name ${HF_DATASET_NAME} \
    --output_file_path ${INTERMEDIATE_OUTPUT} \
    --split train

  # Step 2: run load_sft_data.py
  echo "✏️ Step 2: Formatting for SFT (max_path_len=${MAX_PATH_LEN})..."
  python data_process/load_sft_data.py \
    --input_path ${INTERMEDIATE_OUTPUT} \
    --output_path ${SFT_OUTPUT} \
    --max_path_len ${MAX_PATH_LEN}

  # Step 3: run load_kto_data.py
  echo "⚖️ Step 3: Generating KTO data (max_path_len=${MAX_PATH_LEN})..."
  python data_process/load_kto_data.py \
    --input_path ${INTERMEDIATE_OUTPUT} \
    --output_path ${KTO_OUTPUT} \
    --max_path_len ${MAX_PATH_LEN}

  echo "✅ ${NAME} done! SFT: ${SFT_OUTPUT} | KTO: ${KTO_OUTPUT}"
  echo
done

echo "🎉 All datasets processed!"