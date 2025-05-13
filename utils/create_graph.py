import networkx as nx

def build_graph(graph: list) -> nx.DiGraph:
    """
    Create a networkx graph from a list of triples.
    """
    G = nx.DiGraph()
    for h, r, t in graph:
        r = r.strip().split('.')[-1]
        if not G.has_edge(h, t):
            G.add_edge(h, t, relations=[])
        if r not in G[h][t]['relations']:
            G[h][t]['relations'].append(r)
    return G

def bulid_graph_with_fullrel(graph: list) ->nx.DiGraph:
    """
    Create a fullrel networkx graph from a list of triples.
    """
    G = nx.DiGraph()
    for h, r, t in graph:
        if not G.has_edge(h, t):
            G.add_edge(h, t, relations=[])
        if r not in G[h][t]['relations']:
            G[h][t]['relations'].append(r)
    return G

def get_shortest_paths(q_entity: list, a_entity: list, G: nx.DiGraph) -> list:
    """
    Get all shortest paths between a query entity and an answer entity.
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
            p.append((path[i], G[path[i]][path[i+1]]['relation'], path[i+1]))
        if p:
            print(p)
            result.append(p)
    return result

def find_target_nodes(G: nx.DiGraph, source_node: str, relation: str) -> list:
    out_edges = G.out_edges(source_node, data=True)
    target_nodes = [target for _, target, data in out_edges if data['relation'] == relation]
    return target_nodes
