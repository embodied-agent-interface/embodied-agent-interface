import json
import os.path as osp

import virtualhome_eval.simulation.evolving_graph.utils as utils
from virtualhome_eval.simulation.evolving_graph.eval_utils import *
import virtualhome_eval.evaluation.action_sequencing.prompts.one_shot as one_shot

import logging
logger = logging.getLogger(__name__)

def generate_prompts(args):
    dataset = args.dataset
    output_dir = args.output_dir
    resource_root = osp.join(args.resource_dir, dataset)
    data_dir = osp.join(
        args.dataset_dir, "programs_processed_precond_nograb_morepreconds"
    )
    task_dict_dir = osp.join(resource_root, "task_state_LTL_formula_accurate.json")
    evaluation_dir = args.evaluation_dir
    helm_prompt_path = osp.join(output_dir, "helm_prompt.json")
    scenegraph_id = args.scene_id
    scene_id = f"scene_{scenegraph_id}"
    task_dict = json.load(open(task_dict_dir, "r"))
    task_dict = task_dict[scene_id]

    # load meta for constructing planners
    properties_data = utils.load_properties_data()
    object_placing = utils.load_object_placing()
    name_equivalence = utils.load_name_equivalence()

    helm_prompt_list = []

    for task_name, task_dicts in task_dict.items():
        logger.info(f"CURRENT TASK IS {task_name}!")
        for file_id, task_goal_dict in task_dicts.items():
            # get symbolic goals
            goals = task_goal_dict["vh_goal"]
            action_goals = goals["actions"]
            scene_goals = goals["goal"]
            node_goals = []
            edge_goals = []
            for scene_goal in scene_goals:
                if (
                    "id" in scene_goal
                    and "class_name" in scene_goal
                    and "state" in scene_goal
                ):
                    node_goals.append(scene_goal)
                elif (
                    "from_id" in scene_goal
                    and "to_id" in scene_goal
                    and "relation_type" in scene_goal
                ):
                    edge_goals.append(scene_goal)
                else:
                    raise ValueError("Scene goal is not in correct format")

            # get task name and description
            motion_planner, relevant_id, gd_actions, task_name, _ = construct_planner(
                name_equivalence,
                properties_data,
                object_placing,
                scenegraph_id=scenegraph_id,
                script_id=file_id,
                dataset_root=data_dir,
            )
            _, _, node_goal_str, edge_goal_str, action_goal_str, relevant_name_to_id = (
                motion_planner.get_symbolic_goal_nl(
                    node_goals, edge_goals, action_goals=action_goals
                )
            )

            object_in_scene, cur_change, _ = motion_planner.get_nl_goal_string()

            prompt = one_shot.prompt
            prompt = prompt.replace("<object_in_scene>", object_in_scene)
            prompt = prompt.replace("<cur_change>", cur_change)
            prompt = prompt.replace("<node_goals>", node_goal_str)
            prompt = prompt.replace("<edge_goals>", edge_goal_str)
            prompt = prompt.replace("<action_goals>", action_goal_str)

            helm_prompt_list.append(
                {"identifier": f"{file_id}", "llm_prompt": f"{prompt}"}
            )

    # save helm_prompt_list
    json.dump(helm_prompt_list, open(helm_prompt_path, "w"), indent=4)
    return helm_prompt_path
