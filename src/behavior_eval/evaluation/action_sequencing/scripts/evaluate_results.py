import fire
from multiprocessing import Process, Manager, Queue
import os
import json
from behavior_eval.evaluation.action_sequencing.action_sequence_evaluator import ActionSequenceEvaluator
from collections import defaultdict
import behavior_eval
from typing import Optional

def evaluate_llm_response(demo_name, result_list, lock, output_path, actions_raw):
    ase = ActionSequenceEvaluator(demo_name=demo_name)
    rst = {
        "identifier": demo_name,
        "llm_rst": ase.evaluate_all(actions_raw),
    }
    with lock:
        result_list.append(rst)
        # Append to the file in real-time
        with open(output_path, 'w') as f:
            json.dump(list(result_list), f, indent=4)
    ase.transition_model.env.close()

def worker_task(queue, result_list, lock, output_path):
    while True:
        task = queue.get()
        if task is None:  # Sentinel value to exit
            break
        demo_name, actions_raw = task
        evaluate_llm_response(demo_name, result_list, lock, output_path, actions_raw)

def evaluate_one_llm(llm_response_path, worker_num: Optional[int] = 1, result_dir: Optional[str] = './results'):
    manager = Manager()
    result_list = manager.list()
    lock = manager.Lock()

    llm_response_name = os.path.splitext(os.path.basename(llm_response_path))[0]
    output_path = os.path.join(result_dir, f'log/{llm_response_name}.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    llm_response = json.load(open(llm_response_path))

    # If output_path exists, load first, skip the processed ones
    if os.path.exists(output_path):
        existing_results = json.load(open(output_path))
        processed_identifiers = set([r["identifier"] for r in existing_results])
        llm_response = [r for r in llm_response if r["identifier"] not in processed_identifiers]
        result_list.extend(existing_results)
    
    worker_num = min(worker_num, len(llm_response))
    task_queue = Queue()
    workers = []

    for i in range(worker_num):
        worker = Process(target=worker_task, args=(task_queue, result_list, lock, output_path))
        worker.start()
        workers.append(worker)

    for response in llm_response:
        task_queue.put((response['identifier'], response['llm_output']))

    for i in range(worker_num):
        task_queue.put(None)

    for worker in workers:
        worker.join()

    result_list = list(result_list)  
    with open(output_path, 'w') as f:
        json.dump(result_list, f, indent=4)
    print(f"Results saved to {output_path}")

    summary = {
        "error_type": {},
        "goal_rst": {},
    }
    
    for item in result_list:
        identifier = item['identifier']
        rst = item['llm_rst']
        for k, v in rst.items():
            if k in summary:
                if isinstance(v, dict):
                    for kk, vv in v.items():
                        if vv is not None:
                            if isinstance(vv, int) or isinstance(vv, float):
                                summary[k][kk] = summary[k].get(kk, 0) + vv
                            elif isinstance(vv, bool):
                                summary[k][kk] = summary[k].get(kk, 0) + int(vv)
                            else:
                                summary[k][kk] = summary[k].get(kk, 0) + 1

# {
#     "error_type": {
#         "execution_success": 22,
#         "ErrorType.MISSING_STEP": 34,
#         "parsing": 4,
#         "arguments": 23,
#         "ErrorType.WRONG_TEMPORAL_ORDER": 1,
#         "ErrorType.ADDITIONAL_STEP": 2,
#         "ErrorType.AFFORDANCE_ERROR": 8,
#         "hullucination": 7
#     },
#     "goal_rst": {
#         "all_goal_satisfied_ig": 17,
#         "all_goal_satisfied_graph": 16,
#         "tot_predicates": 366.0,
#         "tot_edge_predicates": 266.0,
#         "tot_node_predicates": 100.0,
#         "satisfied_predicates": 81.0,
#         "satisfied_edge_predicates": 60.0,
#         "satisfied_node_predicates": 21.0
#     }
# }
    organized_summary = {
    "error_type": {
        "execution_success": summary["error_type"].get("execution_success", 0),
        "ErrorType.MISSING_STEP": summary["error_type"].get("ErrorType.MISSING_STEP", 0),
        "ErrorType.WRONG_TEMPORAL_ORDER": summary["error_type"].get("ErrorType.WRONG_TEMPORAL_ORDER", 0),
        "hullucination": summary["error_type"].get("hullucination", 0),
        "parsing": summary["error_type"].get("parsing", 0),
        "arguments": summary["error_type"].get("arguments", 0),
        "ErrorType.ADDITIONAL_STEP": summary["error_type"].get("ErrorType.ADDITIONAL_STEP", 0),
        "ErrorType.AFFORDANCE_ERROR": summary["error_type"].get("ErrorType.AFFORDANCE_ERROR", 0)
    },
    "goal_rst": {
        "all_goal_satisfied_ig": summary["goal_rst"].get("all_goal_satisfied_ig", 0),
        "all_goal_satisfied_graph": summary["goal_rst"].get("all_goal_satisfied_graph", 0),
        "tot_predicates": summary["goal_rst"].get("tot_predicates", 0),
        "tot_edge_predicates": summary["goal_rst"].get("tot_edge_predicates", 0),
        "tot_node_predicates": summary["goal_rst"].get("tot_node_predicates", 0),
        "satisfied_predicates": summary["goal_rst"].get("satisfied_predicates", 0),
        "satisfied_edge_predicates": summary["goal_rst"].get("satisfied_edge_predicates", 0),
        "satisfied_node_predicates": summary["goal_rst"].get("satisfied_node_predicates", 0)
    }
}
    total_task=len(result_list)
    
    # round to 4 decimal places
    new_summary={
        "goal_evaluation": {
            "task_success_rate": round(organized_summary["goal_rst"]["all_goal_satisfied_graph"]/total_task,4) if total_task!=0 else 0,
            "state_goal": round(organized_summary["goal_rst"]["satisfied_node_predicates"]/organized_summary["goal_rst"]["tot_node_predicates"],4) if organized_summary["goal_rst"]["tot_node_predicates"]!=0 else 0,
            "relation_goal": round(organized_summary["goal_rst"]["satisfied_edge_predicates"]/organized_summary["goal_rst"]["tot_edge_predicates"],4) if organized_summary["goal_rst"]["tot_edge_predicates"]!=0 else 0,
            "action_goal": 0,
            "total_goal": round(organized_summary["goal_rst"]["satisfied_predicates"]/organized_summary["goal_rst"]["tot_predicates"],4) if organized_summary["goal_rst"]["tot_predicates"]!=0 else 0,
        },
        "trajectory_evaluation": {
        "execution_success_rate": round(organized_summary["error_type"]["execution_success"]/total_task,4),
        "grammar_error": {
            "parsing": round(organized_summary["error_type"]["parsing"]/total_task,4) if total_task!=0 else 0,
            "hallucination": round(organized_summary["error_type"]["hullucination"]/total_task,4) if total_task!=0 else 0,
            "predicate_argument_number": round(organized_summary["error_type"]["arguments"]/total_task,4) if total_task!=0 else 0,
        },
        "runtime_error": {
            "wrong_order": round(organized_summary["error_type"]["ErrorType.WRONG_TEMPORAL_ORDER"]/total_task,4) if total_task!=0 else 0,
            "missing_step": round(organized_summary["error_type"]["ErrorType.MISSING_STEP"]/total_task,4) if total_task!=0 else 0,
            "affordance": round(organized_summary["error_type"]["ErrorType.AFFORDANCE_ERROR"]/total_task,4) if total_task!=0 else 0,
            "additional_step": round(organized_summary["error_type"]["ErrorType.ADDITIONAL_STEP"]/total_task,4) if total_task!=0 else 0
        }
        },
    }
    
    output_path = output_path.replace('log/', 'summary/')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(new_summary, f, indent=4)
    return new_summary

def evaluate_results(llm_response_dir, worker_num: Optional[int] = 1,result_dir: Optional[str] = './results'):
    os.makedirs(result_dir, exist_ok=True)
    for filename in os.listdir(llm_response_dir):
        file_path = os.path.join(llm_response_dir, filename)
        if os.path.isfile(file_path):
            print(f"Processing file: {file_path}")
            evaluate_one_llm(file_path, worker_num, result_dir)

if __name__ == '__main__':
    fire.Fire(evaluate_results)
