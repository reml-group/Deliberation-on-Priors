#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# List of datasets to process
DATASETS=("cwq" "webqsp")
API_KEY="api key setting in vLLM"
MODEL_NAME_OR_PATH="model_name_or_path setting in vLLM"
BASE_URL="base url setting in vLLM"

for NAME in "${DATASETS[@]}"; do
  echo "=============================="
  echo "🔄 Processing dataset: $NAME"
  echo "=============================="

  INPUT_FILE="./data/test/${NAME}_500.jsonl"
  PG_OUTPUT="./data/PG_${NAME}_500.jsonl"

  # run path_generation.py
  echo "🔍 Step 1: Path Generation with fine-tuned model..."
  python scripts/path_generation.py \
    --input_files ${INPUT_FILE} \
    --output_files ${PG_OUTPUT} \
    --api_key ${API_KEY} \
    --model_name_or_path ${MODEL_NAME_OR_PATH} \
    --base_url ${BASE_URL}

  echo "✅ ${NAME} done! Path Generation: ${PG_OUTPUT}"
  echo
done

echo "🎉 All datasets processed!"