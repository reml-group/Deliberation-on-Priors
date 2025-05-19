#!/bin/bash

set -e  # Exit on error

# Settings for vLLM
API_KEY="your_api_key_here"
MODEL_NAME_OR_PATH="/path/to/your/fine-tuned-model"
BASE_URL="http://localhost:8000/v1"

# List of datasets
DATASETS=("cwq" "webqsp")

for NAME in "${DATASETS[@]}"; do
  echo "=============================="
  echo "🔄 Processing dataset: $NAME"
  echo "=============================="

  INPUT_FILE="./data/test/${NAME}_500.jsonl"
  PG_OUTPUT="./data/PG_${NAME}_500.jsonl"

  # Ensure input exists
  if [ ! -f "${INPUT_FILE}" ]; then
    echo "❌ Input file not found: ${INPUT_FILE}"
    exit 1
  fi

  # Step 1: Path Generation
  echo "🔍 Generating paths..."
  python scripts/path_generation.py \
    --input_files ${INPUT_FILE} \
    --output_files ${PG_OUTPUT} \
    --api_key ${API_KEY} \
    --model_name_or_path ${MODEL_NAME_OR_PATH} \
    --base_url ${BASE_URL}

  echo "✅ Finished ${NAME}: Output saved to ${PG_OUTPUT}"
  echo
done

echo "🎉 All datasets processed!"