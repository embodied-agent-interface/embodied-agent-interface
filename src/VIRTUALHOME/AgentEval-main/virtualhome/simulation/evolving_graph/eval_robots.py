import json
import sys

sys.path.append("../simulation")
from enum import Enum
import re
import copy
import sys

import evolving_graph.utils as utils
from evolving_graph.execution import Relation, State
from evolving_graph.scripts import (
    read_script,
    Action,
    ScriptObject,
    ScriptLine,
    ScriptParseException,
    Script,
    parse_script_line,
)
from evolving_graph.execution import ScriptExecutor, ExecutionInfo
from evolving_graph.environment import EnvironmentGraph, EnvironmentState
from evolving_graph.prune_graph import *
from evolving_graph.filter_relevant_info import *
import re

from difflib import SequenceMatcher
import random
import os
import ast
import tqdm
import os.path as osp
from evolving_graph.motion_planner import MotionPlanner
from evolving_graph.eval_action import *
from evolving_graph.eval_transition import *
from evolving_graph.eval_utils import *



def evaluate_goal_interpretation_plan_succ(
    data_dir,
    t_ids,
    node_goal_list,
    edge_goal_list,
    action_goals,
    num_tasks=50,
    case_path=None,
    save_case=False,
    node_dict=None,
    edge_dict=None,
    action_dict=None,
    plug_analysis=None,
    relation_object_paris=None,
    task_rep_dict=None,
):
    properties_data = utils.load_properties_data()
    object_states = utils.load_object_states()
    object_placing = utils.load_object_placing()
    name_equivalence = utils.load_name_equivalence()

    rep_goals_pair = [0, 0]
    scene_id = [1]
    program_dir = os.path.join(data_dir, "executable_programs")
    all_rel_path = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/resources/relation_types.json"
    all_action_path = (
        "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/resources/action_space.json"
    )
    with open(all_rel_path, "r") as f:
        all_rel = json.load(f)
    with open(all_action_path, "r") as f:
        action_space = json.load(f)

    helm_prompt_l = []

    tot_num = 0.0
    tot_nodes = 0.0
    tot_edges = 0.0
    tot_actions = 0.0
    tot_succ = 0.0
    succ_nodes = 0.0
    succ_edges = 0.0
    succ_actions = 0.0
    pattern = r"file(\d+_\d+)\.txt"

    if relation_object_paris is not None:
        for k, v in relation_object_paris.items():
            relation_object_paris[k] = set(v)

    for scene in scene_id:
        scene_dir = os.path.join(
            program_dir,
            f"TrimmedTestScene{scene}_graph",
            "results_intentions_march-13-18",
        )
        # full_object_in_scene = get_all_object_in_scene(data_dir, scene)
        for file in os.listdir(scene_dir):
            if file.endswith(".txt"):
                match = re.search(pattern, file)
                if match:
                    script_id = match.group(1)
                else:
                    print("Wrong file format. No match found.")
                    continue
                if script_id not in t_ids:
                    continue

                tot_num += 1
                motion_planner, relevant_id, gd_actions, task_name, task_description = (
                    construct_planner(
                        name_equivalence,
                        properties_data,
                        object_placing,
                        scenegraph_id=scene,
                        script_id=script_id,
                        dataset_root=data_dir,
                    )
                )
                node_goals = copy.deepcopy(node_goal_list)
                edge_goals = copy.deepcopy(edge_goal_list)

                motion_planner.reset()
                print(f"{node_goals=}")
                print(f"{edge_goals=}")
                gd_node_goals, gd_edge_goals = find_node_and_edge_in_scene_exact(
                    node_goals, edge_goals, motion_planner
                )

                print(f"{gd_node_goals=}")
                print(f"{gd_edge_goals=}")

                # error analysis
                for goal in gd_node_goals:
                    gd_state = goal["state"]
                    if gd_state not in node_dict.keys():
                        node_dict[gd_state] = [0, 1]
                    else:
                        node_dict[gd_state] = [
                            node_dict[gd_state][0],
                            node_dict[gd_state][1] + 1,
                        ]
                for goal in gd_edge_goals:
                    gd_relation = goal["relation"]
                    gd_object = goal["to_name"]
                    if gd_relation not in relation_object_paris.keys():
                        relation_object_paris[gd_relation] = {gd_object}
                    else:
                        relation_object_paris[gd_relation].add(gd_object)
                    if gd_relation not in edge_dict.keys():
                        edge_dict[gd_relation] = [0, 1]
                    else:
                        edge_dict[gd_relation] = [
                            edge_dict[gd_relation][0],
                            edge_dict[gd_relation][1] + 1,
                        ]
                for action_goal in action_goals:
                    if "|" in action_goal:
                        action_goal_list = action_goal.split("|")
                    else:
                        action_goal_list = [action_goal]
                    for gd_action in action_goal_list:
                        gd_action = gd_action.upper()
                        if gd_action not in action_dict.keys():
                            action_dict[gd_action] = [0, 1]
                        else:
                            action_dict[gd_action] = [
                                action_dict[gd_action][0],
                                action_dict[gd_action][1] + 1,
                            ]

                print(f"{task_name=}")
                print(f"{task_description=}")
                # print(f'{object_states=}')
                if (
                    len(gd_node_goals) == 0
                    and len(gd_edge_goals) == 0
                    and len(action_goals) == 0
                ):
                    return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

                # relevant obj
                object_in_scene, goal_str, relevant_name_to_id = (
                    motion_planner.get_goal_describe_nl(
                        task_name, task_description, object_states
                    )
                )

                for goal in gd_node_goals:
                    gd_state = goal["state"]
                    if gd_state == "PLUGGED_IN":
                        plug_id = relevant_name_to_id[goal["name"]]
                        plug_analysis[3] += 1
                        graph_dict = motion_planner.env_graph.get_node(
                            plug_id
                        ).to_dict()
                        plug_init_state = graph_dict["states"]
                        if "PLUGGED_IN" in plug_init_state:
                            plug_analysis[0] += 1
                        if "PLUGGED_OUT" in plug_init_state:
                            plug_analysis[1] += 1
                        if (
                            "PLUGGED_IN" not in plug_init_state
                            and "PLUGGED_OUT" not in plug_init_state
                        ):
                            plug_analysis[2] += 1

                print(f"{goal_str=}")
                print(f"{object_in_scene=}")
                prompt = open(
                    "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/prompts/goal_interpret_prompt.txt",
                    "r",
                ).read()
                prompt = prompt.replace("<object_in_scene>", object_in_scene)
                prompt = prompt.replace("<goal_str>", goal_str)
                prompt = prompt.replace("<relation_types>", str(all_rel))
                prompt = prompt.replace("<action_space>", str(action_space))
                prompt = prompt.replace("<rel_obj_pairs>", str(relation_object_paris))

                helm_prompt_l.append(
                    {
                        "identifier": f"{script_id}",
                        "llm_prompt": f"{prompt}",
                        "reference": "",
                    }
                )

                tot_retry = 5
                cur_retry = 0
                retry_flag = True
                while retry_flag and cur_retry < tot_retry:
                    goal_words = len(prompt.split())
                    print("Goal int words len", goal_words)
                    predicted_goals = get_gpt_output(prompt, json_object=True)
                    predicted_words = len(predicted_goals.split())
                    print("Goal int words outlen", predicted_words)
                    predicted_goals.strip(" ").strip("\n").strip(" ")
                    try:
                        predicted_goals = eval(predicted_goals)
                        retry_flag = False
                        break
                    except:
                        print("Retry!")
                        cur_retry += 1
                print(f"{predicted_goals=}")

                # error analysis
                pd_node_goals = predicted_goals["node goals"]
                pd_edge_goals = predicted_goals["edge goals"]
                pd_action_goal_res = predicted_goals["action goals"]
                pd_action_goals = []
                print(f"{pd_node_goals=}")
                print(f"{pd_edge_goals=}")
                for pd_action in pd_action_goal_res:
                    if isinstance(pd_action, dict):
                        pd_action_goals.append(pd_action["action"])
                    elif isinstance(pd_action, str):
                        pd_action_goals.append(pd_action)

                existing_nodes = 0.0
                existing_edges = 0.0
                for node_goal in gd_node_goals:
                    if node_goal in pd_node_goals:
                        print(f"found! {node_goal=}")
                        pd_state = node_goal["state"]
                        assert pd_state in node_dict.keys()
                        node_dict[pd_state][0] += 1
                        # print(f'{node_dict=}')
                    else:
                        goal_node_id = relevant_name_to_id[node_goal["name"]]
                        graph_dict = motion_planner.env_graph.get_node(
                            goal_node_id
                        ).to_dict()
                        if node_goal["state"] in graph_dict["states"]:
                            name = node_goal["name"]
                            state = node_goal["state"]
                            print(f"{name}, {state} already in init state")
                            existing_nodes += 1

                for edge_goal in gd_edge_goals:
                    if edge_goal in pd_edge_goals:
                        pd_relation = edge_goal["relation"]
                        assert pd_relation in edge_dict.keys()
                        edge_dict[pd_relation][0] += 1
                    else:
                        goal_from_id = relevant_name_to_id[edge_goal["from_name"]]
                        goal_to_id = relevant_name_to_id[edge_goal["to_name"]]
                        goal_relation = edge_goal["relation"]
                        to_objects = motion_planner.env_graph._get_node_maps_from(
                            goal_from_id, goal_relation
                        )
                        if goal_to_id in to_objects:
                            print(
                                f"{goal_from_id}, {goal_relation}, {goal_to_id} already in init state"
                            )
                            existing_edges += 1
                for action_goal in action_goals:
                    if "|" in action_goal:
                        action_goal_list = action_goal.split("|")
                    else:
                        action_goal_list = [action_goal]
                    for gd_action in action_goal_list:
                        gd_action = gd_action.upper()
                        if gd_action in pd_action_goals:
                            assert gd_action in action_dict.keys()
                            for possible_action in action_goal_list:
                                possible_action = possible_action.upper()
                                action_dict[possible_action][0] += 1
                            break
                rep_goals_pair[0] += existing_nodes
                rep_goals_pair[1] += existing_edges
                (
                    succ_node_goals,
                    tot_node_goals,
                    succ_edge_goals,
                    tot_edge_goals,
                    succ_action_goals,
                    tot_action_goals,
                ) = check_goal_interpretation(
                    predicted_goals,
                    gd_node_goals,
                    gd_edge_goals,
                    action_goals,
                    relevant_name_to_id,
                )
                tot_nodes += tot_node_goals
                tot_edges += tot_edge_goals
                tot_actions += tot_action_goals
                succ_nodes += succ_node_goals
                succ_edges += succ_edge_goals
                succ_actions += succ_action_goals
                succ_score = (succ_node_goals + succ_edge_goals + succ_action_goals) / (
                    tot_node_goals + tot_edge_goals + tot_action_goals
                )
                assert succ_score >= 0 and succ_score <= 1
                tot_succ += succ_score
                print(f"{succ_score=}")
                print(f"{tot_succ=}")

                if not save_case:
                    continue
                node_score = (
                    succ_node_goals / tot_node_goals if tot_node_goals != 0 else -1
                )
                edge_score = (
                    succ_edge_goals / tot_edge_goals if tot_edge_goals != 0 else -1
                )
                if (
                    (succ_score <= 0.2 and succ_score >= 0)
                    or (node_score <= 0.2 and node_score >= 0)
                    or (edge_score <= 0.1 and edge_score >= 0)
                ):
                    # save task, gold goals, predicted goals
                    with open(case_path, "a") as f:
                        f.write(f"Script {script_id}\n")
                        f.write(f"Goal type: {task_name}\n")
                        f.write(f"Goal description: {task_description}")
                        f.write(
                            f"NODE SCORE={node_score}, {succ_node_goals} out of {tot_node_goals} are correct\nEDGE SCORE={edge_score}, {succ_edge_goals} out of {tot_edge_goals} are correct\nTOTAL SCORE={succ_score}, in total {succ_node_goals + succ_edge_goals} out of {tot_node_goals + tot_edge_goals} are correct\n"
                        )
                        f.write(f"{object_in_scene=}\n")
                        f.write(f"{goal_str=}\n")
                        f.write(f"Ground truth node goal: {gd_node_goals}\n")
                        f.write(f"Ground truth edge goal: {gd_edge_goals}\n")
                        f.write(f"Ground truth action goal: {action_goals}\n")
                        f.write(f"LLM generated goals: {predicted_goals}\n")
                        f.write("\n\n")

    if relation_object_paris is not None:
        for k, v in relation_object_paris.items():
            relation_object_paris[k] = list(v)

    return (
        succ_nodes,
        tot_nodes,
        succ_edges,
        tot_edges,
        succ_actions,
        tot_actions,
        tot_succ,
        tot_num,
        node_dict,
        edge_dict,
        action_dict,
        plug_analysis,
        relation_object_paris,
        rep_goals_pair,
        helm_prompt_l,
    )


