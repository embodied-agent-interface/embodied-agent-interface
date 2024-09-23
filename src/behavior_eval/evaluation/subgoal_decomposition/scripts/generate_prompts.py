import os
import json
import behavior_eval
import fire
from multiprocessing import Process, Manager, Queue
import behavior_eval
from behavior_eval.evaluation.action_sequencing.action_sequence_evaluator import ActionSequenceEvaluator
from behavior_eval.evaluation.subgoal_decomposition.subgoal_prompts_utils import get_subgoal_prompt


def get_llm_output(demo_name, result_list, lock, output_path):
    with lock:
        if os.path.exists(output_path):
            with open(output_path, 'r') as f:
                logs = json.load(f)
            for log_list in logs:
                if log_list['identifier'] == demo_name:
                    print(f'Demo {demo_name} has been processed before.')
                    return
    env = ActionSequenceEvaluator(demo_name=demo_name)
    try:
        prompt = get_subgoal_prompt(env)
    except:
        raise Exception(f"Failed to generate prompt for {demo_name}")
    env.transition_model.env.close()
    rst = {
        "identifier": demo_name,
        "llm_prompt": prompt,
    }
    with lock:
        result_list.append(rst)
        with open(output_path, 'w') as f:
            json.dump(list(result_list), f, indent=4)
    

def worker_task(queue, result_list, lock, output_path):
    while True:
        task = queue.get()
        if task is None:
            break
        demo_name = task
        get_llm_output(demo_name, result_list, lock, output_path)

def generate_prompts(worker_num: int = 1, result_dir: str = './results'):
    with open(behavior_eval.demo_name_path) as f:
        demo_list = json.load(f)
    
    manager = Manager()
    result_list = manager.list()
    lock = manager.Lock()

    output_path = os.path.join(result_dir, 'subgoal_decomposition_prompts.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if worker_num > 1:
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
    else:
        for demo_name in demo_list:
            get_llm_output(demo_name, result_list, lock, output_path)
    
    result_list = list(result_list)
    with open(output_path, 'w') as f:
        json.dump(list(result_list), f, indent=4)
    print(f"Results saved to {output_path}")
    return result_list

if __name__ == "__main__":
    fire.Fire(generate_prompts)