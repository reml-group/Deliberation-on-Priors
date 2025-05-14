
from tqdm import tqdm
from datasets import load_dataset
import networkx as nx
import json
import argparse
from utils import *
def read_jsonl(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data.append(json.loads(line))
    return data

def unique_list_of_lists(lst):
    seen = set()
    return [x for x in lst if not (tuple(x) in seen or seen.add(tuple(x)))]

def find_possible_endpoints(graph, start_node, relation) -> tuple[list[str], list[list[str]]]:
    """ 根据起始节点和关系路径，找到可能的终点

    Args:
        graph (_type_): 每一条数据的sub_graph
        start_node (_type_): [q_entity]
        relation (_type_): 模型生成的关系路径

    Returns:
        tuple[list[str], list[list[str]]]: 第一个为可能的终点，第二个为对应的路径
    """
    endpoints = []
    path = []
    def dfs(graph, curr_node, relation_index, curr_path):
        if relation_index == len(relation):
            endpoints.append(curr_node)
            path.append(curr_path)
            return
        current_relation = relation[relation_index]
        for neighbor, attr in graph[curr_node].items():
            if neighbor not in curr_path:
                if 'relations' in attr and current_relation in attr['relations']:
                    dfs(graph, neighbor, relation_index+1, curr_path + [neighbor])
    for node in start_node:
        if node in graph:         
            dfs(graph, node, 0, [node])
    return endpoints, path

def instance_kg_tree(start: list, graph: nx.DiGraph, rel_paths: list):
    """ 实例化推理树 """
    reasoning_tree = []
    is_instance = [0] * len(rel_paths)
    for index, rel_path in enumerate(rel_paths):
        _, path = find_possible_endpoints(graph, start, rel_path)
        if path:
            is_instance[index] = 1
            for p in path:
                reasoning_path = []
                for index, rel in enumerate(rel_path):
                    reasoning_path.append((p[index], rel, p[index+1]))
                if reasoning_path not in reasoning_tree:
                    reasoning_tree.append(reasoning_path)
    return reasoning_tree, is_instance
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str, default="./data/test_webqsp.jsonl", help="Path to input .jsonl file containing questions and generated paths")
    parser.add_argument("--graph_dataset_dir", type=str, default="./datasets/RoG-webqsp/data", help="Directory to the processed Freebase subgraph dataset (in Parquet format)")
    parser.add_argument("--output_path", type=str, default="./data/output_instance.jsonl", help="Path to output .jsonl file to save reasoning trees")
    args = parser.parse_args()

    data_list = read_jsonl(args.input_path)
    dataset = load_dataset('parquet', data_dir=args.graph_dataset_dir, split="test")
    output_file_path = args.output_path

    dataset_idx = 0

    with open(output_file_path, 'w', encoding='utf-8') as file:
        for sample in tqdm(data_list):
            question = sample['question']
            matched_data = None

            while dataset_idx < len(dataset):
                candidate = dataset[dataset_idx]
                dataset_idx += 1
                if candidate['question'] == question:
                    matched_data = candidate
                    break

            if matched_data is None:
                print(f"⚠️ Warning: question not found in dataset: {question}")
                continue

            relation_paths = unique_list_of_lists(sample['gen_rel_paths'])
            graph = bulid_graph_with_fullrel(matched_data['graph'])

            reasoning_tree = []
            is_instance = []

            if relation_paths:
                for relation_path in relation_paths:
                    reasoning_tree_single, is_instance_single = instance_kg_tree(sample['q_entity'], graph, [relation_path])
                    reasoning_tree.append(reasoning_tree_single)
                    is_instance.append(is_instance_single[0])

            sample['gen_rel_paths'] = relation_paths
            sample['reasoning_tree'] = reasoning_tree
            sample['is_instance'] = is_instance

            file.write(json.dumps(sample, ensure_ascii=False) + '\n')

    print(f'✅ Finished writing to {output_file_path}')