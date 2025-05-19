import os
import argparse
import json
from tqdm import tqdm
from openai import OpenAI

from utils import extract_dict_from_str, read_jsonl
from utils import path_generation_template

def generate_paths(
    input_file: str,
    output_file: str,
    api_key: str,
    base_url: str,
    model_name_or_path: str,
):
    client = OpenAI(api_key=api_key, base_url=base_url)
    datalist = read_jsonl(input_file)

    with open(output_file, 'w', encoding='utf-8') as file:
        for data in tqdm(datalist, desc=f"Generating paths for {os.path.basename(input_file)}"):
            question = data['question']
            q_entity = data['q_entity']
            a_entity = data['a_entity']
            completion = client.chat.completions.create(
                model=model_name_or_path,
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
            data["gen_rel_paths"] = relation_paths
            file.write(json.dumps(data, ensure_ascii=False) + '\n')
    print(f'✅ Finished writing to {output_file}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, default="your api key in vllm")
    parser.add_argument("--base_url", type=str, default="http://0.0.0.0:8000/v1")
    parser.add_argument("--model_name_or_path", type=str, default="your/path/to/fine-tuned_model")
    parser.add_argument("--input_file", type=str, required=True, help="Path to input .jsonl file")
    parser.add_argument("--output_file", type=str, required=True, help="Path to output .jsonl file")
    args = parser.parse_args()

    generate_paths(
        input_file=args.input_file,
        output_file=args.output_file,
        api_key=args.api_key,
        base_url=args.base_url,
        model_name_or_path=args.model_name_or_path,
    )


if __name__ == "__main__":
    main()