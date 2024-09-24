import os
import json
import os.path as osp
import virtualhome_eval.simulation.evolving_graph.utils as utils
from multiprocessing import Process, Manager, Queue
from virtualhome_eval.evaluation.subgoal_decomposition.prompts.meta_prompt import generate_meta_prompt, generate_system_setup, get_meta_prompt_component
from virtualhome_eval.simulation.evolving_graph.eval_utils import *
from virtualhome_eval.evaluation.subgoal_decomposition.subgoal_prompts_utils import get_relevant_nodes, get_formatted_relevant_nodes, get_initial_states_and_final_goals, add_task_info_into_prompt_component, prompt_generated

def generate_prompts(args):
    dataset = args.dataset
    output_dir = args.output_dir
    evaluation_dir = args.evaluation_dir
    assert dataset == 'virtualhome', 'Subgoal decomposition is only supported for VirtualHome dataset'
    resource_root = osp.join(args.resource_dir, dataset)
    data_dir = osp.join(args.dataset_dir, "programs_processed_precond_nograb_morepreconds")
    task_dict_dir = osp.join(resource_root, "task_state_LTL_formula_accurate.json")
    scenegraph_id = args.scene_id
    scene_id = f"scene_{scenegraph_id}"
    task_dict = json.load(open(task_dict_dir, "r"))
    task_dict = task_dict[scene_id]

    # meta_prompt_file_path = os.path.join(evaluation_dir, 'subgoal_decomposition', 'prompts', 'meta_prompt.json')
    # generate_meta_prompt(meta_prompt_file_path)
    system_setup_file_path = os.path.join(evaluation_dir, 'subgoal_decomposition', 'prompts', 'system_setup.json')
    generate_system_setup(system_setup_file_path)

    # load meta for constructing planners
    properties_data = utils.load_properties_data()
    object_placing = utils.load_object_placing()
    name_equivalence = utils.load_name_equivalence()

    helm_prompt_path = osp.join(output_dir, "helm_prompt.json")
    helm_prompt_list = json.load(open(helm_prompt_path, "r")) if osp.exists(helm_prompt_path) else None
    helm_prompt_list = [] if helm_prompt_list is None else helm_prompt_list
    for task_name, task_detail in task_dict.items():
        logger.info(f"CURRENT TASK IS {task_name}!")
        for file_id, task_goal_dict in task_detail.items():
            if prompt_generated(helm_prompt_list, scene_id, file_id):
                continue
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

            motion_planner, relevant_id, gd_actions, task_name, _ = construct_planner(
                name_equivalence,
                properties_data,
                object_placing,
                scenegraph_id=scenegraph_id,
                script_id=file_id,
                dataset_root=data_dir
            )
            _, _, node_goal_str, edge_goal_str, action_goal_str, _ = motion_planner.get_symbolic_goal_nl(
                    node_goals, edge_goals, action_goals=action_goals
                )
            relevant_nodes, related_ids = get_relevant_nodes(motion_planner)
            relevant_nodes = get_formatted_relevant_nodes(relevant_nodes)
            init_states, final_states, action_states = get_initial_states_and_final_goals(motion_planner, node_goals, edge_goals, action_goals)
            relevant_nodes_str = "\n".join(relevant_nodes) if len(relevant_nodes) > 0 else "None"
            init_states_str = "\n".join(init_states) if len(init_states) > 0 else "None"
            final_states_str = "\n".join(final_states) if len(final_states) > 0 else "None"
            action_states_str = "\n".join(action_states) if len(action_states) > 0 else "None"
            if action_states_str == 'None' and final_states_str == 'None':
                continue

            necessity = 'Yes' if action_states_str != "None" else 'No'
            template_prompt = get_meta_prompt_component()
            prompt = add_task_info_into_prompt_component(template_prompt, task_name, relevant_nodes_str, init_states_str, final_states_str, action_states_str, necessity)
            helm_prompt_list.append(
                {
                    'identifier': f'{scene_id}_{file_id}',
                    'llm_prompt': prompt
                }
            )
    with open(helm_prompt_path, 'w') as f:
        json.dump(helm_prompt_list, f, indent=4)
    return helm_prompt_path