import json

def read_jsonl(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data.append(json.loads(line))
    return data

def get_relpaths_from_tuple(data):
    """
    输入是ground_paths_with_entity，输出是relation paths的list
    """
    list_of_paths = []
    for paths in data:
        relation_paths = []
        for path in paths:
            relation_paths.append(path[1])
        if relation_paths not in list_of_paths:
            list_of_paths.append(relation_paths)
    return list_of_paths