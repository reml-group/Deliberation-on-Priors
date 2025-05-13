import os
import argparse
import json
from tqdm import tqdm
from openai import OpenAI

from utils import extract_dict_from_str, read_jsonl
from utils import path_generation_template

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, default="your api key in vllm")
    parser.add_argument("--base_url", type=str, default="http://0.0.0.0:8000/v1")
    parser.add_argument("--model_name_or_path", type=str, default="your/path/to/fine-tuned_model")
    parser.add_argument("--input_files", nargs='+', required=True, help="List of input .jsonl files")
    parser.add_argument("--output_files", nargs='+', required=True, help="List of output .jsonl files")
    args = parser.parse_args()

    assert len(args.input_files) == len(args.output_files), "Number of input and output files must match"

    client = OpenAI(api_key=args.api_key, base_url=args.base_url)

    for input_path, output_path in zip(args.input_files, args.output_files):
        datalist = read_jsonl(input_path)
        with open(output_path, 'w', encoding='utf-8') as file:
            for data in tqdm(datalist, desc=f"Generating paths for {os.path.basename(input_path)}"):
                question = data['question']
                q_entity = data['q_entity']
                a_entity = data['a_entity']
                completion = client.chat.completions.create(
                    model=args.model_name_or_path,
                    messages=[
                        {"role": "user", "content": path_generation_template.format(question=question, start_entities=q_entity)},
                    ],
                    n=3,
                    max_tokens=1024,
                    temperature=1.0,
                    top_p=0.95,
                )
                relation_paths = []
                for choice in completion.choices:
                    relation_path = extract_dict_from_str(choice.message.content)
                    if relation_path:
                        for rel_path in relation_path:
                            if rel_path not in relation_paths:
                                relation_paths.append(rel_path)
                data["sft_rel_paths"] = relation_paths
                file.write(json.dumps(data, ensure_ascii=False) + '\n')
            print(f'✅ Finished writing to {output_path}')