def evaluate_action_plan_succ(
    data_dir, t_ids, node_goal_list, edge_goal_list, action_goals, num_tasks=50
):
    succ = 0

    properties_data = utils.load_properties_data()
    object_states = utils.load_object_states()
    object_placing = utils.load_object_placing()
    name_equivalence = utils.load_name_equivalence()

    scene_id = [1]
    program_dir = os.path.join(data_dir, "executable_programs")

    tot_num = 0.0
    tot_succ = 0.0
    tot_exec = 0.0
    map_suc = 0.0
    pattern = r"file(\d+_\d+)\.txt"

    helm_prompt_l = []

    for scene in scene_id:
        scene_dir = os.path.join(
            program_dir,
            f"TrimmedTestScene{scene}_graph",
            "results_intentions_march-13-18",
        )
        for file in os.listdir(scene_dir):
            if file.endswith(".txt"):
                match = re.search(pattern, file)
                if match:
                    script_id = match.group(1)
                else:
                    print("Wrong file format. No match found.")
                    continue
                if script_id not in t_ids:
                    continue
                # print(f'{script_id=}')
                tot_num += 1
                motion_planner, relevant_id, gd_actions, task_name, task_description = (
                    construct_planner(
                        name_equivalence,
                        properties_data,
                        object_placing,
                        scenegraph_id=scene,
                        script_id=script_id,
                        dataset_root=data_dir,
                    )
                )
                node_goals = copy.deepcopy(node_goal_list)
                edge_goals = copy.deepcopy(edge_goal_list)

                motion_planner.reset()
                relevant_nodes = motion_planner.get_relevant_nodes(script_id=script_id)

                # cur_state = motion_planner.get_current_state_string()
                # target_state = str(motion_planner.final_state_dict)
                # cur_change, target_change = motion_planner.get_complete_goal_string()
                # cur_change = str(cur_change)
                # target_change = str(target_change)

                # test LLM translated goals
                # mapping_prompt = open('/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/prompts/mapping_prompt.txt', 'r').read()
                # properties_data = motion_planner.properties_data
                # relevant_properties_data = {}
                # for node_name in relevant_nodes:
                #     relevant_properties_data[node_name] = properties_data[node_name] if node_name in properties_data else []
                # print(f'{relevant_properties_data=}')
                # mapping_prompt = mapping_prompt.replace('<node_goals>', str(node_goals))
                # mapping_prompt = mapping_prompt.replace('<edge_goals>', str(edge_goals))
                # mapping_prompt = mapping_prompt.replace('<relevant_nodes>', relevant_nodes)
                # mapping_prompt = mapping_prompt.replace('<node+property>', str(relevant_properties_data))
                # mapping_prompt_words = len(mapping_prompt.split())
                # print('mapping prompt words len', mapping_prompt_words)
                # concrete_goals = get_gpt_output(mapping_prompt, json_object=True)
                # mapping_prompt_words_out = len(concrete_goals.split())
                # print('mapping prompt words outlen', mapping_prompt_words_out)
                # concrete_goals = eval(concrete_goals)
                # print(f'{concrete_goals=}')
                # llm_node_goals = concrete_goals['concrete node goals']
                # try:
                #     llm_node_goals = [eval(node_goal) for node_goal in llm_node_goals]
                # except:
                #     llm_node_goals = llm_node_goals
                # llm_edge_goals = concrete_goals['concrete edge goals']
                # try:
                #     llm_edge_goals = [eval(edge_goal) for edge_goal in llm_edge_goals]
                # except:
                #     llm_edge_goals = llm_edge_goals
                # if '|' not in node_goals:
                #     node_flag = True
                # node_goals, edge_goals = find_node_and_edge_in_scene(node_goals, edge_goals, relevant_nodes, motion_planner)
                # # print(f'{node_goals=}')
                # # print(f'{edge_goals=}')
                # if node_flag:
                #     llm_node_goals = node_goals

                # relevant obj
                (
                    object_in_scene,
                    cur_change,
                    node_goal_str,
                    edge_goal_str,
                    relevant_name_to_id,
                ) = motion_planner.get_symbolic_goal_nl(node_goals, edge_goals)

                # full obj
                # object_in_scene = full_object_in_scene

                # translate_prompt = open('/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/prompts/translation_prompt.txt', 'r').read()
                # translate_prompt = translate_prompt.replace('<node_goals>', str(node_goals))
                # translate_prompt = translate_prompt.replace('<edge_goals>', str(edge_goals))
                # translate_words = len(translate_prompt.split())
                # print('action goal translation prompt words len', translate_words)
                # llm_goal_str = get_gpt_output(translate_prompt, json_object=True)
                # translate_words_out = len(llm_goal_str.split())
                # print('action goal translation prompt words len', translate_words_out)
                # llm_goal_str = eval(llm_goal_str)
                # llm_node_goal_str = llm_goal_str['node_goals']
                # llm_edge_goal_str = llm_goal_str['edge_goals']
                # llm_goal_final = f'Node goals are: {llm_node_goal_str}. Edge goals are: {llm_edge_goal_str}.'
                object_in_scene, cur_change, target_change = (
                    motion_planner.get_nl_goal_string()
                )

                # print(f'{target_change=}')
                # change_in_init, change_in_target = motion_planner.get_current_goal_string()
                # print(f'{change_in_init=}\n{change_in_target=}')
                # prompt = open('/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/prompts/action_plan_prompt_few_shot.txt', 'r').read()
                # prompt = prompt.replace('<cur_state>', cur_state)
                # prompt = prompt.replace('<target_state>', target_state)
                # prompt = prompt.replace('<cur_change>', cur_change)
                # prompt = prompt.replace('<target_change>', target_change)

                # NL state change
                # prompt = open('/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/prompts/action_plan_prompt_nl.txt', 'r').read()
                # prompt = prompt.replace('<object_in_scene>', object_in_scene)
                # prompt = prompt.replace('<cur_change>', cur_change)
                # prompt = prompt.replace('<target_change>', target_change)

                gold_succ = validate_programs_based_on_goal_states(
                    motion_planner.final_state_dict,
                    node_goals,
                    edge_goals,
                    motion_planner.acting_char_id,
                )
                if not gold_succ:
                    tot_num -= 1
                    continue
                # if node_goals == llm_node_goals and edge_goals == llm_edge_goals:
                #     map_suc += 1
                #     print('LLM map succeed')

                # NL goals
                prompt = open(
                    "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/prompts/action_plan_prompt_goal_nl_json.txt",
                    "r",
                ).read()
                prompt = prompt.replace("<object_in_scene>", object_in_scene)
                prompt = prompt.replace("<cur_change>", cur_change)
                prompt = prompt.replace("<node_goals>", node_goal_str)
                prompt = prompt.replace("<edge_goals>", edge_goal_str)

                # LLM goals
                # print(f'{node_goal_str=}')
                # print(f'{edge_goal_str=}')
                # print(f'{object_in_scene=}')
                # print(f'{cur_change=}')
                # print(f'{llm_goal_final=}')
                # prompt = open('/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/prompts/action_plan_prompt_goal_llm_trans.txt', 'r').read()
                # prompt = prompt.replace('<object_in_scene>', object_in_scene)
                # prompt = prompt.replace('<cur_change>', cur_change)
                # prompt = prompt.replace('<goals>', llm_goal_final)

                # helm_prompt_l.append({"identifier": f"{script_id}", "llm_prompt": f"{prompt}", "reference": ""})

                # print(f'{object_in_scene=}')
                # print(f'{cur_change=}')
                # print(f'{node_goal_str=}')
                # print(f'{edge_goal_str=}')

                retry_cnt = 0
                feasible = 0
                retry_tot = 3
                while retry_cnt < retry_tot and not feasible:
                    print("gpt predicts...")
                    # , model='gpt-4-turbo-preview'
                    # action_prompt_words = len(prompt.split())
                    # print('action prompt words len', action_prompt_words)
                    actions = get_gpt_output(
                        message=prompt, json_object=True, temperature=1
                    )
                    # action_prompt_words_out = len(actions.split())
                    # print('action prompt words outlen', action_prompt_words_out)
                    # turn actions json string into dict
                    try:
                        actions = json.loads(actions)
                        actions = json_to_action(actions, relevant_name_to_id)
                        if isinstance(actions, str):
                            try:
                                actions = ast.literal_eval(actions)
                            except:
                                actions = actions.split("\n")
                    except:
                        retry_cnt += 1
                        print("Fail to generate the action sequence")
                        if retry_cnt < retry_tot:
                            print("Retry...")
                            continue
                        else:
                            break
                    # print(f'json actions: {actions}')
                    # print(f'{relevant_name_to_id=}')
                    # actions = gd_actions
                    # print(f'gold actions: {gd_actions}')
                    # print(f'predicted {actions=}')
                    if actions == gd_actions:
                        tot_succ += 1
                        tot_exec += 1
                        break
                    try:
                        # for action in actions:
                        #     motion_planner.execute_primitive_action(action)
                        motion_planner.reset()
                        flag = motion_planner.execute_sequence_primitive_action(actions)
                        tot_exec += 1
                        print("Executable!")
                        feasible = 1
                    # succ = int(motion_planner.execute_sequence_primitive_action(actions))
                    # succ = int(motion_planner.execute_sequence_primitive_action_relaxed(actions, relevant_id, character_id=65))
                    # motion_planner.reset()
                    except:
                        print("Fail to execute the action sequence")
                        retry_cnt += 1
                        if retry_cnt < retry_tot:
                            print("Retry...")
                            continue
                        else:
                            break
                # cur_state, target_state = motion_planner.filter_unique_subdicts(motion_planner.env_state.to_dict(), motion_planner.final_state_dict)
                # if not motion_planner.check_state_dict_same(cur_state, target_state):
                # print(f'{cur_state=}, {target_state=}')

                # succ = motion_planner.execute_sequence_primitive_action_score(actions, relevant_id, character_id=65)
                # succ = gold_succ
                if not feasible:
                    continue
                succ = validate_programs_based_on_goal_states(
                    motion_planner.env_state.to_dict(),
                    node_goals,
                    edge_goals,
                    motion_planner.acting_char_id,
                )
                action_str = " ".join(actions)
                act_succ = check_order_with_or(action_goals, action_str)
                if succ == 1 and act_succ == 1:
                    print("Pass goal test!")
                tot_succ += succ
            if tot_num >= num_tasks:
                break
        succ = tot_succ / tot_num if tot_num != 0 else 0
        exe_rate = tot_exec / tot_num if tot_num != 0 else 0
        map_rate = map_suc / tot_num if tot_num != 0 else 0
        print(
            f"For scene {scene}, {map_suc=}, {tot_succ=}, {tot_num=}, {tot_exec=}, {map_rate=}, {succ=}, {exe_rate=}"
        )

    return map_suc, tot_succ, tot_exec, tot_num, helm_prompt_l


