import json
import copy
import os
import os.path as osp
import copy

import simulation.evolving_graph.utils as utils
from simulation.evolving_graph.eval_utils import *


system_prompt = "You are a helpful assistant in interpreting natural language goals into symbolic goals using given format. For this task, please only output a parsable json string inside brackets. Please start your answer with { and end your answer with }. Don't include any notes or explanations with the output json string."

def goal_input_preparation(args):
    dataset = args.dataset
    resource_root = osp.join(args.resource_dir, dataset)
    data_dir = osp.join(
        args.dataset_dir, "programs_processed_precond_nograb_morepreconds"
    )
    task_dict_dir = osp.join(resource_root, "task_state_LTL_formula_accurate.json")
    helm_prompt_path = osp.join(args.helm_dir, "goal_interpretation_vh_complete.json")
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
        print(f"CURRENT TASK IS {task_name}!")
        for script_id, task_goal_dict in task_dicts.items():
            # get task name and description
            motion_planner, _, _, task_name, task_description = (
                construct_planner(
                    name_equivalence,
                    properties_data,
                    object_placing,
                    scenegraph_id=scenegraph_id,
                    script_id=script_id,
                    dataset_root=data_dir,
                )
            )
            object_in_scene, goal_str, relevant_name_to_id = (
                motion_planner.get_goal_describe_nl(
                    task_name, task_description, object_states
                )
            )
            prompt = open(
                    "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/prompts/goal_interpret_prompt_complete.txt",
                    "r",
                ).read()
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



