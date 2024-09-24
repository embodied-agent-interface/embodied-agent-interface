import os
import ast
import json
import fire
import behavior_eval
from typing import Optional
from multiprocessing import Process, Manager, Queue
from behavior_eval.evaluation.subgoal_decomposition.subgoal_sim_utils import evaluate_task, get_all_raw_task_goal, get_all_task_list, EvalStatistics
from behavior_eval.evaluation.subgoal_decomposition.subgoal_eval_utils import traj_eval_stats, goal_eval_stats, extract_model_names

def simulate_llm_response(demo_name, lock, llm_plan_path, eval_stat_path):
    report = evaluate_task(demo_name, llm_plan_path)
    goal_info = report[-1]
    with lock:
        eval_statistics = EvalStatistics(get_all_task_list(), eval_stat_path)
        if report[0] != 'Correct':
            eval_statistics.update_eval_rst_dict(demo_name, False, str(report[:-1]), goal_info)
        else:
            eval_statistics.update_eval_rst_dict(demo_name, True, str(report[:-1]), goal_info)
        eval_statistics.save_eval_rst_dict()

def worker_task(queue, lock, eval_stat_path):
    while True:
        task = queue.get()
        if task is None:
            break
        demo_name, llm_plan_path = task
        simulate_llm_response(demo_name, lock, llm_plan_path, eval_stat_path)


def simulate_one_llm(llm_response_path, llm_name: str, worker_num: int=1, result_dir: str='./results'):
    get_all_raw_task_goal()
    manager = Manager()
    lock = manager.Lock()

    # llm_name = os.path.basename(llm_response_path).split('_')[0]
    eval_stat_path = os.path.join(result_dir, 'log', f'{llm_name}.json')
    os.makedirs(os.path.dirname(eval_stat_path), exist_ok=True)

    task_list = get_all_task_list()
    cur_eval_stats = EvalStatistics(task_list, eval_stat_path)
    real_task_list = [task_name for task_name in task_list if not cur_eval_stats.check_evaluated_task(task_name)]

    if worker_num > 1:
        worker_num = min(worker_num, len(real_task_list))
        task_queue = Queue()
        workers = []
        for i in range(worker_num):
            worker = Process(target=worker_task, args=(task_queue, lock, eval_stat_path))
            worker.start()
            workers.append(worker)
        
        for demo_name in real_task_list:
            task_queue.put((demo_name, llm_response_path))
        for i in range(worker_num):
            task_queue.put(None)
        for worker in workers:
            worker.join()
    else:
        for demo_name in real_task_list:
            simulate_llm_response(demo_name, lock, llm_response_path, eval_stat_path)
    print(f'Results saved to {eval_stat_path}')
    summary = {
        "trajectory_evaluation": {},
        "goal_evaluation": {}
    }
    traj_stats = traj_eval_stats(eval_stat_path)
    goal_stats = goal_eval_stats(eval_stat_path)
    summary['trajectory_evaluation'] = traj_stats
    summary['goal_evaluation'] = goal_stats

    summary_path = os.path.join(result_dir, 'summary', f'{llm_name}.json')
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=4)
    return summary

def evaluate_results(llm_response_dir, worker_num: int=1, result_dir: str='./results'):
    os.makedirs(result_dir, exist_ok=True)
    available_model_names = extract_model_names(llm_response_dir)
    if not available_model_names:
        print('No model found in the directory')
        return
    for model_name in available_model_names:
        model_path = os.path.join(llm_response_dir, f'{model_name}_outputs.json')
        assert os.path.exists(model_path), f'{model_path} not found in the directory'
        simulate_one_llm(model_path, model_name, worker_num, result_dir)

if  __name__ == '__main__':
    fire.Fire(evaluate_results)