def evaluate_subgoal_plan_succ(dataset, motion_planner: MotionPlanner):
    succ = 0
    for task in dataset:
        motion_planner.reset(task)
        state, goal = (
            motion_planner.get_current_state_string(),
            motion_planner.get_current_goal_string(),
        )
        subgoals = prompt_for_subgoal_sequence_plan(state, goal)
        succ += int(motion_planner.execute_subgoal_sequence(actions))
    return succ / len(dataset)






def operator_vis_main():
    model_name = "gpt-4o"
    save_root = f"/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/output/operator_eval_{model_name}"
    if not os.path.exists(save_root):
        os.makedirs(save_root)
    fig_root = os.path.join(save_root, "fig")
    if not os.path.exists(fig_root):
        os.makedirs(fig_root)
    task_score_dict_path = os.path.join(save_root, "task_score_dict.json")
    task_score_fig_path = os.path.join(fig_root, "task_score_dict.png")
    operator_score_dict_path = os.path.join(save_root, "operator_score_dict.json")
    operator_score_fig_path = os.path.join(fig_root, "operator_score_dict.png")
    precond_predicate_type_res_dict_path = os.path.join(
        save_root, "precond_predicate_type_res_dict.json"
    )
    precond_predicate_type_res_fig_path = os.path.join(
        fig_root, "precond_predicate_type_res_dict.png"
    )
    precond_predicate_res_dict_path = os.path.join(
        save_root, "precond_predicate_res_dict.json"
    )
    precond_predicate_res_fig_path = os.path.join(
        fig_root, "precond_predicate_res_dict.png"
    )
    effect_predicate_type_res_dict_path = os.path.join(
        save_root, "effect_predicate_type_res_dict.json"
    )
    effect_predicate_type_res_fig_path = os.path.join(
        fig_root, "effect_predicate_type_res_dict.png"
    )
    effect_predicate_res_dict_path = os.path.join(
        save_root, "effect_predicate_res_dict.json"
    )
    effect_predicate_res_fig_path = os.path.join(
        fig_root, "effect_predicate_res_dict.png"
    )
    full_predicate_type_res_dict_path = os.path.join(
        save_root, "full_predicate_type_res_dict.json"
    )
    full_predicate_type_res_fig_path = os.path.join(
        fig_root, "full_predicate_type_res_dict.png"
    )
    full_predicate_res_dict_path = os.path.join(
        save_root, "full_predicate_res_dict.json"
    )
    full_predicate_res_fig_path = os.path.join(fig_root, "full_predicate_res_dict.png")

    path_args = {
        "precond_predicate_type_res_dict_path": precond_predicate_type_res_dict_path,
        "precond_predicate_res_dict_path": precond_predicate_res_dict_path,
        "effect_predicate_type_res_dict_path": effect_predicate_type_res_dict_path,
        "effect_predicate_res_dict_path": effect_predicate_res_dict_path,
        "full_predicate_type_res_dict_path": full_predicate_type_res_dict_path,
        "full_predicate_res_dict_path": full_predicate_res_dict_path,
        "precond_predicate_type_res_fig_path": precond_predicate_type_res_fig_path,
        "precond_predicate_res_fig_path": precond_predicate_res_fig_path,
        "effect_predicate_type_res_fig_path": effect_predicate_type_res_fig_path,
        "effect_predicate_res_fig_path": effect_predicate_res_fig_path,
        "full_predicate_type_res_fig_path": full_predicate_type_res_fig_path,
        "full_predicate_res_fig_path": full_predicate_res_fig_path,
        "task_score_dict_path": task_score_dict_path,
        "operator_score_dict_path": operator_score_dict_path,
        "task_score_fig_path": task_score_fig_path,
        "operator_score_fig_path": operator_score_fig_path,
    }

    # visualization
    operator_visualization(**path_args)

