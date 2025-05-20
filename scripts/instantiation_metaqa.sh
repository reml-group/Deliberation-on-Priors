#!/bin/bash

set -e

echo "=============================="
echo "🧩 Instantiating reasoning paths for MetaQA"
echo "=============================="

INPUT_PATH="./data/PG/metaqa_600.jsonl"       # 输入：path generation 的输出结果
KB_PATH="./data/metaqa/kb.txt"               # MetaQA 的知识库文件
OUTPUT_PATH="./data/instance/metaqa_600.jsonl"

# 创建输出目录
mkdir -p "$(dirname "${OUTPUT_PATH}")"

# 检查输入文件是否存在
if [ ! -f "${INPUT_PATH}" ]; then
  echo "❌ Input file not found: ${INPUT_PATH}"
  exit 1
fi

# 调用实例化脚本
python reasoning/instantiation_metaqa.py \
  --input_path "${INPUT_PATH}" \
  --output_path "${OUTPUT_PATH}" \
  --kb_path "${KB_PATH}"

echo "✅ Finished instantiating MetaQA: Output saved to ${OUTPUT_PATH}"
echo "🎉 Instantiation complete!"