from openai import OpenAI
import json
import argparse
import logging
import os
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tqdm import tqdm
from utils import path_selection_prompt, verification_prompt, constraint_extraction_prompt, llm_only_answering_prompt
from utils import *
def chat_llm(client: OpenAI, model, input: str):
    system_prompt = """You are an expert in KG reasoning."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input},
        ],
        stream=False
    )
    return response.choices[0].message.content, response.usage

def process_data(data):
    question = data["question"]
    topic_entities = data["q_entity"]
    # constraints = data["constraints"]
    paths = []
    full_paths = []
    start_entities = []
    for index, flag in enumerate(data["is_instance"]):
        if flag == 1:
            paths.append(data["gen_rel_paths"][index])
            full_paths.append(data["reasoning_tree"][index])
            start_entities.append(data["reasoning_tree"][index][0][0][0])
    a_entity = data["a_entity"]
    return question, topic_entities, paths, full_paths, start_entities, a_entity

def log_function_call(function_name, inputs, usage, output):
    """记录函数调用日志"""
    log_entry = f"\nFunction: {function_name}\nInputs: {inputs}\nInput_tokens: {usage.prompt_tokens}\nOutput_tokens: {usage.completion_tokens}\nTotal_tokens: {usage.total_tokens}\n Output: {output}\n"
    logging.info(log_entry)  # 记录到日志文件
def log_error(error):
    """记录错误日志"""
    logging.error(error)  # 记录到日志文件
def log_llm_calls(llm_calls):
    """记录 LLM 调用信息"""
    log_entry = f"\nLLM Calls: {llm_calls}\n"
    logging.info(log_entry)  # 记录到日志文件

def log_ground_truth(ground_truth):
    """记录 LLM 调用信息"""
    log_entry = f"\nGround truth of the question: {ground_truth}\n"
    logging.info(log_entry)  # 记录到日志文件

def answer_trying(client: OpenAI, model, question, topic_entities, constraints, path, triplets, ground_truth):
    output, usage = chat_llm(client=client, 
                      model=model, 
                      input=verification_prompt.format(question=question, topic_entities=topic_entities, constraints=constraints, path=path, triplets=triplets))
    log_function_call("answer_trying", {"question": question, "topic_entities": topic_entities, "constraints": constraints, "path": path, "triplets": triplets}, usage, output)
    log_ground_truth(ground_truth)
    return output

def select_path(client: OpenAI, model, question, topic_entities, memory, paths):
    selected_path_answer, usage = chat_llm(client=client, 
                                    model=model, 
                                    input=path_selection_prompt.format(question=question, topic_entities=topic_entities, memory=memory, paths=paths))
    log_function_call("select_path", {"question": question, "topic_entities": topic_entities, "memory": memory, "paths": paths}, usage, selected_path_answer)
    return selected_path_answer

def constraint_extract(client: OpenAI, model, question):
    constraints, usage = chat_llm(client=client, 
                            model=model, 
                            input=constraint_extraction_prompt.format(question=question))
    log_function_call("constraint_extract", {"question": question}, usage, constraints)
    # cons = extract_and_parse_lists(constraints)[0]
    return constraints

def llms_only_answering(client: OpenAI, model, question, topic_entities, constraints):
    output, usage = chat_llm(client=client, 
                      model=model, 
                      input=llm_only_answering_prompt.format(question=question, constraints=constraints))
    log_function_call("llms_only_answering", {"question": question, "topic_entities": topic_entities, "constraints": constraints}, usage, output)
    return output

def reasoning_by_multi_agent(client: OpenAI, model, data: list):
    """多智能体迭代推理
    """
    question, topic_entities, paths, full_paths, start_entities, a_entity = data
    memory = []
    selected_path = []
    triplets = []
    answer = []
    flag = False
    extra_checking_answer = ["ok"]
    llm_calls = 0
    constraints = []
    # 提取约束条件
    constraints = constraint_extract(client, model, question)
    llm_calls += 1
    if is_only_empty_lists(full_paths):
        log_error("No reasoning tree")
        response = llms_only_answering(
            client=client, 
            model=model, 
            question=question, 
            topic_entities=topic_entities, 
            constraints=constraints
        )
        llm_calls += 1
        extra_checking_answer = ["No reasoning tree"]
        log_llm_calls(llm_calls)
        return response, extra_checking_answer, llm_calls
    
    while len(paths) > 1:
        str_paths = assemble_paths(start_entities, paths)

        try:
            response = select_path(client, model, question, topic_entities, memory, str_paths)
            selected_path_index = extract_number(response, len(paths))
            llm_calls += 1
        except Exception as e:
            log_error(f"[Path Selection Error] {e}")
            break
        # 没选中path的话直接退出
        if selected_path_index is None or not (0 <= selected_path_index < len(paths)):
            log_error(f"❌ Invalid path index: {selected_path_index}, available: {len(paths)}")
            flag = True
            break
        selected_path.append(str_paths[selected_path_index].split(':')[-1])
        triplets.append(full_paths[selected_path_index])
        
        try:
            ans_response = answer_trying(client, model, question, topic_entities, constraints, selected_path, triplets, a_entity)
            llm_calls += 1
            test_dict = extract_dict_from_string(ans_response)
        except Exception as e:
            log_error(f"[Answer Parsing Error] {e}")
            break

        answer = test_dict.get("answer", [])
        if check_sufficient(test_dict.get("sufficient", "")):
            log_llm_calls(llm_calls)
            return answer, extra_checking_answer, llm_calls
        else:
            memory.append({"selected_path": selected_path[-1], "feedback": test_dict.get("reason", "")})

        paths.pop(selected_path_index)
        full_paths.pop(selected_path_index)
        start_entities.pop(selected_path_index)
        
    if len(paths) == 1 and not flag:
        selected_path.append(assemble_paths(start_entities, paths)[0].split(':')[-1])
        triplets.append(full_paths[0])
        try:
            ans_response = answer_trying(client, model, question, topic_entities, constraints, selected_path, triplets, a_entity)
            llm_calls += 1
            test_dict = extract_dict_from_string(ans_response)
            answer = test_dict.get("answer", [])
        except Exception as e:
            log_error(f"[Final Answer Error] {e}")

    log_llm_calls(llm_calls)
    return answer, extra_checking_answer, llm_calls

def run_reasoning_pipeline(
    model,
    api_key,
    base_url,
    input_path,
    output_dir,
    log_prefix,
    num_repeat=1
):
    client = OpenAI(api_key=api_key, base_url=base_url)

    filename = os.path.splitext(os.path.basename(input_path))[0]
    datalist = read_jsonl(input_path)

    for round_num in range(1, num_repeat + 1):
        # 构造路径
        result_path = os.path.join(output_dir, f"{filename}_{model}_round{round_num}.jsonl")
        log_path = os.path.join(output_dir, f"{log_prefix}_{filename}_{model}_round{round_num}.txt")

        # 配置日志
        logging.basicConfig(filename=log_path, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", force=True)

        logging.info(f"========== Start Round {round_num} on {filename} ==========")
        logging.info(f"Model ID: {model}")
        logging.info(f"Input file: {input_path}")
        logging.info(f"Output file: {result_path}")

        res = []
        res_without_path = []
        for index, data in tqdm(enumerate(datalist), total=len(datalist)):
            logging.info(f"🔥 Processing data index: {index}")

            if data.get("ground_rel_paths") == []:
                log_error("No ground paths")
                continue

            try:
                answer, extra_checking_answer, llm_calls = reasoning_by_multi_agent(
                    client=client,
                    model=model,
                    data=process_data(data)
                )
                if extra_checking_answer == ["No reasoning tree"]:
                    res_without_path.append({"question": data["question"], "a_entity": data["a_entity"], "answer": answer, "flag": extra_checking_answer, "llm_calls": llm_calls, "hit@1": 0, "hit": 0, "precision": 0.0, "recall": 0.0, "f1": 0})
                else:
                    res.append({
                        "question": data["question"],
                        "a_entity": data["a_entity"],
                        "answer": answer,
                        "flag": extra_checking_answer,
                        "llm_calls": llm_calls
                    })
            except Exception as e:
                log_error(f"Error processing index {index}: {e}")
                continue
                
        error = []
        for data in res:
            try:
                data["hit@1"] = caculate_hit1(data["answer"], data["a_entity"])
                data["hit"] = caculate_hit(data["answer"], data["a_entity"])
                data["precision"] = caculate_precision(data["answer"], data["a_entity"])
                data["recall"] = caculate_recall(data["answer"], data["a_entity"])
                data["f1"] = caculate_f1(data["answer"], data["a_entity"])
            except Exception as e:
                error.append(data)
                data.update({"hit@1": 0, "hit": 0, "precision": 0, "recall": 0, "f1": 0})
                log_error(f"Metric calculation error on index {res.index(data)}: {e}")

        for data in res_without_path:
            res.append(data)
        # 写入结果
        with open(result_path, "w", encoding='utf-8') as f:
            for item in res:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        logging.info(f"✅ Round {round_num} completed. Total: {len(res)}, Errors: {len(error)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--model", type=str, required=True, help="Model name to use in vLLM/OpenAI call, e.g., 'gpt-4.1' or 'llama3.1-8B-Instruct'")
    parser.add_argument("--api_key", type=str, required=True, help="API key")
    parser.add_argument("--base_url", type=str, default="http://localhost:8000/v1", help="vLLM or OpenAI-compatible endpoint base URL")

    parser.add_argument("--input_path", type=str, required=True, help="input JSONL file (instantiated reasoning data)")
    parser.add_argument("--output_dir", type=str, default="./output/reasoning_results", help="Directory to save output files")
    parser.add_argument("--log_prefix", type=str, default="log", help="Prefix for log file names")
    parser.add_argument("--num_repeat", type=int, default=1, help="How many times to repeat each reasoning process (for robustness)")

    args = parser.parse_args()

    run_reasoning_pipeline(
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
        input_path=args.input_path,
        output_dir=args.output_dir,
        log_prefix=args.log_prefix,
        num_repeat=args.num_repeat
    )