def check_goal_interpretation(
    predicted_goals, node_goals, edge_goals, action_goals, relevant_name_to_id
):
    tot_node_goals = 0.0
    tot_edge_goals = 0.0
    tot_action_goals = 0.0
    succ_node_goals = 0.0
    succ_edge_goals = 0.0
    succ_action_goals = 0.0
    pd_node_goals = predicted_goals["node goals"]
    pd_edge_goals = predicted_goals["edge goals"]
    pd_action_goal_res = predicted_goals["action goals"]
    pd_action_goals = []
    for pd_action in pd_action_goal_res:
        if isinstance(pd_action, dict):
            pd_action_goals.append(pd_action["action"])
        elif isinstance(pd_action, str):
            pd_action_goals.append(pd_action)
    print(f"{pd_node_goals=}")
    print(f"{pd_edge_goals=}")
    print(f"{pd_action_goals=}")
    print(f"{node_goals=}")
    print(f"{edge_goals=}")
    print(f"{action_goals=}")
    # pd_node_goals = [eval(node_goal) for node_goal in pd_node_goals]
    # pd_edge_goals = [eval(edge_goal) for edge_goal in pd_edge_goals]
    for node_goal in node_goals:
        tot_node_goals += 1
        if node_goal in pd_node_goals:
            succ_node_goals += 1
    for edge_goal in edge_goals:
        tot_edge_goals += 1
        if edge_goal in pd_edge_goals:
            succ_edge_goals += 1
    for action_goal in action_goals:
        if "|" in action_goal:
            action_goal_list = action_goal.split("|")
        else:
            action_goal_list = [action_goal]
        tot_action_goals += 1
        for gd_action in action_goal_list:
            gd_action = gd_action.upper()
            if gd_action in pd_action_goals:
                succ_action_goals += 1
                break

    print(
        f"{succ_node_goals=}, {tot_node_goals=}, {succ_edge_goals=}, {tot_edge_goals=}, {succ_action_goals=}, {tot_action_goals=}"
    )
    return (
        succ_node_goals,
        tot_node_goals,
        succ_edge_goals,
        tot_edge_goals,
        succ_action_goals,
        tot_action_goals,
    )


def find_node_and_edge_in_scene(node_goals, edge_goals, relevant_nodes, motion_planner):
    # print(f'{edge_goals=}')
    for edge_goal in edge_goals:
        found = False
        if edge_goal["from_name"][0] == "?" and edge_goal["from_name"][-1] == "?":
            if edge_goal["from_name"] == "?character?":
                edge_goal["from_name"] = "character"
                continue
            # print(edge_goal['from_name'])
            if "|" in edge_goal["from_name"]:
                wildcard_list = edge_goal["from_name"].split("|")
            else:
                wildcard_list = [edge_goal["from_name"]]
            for wildcard in wildcard_list:
                target_properties = extract_properties(wildcard)
                # print(f'{target_properties=}')
                for node in relevant_nodes:
                    node_properties = motion_planner.properties_data.get(node, [])
                    node_properties = [str(prop) for prop in node_properties]
                    if all(prop in node_properties for prop in target_properties):
                        edge_goal["from_name"] = node
                        print(f"wildcard match: {wildcard} -> {node}")
                        found = True
                        break
                if found:
                    break
            if not found:
                print("No relevant node found for edge from_name goal!")
        found = False
        if edge_goal["to_name"][0] == "?" and edge_goal["to_name"][-1] == "?":
            if edge_goal["to_name"] == "?character?":
                edge_goal["to_name"] = "character"
                continue
            # print(edge_goal['to_name'])
            if "|" in edge_goal["to_name"]:
                wildcard_list = edge_goal["to_name"].split("|")
            else:
                wildcard_list = [edge_goal["to_name"]]
            for wildcard in wildcard_list:
                target_properties = extract_properties(wildcard)
                # print(f'{target_properties=}')
                for node in relevant_nodes:
                    node_properties = motion_planner.properties_data.get(node, [])
                    node_properties = [str(prop) for prop in node_properties]
                    if all(prop in node_properties for prop in target_properties):
                        edge_goal["to_name"] = node
                        print(f"wildcard match: {wildcard} -> {node}")
                        found = True
                        break
                if found:
                    break
            if not found:
                print("No relevant node found for edge from_name goal!")
    node_goals_select = []
    # print(f'{node_goals=}')
    for node_goal in node_goals:
        if "|" not in node_goal:
            node_goal = ast.literal_eval(node_goal)
            node_goals_select.append(node_goal)
            continue
        for node in relevant_nodes:
            if node in node_goal:
                selected_dict = find_target_dict(node_goal, node)
                node_goals_select.append(selected_dict)
                break
    node_goals = node_goals_select
    return node_goals, edge_goals

def main_exp():
    print("Example 4")
    print("---------")

    # load object alias, states, and placing
    properties_data = utils.load_properties_data()
    object_states = utils.load_object_states()
    object_placing = utils.load_object_placing()
    name_equivalence = utils.load_name_equivalence()
    # init graph
    init_scene_graph = utils.load_graph("../example_graphs/TestScene6_graph.json")
    # Task action sequence
    script = read_script("example_scripts/example_script_3.txt")
    # final state (ground truth)
    final_state_path = "/viscam/u/shiyuz/virtualhome/virtualhome/example_graphs/TestScene6_graph_script3_res.json"
    with open(final_state_path, "r") as f:
        final_state_dict = json.load(f)

    planner = MotionPlanner(
        init_scene_graph,
        final_state_dict,
        name_equivalence,
        properties_data,
        object_placing,
    )

    # func1 and func2 (reset, get_current_state_string)
    planner.reset()
    # print(planner.get_current_state_string())
    # func3 (get_current_goal_string)
    change_in_init, change_in_target = planner.get_current_goal_string()

    # test of (execute_primitive_action_script)
    planner.reset()
    before_state = planner.get_current_state()
    planner.execute_primitive_action_script(script)
    after_state = planner.get_current_state()
    print("finish test 4 on func execute_primitive_action_script()")

    out_file = "../example_graphs/TestScene6_graph_script3_planner.txt"
    planner.show_status_change_direct(
        before_state, after_state, init_scene_graph, out_file
    )

    # test of func4 and 5 (execute_primitive_action, execute_sequence_primitive_action)
    # test of execution commands sequence
    planner.reset()
    actions = ["[Walk] <fridge> (234) ", "[Open] <fridge> (234)"]
    before_state = planner.get_current_state()
    suc = planner.execute_sequence_primitive_action(actions)
    after_state = planner.get_current_state()

    print(f"execute success: {suc}")

    out_file = "../example_graphs/TestScene6_graph_script3_planner_seq.txt"
    planner.show_status_change_direct(
        before_state, after_state, init_scene_graph, out_file
    )
    print(
        "finish test 5 on func execute_primitive_action() and execute_sequence_primitive_action()"
    )

    # test of func6 (incremental_subgoal_plan)
    planner.reset()
    subgoals = ["#CLOSE# <fridge> (234) <char162> (162)", "<fridge> (234): {OPEN}"]
    suc = planner.incremental_subgoal_plan(subgoals, 2)
    print(f"incremental subgoal plan success: {suc}")
    print("finish test 6 on func incremental_subgoal_plan()")

    # test of func7 (execute_subgoal_sequence)
    planner.reset()
    subgoals = [["#CLOSE# <fridge> (234) <char162> (162)"], ["<fridge> (234): {OPEN}"]]
    suc = planner.execute_subgoal_sequence(subgoals, 1)
    print(f"execute subgoal sequence success: {suc}")
    print("finish test 7 on func execute_subgoal_sequence()")


