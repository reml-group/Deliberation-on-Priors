import argparse
from datasets import load_dataset
import json
import networkx as nx
from tqdm import tqdm
from utils import build_graph, bulid_graph_with_fullrel
def expand_paths(compressed_paths):
    # 展开路径的辅助函数
    def backtrack(current_path, index, path):
        # 如果当前路径已经包含了所有节点对，则将其添加到结果中
        if len(current_path) == len(path):
            result.append(current_path[:])
            return
        for i in range(index, len(path)):
            node, rel_list, next_node = path[i]
            # 遍历当前节点的所有关系
            for rel in rel_list:
                # 将当前关系添加到路径中，并递归处理剩余的路径
                current_path.append((node, rel, next_node))
                backtrack(current_path, i+1, path)
                current_path.pop()

    result = []
    current_path = []
    for path in compressed_paths:
        backtrack(current_path, 0, path)
    return result
def get_shortest_paths(q_entity: list, a_entity: list, G: nx.DiGraph) -> list:
    """
    Get all shortest paths between a topic entity and an answer entity.
    """
    paths = []
    for q in q_entity:
        if q not in G:
            continue
        for a in a_entity:
            if a not in G:
                continue
            try:
                for path in nx.all_shortest_paths(G, q, a):
                    paths.append(path)
            except:
                pass
    result = []
    for path in paths:
        p = []
        for i in range(len(path)-1):
            p.append((path[i], G[path[i]][path[i+1]]['relations'], path[i+1]))
        if p:
            result.append(p)
    return expand_paths(result)

def get_ground_path(sample):
    graph = build_graph(sample["graph"])
    paths = get_shortest_paths(sample["q_entity"], sample["a_entity"], graph)
    ground_paths = set()
    for path in paths:
        ground_paths.add(tuple([p[1] for p in path]))
    sample["ground_paths"] = list(ground_paths)
    return sample

def get_ground_path_with_entity(sample):
    # graph = build_graph(sample["graph"])
    graph = bulid_graph_with_fullrel(sample["graph"])
    paths = get_shortest_paths(sample["q_entity"], sample["a_entity"], graph)
    sample["ground_paths_with_entity"] = paths
    return sample

def get_ground_path_with_entity_split(graph, q_entity, a_entity):
    # graph = build_graph(sample["graph"])
    graph = bulid_graph_with_fullrel(graph)
    paths = get_shortest_paths(q_entity, a_entity, graph)
    return paths

def get_ground_path_with_entity_per_q_entity(sample):
    # graph = build_graph(sample["graph"])
    per_qentity_paths = []
    graph = bulid_graph_with_fullrel(sample["graph"])
    for q_entity in sample["q_entity"]:
        paths = get_shortest_paths([q_entity], sample["a_entity"], graph)
        per_qentity_paths.append(paths)
    sample["ground_paths_with_entity"] = per_qentity_paths
    return sample

def data2jsonl(dataset, output_file_path):
    print("Converting dataset to json format...")
    for sample in tqdm(dataset):
        data = {
            "question": sample["question"],
            "q_entity": sample["q_entity"],
            "a_entity": sample["a_entity"],
            "ground_paths_with_entity": sample["ground_paths_with_entity"]
        }
        output_file_path.write(json.dumps(data) + "\n")
        output_file_path.flush()
    output_file_path.close()
    print("Done!")
    
# 给每条数据添加ground_paths
def load_data_with_path(args):
    dataset = load_dataset('parquet', data_dir=args.dataset_file_path, split=args.split)
    dataset = dataset.map(get_ground_path_with_entity)
    data2jsonl(dataset, open(args.output_file_path, "w"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_file_path", type=str, default=" /path/to/your/datasets/RoG-cwq")
    parser.add_argument("--output_file_path", type=str, default=" /path/to/your/datasets/train_data_ori.jsonl")
    parser.add_argument("--split", type=str, default="train")
    args = parser.parse_args()
    load_data_with_path(args)
    

    
