str_s = "The helpful relation paths are: {'relation_pat': []"
import ast
import re

def extract_dict_from_str(input_string):
    # 处理被截断的情况：确保字符串末尾正确
    if not input_string.endswith("}"):
        if input_string.endswith("'"):
            input_string += "]}"
        elif input_string[-1].isalnum():
            input_string += "']}"
        elif input_string.endswith("]"):
            input_string += "}"

    # 确保大括号匹配
    if input_string.count('{') > input_string.count('}'):
        input_string += '}'

    # 正则表达式提取所有类似 [xxx, yyy] 的部分
    list_pattern = r"\[(.*?)]"  # 匹配所有方括号中的内容
    matches = re.findall(list_pattern, input_string)

    lists_in_values = []
    
    # 解析出所有字典中的值为列表的部分
    for match in matches:
        try:
            # 尝试将每个匹配的部分转化为列表
            parsed_list = ast.literal_eval(f"[{match}]")  # 再加上外部的[]确保是列表
            if isinstance(parsed_list, list):
                if parsed_list:
                    lists_in_values.append(parsed_list)
        except (SyntaxError, ValueError) as e:
            print(f"Error parsing list: {e}")
            # print(input_string)
    
    if lists_in_values:
        return lists_in_values
    else:
        print("未能解析出有效的列表")
        return None
    
    
def merge_list_of_dicts(dict_list):
    """
    将多个 {'entity': paths} 形式的字典合并为一个，支持多个实体，自动合并路径并去重
    """
    merged = {}

    for d in dict_list:
        for entity, paths in d.items():
            if entity not in merged:
                merged[entity] = set()
            for path in paths:
                merged[entity].add(tuple(path))  # 用 tuple 去重

    # 转回 list
    for entity in merged:
        merged[entity] = [list(p) for p in merged[entity]]

    return merged

def extract_partial_entity_paths(input_string):
    """
    尽可能从截断的 LLM 输出中提取出可恢复的路径信息。
    返回格式： [{'entity': ..., 'paths': [[...], [...]]}, ...]
    """

    dict_start = input_string.find("{")
    dict_str = input_string[dict_start:].strip()

    # 强行补全右括号：使大括号配对数量一致
    open_braces = dict_str.count("{")
    close_braces = dict_str.count("}")
    dict_str += "}" * (open_braces - close_braces)

    # 尝试部分解析，逐个 entity 提取
    result = []

    # 匹配每个实体块：例如 'Super Bowl': {...}
    entity_blocks = re.findall(r"'(.*?)'\s*:\s*{(.*?)}(?=,\s*'|\s*}$)", dict_str, re.DOTALL)

    for entity, paths_block in entity_blocks:
        entity_paths = []

        # 匹配每个路径行：例如 'relation_path 1': ['...']
        path_matches = re.findall(r"\[([^\[\]]+?)\]", paths_block)
        for path_str in path_matches:
            try:
                # 解析为路径（每个元素是字符串）
                rels = [s.strip().strip("'\"") for s in path_str.split(",") if s.strip()]
                if rels:
                    entity_paths.append(rels)
            except Exception as e:
                print(f"⚠️ 跳过非法路径: {path_str}")

        result.append({entity: entity_paths})
    
    merged_result = merge_list_of_dicts(result)

    return merged_result