def action_eval():
    print("enter action eval!!", flush=True)
    data_dir = "/viscam/u/shiyuz/virtualhome/virtualhome/dataset/programs_processed_precond_nograb_morepreconds"

    task_dict_dir = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/resources/task_state_updated.json"
    task_dict = json.load(open(task_dict_dir, "r"))
    scene_1_dict = task_dict["scene_1"]

    all_num = 0.0

    all_valid_correct = 0
    all_format_correct = 0
    all_no_hallucination = 0
    all_executable_plan = 0
    all_actions_correct = 0
    all_correct_plan = 0

    all_wrong_order_num = 0
    all_missing_step_num = 0
    all_affordance_num = 0
    all_unseen_num = 0
    all_additional_step_num = 0
    all_other_num = 0

    all_node_success_rate_list = []
    all_edge_success_rate_list = []
    all_action_success_rate_list = []
    all_full_success_rate_list = []

    result_dict = {}
    save_case = True
    output_dir = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/output"
    case_path = os.path.join(output_dir, f"error_case.txt")
    helm_prompt_path = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/prompts/helm_prompt/action_evaluation_vh.json"

    helm_prompt_list = []
    if save_case:
        with open(case_path, "w") as f:
            f.write("Start case analysis!\n")
    for task_name, task_details in scene_1_dict.items():
        print(f"CURRENT TASK IS {task_name}!", flush=True)
        # if task_name not in ["Cook some food"]:
        #     continue
        task_total_number = 0

        task_valid_correct = 0
        task_format_correct = 0
        task_no_hallucination = 0
        task_executable_plan = 0
        task_actions_correct = 0
        task_correct_plan = 0

        task_wrong_order_num = 0
        task_missing_step_num = 0
        task_affordance_num = 0
        task_unseen_num = 0
        task_additional_step_num = 0
        task_other_num = 0

        task_node_success_rate_list = []
        task_edge_success_rate_list = []
        task_action_success_rate_list = []
        task_full_success_rate_list = []

        t_ids = task_details["task_file_list_with_ans"]
        # goal_id_to_task = group_by_value(t_ids)
        goal_id_to_task = group_by_index(t_ids)
        for goal_id, task_id_list in goal_id_to_task.items():
            goal_id = int(goal_id)
            goals = task_details["goal_candidates"][goal_id]
            node_goals = list(goals["selected_node_state"].keys())
            edge_goals = list(goals["selected_edge_state"].keys()) + list(
                goals["accurate_edge_state"].keys()
            )
            edge_goals = [eval(edge_goal) for edge_goal in edge_goals]
            action_goals = goals["actions"]
            print(f"{node_goals=}", flush=True)
            print(f"{edge_goals=}", flush=True)
            (
                tot_num,
                group_valid_correct,
                group_format_correct,
                group_no_hallucination,
                group_executable_plan,
                group_actions_correct,
                group_correct_plan,
                group_wrong_order_num,
                group_missing_step_num,
                group_affordance_num,
                group_unseen_num,
                group_additional_step_num,
                group_other_num,
                group_node_success_rate_list,
                group_edge_success_rate_list,
                group_action_success_rate_list,
                group_full_success_rate_list,
                helm_prompt_l,
            ) = evaluate_action_sequence(
                data_dir,
                task_id_list,
                node_goals,
                edge_goals,
                action_goals,
                num_tasks=10,
            )
            helm_prompt_list += helm_prompt_l
            # print(f'For task {task_name}, {tot_succ=}, {tot_num=}, {tot_exec=}')
            # result_dict[task_name] = [tot_exec, tot_succ, tot_num]
            # all_map += tot_map
            task_total_number += tot_num

            task_valid_correct += group_valid_correct
            task_format_correct += group_format_correct
            task_no_hallucination += group_no_hallucination
            task_executable_plan += group_executable_plan
            task_actions_correct += group_actions_correct
            task_correct_plan += group_correct_plan

            task_wrong_order_num += group_wrong_order_num
            task_missing_step_num += group_missing_step_num
            task_affordance_num += group_affordance_num
            task_unseen_num += group_unseen_num
            task_additional_step_num += group_additional_step_num
            task_other_num += group_other_num

            task_node_success_rate_list += group_node_success_rate_list
            task_edge_success_rate_list += group_edge_success_rate_list
            task_action_success_rate_list += group_action_success_rate_list
            task_full_success_rate_list += group_full_success_rate_list

        # drop all -1 value
        print(f"total task number: {task_total_number}")
        task_node_success_rate_list = [
            rate for rate in task_node_success_rate_list if rate != -1
        ]
        task_edge_success_rate_list = [
            rate for rate in task_edge_success_rate_list if rate != -1
        ]
        task_action_success_rate_list = [
            rate for rate in task_action_success_rate_list if rate != -1
        ]
        task_full_success_rate_list = [
            rate for rate in task_full_success_rate_list if rate != -1
        ]

        all_node_success_rate_list += copy.deepcopy(task_node_success_rate_list)
        all_edge_success_rate_list += copy.deepcopy(task_edge_success_rate_list)
        all_action_success_rate_list += copy.deepcopy(task_action_success_rate_list)
        all_full_success_rate_list += copy.deepcopy(task_full_success_rate_list)

        # if empy, set to -1
        if len(task_node_success_rate_list) == 0:
            task_node_success_rate_list = [-1]
        if len(task_edge_success_rate_list) == 0:
            task_edge_success_rate_list = [-1]
        if len(task_action_success_rate_list) == 0:
            task_action_success_rate_list = [-1]

        # calculate the average success rate
        task_node_success_rate = np.mean(task_node_success_rate_list)
        task_edge_success_rate = np.mean(task_edge_success_rate_list)
        task_action_success_rate = np.mean(task_action_success_rate_list)
        task_full_success_rate = np.mean(task_full_success_rate_list)

        result_dict[task_name] = [
            task_total_number,
            task_valid_correct,
            task_format_correct,
            task_no_hallucination,
            task_executable_plan,
            task_actions_correct,
            task_correct_plan,
            task_wrong_order_num,
            task_missing_step_num,
            task_affordance_num,
            task_unseen_num,
            task_additional_step_num,
            task_other_num,
            task_node_success_rate,
            task_edge_success_rate,
            task_action_success_rate,
            task_full_success_rate,
        ]

        # print('result_dict[task_name] = [task_total_number, task_valid_correct, task_format_correct, task_no_hallucination, task_executable_plan, task_actions_correct, task_correct_plan, task_wrong_order_num, task_missing_step_num, task_affordance_num, task_unseen_num, task_additional_step_num, task_other_num, task_node_score_list, task_edge_score_list, task_full_score_list]')

        # print(f'{result_dict=}', flush=True)

        # print(f'For task {task_name}, total number: {task_total_number}')
        # print(f'For task {task_name}, valid correct number: {task_valid_correct}')
        # print(f'For task {task_name}, format correct number: {task_format_correct}')
        # print(f'For task {task_name}, no hallucination number: {task_no_hallucination}')
        # print(f'For task {task_name}, executable plan number: {task_executable_plan}')
        # print(f'For task {task_name}, actions correct number: {task_actions_correct}')
        # print(f'For task {task_name}, correct plan number: {task_correct_plan}')
        # print(f'For task {task_name}, wrong order number: {task_wrong_order_num}')
        # print(f'For task {task_name}, missing step number: {task_missing_step_num}')
        # print(f'For task {task_name}, affordance number: {task_affordance_num}')
        # print(f'For task {task_name}, unseen number: {task_unseen_num}')
        # print(f'For task {task_name}, additional step number: {task_additional_step_num}')
        # print(f'For task {task_name}, other number: {task_other_num}')

        # print(f'For task {task_name}, node precision/recall/f1 score is {task_node_score_list}')
        # print(f'For task {task_name}, edge precision/recall/f1 score is {task_edge_score_list}')
        # print(f'For task {task_name}, full precision/recall/f1 score is {task_full_score_list}')

        all_num += task_total_number

        all_valid_correct += task_valid_correct
        all_format_correct += task_format_correct
        all_no_hallucination += task_no_hallucination
        all_executable_plan += task_executable_plan
        all_actions_correct += task_actions_correct
        all_correct_plan += task_correct_plan

        all_wrong_order_num += task_wrong_order_num
        all_missing_step_num += task_missing_step_num
        all_affordance_num += task_affordance_num
        all_unseen_num += task_unseen_num
        all_additional_step_num += task_additional_step_num
        all_other_num += task_other_num

    # calculate the average precision/recall/f1 score for all tasks
    all_node_success_rate_list = [
        rate for rate in all_node_success_rate_list if rate != -1
    ]
    all_edge_success_rate_list = [
        rate for rate in all_edge_success_rate_list if rate != -1
    ]
    all_action_success_rate_list = [
        rate for rate in all_action_success_rate_list if rate != -1
    ]
    all_full_success_rate_list = [
        rate for rate in all_full_success_rate_list if rate != -1
    ]

    # calculate the avg score
    if len(all_node_success_rate_list) == 0:
        all_node_success_rate_list = [-1]
    if len(all_edge_success_rate_list) == 0:
        all_edge_success_rate_list = [-1]
    if len(all_action_success_rate_list) == 0:
        all_action_success_rate_list = [-1]

    all_node_success_rate = np.mean(all_node_success_rate_list)
    all_edge_success_rate = np.mean(all_edge_success_rate_list)
    all_action_success_rate = np.mean(all_action_success_rate_list)
    all_full_success_rate = np.mean(all_full_success_rate_list)

    result_dict["all"] = [
        all_num,
        all_valid_correct,
        all_format_correct,
        all_no_hallucination,
        all_executable_plan,
        all_actions_correct,
        all_correct_plan,
        all_wrong_order_num,
        all_missing_step_num,
        all_affordance_num,
        all_unseen_num,
        all_additional_step_num,
        all_other_num,
        all_node_success_rate,
        all_edge_success_rate,
        all_action_success_rate,
        all_full_success_rate,
    ]

    print(
        "result_dict[task_name] = [task_total_number, task_valid_correct, task_format_correct, task_no_hallucination, task_executable_plan, task_actions_correct, task_correct_plan, task_wrong_order_num, task_missing_step_num, task_affordance_num, task_unseen_num, task_additional_step_num, task_other_num, task_node_score_list, task_edge_score_list, task_full_score_list]"
    )
    print(f"{result_dict=}", flush=True)

    print(f"For all tasks, total number: {all_num}")
    print(f"For all tasks, valid correct number: {all_valid_correct}")
    print(f"For all tasks, format correct number: {all_format_correct}")
    print(f"For all tasks, no hallucination number: {all_no_hallucination}")
    print(f"For all tasks, executable plan number: {all_executable_plan}")
    print(f"For all tasks, actions correct number: {all_actions_correct}")
    print(f"For all tasks, correct plan number: {all_correct_plan}")
    print(f"For all tasks, wrong order number: {all_wrong_order_num}")
    print(f"For all tasks, missing step number: {all_missing_step_num}")
    print(f"For all tasks, affordance number: {all_affordance_num}")
    print(f"For all tasks, unseen number: {all_unseen_num}")
    print(f"For all tasks, additional step number: {all_additional_step_num}")
    print(f"For all tasks, other number: {all_other_num}")

    print(f"For all tasks, node success rate is {all_node_success_rate}")
    print(f"For all tasks, edge success rate is {all_edge_success_rate}")
    print(f"For all tasks, action success rate is {all_action_success_rate}")
    print(f"For all tasks, full success rate is {all_full_success_rate}")

    # save helm_prompt
    # json.dump(helm_prompt_list, open(helm_prompt_path, 'w'), indent=4)


