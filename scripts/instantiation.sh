#!/bin/bash

set -e

# === 参数配置 ===
DATASETS=("cwq" "webqsp")

for NAME in "${DATASETS[@]}"; do
  echo "=============================="
  echo "🧩 Instantiating reasoning paths for ${NAME}"
  echo "=============================="

  INPUT_PATH="./data/PG/${NAME}_500.jsonl"   # output of path generation
  HF_DATASET_NAME="rmanluo/RoG-${NAME}"       
  OUTPUT_PATH="./data/instance/${NAME}_500.jsonl"

  mkdir -p "$(dirname "${OUTPUT_PATH}")"

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