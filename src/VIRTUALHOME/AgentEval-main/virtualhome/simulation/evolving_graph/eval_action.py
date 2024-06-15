import json
import sys

sys.path.append("../simulation")

import re
import copy
import sys
import os
import copy
import ast

import evolving_graph.utils as utils
from evolving_graph.eval_utils import *


model_name = "gpt-3.5-turbo-0125"
system_prompt = "You are an action planner designing action commands for a household robot. For this task, please only output a parsable json string inside brackets. Please start your answer with { and end your answer with }. Don't include any notes or explanations with the output json string."
use_action = True


def action_input_preparation():
    data_dir = "/viscam/u/shiyuz/virtualhome/virtualhome/dataset/programs_processed_precond_nograb_morepreconds"
    task_dict_dir = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/resources/task_state_LTL_formula_accurate.json"
    helm_prompt_path = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/helm/helm_prompt/action_sequencing_vh_w_actions.json"
    scenegraph_id = 1
    scene_id = f"scene_{scenegraph_id}"
    task_dict = json.load(open(task_dict_dir, "r"))
    task_dict = task_dict[scene_id]

    # load meta for constructing planners
    properties_data = utils.load_properties_data()
    object_placing = utils.load_object_placing()
    name_equivalence = utils.load_name_equivalence()

    helm_prompt_list = []

    for task_name, task_dicts in task_dict.items():
        print(f"CURRENT TASK IS {task_name}!")
        for file_id, task_goal_dict in task_dicts.items():
            # get symbolic goals
            goals = task_goal_dict["vh_goal"]
            action_goals = goals["actions"]
            scene_goals = goals["goal"]
            node_goals = []
            edge_goals = []
            for scene_goal in scene_goals:
                if "id" in scene_goal and "class_name" in scene_goal and "state" in scene_goal:
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

            prompt = open(
                "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/prompts/action_sequence_prompt_w_action.txt",
                "r",
            ).read()
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


def action_llm_prediction():
    if use_action:
        helm_prompt_path = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/helm/helm_prompt/action_sequencing_vh_w_actions.json"
        helm_output_path = f"/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/helm/helm_output/action_sequencing_vh_w_actions_{model_name}.json"
    else:
        helm_prompt_path = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/helm/helm_prompt/action_sequencing_vh_wo_actions.json"
        helm_output_path = f"/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/helm/helm_output/action_sequencing_vh_wo_actions_{model_name}.json"

    helm_output = []
    helm_prompt = json.load(open(helm_prompt_path, "r"))
    for prompt_dict in helm_prompt:
        id = prompt_dict["identifier"]
        prompt = prompt_dict["llm_prompt"]
        print(f"GPT starts prediction: {id}", flush=True)
        predicted_action = get_gpt_output(
            prompt, model_name, temperature=1, system_prompt=system_prompt
        )
        helm_output.append({"identifier": id, "llm_output": predicted_action})
    json.dump(helm_output, open(helm_output_path, "w"), indent=4)