def goal_eval():
    data_dir = "/viscam/u/shiyuz/virtualhome/virtualhome/dataset/programs_processed_precond_nograb_morepreconds"

    task_dict_dir = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/resources/task_state_updated.json"
    task_dict = json.load(open(task_dict_dir, "r"))
    scene_1_dict = task_dict["scene_1"]
    all_nodes = 0.0
    all_rep_nodes = 0.0
    all_edge = 0.0
    all_rep_edges = 0.0
    all_actions = 0.0
    all_succ_nodes = 0.0
    all_succ_edges = 0.0
    all_succ_actions = 0.0
    all_succ = 0.0
    all_num = 0.0
    result_dict = {}
    save_case = True
    fail_task = []
    output_dir = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/output"
    case_path = os.path.join(output_dir, "error_case.txt")
    if save_case:
        with open(case_path, "w") as f:
            f.write("Start case analysis!\n")
    helm_prompt_path = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/prompts/helm_prompt/goal_interpretation_vh.json"

    node_dict = {}
    edge_dict = {}
    action_dict = {}
    relation_object_paris = {}
    plug_analysis = [0, 0, 0, 0]
    rel_obj_path = os.path.join(output_dir, "relation_object_pairs.json")
    if os.path.exists(rel_obj_path):
        relation_object_paris = json.load(open(rel_obj_path, "r"))
    task_rep_dict = {}
    helm_prompt_list = []

    for task_name, task_details in scene_1_dict.items():
        print(f"CURRENT TASK IS {task_name}!")
        # if task_name != 'Watch TV':
        #     continue
        # if not os.path.exists(case_path):
        #     os.mkdir(case_path)
        t_ids = task_details["task_file_list_with_ans"]
        goal_id_to_task = group_by_index(t_ids)
        for goal_id, task_id_list in goal_id_to_task.items():
            goal_id = int(goal_id)
            goals = task_details["goal_candidates"][goal_id]
            node_goals = list(goals["selected_node_state"].keys())
            edge_goals = list(goals["selected_edge_state"].keys()) + list(
                goals["accurate_edge_state"].keys()
            )
            edge_goals = [eval(edge_goal) for edge_goal in edge_goals]
            action_goals = goals["actions"]
            print(f"Before check {node_goals=}")
            print(f"Before check {edge_goals=}")
            # try:
            (
                succ_nodes,
                tot_nodes,
                succ_edges,
                tot_edges,
                succ_actions,
                tot_actions,
                tot_succ,
                tot_num,
                node_dict,
                edge_dict,
                action_dict,
                plug_analysis,
                relation_object_paris,
                rep_goals_pair,
                helm_prompt_l,
            ) = evaluate_goal_interpretation_plan_succ(
                data_dir,
                task_id_list,
                node_goals,
                edge_goals,
                action_goals,
                num_tasks=10,
                case_path=case_path,
                save_case=save_case,
                node_dict=node_dict,
                edge_dict=edge_dict,
                action_dict=action_dict,
                plug_analysis=plug_analysis,
                relation_object_paris=relation_object_paris,
            )
            helm_prompt_list += helm_prompt_l
            # except:
            #     fail_task.append((task_name, task_id_list))
            #     continue
            print(
                f"For task {task_name}, {succ_nodes=}, {tot_nodes=}, {succ_edges=}, {tot_edges=}, {rep_goals_pair=} , {succ_actions=}, {tot_actions=} {tot_succ=}, {tot_num=}"
            )
            all_succ_nodes += succ_nodes + rep_goals_pair[0]
            all_nodes += tot_nodes
            all_rep_nodes += rep_goals_pair[0]
            all_succ_edges += succ_edges + rep_goals_pair[1]
            all_edge += tot_edges
            all_rep_edges += rep_goals_pair[1]
            all_succ_actions += succ_actions
            all_actions += tot_actions
            all_succ += tot_succ
            all_num += tot_num
            result_dict[task_name] = [
                succ_nodes,
                all_rep_nodes,
                tot_nodes,
                succ_edges,
                all_rep_edges,
                tot_edges,
                succ_actions,
                tot_actions,
                tot_succ,
                tot_num,
            ]
    # error analysis
    if save_case:
        for k, v in node_dict.items():
            node_dict[k] = [v[0], v[1], float(v[0] / v[1])]
        for k, v in edge_dict.items():
            edge_dict[k] = [v[0], v[1], float(v[0] / v[1])]
        for k, v in action_dict.items():
            action_dict[k] = [v[0], v[1], float(v[0] / v[1])]
        json.dump(node_dict, open(os.path.join(output_dir, "node_dict.json"), "w"))
        json.dump(edge_dict, open(os.path.join(output_dir, "edge_dict.json"), "w"))
        json.dump(action_dict, open(os.path.join(output_dir, "action_dict.json"), "w"))
    for k, v in relation_object_paris.items():
        relation_object_paris[k] = list(v)
    if not os.path.exists(rel_obj_path):
        json.dump(relation_object_paris, open(rel_obj_path, "w"))
    print(
        f"For all task, {all_succ_nodes=}, {all_nodes=}, {all_succ_nodes/all_nodes=}, {all_succ_edges=}, {all_edge=}, {all_succ_edges/all_edge=}, {all_succ_actions=}, {all_actions=}, {all_succ_actions/all_actions=} {all_succ=}, {all_num=}, {all_succ/all_num=}"
    )
    print(f"{result_dict}")
    print(f"{plug_analysis=}")
    print(f"{fail_task=}")

    # save helm_prompt_list
    json.dump(helm_prompt_list, open(helm_prompt_path, "w"), indent=4)


