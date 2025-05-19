#!/bin/bash

set -e

# === 参数配置 ===
DATASETS=("cwq" "webqsp")

for NAME in "${DATASETS[@]}"; do
  echo "=============================="
  echo "🧩 Instantiating reasoning paths for ${NAME}"
  echo "=============================="

  INPUT_PATH="./data/PG_${NAME}_500.jsonl"   # Path generation 的输出
  HF_DATASET_NAME="rmanluo/RoG-${NAME}"       # Parquet 子图目录
  OUTPUT_PATH="./data/instance_${NAME}_500.jsonl"

  if [ ! -f "${INPUT_PATH}" ]; then
    echo "❌ Input file not found: ${INPUT_PATH}"
    exit 1
  fi

  python scripts/instantiation.py \
    --input_path "${INPUT_PATH}" \
    --hf_dataset_name "${HF_DATASET_NAME}" \
    --output_path "${OUTPUT_PATH}"

  echo "✅ Finished instantiating ${NAME}: Output saved to ${OUTPUT_PATH}"
  echo
done

echo "🎉 All datasets instantiation complete!"