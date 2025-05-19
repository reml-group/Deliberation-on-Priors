#!/bin/bash

set -e

# ===== 参数配置 =====
API_KEY="your_api_key_here"
MODEL="gpt-4.1"
BASE_URL=""

INPUT_DIR="./data/instance"
OUTPUT_DIR="./output/reasoning_results"
LOG_PREFIX="log"

mkdir -p "${OUTPUT_DIR}"

DATASETS=("cwq" "webqsp")

for NAME in "${DATASETS[@]}"; do
  echo "=============================="
  echo "🧠 Running reasoning on dataset: ${NAME}"
  echo "=============================="

  INPUT_PATH="${INPUT_DIR}/${NAME}_500.jsonl"

  if [ ! -f "${INPUT_PATH}" ]; then
    echo "❌ Input file not found: ${INPUT_PATH}"
    exit 1
  fi

  python scripts/introspection.py \
    --model "${MODEL}" \
    --api_key "${API_KEY}" \
    --base_url "${BASE_URL}" \
    --input_path "${INPUT_PATH}" \
    --output_dir "${OUTPUT_DIR}" \
    --log_prefix "${LOG_PREFIX}" \
    --num_repeat 1

  echo "✅ ${NAME} reasoning complete. Results saved to ${OUTPUT_DIR}"
  echo
done

echo "🎉 All datasets processed!"