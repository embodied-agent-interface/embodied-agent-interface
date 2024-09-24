import json
import os
import os.path as osp
from virtualhome_eval.simulation.evolving_graph.eval_utils import *
from virtualhome_eval.simulation.evolving_graph.logic_score import *
import virtualhome_eval.evaluation.transition_modeling.prompts.one_shot as one_shot

import logging
logger = logging.getLogger(__name__)

def generate_prompts(args):
    helm_prompt_list = []
    dataset = args.dataset
    scenegraph_id = args.scene_id
    scene_id = f"scene_{scenegraph_id}"

    resource_root = osp.join(args.resource_dir, dataset)

    pddl_root = osp.join(resource_root, "pddl_files")
    pddl_problem_dir = osp.join(resource_root, "problem_pddl")
    os.makedirs(pddl_root, exist_ok=True)
    os.makedirs(pddl_problem_dir, exist_ok=True)

    success_dict_path = osp.join(resource_root, "success_task.json")
    id2action_path = osp.join(resource_root, "id2action.json")
    gold_action_path = osp.join(resource_root, "gold_action.json")

    task_dict_dir = osp.join(resource_root, "task_state_LTL_formula_accurate.json")
    helm_prompt_path = osp.join(args.output_dir, "helm_prompt.json")
    task_dict = json.load(open(task_dict_dir, "r"))
    success_file_id = json.load(open(success_dict_path, "r"))
    id2action = json.load(open(id2action_path, "r"))
    gold_action_dict = json.load(open(gold_action_path, "r"))

    task_dict = task_dict[scene_id]

    for task_name, task_dicts in task_dict.items():
        if task_name in ["Wash dishes by hand", "Write an email", "Wash hands"]:
            continue
        logger.info(f"task name is {task_name}")
        task_name = "_".join(task_name.split())
        task_problem_dir = os.path.join(pddl_problem_dir, task_name)

        for file_id, _ in task_dicts.items():
            if os.path.exists(success_dict_path):
                if file_id not in success_file_id:
                    continue

            problem_path = os.path.join(task_problem_dir, f"{file_id}.pddl")
            problem_file = open(problem_path, "r").read()

            gold_actions_name = id2action[file_id]
            action_handlers = ""
            for action_name in gold_actions_name:
                action_param = gold_action_dict[action_name]["action_parameters"]
                action_handlers += f"(:action {action_name}\n  :parameters {action_param}\n  :precondition ()\n  :effect ()\n)\n"

            prompt = one_shot.prompt
            prompt = prompt.replace("<problem_file>", problem_file)
            prompt = prompt.replace("<action_handlers", action_handlers)
            helm_prompt_list.append(
                {"identifier": f"{file_id}", "llm_prompt": f"{prompt}"}
            )

    # save helm prompt
    json.dump(helm_prompt_list, open(helm_prompt_path, "w"), indent=4)
    return helm_prompt_path

