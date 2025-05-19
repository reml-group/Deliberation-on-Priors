import json
import os
import argparse
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tqdm import tqdm
from utils import read_jsonl, path_generation_template, path_generation_response_template
import random
import copy

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

def entity_path_swapping(path_dict):
    copy_dict = copy.deepcopy(path_dict)
    keys = list(copy_dict.keys())
    key1, key2 = random.sample(keys, 2)
    copy_dict[key1], copy_dict[key2] = copy_dict[key2], copy_dict[key1]
    return copy_dict

def relation_deletion(path_dict):
    keys = list(path_dict.keys())
    selected_key = random.choice(keys)
    new_dict = {selected_key: path_dict[selected_key]}
    return new_dict

def path_truncation(paths, max_path_len: int = 4):
    flag = False
    result = {}
    for k, v in result.items():
        for index, path in enumerate(result[k]):
            if len(path) >= max_path_len:
                result[k][index] = path[:-1]
                flag = True
    for path in paths:
        if len(path) > 2:
            continue
        topic_entity = path[0][0]
        if topic_entity not in result:
            result[topic_entity] = []
        r_p = []
        for p in path:
            r_p.append(p[1])
        if len(r_p) > 1:
            r_p = r_p[:-1]
            flag = True
        if r_p not in result[topic_entity]:
            result[topic_entity].append(r_p)
    for k, v in result.items():
        result[k] = {f"relation_path {i+1}": path for i, path in enumerate(result[k])}
    return flag, result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_path",
        type=str,
        required=True,
        help="Input .jsonl file with ground_paths_with_entity (from load_data.py)"
    )
    parser.add_argument(
        "--output_path",
        type=str,
        required=True,
        help="Output .jsonl file containing KTO training samples"
    )
    parser.add_argument(
        "--max_path_len",
        type=int,
        default=4,
        help="Maximum number of relations allowed in a reasoning path"
    )
    args = parser.parse_args()

    data_list = read_jsonl(args.input_path)
    pos_data, neg_data = [], []

    for data in tqdm(data_list):
        if not data.get("ground_paths_with_entity"):
            continue

        path_dict = generate_path_dict(data["ground_paths_with_entity"], max_path_len=args.max_path_len)
        if not path_dict:
            continue

        # Positive sample
        pos_sample = {
            "prompt": path_generation_template.format(
                question=data["question"], start_entities=data["q_entity"]
            ),
            "response": path_generation_response_template.format(
                relation_paths=path_dict
            ),
            "kto_tag": True,
        }
        pos_data.append(pos_sample)

        # Negative sample: randomly keep one
        if len(path_dict) >= 2:
            neg_sample_1 = {
                "prompt": pos_sample["prompt"],
                "response": path_generation_response_template.format(
                    relation_paths=relation_deletion(path_dict)
                ),
                "kto_tag": False,
            }
            neg_data.append(neg_sample_1)

            # Negative sample: exchange keys
            neg_sample_2 = {
                "prompt": pos_sample["prompt"],
                "response": path_generation_response_template.format(
                    relation_paths=entity_path_swapping(dict(path_dict))
                ),
                "kto_tag": False,
            }
            neg_data.append(neg_sample_2)

        # Negative sample: delete last hop
        flag, shortened_dict = path_truncation(data["ground_paths_with_entity"], max_path_len=args.max_path_len)
        if flag and shortened_dict:
            neg_sample_3 = {
                "prompt": pos_sample["prompt"],
                "response": path_generation_response_template.format(
                    relation_paths=shortened_dict
                ),
                "kto_tag": False,
            }
            neg_data.append(neg_sample_3)

    # Save all samples
    output_dir = os.path.dirname(args.output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(args.output_path, 'w', encoding='utf-8') as f:
        for d in pos_data + neg_data:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    print(f"✅ Saved {len(pos_data)} positive and {len(neg_data)} negative samples to {args.output_path}")

if __name__ == "__main__":
    main()

