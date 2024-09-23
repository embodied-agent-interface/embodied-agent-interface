import os
import json
import fire
import logging
logger = logging.getLogger(__name__)
from multiprocessing import Process, Manager, Queue
from virtualhome_eval.evaluation.subgoal_decomposition.subgoal_sim_utils import evaluate_task, EvalStatistics, get_scene_id_and_file_id, get_llm_outputs_dict, get_llm_tasks_names
from virtualhome_eval.evaluation.subgoal_decomposition.subgoal_eval_utils import traj_eval_stats, goal_eval_stats, extract_model_names

def simulate_llm_response(
    args, scene_id, file_id, lock, llm_response, eval_stat_path, task_names
):
    task_name = f'scene_{scene_id}_{file_id}'
    resource_dir = args.resource_dir
    vocab_path = os.path.join(resource_dir, 'vocabulary.json')
    report = evaluate_task(vocab_path, scene_id, file_id, llm_response, args)
    with lock:
        eval_statistics = EvalStatistics(task_names, eval_stat_path)
        if report[0] != 'Correct':
            eval_statistics.update_eval_rst_dict(task_name, False, str(report))
        else:
            eval_statistics.update_eval_rst_dict(task_name, True, str(report))
        eval_statistics.save_eval_rst_dict()

def worker_task(queue, lock, eval_stat_path, task_names, passing_args):
    while True:
        task = queue.get()
        if task is None:
            break
        scene_id, file_id, llm_response = task
        args = dict_args_to_args(passing_args)
        simulate_llm_response(args, scene_id, file_id, lock, llm_response, eval_stat_path, task_names)

def args_to_dict(args):
    new_args = {}
    new_args['mode'] = args.mode
    new_args['eval_type'] = args.eval_type
    new_args['resource_dir'] = args.resource_dir
    new_args['llm_response_path'] = args.llm_response_path
    new_args['dataset_dir'] = args.dataset_dir
    new_args['dataset'] = args.dataset
    new_args['output_dir'] = args.output_dir
    new_args['scene_id'] = args.scene_id
    new_args['evaluation_dir'] = args.evaluation_dir
    new_args['num_workers'] = args.num_workers
    return new_args

def dict_args_to_args(dict_args):
    class Args:
        pass
    args = Args()
    for key, value in dict_args.items():
        setattr(args, key, value)
    return args
    


def simulate_one_llm(args, llm_response_path, result_dir: str='./results'):
    manager = Manager()
    lock = manager.Lock()

    llm_responses = get_llm_outputs_dict(llm_response_path)
    llm_name = os.path.basename(llm_response_path).split('.')[0]
    eval_stat_path = os.path.join(result_dir, 'error_info.json')
    print(f"Error info will be saved to {eval_stat_path}")
    os.makedirs(os.path.dirname(eval_stat_path), exist_ok=True)

    task_list = [(get_scene_id_and_file_id(item['identifier']), item['llm_output']) for item in llm_responses]
    task_names = get_llm_tasks_names(llm_responses)
    real_task_list = []
    eval_statistics = EvalStatistics(task_names, eval_stat_path)
    for (scene_id, file_id), llm_response in task_list:
        task_name = f'scene_{scene_id}_{file_id}'
        if not eval_statistics.check_evaluated_task(task_name):
            real_task_list.append((scene_id, file_id, llm_response))
    worker_num = args.num_workers
    if worker_num > 1:
        worker_num = min(worker_num, len(real_task_list))
        task_queue = Queue()
        workers = []
        for i in range(worker_num):
            dict_args = args_to_dict(args)
            worker = Process(target=worker_task, args=(task_queue, lock, eval_stat_path, task_names, dict_args))
            worker.start()
            workers.append(worker)
        
        for scene_id, file_id, llm_response in real_task_list:
            task_queue.put((scene_id, file_id, llm_response))
        for i in range(worker_num):
            task_queue.put(None)
        for worker in workers:
            worker.join()
    else:
        for scene_id, file_id, llm_response in real_task_list:
            simulate_llm_response(
                args, scene_id, file_id, lock, llm_response, eval_stat_path, task_names
            )
    logger.info(f'Results saved to {eval_stat_path}')
    summary = {
        "trajectory_evaluation": {},
        "goal_evaluation": {}
    }
    traj_stats = traj_eval_stats(eval_stat_path)
    goal_stats = goal_eval_stats(eval_stat_path, args)
    summary['trajectory_evaluation'] = traj_stats
    summary['goal_evaluation'] = goal_stats
    return summary


def evaluate_results(args):
    dataset = args.dataset
    llm_response_path = os.path.join(
        args.llm_response_path, dataset, "subgoal_decomposition"
    )
    model_names = extract_model_names(llm_response_path)
    all_results = {}
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    for model_name in model_names:
        output_path = os.path.join(output_dir, model_name)
        os.makedirs(output_path, exist_ok=True)
        
        resource_root = os.path.join(args.resource_dir, dataset)
        data_dir = os.path.join(args.dataset_dir, "programs_processed_precond_nograb_morepreconds")

        os.makedirs(output_path, exist_ok=True)
        llm_response_json = os.path.join(llm_response_path, f'{model_name}_outputs.json')
        summary = simulate_one_llm(args, llm_response_json, result_dir=output_path)
        save_path = os.path.join(output_path, "summary.json")
        with open(save_path, "w") as f:
            json.dump(summary, f, indent=4)
            logger.info(f"Evaluate results of {model_name} saved to {save_path}")
        all_results[model_name] = summary
    return all_results