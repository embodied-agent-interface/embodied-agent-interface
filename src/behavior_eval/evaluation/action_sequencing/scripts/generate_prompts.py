import os
import json
from typing import Optional
from multiprocessing import Process, Manager, Queue
import behavior_eval
from behavior_eval.evaluation.action_sequencing.action_sequence_evaluator import ActionSequenceEvaluator
import fire

def get_llm_prompt(demo_name, result_list, lock, output_path):
    env = ActionSequenceEvaluator(demo_name=demo_name)
    prompt = env.get_prompt()
    rst = {
        "identifier": demo_name,
        "llm_prompt": prompt,
    }
    with lock:
        result_list.append(rst)
        with open(output_path, 'w') as f:
            json.dump(list(result_list), f, indent=4)
    env.transition_model.env.close()

def worker_task(queue, result_list, lock, output_path):
    while True:
        task = queue.get()
        if task is None:  # Sentinel value to exit
            break
        demo_name = task
        get_llm_prompt(demo_name, result_list, lock, output_path)

def generate_prompts(worker_num: Optional[int] = 1, result_dir: Optional[str] = './results'):
    with open(behavior_eval.demo_name_path) as f:
        demo_list = json.load(f)

    manager = Manager()
    result_list = manager.list()
    lock = manager.Lock()

    output_path = os.path.join(result_dir, 'action_sequence_prompts.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    processed_identifiers = set()
    # If output_path exists, load first, skip the processed ones
    if os.path.exists(output_path):
        existing_results = json.load(open(output_path))
        processed_identifiers = set([r["identifier"] for r in existing_results])
        new_demo_list = [r for r in demo_list if r not in processed_identifiers]
        demo_list = new_demo_list
        result_list.extend(existing_results)
    
    for demo_name in list(processed_identifiers):
        print(f"Skipping {demo_name}")
        
    worker_num = min(worker_num, len(demo_list))
    task_queue = Queue()
    workers = []

    for i in range(worker_num):
        worker = Process(target=worker_task, args=(task_queue, result_list, lock, output_path))
        worker.start()
        workers.append(worker)

    for demo_name in demo_list:
        task_queue.put(demo_name)

    for i in range(worker_num):
        task_queue.put(None)

    for worker in workers:
        worker.join()

    result_list = list(result_list)  
    with open(output_path, 'w') as f:
        json.dump(result_list, f, indent=4)
    print(f"Results saved to {output_path}")
    return result_list

# Example usage
if __name__ == "__main__":
    fire.Fire(generate_prompts)