def operator_parser():
    gold_domain_path = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/resources/pddl_files/virtualhome.pddl"
    pddl_operator_dict = extract_action_details(domain_file_path=gold_domain_path)
    print(f"{pddl_operator_dict=}")
    pddl_operator_path = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/resources/pddl_files/gold_action.json"
    # save
    with open(pddl_operator_path, "w") as f:
        json.dump(pddl_operator_dict, f, indent=4)


def main_dataset(
    data_dir="/viscam/u/shiyuz/virtualhome/virtualhome/dataset/programs_processed_precond_nograb_morepreconds",
):
    scene_id = [1, 2, 3, 4, 5, 6, 7]
    program_dir = os.path.join(data_dir, "executable_programs")

    tot_num = 0.0
    tot_succ = 0.0
    pattern = r"file(\d+)_(\d+)\.txt"
    for scene in scene_id:
        grouping_dict = {}
        grouping_path = os.path.join(
            program_dir,
            f"TrimmedTestScene{scene}_graph",
            "results_intentions_march-13-18",
            "task_type.json",
        )
        scene_dir = os.path.join(
            program_dir,
            f"TrimmedTestScene{scene}_graph",
            "results_intentions_march-13-18",
        )
        task_name_dict = {}
        for file in os.listdir(scene_dir):
            if file.endswith(".txt"):
                # read file and get first row
                match = re.search(pattern, file)
                if match:
                    # Extracting the ids
                    id1, id2 = match.groups()
                else:
                    print("No match found")
                    continue
                file_id = f"{id1}_{id2}"
                with open(os.path.join(scene_dir, file), "r") as f:
                    first_row = f.readline()
                    first_row = first_row.strip("\n").strip(" ").strip("\n")
                    if first_row not in task_name_dict.keys():
                        task_name_dict[first_row] = 1
                        grouping_dict[first_row] = [file_id]
                    else:
                        task_name_dict[first_row] += 1
                        grouping_dict[first_row].append(file_id)
        task_dict = dict(sorted(task_name_dict.items(), key=lambda item: item[1]))
        json.dump(grouping_dict, open(grouping_path, "w"))

        print(f"scene graph {scene}: {grouping_dict=}")
        print(f"scene graph {scene}: {task_dict=}")



def get_effect_free_actions() -> list:
    actions = [
        "Drink",
        "Touch",
        "Look At",
        "Look At short",
        "Look At Long",
        "Eat",
        "watch",
        "greet",
        "read",
        "Type",
        "push",
        "pull",
        "move",
        "squeeze",
        "cut",
        "sleep",
        "wakeup",
        "run",
        "wipe",
        "puton",
        "putoff",
        "pour",
        "wash",
        "rinse",
        "scrub",
    ]
    actions = [action.lower().replace(" ", "") for action in actions]
    return actions


def get_related_ids(file_path, character_id=65):
    with open(file_path, "r") as f:
        lines = f.readlines()
        program = "".join([line for line in lines if line[0] == "["])

    # match ids with the format like '(x.xxx)'
    id_pattern = r"\(\d+\.\d+\)"
    related_ids = re.findall(id_pattern, program)

    # now, for each matched id, we only keep the 'xxx' part of '(x.xxx)'
    related_ids = set(((id.strip("(").strip(")")).split("."))[1] for id in related_ids)
    related_ids = [int(id) for id in related_ids]
    related_ids.append(character_id)
    return related_ids

def analysis_script_actions(dataset_root_path, task_name="Wash clothes", scene_id=1):
    """
    This function is used to analyze the actions in the script
    """
    assert dataset_root_path is not None, "Please provide the dataset root path."
    # first, we need to identify what graph and what type of task we are dealing with
    # for convenience, we first address the scene one and the first task type
    dataset_meta_info_path = os.path.join(
        dataset_root_path,
        "executable_programs",
        f"TrimmedTestScene{scene_id}_graph",
        "results_intentions_march-13-18",
    )
    graph_state_path = os.path.join(
        dataset_root_path,
        "init_and_final_graphs",
        f"TrimmedTestScene{scene_id}_graph",
        "results_intentions_march-13-18",
    )
    assert os.path.exists(
        dataset_meta_info_path
    ), "The dataset meta info path does not exist."
    assert os.path.exists(graph_state_path), "The graph state path does not exist."
    meta_info_file_path = os.path.join(dataset_meta_info_path, "task_type.json")

    # read dictionary from task_type.json
    task_type_dict = json.load(open(meta_info_file_path, "r"))
    # handle the task 'Wash clothes' first
    task_file_list = task_type_dict[task_name]

    # constant values for the planner
    properties_data = utils.load_properties_data()
    object_placing = utils.load_object_placing()
    name_equivalence = utils.load_name_equivalence()
    effect_free_actions = get_effect_free_actions()
    effect_free_actions_dict = {key: 0 for key in effect_free_actions}
    # read graph states based on file id in task_file_list
    for file_id in task_file_list:
        state_file_path = os.path.join(graph_state_path, f"file{file_id}.json")
        state_dict = json.load(open(state_file_path, "r"))
        final_state_dict = state_dict["final_graph"]
        final_scene_graph = EnvironmentGraph(final_state_dict)
        planner = MotionPlanner(
            final_scene_graph,
            final_state_dict,
            name_equivalence,
            properties_data,
            object_placing,
        )
        id_2_name_dict = planner.id_to_name
        actions = extract_actions(
            state_file_path.replace(
                "init_and_final_graphs", "executable_programs"
            ).replace("json", "txt")
        )
        actions, relevant_id = reformat_actions(actions)
        print(actions)
        # for each action, use regex to filter out format like this "[...]"
        rule = r"\[.*?\]"
        actions = [re.findall(rule, action) for action in actions]
        actions = [
            action[0].lower().replace(" ", "") for action in actions if len(action) > 0
        ]
        # convert set to list
        actions = [action for action in actions if action[1:-1] in effect_free_actions]
        for action in actions:
            a = action[1:-1]
            effect_free_actions_dict[a] += 1

        # print(f'========file_id {file_id} ==========')
        # print(actions)
    # sort the dict
    effect_free_actions_dict = dict(
        sorted(effect_free_actions_dict.items(), key=lambda item: item[1], reverse=True)
    )
    print(effect_free_actions_dict)