def evaluate_action_sequence(
    data_dir, t_ids, node_goal_list, edge_goal_list, action_goals, num_tasks=50
):

    properties_data = utils.load_properties_data()
    object_placing = utils.load_object_placing()
    name_equivalence = utils.load_name_equivalence()

    scene_id = [1]
    program_dir = os.path.join(data_dir, "executable_programs")

    tot_num = 0.0
    pattern = r"file(\d+_\d+)\.txt"

    # metrics

    # format correct
    task_valid_correct = 0
    task_format_correct = 0
    # no hallucination
    task_no_hallucination = 0
    # runtime correct
    task_executable_plan = 0
    task_error_dict = {
        "wrong_order": 0,
        "missing_step": 0,
        "affordance": 0,
        "unseen": 0,
        "additional_step": 0,
        "other": 0,
    }
    # action correct
    task_actions_correct = 0
    # everything correct
    task_correct_plan = 0

    # ---------------

    wrong_order_num = 0
    missing_step_num = 0
    affordance_num = 0
    unseen_num = 0
    additional_step_num = 0
    other_num = 0

    helm_prompt_l = []
    node_success_rate_list = []
    edge_success_rate_list = []
    action_success_rate_list = []
    full_success_rate_list = []

    for scene in scene_id:
        scene_dir = os.path.join(
            program_dir,
            f"TrimmedTestScene{scene}_graph",
            "results_intentions_march-13-18",
        )
        for file in os.listdir(scene_dir):
            if not file.endswith(".txt"):
                continue
            match = re.search(pattern, file)
            if match:
                script_id = match.group(1)
            else:
                print("Wrong file format. No match found.")
                continue
            if script_id not in t_ids:
                continue
            # if script_id != '604_2':
            #     continue
            # print(f'{script_id=}')
            tot_num += 1

            motion_planner, relevant_id, gd_actions, task_name, _ = construct_planner(
                name_equivalence,
                properties_data,
                object_placing,
                scenegraph_id=scene,
                script_id=script_id,
                dataset_root=data_dir,
            )

            node_goals = copy.deepcopy(node_goal_list)
            edge_goals = copy.deepcopy(edge_goal_list)

            motion_planner.reset()
            # relevant node id pairs
            relevant_nodes_ids = motion_planner.get_relevant_nodes(script_id=script_id)
            node_goals, edge_goals = find_node_and_edge_in_scene_exact(
                node_goals, edge_goals, motion_planner
            )
            # relevant obj
            print(f"{node_goals=}")
            print(f"{edge_goals=}")
            _, _, node_goal_str, edge_goal_str, relevant_name_to_id = (
                motion_planner.get_symbolic_goal_nl(node_goals, edge_goals)
            )

            object_in_scene, cur_change, _ = motion_planner.get_nl_goal_string()

            gold_succ = validate_programs_based_on_goal_states(
                motion_planner.final_state_dict,
                node_goals,
                edge_goals,
                motion_planner.acting_char_id,
            )
            if not gold_succ:
                tot_num -= 1
                continue

            # NL goals
            # print(f'{object_in_scene=}', flush=True)
            # print(f'{cur_change=}', flush=True)
            # print(f'{node_goal_str=}', flush=True)
            # print(f'{edge_goal_str=}', flush=True)
            prompt = open(
                "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/prompts/action_plan_prompt_goal_nl_json.txt",
                "r",
            ).read()
            prompt = prompt.replace("<object_in_scene>", object_in_scene)
            prompt = prompt.replace("<cur_change>", cur_change)
            prompt = prompt.replace("<node_goals>", node_goal_str)
            prompt = prompt.replace("<edge_goals>", edge_goal_str)

            retry_cnt = 0
            executable = False
            retry_tot = 1

            hallucination_error = False
            runtime_error = False
            format_correct_flag = False

            while retry_cnt < retry_tot and not format_correct_flag:
                print("gpt predicts...", flush=True)
                # initialize errors
                format_error = False

                actions = get_gpt_output(
                    message=prompt, json_object=True, temperature=1
                )
                original_actions = {}

                try:
                    actions = json.loads(actions)
                    for obj_lst in actions.values():
                        for obj in obj_lst:
                            if obj not in relevant_name_to_id.keys():
                                print(f"Object {obj} not in relevant objects")
                                print(f"{relevant_name_to_id=}")
                                hallucination_error = True
                    original_actions = copy.deepcopy(actions)
                    actions = json_to_action(actions, relevant_name_to_id)
                    # print(f'after json {actions}')
                    if isinstance(actions, str):
                        try:
                            actions = ast.literal_eval(actions)
                        except:
                            actions = actions.split("\n")
                    format_correct_flag = True
                except Exception as e:
                    retry_cnt += 1
                    print("Fail to generate the action sequence", flush=True)
                    if retry_cnt < retry_tot:
                        print("Retry...")
                        continue
                    else:
                        format_error = True
                        raise e
                        break

            # format check (try retry_tot times)
            print(f"{actions=}")
            if len(actions) > 0 or hallucination_error:
                task_valid_correct += 1
            else:
                print(
                    f"Task {task_name}, file {script_id} has no valid action sequence"
                )
                format_error = True

            # hallucination check
            if not format_error:
                if check_no_hallucination(original_actions) and not hallucination_error:
                    task_no_hallucination += 1
                else:
                    print(
                        f"Task {task_name}, file {script_id} has hallucination error",
                        flush=True,
                    )
                    hallucination_error = True

            # parameters number check
            if not format_error and not hallucination_error:
                print(f"{original_actions=}")
                if check_action_grammar(original_actions):
                    task_format_correct += 1
                else:
                    print(
                        f"Task {task_name}, file {script_id} has grammar error",
                        flush=True,
                    )
                    format_error = True

            print(f"{format_error=}")
            print(f"{hallucination_error=}")
            # runtime check
            if not format_error and not hallucination_error:
                print(f"{actions=}")
                # if gold, directly pass all check
                if actions == gd_actions:
                    # tot_succ += 1
                    task_executable_plan += 1
                    task_correct_plan += 1
                else:
                    # try:
                    motion_planner.reset()
                    exe_flag = True
                    history_actions = []
                    failed_info = []
                    # executable = False
                    prev_env_states = copy.deepcopy(motion_planner.env_state)
                    history_env_states = [copy.deepcopy(prev_env_states.to_dict())]
                    if len(actions) == 0:
                        exe_flag = False
                    for action in actions:
                        print(f"{action=}")
                        exe_flag, my_info = (
                            motion_planner.my_execute_primitive_action_eval(action)
                        )
                        if not exe_flag:
                            print(f"Current action {action} not executable.")
                            print(f"{my_info=}")
                            failed_error_code = my_info.get_error_type()
                            failed_error_seq = my_info.get_error_string()
                            failed_error_code, failed_error_seq = (
                                check_fg_satisfied_in_prev_states(
                                    history_env_states,
                                    failed_error_code,
                                    failed_error_seq,
                                    node_goals,
                                    edge_goals,
                                    motion_planner.acting_char_id,
                                )
                            )
                            if failed_error_code == 0:
                                print(
                                    f"Current action {action} has wrong order error on task {script_id}."
                                )
                            # failed_action_seq = cur_executed_actions + action_seq
                            history_actions_cp = copy.deepcopy(history_actions)
                            failed_info.append(
                                (
                                    failed_error_code,
                                    history_actions_cp,
                                    failed_error_seq,
                                )
                            )
                            print(f"{failed_error_code=}")
                            print(f"{history_actions_cp=}")
                            break
                        else:
                            print(f"Current action {action} executable.", flush=True)
                            history_actions.append(action)
                            new_env_state = copy.deepcopy(
                                motion_planner.env_state.to_dict()
                            )
                            history_env_states.append(new_env_state)

                    if exe_flag:
                        # tot_exec += 1
                        task_executable_plan += 1
                        print("Executable!", flush=True)
                        # executable = True
                    else:
                        runtime_error = True
                        if len(failed_info) > 0:
                            failed_first_item = failed_info[0]
                            error_type, failed_exe_action_seq, failed_error_seq = (
                                failed_first_item
                            )
                            error_str, task_error_dict = set_error_type(
                                task_error_dict, error_type
                            )
                            print(f"  Wrong Error Type: {error_str}")
                            print(f"  Wrong Action Sequence: {failed_exe_action_seq}")
                            print(f"  Wrong Error Sequence: {failed_error_seq}")
                        else:
                            print("  We confront an unknown error!")
                            task_error_dict["other"] += 1

                        wrong_order_num += task_error_dict["wrong_order"]
                        missing_step_num += task_error_dict["missing_step"]
                        affordance_num += task_error_dict["affordance"]
                        unseen_num += task_error_dict["unseen"]
                        additional_step_num += task_error_dict["additional_step"]
                        other_num += task_error_dict["other"]

            # success plan check
            if not format_error and not hallucination_error:
                (
                    node_success_rate,
                    edge_success_rate,
                    action_success_rate,
                    whole_success_rate,
                ) = scene_evaluate(
                    motion_planner.env_state.to_dict(),
                    node_goals,
                    edge_goals,
                    motion_planner.acting_char_id,
                    relevant_node_ids=relevant_nodes_ids,
                    action_seq=actions,
                    action_goals=action_goals,
                )

                print(f"{node_success_rate=}")
                print(f"{edge_success_rate=}")
                print(f"{action_success_rate=}")
                print(f"{whole_success_rate=}")

                node_success_rate_list.append(node_success_rate)
                edge_success_rate_list.append(edge_success_rate)
                action_success_rate_list.append(action_success_rate)
                full_success_rate_list.append(whole_success_rate)

                # succ = validate_programs_based_on_goal_states(
                #     motion_planner.env_state.to_dict(),
                #     node_goals,
                #     edge_goals,
                #     motion_planner.acting_char_id,
                # )

                action_str = " ".join(actions)
                act_succ = check_order_with_or(action_goals, action_str)
                if act_succ:
                    task_actions_correct += 1
                else:
                    print(
                        f"Task {task_name}, file {script_id} does not achieve action goal",
                        flush=True,
                    )

                # if succ and act_succ:
                #     task_correct_plan += 1
                #     assert (
                #         node_success_rate in [-1, 1]
                #         and edge_success_rate in [-1, 1]
                #         and action_success_rate in [-1, 1]
                #     )
                #     print("EVERYTHING SUCCEED!", flush=True)
            else:
                node_success_rate_list.append(-1)
                edge_success_rate_list.append(-1)
                action_success_rate_list.append(-1)
                full_success_rate_list.append(-1)

            if tot_num >= num_tasks:
                break

        # succ = tot_succ / tot_num if tot_num != 0 else 0
        # exe_rate = task_executable_plan / tot_num if tot_num != 0 else 0
        # map_rate = map_suc / tot_num if tot_num != 0 else 0
        # print(f'For scene {scene}, {tot_succ=}, {tot_num=}, {tot_exec=}, {map_rate=}, {succ=}, {exe_rate=}')

    return (
        tot_num,
        task_valid_correct,
        task_format_correct,
        task_no_hallucination,
        task_executable_plan,
        task_actions_correct,
        task_correct_plan,
        wrong_order_num,
        missing_step_num,
        affordance_num,
        unseen_num,
        additional_step_num,
        other_num,
        node_success_rate_list,
        edge_success_rate_list,
        action_success_rate_list,
        full_success_rate_list,
        helm_prompt_l,
    )
