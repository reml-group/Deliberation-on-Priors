import json
import os
import argparse
from tqdm import tqdm
from utils import read_jsonl, path_generation_template, path_generation_response_template

def generate_path_dict(paths: list, sup_dict: dict = None, max_path_len: int = 4):
    result = {} if sup_dict is None else sup_dict.copy()
    for path in paths:
        if len(path) > max_path_len:
            continue
        topic_entity = path[0][0]
        if topic_entity not in result:
            result[topic_entity] = []
        rel_path = [p[1] for p in path]
        if rel_path not in result[topic_entity]:
            result[topic_entity].append(rel_path)
    for k, v in result.items():
        result[k] = {f"relation_path {i+1}": path for i, path in enumerate(v)}
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_path",
        type=str,
        required=True,
        help="Input .jsonl file containing ground_paths_with_entity; this is the output of data_process/load_data.py"
    )
    parser.add_argument(
        "--output_path",
        type=str,
        required=True,
        help="Output .jsonl file containing prompt-response pairs for SFT"
    )
    parser.add_argument(
        "--max_path_len",
        type=int,
        required=True,
        help="Maximum number of relations allowed in each reasoning path. Paths longer than this will be filtered out."
    )
    args = parser.parse_args()

    input_path = args.input_path
    output_path = args.output_path

    # Create output directory if needed
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load data
    data_list = read_jsonl(input_path)

    with open(output_path, 'w', encoding='utf-8') as file:
        for data in tqdm(data_list):
            if data.get("ground_paths_with_entity"):
                sample = {
                    "prompt": path_generation_template.format(
                        question=data["question"],
                        start_entities=data["q_entity"]
                    ),
                    "response": path_generation_response_template.format(
                        relation_paths=generate_path_dict(paths=data["ground_paths_with_entity"], max_path_len=args.max_path_len)
                    )
                }
                file.write(json.dumps(sample, ensure_ascii=False) + "\n")

    print(f"✅ Finished writing to {output_path}")