def analysis_graph_difference(
    dataset_root_path,
    task_state_file_path,
    task_name="Wash clothes",
    scene_id=1,
    validation_mode=True,
):
    """
    This function is used to decide whether obtaining subgoals through intersection among tasks in the same type is a good choice.
    Though, I do have a lot of concerns before I start to write this code:
    1. some intermediate changes can be hidden, eg, write a paper with a pencil
    2. the intersection can be quite noisy, and may not fully represent the true intension over this task type
    """
    assert dataset_root_path is not None, "Please provide the dataset root path."
    # first, we need to identify what graph and what type of task we are dealing with
    # for convenience, we first address the scene one and the first task type
    dataset_meta_info_path = os.path.join(
        dataset_root_path,
        "executable_programs",
        f"TrimmedTestScene{scene_id}_graph",
        "results_intentions_march-13-18",
    )
    graph_state_path = os.path.join(
        dataset_root_path,
        "init_and_final_graphs",
        f"TrimmedTestScene{scene_id}_graph",
        "results_intentions_march-13-18",
    )
    assert os.path.exists(
        dataset_meta_info_path
    ), "The dataset meta info path does not exist."
    assert os.path.exists(graph_state_path), "The graph state path does not exist."
    meta_info_file_path = os.path.join(dataset_meta_info_path, "task_type.json")

    # read dictionary from task_type.json
    task_type_dict = json.load(open(meta_info_file_path, "r"))
    # handle the task 'Wash clothes' first
    task_file_list = task_type_dict[task_name]

    # constant values for the planner
    properties_data = utils.load_properties_data()
    object_placing = utils.load_object_placing()
    name_equivalence = utils.load_name_equivalence()

    # read graph states based on file id in task_file_list
    node_states_list = {}
    edge_appearance_list = {}
    for file_id in tqdm.tqdm(task_file_list, total=len(task_file_list)):
        state_file_path = os.path.join(graph_state_path, f"file{file_id}.json")
        state_dict = json.load(open(state_file_path, "r"))
        init_state_dict, final_state_dict = (
            state_dict["init_graph"],
            state_dict["final_graph"],
        )

        init_scene_graph = EnvironmentGraph(init_state_dict)
        planner = MotionPlanner(
            init_scene_graph,
            final_state_dict,
            name_equivalence,
            properties_data,
            object_placing,
        )
        id_2_name_dict = planner.id_to_name

        # diff_init_dict, diff_final_dict = MotionPlanner.filter_unique_subdicts(init_state_dict, final_state_dict)
        diff_init_dict, diff_final_dict = MotionPlanner.filter_unique_subdicts(
            init_state_dict, final_state_dict
        )
        node_changes, edge_changes = MotionPlanner.get_node_edge_changes(
            diff_init_dict, diff_final_dict
        )
        # print(f"node changes: {node_changes}")
        edge_changes = ignore_CLOSE(
            edge_changes
        )  # CLOSE relation proves to be irrelevant
        # print(f"edge_changes: {edge_changes}")

        # ------------------------
        # insert object stats here
        # ------------------------

        #  now we get the node and edge stats of the graph state difference
        for key, values in node_changes.items():
            if key == "remove":
                continue
            for value in values:
                if key == "add":
                    id, name = value["id"], value["class_name"]
                    states = value["states"]
                elif key == "modify":
                    id, name = value[1]["id"], value[1]["class_name"]
                    states = value[1]["states"]
                for state in states:
                    tmp = {}
                    tmp["name"] = name
                    tmp["state"] = state
                    tmp = str(tmp)
                    if tmp not in node_states_list:
                        node_states_list[tmp] = [(file_id, id)]
                    else:
                        node_states_list[tmp].append((file_id, id))

        for key, values in edge_changes.items():
            if key == "remove":
                continue
            for value in values:
                if key == "add":
                    from_id, relation, to_id = (
                        value["from_id"],
                        value["relation_type"],
                        value["to_id"],
                    )
                elif key == "modify":
                    from_id, relation, to_id = (
                        value[1]["from_id"],
                        value[1]["relation_type"],
                        value[1]["to_id"],
                    )
                from_name, to_name = id_2_name_dict[from_id], id_2_name_dict[to_id]
                tmp = {}
                tmp["from_name"] = from_name
                tmp["relation"] = relation
                tmp["to_name"] = to_name
                tmp = str(tmp)
                # if 'office' in tmp.lower() or 'room' in tmp.lower():
                #     continue
                if tmp not in edge_appearance_list:
                    edge_appearance_list[tmp] = [(file_id, from_id, to_id)]
                else:
                    edge_appearance_list[tmp].append((file_id, from_id, to_id))
    node_stats = {}
    edge_stats = {}

    for key, values in node_states_list.items():
        node_stats[key] = len(values)

    for key, values in edge_appearance_list.items():
        edge_stats[key] = len(values)

    # diff programs share diff specific goals, therefore, we need to specify the wildcard
    edge_wildcard_stats = {}
    for key, value in edge_stats.items():
        key_dict = eval(key)
        from_name, relation, to_name = (
            key_dict["from_name"],
            key_dict["relation"],
            key_dict["to_name"],
        )

        get_from_properties = (
            properties_data[from_name] if from_name in properties_data else []
        )
        get_to_properties = (
            properties_data[to_name] if to_name in properties_data else []
        )
        get_from_properties = sorted(get_from_properties, key=lambda prop: prop.value)
        get_to_properties = sorted(get_to_properties, key=lambda prop: prop.value)

        search_to_name = copy.deepcopy(key_dict)
        search_to_name["to_name"] = (
            f"?{str(get_to_properties)}?" if to_name != "character" else f"?character?"
        )
        search_from_name = copy.deepcopy(key_dict)
        search_from_name["from_name"] = (
            f"?{str(get_from_properties)}?"
            if from_name != "character"
            else f"?character?"
        )
        enabled_search_to, enabled_search_from = False, False

        if str(search_to_name) not in edge_wildcard_stats:
            edge_wildcard_stats[str(search_to_name)] = [{}, 0]
            enabled_search_to = True
        if str(search_from_name) not in edge_wildcard_stats:
            edge_wildcard_stats[str(search_from_name)] = [{}, 0]
            enabled_search_from = True

        if enabled_search_to or enabled_search_from:
            for key_1, value_1 in edge_stats.items():
                key_1_dict = eval(key_1)
                # get all info from edge_stats
                from_name, relation, to_name = (
                    key_1_dict["from_name"],
                    key_1_dict["relation"],
                    key_1_dict["to_name"],
                )

                if enabled_search_to:
                    get_to_properties_1 = (
                        properties_data[to_name] if to_name in properties_data else []
                    )
                    get_to_properties_1 = sorted(
                        get_to_properties_1, key=lambda prop: prop.value
                    )
                    validation_to_name = (
                        f"?{str(get_to_properties_1)}?"
                        if to_name != "character"
                        else f"?character?"
                    )
                    if (
                        from_name == key_dict["from_name"]
                        and relation == key_dict["relation"]
                        and validation_to_name == search_to_name["to_name"]
                    ):
                        edge_wildcard_stats[str(search_to_name)][0][to_name] = (
                            value_1
                            if to_name
                            not in edge_wildcard_stats[str(search_to_name)][0]
                            else edge_wildcard_stats[str(search_to_name)][0][to_name]
                            + value_1
                        )
                        edge_wildcard_stats[str(search_to_name)][1] += value_1

                if enabled_search_from:
                    get_from_properties_1 = (
                        properties_data[from_name]
                        if from_name in properties_data
                        else []
                    )
                    get_from_properties_1 = sorted(
                        get_from_properties_1, key=lambda prop: prop.value
                    )
                    validation_from_name = (
                        f"?{str(get_from_properties_1)}?"
                        if from_name != "character"
                        else f"?character?"
                    )
                    if (
                        to_name == key_dict["to_name"]
                        and relation == key_dict["relation"]
                        and validation_from_name == search_from_name["from_name"]
                    ):
                        edge_wildcard_stats[str(search_from_name)][0][from_name] = (
                            value_1
                            if from_name
                            not in edge_wildcard_stats[str(search_from_name)][0]
                            else edge_wildcard_stats[str(search_from_name)][0][
                                from_name
                            ]
                            + value_1
                        )
                        edge_wildcard_stats[str(search_from_name)][1] += value_1

    # sort stats
    node_stats = dict(
        sorted(node_stats.items(), key=lambda item: item[1], reverse=True)
    )
    edge_wildcard_stats = dict(
        sorted(edge_wildcard_stats.items(), key=lambda item: item[1][1], reverse=True)
    )

    node_len = 0
    edge_len = 0
    print(f"====Node Stats====")
    for key, value in node_stats.items():
        node_len += value
        print(f"[{key}]: {value}")
    print(f"====Edge Wildcard Stats====")
    for key, value in edge_wildcard_stats.items():
        edge_len += value[1]
        print(f"[{key}]: {value}")

    # select_graph_states(node_stats, edge_wildcard_stats, task_name, graph_state_path, task_file_list, task_state_file_path, scene_id)
    select_graph_states_V2(
        node_stats,
        edge_stats,
        edge_wildcard_stats,
        task_name,
        graph_state_path,
        task_file_list,
        task_state_file_path,
        scene_id,
    )


if __name__ == "__main__":
    # main_exp()
    # goal_eval()
    # action_eval()
    # tm_input_preparation()
    # llm_prediction()
    evaluate_operator_succ()
    # task_categorization()
    # operator_vis_main()
    # evaluate_pddl_planner()
    # stats()
    # pddl_problem_construction()
    # construct_behavior_pddl()
    # operator_parser()
