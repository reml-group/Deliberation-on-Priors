import json

def read_jsonl(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Error in line {line_number}: {e}")
                print(f"Line content: {line.strip()}")
                break  # 可以选择在这里中断程序，或者继续处理其他行
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

def list_in_list(list1, list2):
    for l in list1:
        if l in list2:
            return True
    return False
def is_only_empty_lists(lst):
    for item in lst:
        if not isinstance(item, list) or item:  # 如果不是列表，或者列表不为空
            return False
    return True
def assemble_paths(start_entities, paths):
    result = []
    path_count = 1
    for index, entity in enumerate(start_entities):
        path = paths[index]
        path_str = f"Path {path_count}:{entity}"
        for i, relation in enumerate(path):
            path_str += f" -> {relation} -> Unknown Entity"
        result.append(path_str)
        path_count += 1
    return result
