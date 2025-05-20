
from tqdm import tqdm
import networkx as nx
import json
import argparse
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
                for i, rel in enumerate(rel_path):
                    reasoning_path.append((p[i], rel, p[i+1]))
                if reasoning_path not in reasoning_tree:
                    reasoning_tree.append(reasoning_path)
    return reasoning_tree, is_instance

def build_graph_with_fullrel(graph: list)->nx.DiGraph:

    G = nx.DiGraph()
    for h,r,t in graph:
        if not G.has_edge(h, t):
            G.add_edge(h,t, relations=[])
        if r not in G[h][t]['relations']:
            G[h][t]['relations'].append(r)
        if not G.has_edge(t, h):
            G.add_edge(t,h, relations=[])
        if r not in G[t][h]['relations']:
            G[t][h]['relations'].append('~'+r)

    return G


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str, required=True, help="Input .jsonl file (with sft_rel_paths)")
    parser.add_argument("--output_path", type=str, required=True, help="Output file to write instance results")
    parser.add_argument("--kb_path", type=str, required=True, help="Path to kb.txt file of MetaQA")

    args = parser.parse_args()

    # Load knowledge base
    triples = []
    with open(args.kb_path, "r", encoding="utf-8") as f:
        for line in f:
            h, r, t = line.strip().split("|")
            triples.append((h, r, t))
    graph = build_graph_with_fullrel(triples)

    # Load data
    data_list = read_jsonl(args.input_path)
    with open(args.output_path, 'w', encoding='utf-8') as file:
        for sample in tqdm(data_list):
            reasoning_tree = []
            is_instance = []
            relation_paths = unique_list_of_lists(sample['gen_rel_paths'])
            relation_paths = [path for path in relation_paths if len(path) <= sample["hop"]]

            if relation_paths:
                for relation_path in relation_paths:
                    tree, flag = instance_kg_tree(sample['q_entity'], graph, [relation_path])
                    reasoning_tree.append(tree)
                    is_instance.append(flag[0])

            sample['gen_rel_paths'] = relation_paths
            sample['reasoning_tree'] = reasoning_tree
            sample['is_instance'] = is_instance

            file.write(json.dumps(sample, ensure_ascii=False) + '\n')

    print(f"✅ Finished writing to {args.output_path}")