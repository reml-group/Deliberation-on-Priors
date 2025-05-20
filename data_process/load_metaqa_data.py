import networkx as nx
import os
import json
import argparse

def get_shortest_paths(q_entity: list,a_entity: list,G: nx.DiGraph) -> list:

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
            p.append((path[i], G[path[i]][path[i+1]]['relations'][0], path[i+1]))
        if p:
            result.append(p)
    return result

def bulid_graph_with_fullrel(graph: list) -> nx.DiGraph:
    G = nx.DiGraph()
    for h, r, t in graph:
        if not G.has_edge(h, t):
            G.add_edge(h, t, relations=[])
        if r not in G[h][t]['relations']:
            G[h][t]['relations'].append(r)
        if not G.has_edge(t, h):
            G.add_edge(t, h, relations=[])
        if r not in G[t][h]['relations']:
            G[t][h]['relations'].append('~' + r)
    return G

def get_ground_path_with_entity(q_entity,a_entity,graph):
    paths = get_shortest_paths(list([q_entity]), list([a_entity]), graph)
    return paths

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kb_path", type=str, required=True, help="Path to kb.txt file")
    parser.add_argument("--dataset_dir", type=str, required=True, help="Directory containing 1-hop, 2-hop, 3-hop folders")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory to save processed .jsonl files")
    args = parser.parse_args()
    
    # Build graph
    triple_list = []
    with open(args.kb_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) == 3:
                triple_list.append((parts[0], parts[1], parts[2]))

    graph = bulid_graph_with_fullrel(triple_list)

    hop_dirs = ['1-hop', '2-hop', '3-hop']

    for hop in hop_dirs:
        hop_path = os.path.join(args.dir_path, hop)
        if not os.path.isdir(hop_path):
            continue
        
        for filename in os.listdir(hop_path):
            if not filename.endswith('.txt'):
                continue

            input_path = os.path.join(hop_path, filename)
            output_subdir = os.path.join(args.output_dir, hop)
            os.makedirs(output_subdir, exist_ok=True)
            output_path = os.path.join(output_subdir, filename.replace('.txt', '.jsonl'))
                 
            with open(input_path, "r", encoding="utf-8") as f_in, open(output_path, "w", encoding="utf-8") as f_out:
                for line in f_in:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split("\t")
                    if len(parts) != 2:
                        continue
                    question = parts[0]
                    answer_entities = parts[1].split("|")
                    q_entity = question.split('[')[1].split(']')[0]

                    ground_paths_with_entity = []
                    for a_entity in answer_entities:
                        paths = get_ground_path_with_entity(q_entity, a_entity, graph)
                        ground_paths_with_entity.append(paths)

                    sample = {
                        "question": question,
                        "q_entity": q_entity,
                        "a_entity": answer_entities,
                        "ground_paths_with_entity": ground_paths_with_entity
                    }
                    f_out.write(json.dumps(sample, ensure_ascii=False) + "\n")

    print("✅ Finished processing MetaQA.")

if __name__ == "__main__":
    main()