import json
import sys

sys.path.append("../simulation")

import re
import copy
import sys
import os
import os.path as osp
import copy
import ast
import random
import math
from collections import defaultdict

import evolving_graph.utils as utils
from evolving_graph.eval_utils import *



model_name = "gpt-4o"
system_prompt = "You are a helpful assistant in interpreting natural language goals into symbolic goals using given format. For this task, please only output a parsable json string inside brackets. Please start your answer with { and end your answer with }. Don't include any notes or explanations with the output json string."

def goal_input_preparation():
    dataset = "virtualhome"
    resource_root = (
        f"/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/resources/{dataset}"
    )
    data_dir = "/viscam/u/shiyuz/virtualhome/virtualhome/dataset/programs_processed_precond_nograb_morepreconds"
    task_dict_dir = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/resources/task_state_LTL_formula_accurate.json"
    helm_prompt_path = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/helm/helm_prompt/goal_interpretation_vh_complete.json"
    rel_obj_path = os.path.join(resource_root, "relation_object_pairs.json")
    all_rel_path = os.path.join(resource_root, "relation_types.json")
    all_action_path = os.path.join(resource_root, "action_space.json")
    scenegraph_id = 1
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
            # get symbolic goals
            # goals = task_goal_dict["vh_goal"]
            # action_goals = goals["actions"]
            # scene_goals = goals["goal"]
            # node_goals = []
            # edge_goals = []
            # for scene_goal in scene_goals:
            #     if "id" in scene_goal and "class_name" in scene_goal and "state" in scene_goal:
            #         node_goals.append(scene_goal)
            #     elif (
            #         "from_id" in scene_goal
            #         and "to_id" in scene_goal
            #         and "relation_type" in scene_goal
            #     ):
            #         edge_goals.append(scene_goal)
            #     else:
            #         raise ValueError("Scene goal is not in correct format")
            # print(f"Before check {node_goals=}")
            # print(f"Before check {edge_goals=}")

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


def goal_llm_prediction():
    helm_prompt_path = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/helm/helm_prompt/goal_interpretation_vh.json"
    helm_output_path = f"/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/helm/helm_output/goal_interpretation_vh_{model_name}.json"
    
    helm_output = []
    helm_prompt = json.load(open(helm_prompt_path, "r"))
    for prompt_dict in helm_prompt:
        id = prompt_dict["identifier"]
        prompt = prompt_dict["llm_prompt"]
        print(f"GPT starts prediction: {id}", flush=True)
        predicted_action = get_gpt_output(prompt, model_name, temperature=1, system_prompt=system_prompt)
        helm_output.append({"identifier": id, "llm_output": predicted_action})
    json.dump(helm_output, open(helm_output_path, "w"), indent=4)


def goal_output_evaluation():
    dataset = "virtualhome"
    helm_output_path = f"/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/helm/helm_output/goal_interpretation_vh_{model_name}.json"
    resource_root = (
        f"/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/resources/{dataset}"
    )
    data_dir = "/viscam/u/shiyuz/virtualhome/virtualhome/dataset/programs_processed_precond_nograb_morepreconds"

    # indexing path
    task_dict_dir = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/resources/task_state_LTL_formula_accurate.json"
    id_to_task_path = os.path.join(resource_root, "id2task.json")
    
    # load data
    task_dicts = json.load(open(task_dict_dir, "r"))
    helm_output = json.load(open(helm_output_path, "r"))
    id2task = json.load(open(id_to_task_path, "r"))

    properties_data = utils.load_properties_data()
    object_placing = utils.load_object_placing()
    name_equivalence = utils.load_name_equivalence()

    scenegraph_id = 1
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
        # if task not in ["Turn on light"]:
        #     continue
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
        
        gold_node_goals = list(set(gold_node_goals))
        gold_edge_goals = list(set(gold_edge_goals))
        gold_action_goals = list(set(gold_action_goals))
        
        output = output_dict["llm_output"]
        try:
            output = json.loads(output)
        except Exception as e:
            try:
                output = parse_json(output)
                if output is None or len(output) == 0:
                    format_wrong_goals += (
                        len(gold_node_goals)
                        + len(gold_edge_goals)
                        + len(gold_action_goals)
                    )
                    print(f"format wrong num is {format_wrong_goals}")
                    continue
            except Exception as e:
                format_wrong_goals += (
                    len(gold_node_goals) + len(gold_edge_goals) + len(gold_action_goals)
                )
                print(f"format wrong num is {format_wrong_goals}")
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
            
        pred_node_goals = output.get("node goals", [])
        pred_edge_goals = output.get("edge goals", [])
        pred_action_goals = output.get("action goals", [])
        if len(pred_action_goals) > 0:
            pred_action_goals = [pred_action_goal["action"].upper() for pred_action_goal in pred_action_goals]
        pred_node_goals = list(set(pred_node_goals))
        pred_edge_goals = list(set(pred_edge_goals))
        pred_action_goals = list(set(pred_action_goals))

        print(f'{task_name=}')
        print(f'{task_description=}')
        print(f"{name_to_id=}")
        # check node goals and calculate TP, FP, FN
        delta_TP_node_goals = 0
        delta_FP_node_goals = 0
        delta_FN_node_goals = 0
        print('Predicted node goals:')
        for node_goal in pred_node_goals:
            if node_goal["name"] not in name_to_id:
                hallucination_goals += 1
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
            if edge_goal["from_name"] not in name_to_id or edge_goal["to_name"] not in name_to_id:
                hallucination_goals += 1
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
        for action_goal in pred_action_goals:
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
        assert total_node_goals == TP_node_goals + FP_node_goals
        assert total_edge_goals == TP_edge_goals + FP_edge_goals
        assert total_action_goals == TP_action_goals + FP_action_goals
    
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
    



