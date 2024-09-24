import json
import os
import os.path as osp

import virtualhome_eval.simulation.evolving_graph.utils as utils
from virtualhome_eval.simulation.evolving_graph.eval_utils import *
import virtualhome_eval.evaluation.goal_interpretation.prompts.one_shot as one_shot

import logging
logger = logging.getLogger(__name__)


def generate_prompts(args):
    resource_root = osp.join(args.resource_dir, "virtualhome")
    output_dir = args.output_dir
    data_dir = osp.join(
        args.dataset_dir, "programs_processed_precond_nograb_morepreconds"
    )
    task_dict_dir = osp.join(resource_root, "task_state_LTL_formula_accurate.json")
    evaluation_dir = args.evaluation_dir
    helm_prompt_path = osp.join(output_dir, "helm_prompt.json")
    rel_obj_path = os.path.join(resource_root, "relation_object_pairs.json")
    all_rel_path = os.path.join(resource_root, "relation_types.json")
    all_action_path = os.path.join(resource_root, "action_space.json")

    scenegraph_id = args.scene_id
    scene_id = f"scene_{scenegraph_id}"

    all_rel = json.load(open(all_rel_path, "r"))
    action_space = json.load(open(all_action_path, "r"))
    task_dict = json.load(open(task_dict_dir, "r"))
    task_dict = task_dict[scene_id]
    relation_object_paris = json.load(open(rel_obj_path, "r"))
    if relation_object_paris is not None:
        for k, v in relation_object_paris.items():
            relation_object_paris[k] = set(v)
    # load meta for constructing planners
    properties_data = utils.load_properties_data()
    object_states = utils.load_object_states()
    object_placing = utils.load_object_placing()
    name_equivalence = utils.load_name_equivalence()

    helm_prompt_list = []

    for task_name, task_dicts in task_dict.items():
        logger.info(f"CURRENT TASK IS {task_name}!")
        for script_id, task_goal_dict in task_dicts.items():
            # get task name and description
            motion_planner, _, _, task_name, task_description = construct_planner(
                name_equivalence,
                properties_data,
                object_placing,
                scenegraph_id=scenegraph_id,
                script_id=script_id,
                dataset_root=data_dir,
            )
            object_in_scene, goal_str, relevant_name_to_id = (
                motion_planner.get_goal_describe_nl(
                    task_name, task_description, object_states
                )
            )
            prompt = one_shot.prompt
            prompt = prompt.replace("<object_in_scene>", object_in_scene)
            prompt = prompt.replace("<goal_str>", goal_str)
            prompt = prompt.replace("<relation_types>", str(all_rel))
            prompt = prompt.replace("<action_space>", str(action_space))
            prompt = prompt.replace("<rel_obj_pairs>", str(relation_object_paris))

            helm_prompt_list.append(
                {"identifier": f"{script_id}", "llm_prompt": f"{prompt}"}
            )

    # save helm_prompt_list
    json.dump(helm_prompt_list, open(helm_prompt_path, "w"), indent=4)

    return helm_prompt_path