def goal_output_evaluation(args):
    dataset = args.dataset
    model_name = args.model_name
    helm_output_path = osp.join(
        args.helm_dir, f"helm_output/goal_interpretation/{model_name}_outputs.json"
    )
    resource_root = osp.join(args.resource_dir, dataset)
    data_dir = osp.join(args.dataset_dir, "programs_processed_precond_nograb_morepreconds")
    task_dict_dir = osp.join(resource_root, "task_state_LTL_formula_accurate.json")
    id_to_task_path = os.path.join(resource_root, "id2task.json")
    
    # load data
    task_dicts = json.load(open(task_dict_dir, "r"))
    helm_output = json.load(open(helm_output_path, "r"))
    id2task = json.load(open(id_to_task_path, "r"))

    properties_data = utils.load_properties_data()
    object_placing = utils.load_object_placing()
    name_equivalence = utils.load_name_equivalence()

    scenegraph_id = args.scene_id
    scene_id = f"scene_{scenegraph_id}"
    task_dicts = task_dicts[scene_id]

    total_node_goals = 0
    hallucination_goals = 0

    TP_node_goals = 0
    FP_node_goals = 0
    FN_node_goals = 0

    total_edge_goals = 0
    TP_edge_goals = 0
    FP_edge_goals = 0
    FN_edge_goals = 0

    total_action_goals = 0
    TP_action_goals = 0
    FP_action_goals = 0
    FN_action_goals = 0

    format_wrong_goals = 0

    for output_dict in helm_output:
        file_id = output_dict["identifier"]

        # get symbolic goals
        task = id2task[file_id]
        print(f"Task is {task}, file_id is {file_id}")
        program_dict = task_dicts[task][file_id]
        goals = program_dict["vh_goal"]
        gold_action_goals = goals["actions"]
        scene_goals = goals["goal"]
        gold_node_goals = []
        gold_edge_goals = []
        for scene_goal in scene_goals:
            if "id" in scene_goal and "class_name" in scene_goal and "state" in scene_goal:
                gold_node_goals.append(scene_goal)
            elif (
                "from_id" in scene_goal
                and "to_id" in scene_goal
                and "relation_type" in scene_goal
            ):
                gold_edge_goals.append(scene_goal)
            else:
                raise ValueError("Scene goal is not in correct format")
        
        gold_node_goals = remove_duplicate_dicts(gold_node_goals)
        gold_edge_goals = remove_duplicate_dicts(gold_edge_goals)
        gold_action_goals = list(set(gold_action_goals))
        
        output = output_dict["llm_output"]
        # if llm output starts with ```json
        output = output.replace("<|eot_id|>", "")
        if output.startswith("```json"):
            output = output[7:]
            output = output.strip("```")
        output = output.strip().replace("\n", "")
        output = output.replace("\'", "\"")
        try:
            output = json.loads(output)
        except Exception as e:
            format_wrong_goals += 1
            print(f"format wrong num is {format_wrong_goals}")
            print(
                f"model {model_name}, task {task}, file_id {file_id} has format wrong output"
            )
            continue

        
        print(f"Ground truth {gold_node_goals=}")
        print(f"Ground truth {gold_edge_goals=}")
        print(f"Ground truth {gold_action_goals=}")
        
        # get the obj_to_id mapping
        motion_planner, _, _, task_name, task_description = construct_planner(
            name_equivalence,
            properties_data,
            object_placing,
            scenegraph_id=scenegraph_id,
            script_id=file_id,
            dataset_root=data_dir,
        )
        relevant_nodes_ids = motion_planner.get_relevant_nodes(script_id=file_id)
        name_to_id = {}
        for tup in relevant_nodes_ids:
            name_to_id[tup[0]] = tup[1]
            
        print(f'predicted {output=}')
        pred_node_goals = output.get("node goals", [])
        pred_edge_goals = output.get("edge goals", [])
        pred_action_goals = output.get("action goals", [])
        pred_node_goals = remove_duplicate_dicts(pred_node_goals)
        pred_edge_goals = remove_duplicate_dicts(pred_edge_goals)
        pred_action_goals = remove_duplicate_dicts(pred_action_goals)

        print(f'{task_name=}')
        print(f'{task_description=}')
        print(f"{name_to_id=}")
        # check node goals and calculate TP, FP, FN
        delta_TP_node_goals = 0
        delta_FP_node_goals = 0
        delta_FN_node_goals = 0
        print('Predicted node goals:')
        for node_goal in pred_node_goals:
            if len(node_goal) == 0:
                continue
            if "name" not in node_goal or "state" not in node_goal:
                format_wrong_goals += 1
                total_node_goals += 1
                print(f"model {model_name}, task {task}, file_id {file_id} has format wrong output")
                continue
            if node_goal["name"] not in name_to_id:
                hallucination_goals += 1
                print(
                    f"model {model_name}, task {task}, file_id {file_id} has hallucination output"
                )
                print(f'hallucinated output is {node_goal}')
                continue
            indexed_node_goals = {
                "id": name_to_id[node_goal["name"]],
                "class_name": node_goal["name"],
                "state": node_goal["state"],
            }
            print(indexed_node_goals)
            if indexed_node_goals in gold_node_goals:
                delta_TP_node_goals += 1
            else:
                delta_FP_node_goals += 1
        delta_FN_node_goals += len(gold_node_goals) - delta_TP_node_goals
        total_node_goals += delta_TP_node_goals + delta_FP_node_goals
        TP_node_goals += delta_TP_node_goals
        FP_node_goals += delta_FP_node_goals
        FN_node_goals += delta_FN_node_goals
        print(
            f"TP_node_goals: {delta_TP_node_goals}, FP_node_goals: {delta_FP_node_goals}, FN_node_goals: {delta_FN_node_goals}"
        )

        # check edge goals and calculate TP, FP, FN
        print('Predicted edge goals:')
        delta_TP_edge_goals = 0
        delta_FP_edge_goals = 0
        delta_FN_edge_goals = 0
        for edge_goal in pred_edge_goals:
            if len(edge_goal) == 0:
                continue
            if "from_name" not in edge_goal or "to_name" not in edge_goal or "relation" not in edge_goal:
                format_wrong_goals += 1
                total_edge_goals += 1
                print(
                    f"model {model_name}, task {task}, file_id {file_id} has format wrong output"
                )
                continue
            if edge_goal["from_name"] not in name_to_id or edge_goal["to_name"] not in name_to_id:
                hallucination_goals += 1
                print(f'model {model_name}, task {task}, file_id {file_id} has hallucination output')
                print(f'hallucinated output is {edge_goal}')
                continue
            indexed_edge_goals = {"from_id": name_to_id[edge_goal["from_name"]], "to_id": name_to_id[edge_goal["to_name"]], "relation_type": edge_goal["relation"]}
            print(indexed_edge_goals)
            if indexed_edge_goals in gold_edge_goals:
                delta_TP_edge_goals += 1
            else:
                delta_FP_edge_goals += 1
        delta_FN_edge_goals += len(gold_edge_goals) - delta_TP_edge_goals
        total_edge_goals += delta_TP_edge_goals + delta_FP_edge_goals
        TP_edge_goals += delta_TP_edge_goals
        FP_edge_goals += delta_FP_edge_goals
        FN_edge_goals += delta_FN_edge_goals
        print(
            f"TP_edge_goals: {delta_TP_edge_goals}, FP_edge_goals: {delta_FP_edge_goals}, FN_edge_goals: {delta_FN_edge_goals}"
        )

        # check action goals and calculate TP, FP, FN
        print('Predicted action goals:')
        delta_TP_acion_goals = 0
        delta_FP_action_goals = 0
        delta_FN_action_goals = 0
        gold_action_goals_cp = copy.deepcopy(gold_action_goals)
        for action_goal_dict in pred_action_goals:
            if len(action_goal_dict) == 0:
                continue
            if "action" not in action_goal_dict:
                format_wrong_goals += 1
                total_action_goals += 1
                print(
                    f"model {model_name}, task {task}, file_id {file_id} has format wrong output"
                )
                continue
            action_goal = action_goal_dict["action"].upper()
            print(action_goal)
            found_flag = False
            for gd_action_goals in gold_action_goals_cp:
                if '|' in gd_action_goals:
                    gd_action_goals = gd_action_goals.split('|')
                    # change to upper case
                    gd_action_goals = [gd_action_goal.upper() for gd_action_goal in gd_action_goals]
                else:
                    gd_action_goals = [gd_action_goals.upper()]
                if action_goal in gd_action_goals:
                    delta_TP_acion_goals += 1
                    found_flag = True
                    if gd_action_goals in gold_action_goals:
                        gold_action_goals_cp.remove(gd_action_goals)
                    break
            if not found_flag:
                delta_FP_action_goals += 1
        delta_FN_action_goals += len(gold_action_goals) - delta_TP_acion_goals
        total_action_goals += delta_TP_acion_goals + delta_FP_action_goals
        TP_action_goals += delta_TP_acion_goals
        FP_action_goals += delta_FP_action_goals
        FN_action_goals += delta_FN_action_goals
        print(
            f"TP_action_goals: {delta_TP_acion_goals}, FP_action_goals: {delta_FP_action_goals}, FN_action_goals: {delta_FN_action_goals}"
        )
    
    node_precision, node_recall, node_f1 = precision_recall_f1(TP_node_goals, FP_node_goals, FN_node_goals)
    print(f"Node: TP: {TP_node_goals}, FP: {FP_node_goals}, FN: {FN_node_goals}, Precision: {node_precision}, Recall: {node_recall}, F1: {node_f1}")

    edge_precision, edge_recall, edge_f1 = precision_recall_f1(TP_edge_goals, FP_edge_goals, FN_edge_goals)
    print(f"Edge: TP: {TP_edge_goals}, FP: {FP_edge_goals}, FN: {FN_edge_goals}, Precision: {edge_precision}, Recall: {edge_recall}, F1: {edge_f1}")

    action_precision, action_recall, action_f1 = precision_recall_f1(TP_action_goals, FP_action_goals, FN_action_goals)
    print(f"Action: TP: {TP_action_goals}, FP: {FP_action_goals}, FN: {FN_action_goals}, Precision: {action_precision}, Recall: {action_recall}, F1: {action_f1}")

    all_TP = TP_node_goals + TP_edge_goals + TP_action_goals
    all_FP = FP_node_goals + FP_edge_goals + FP_action_goals
    all_FN = FN_node_goals + FN_edge_goals + FN_action_goals
    all_precision, all_recall, all_f1 = precision_recall_f1(all_TP, all_FP, all_FN)
    print(f"All: TP: {all_TP}, FP: {all_FP}, FN: {all_FN}, Precision: {all_precision}, Recall: {all_recall}, F1: {all_f1}")

    format_wrong_rate = format_wrong_goals / (total_node_goals + total_edge_goals + total_action_goals)
    print(f"Format wrong num is {format_wrong_goals}, Total goals num is {total_node_goals + total_edge_goals + total_action_goals}")
    print(f"Format wrong rate is {format_wrong_rate}")

    hallucination_rate = hallucination_goals / (total_node_goals + total_edge_goals + total_action_goals)
    print(f"Hallucination num is {hallucination_goals}, Total goals num is {total_node_goals + total_edge_goals + total_action_goals}")
    print(f"Hallucination rate is {hallucination_rate}")

    return [node_precision, node_recall, node_f1, edge_precision, edge_recall, edge_f1, action_precision, action_recall, action_f1, all_precision, all_recall, all_f1, format_wrong_rate, hallucination_rate]
    



