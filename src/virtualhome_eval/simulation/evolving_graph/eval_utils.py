import os
from virtualhome_eval.simulation.evolving_graph.environment import EnvironmentGraph
import json
import time
import ast
import re
import copy
from collections import OrderedDict
import logging

from virtualhome_eval.simulation.evolving_graph.motion_planner import MotionPlanner
import virtualhome_eval.simulation.evolving_graph.utils as utils
import logging

logger = logging.getLogger(__name__)

valid_actions = {
    "DRINK": ("DRINK", 1),
    "EAT": ("EAT", 1),
    "CUT": ("CUT", 1),
    "TOUCH": ("TOUCH", 1),
    "LOOKAT": ("LOOKAT", 1),
    "LOOKAT_SHORT": ("LOOKAT_SHORT", 1),
    "LOOKAT_MEDIUM": ("LOOKAT_MEDIUM", 1),
    "LOOKAT_LONG": ("LOOKAT_LONG", 1),
    "WATCH": ("WATCH", 1),
    "READ": ("READ", 1),
    "TYPE": ("TYPE", 1),
    "PUSH": ("PUSH", 1),
    "PULL": ("PULL", 1),
    "MOVE": ("MOVE", 1),
    "SQUEEZE": ("SQEEZE", 1),
    "SLEEP": ("SLEEP", 0),
    "WAKEUP": ("WAKEUP", 0),
    "RINSE": ("RINSE", 1),
    "SCRUB": ("SCRUB", 1),
    "WASH": ("WASH", 1),
    "GRAB": ("GRAB", 1),
    "SWITCHOFF": ("SWITCHOFF", 1),
    "SWITCHON": ("SWITCHON", 1),
    "CLOSE": ("CLOSE", 1),
    "FIND": ("FIND", 1),
    "WALK": ("WALK", 1),
    "OPEN": ("OPEN", 1),
    "POINTAT": ("POINTAT", 1),
    "PUTBACK": ("PUTBACK", 2),
    "PUTIN": ("PUTIN", 2),
    "PUTOBJBACK": ("PUTOBJBACK", 1),
    "RUN": ("RUN", 1),
    "SIT": ("SIT", 1),
    "STANDUP": ("STANDUP", 0),
    "TURNTO": ("TURNTO", 1),
    "WIPE": ("WIPE", 1),
    "PUTON": ("PUTON", 1),
    "PUTOFF": ("PUTOFF", 1),
    "GREET": ("GREET", 1),
    "DROP": ("DROP", 1),
    "LIE": ("LIE", 1),
    "POUR": ("POUR", 2),
}

state_transform_dictionary = {
    "CLOSED": "CLOSED",
    "OPEN": "OPEN",
    "ON": "ON",
    "OFF": "OFF",
    "SITTING": "SITTING",
    "DIRTY": "DIRTY",
    "CLEAN": "CLEAN",
    "LYING": "LYING",
    "PLUGGED_IN": "PLUGGED_IN",
    "PLUGGED_OUT": "PLUGGED_OUT",
    "ONTOP": "ONTOP",  # relation on should be converted into ontop
    "OBJ_ONTOP": "OBJ_ONTOP",
    "ON_CHAR": "ON_CHAR",
    "INSIDE": "INSIDE",
    "OBJ_INSIDE": "OBJ_INSIDE",
    "INSIDE_ROOM": "INSIDE_ROOM",
    "BETWEEN": "BETWEEN",
    "NEXT_TO": "NEXT_TO",
    "OBJ_NEXT_TO": "OBJ_NEXT_TO",
    "FACING": "FACING",
    "HOLDS_RH": "HOLDS_RH",
    "HOLDS_LH": "HOLDS_LH",
    "SITTINGRELATION": "ONTOP",  # relation sitting should be converted into ontop
}

def load_json_preserving_order(json_string):
    # Remove newlines and extra spaces
    json_string = re.sub(r"\s+", " ", json_string.strip())
    # Extract key-value pairs
    pattern = r'"(\w+)"\s*:\s*(\[[^\]]+\])'
    matches = re.findall(pattern, json_string)
    result = []
    for key, value in matches:
        # Parse the value (which is a JSON array)
        parsed_value = json.loads(value)
        result.append({key: parsed_value})
    return result


def parse_json(raw_llm_output):
    # Replace single quotes with double quotes, use lower case, fix "toggleon":
    raw_llm_output = (
        raw_llm_output.lower().replace("'", '"').replace("toggledon", "toggled_on")
    )
    # Extract the substring between the first { and the first } after it:
    match = re.search(r"{[^{}]*}", raw_llm_output, re.DOTALL)
    if match:
        result = match.group(0)
        try:
            return json.loads(result)
        except:
            logger.info("Error parsing JSON-like content.")
    else:
        logger.info("No valid JSON-like content found.")
    # format error
    return None


def remove_duplicate_dicts(list_of_dicts):
    def make_hashable(item):
        if isinstance(item, dict):
            return frozenset((key, make_hashable(value)) for key, value in item.items())
        elif isinstance(item, list):
            return tuple(make_hashable(element) for element in item)
        return item

    unique_dicts = {make_hashable(item): item for item in list_of_dicts}
    return list(unique_dicts.values())


def extract_script(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
        task_name = lines[0]
        task_description = lines[1]
        actions = [line.strip() for line in lines if line.startswith("[")]
    return task_name, task_description, actions


def get_gpt_output(
    message,
    model="gpt-4o",
    max_tokens=512,
    temperature=0,
    json_object=True,
    system_prompt=None,
):
    import openai
    if json_object:
        if isinstance(message, str) and not "json" in message.lower():
            message = "You are a helpful assistant designed to output JSON. " + message
    if openai.__version__.startswith("0."):
        if isinstance(message, str):
            messages = [{"role": "user", "content": message}]
        else:
            messages = message
        try:
            chat = openai.ChatCompletion.create(model=model, messages=messages)
        except Exception as e:
            logger.info(f"{e}\nTry after 1 min")
            time.sleep(61)
            chat = openai.ChatCompletion.create(model=model, messages=messages)
        reply = chat.choices[0].message.content
    else:
        if system_prompt is not None:
            messages = [{"role": "system", "content": system_prompt}]
        else:
            messages = []
        if isinstance(message, str):
            messages += [{"role": "user", "content": message}]
        else:
            messages = message
        kwargs = {"response_format": {"type": "json_object"}} if json_object else {}
        try:
            chat = openai.OpenAI().chat.completions.create(
                messages=messages, model=model, temperature=temperature, **kwargs
            )
        except Exception as e:
            logger.info(f"{e}\nTry after 1 min")
            time.sleep(61)
            chat = openai.OpenAI().chat.completions.create(
                messages=messages, model=model, temperature=temperature, **kwargs
            )
        reply = chat.choices[0].message.content
    return reply


def special_print(s):
    lines = s.split("\\n")
    for line in lines:
        logger.info(line)


def special_write(s, f):
    lines = s.split("\\n")
    for line in lines:
        f.write(line)


def get_object_id_goal(name, id_2_name_dict):
    candidates = []
    for id, n in id_2_name_dict.items():
        if n == name:
            candidates.append(id)
    return candidates


def get_object_based_on_id(id, graph_dict):
    for obj in graph_dict["nodes"]:
        if obj["id"] == id:
            return obj
    return None


def at_least_one_matched(src_str, tgt_strs) -> bool:
    if src_str in tgt_strs:
        return True
    return False


def extract_properties(input_str):
    pattern = r"<(Property\.[A-Z]+): \d+>"
    prop_list = re.findall(pattern, input_str)
    return prop_list


def find_target_dict(data, target):
    dict_strings = data.split("|")
    for dict_string in dict_strings:
        if dict_string == "None" or dict_string is None:
            continue
        try:
            dict_obj = ast.literal_eval(dict_string)
        except:
            logger.info(f"{dict_string=}")
        if dict_obj.get("name") == target:
            return dict_obj
    return None


def check_order_with_or(action_goals, input_string):
    if len(action_goals) == 0:
        return True
    start_index = 0
    for goal_group in action_goals:
        options = goal_group.split("|")
        found = False
        for option in options:
            option = option.upper()
            option = option.replace(" ", "")
            index = input_string.find(option, start_index)
            if index != -1:
                start_index = index + len(option)
                found = True
                break
        if not found:
            return False
    return True


def check_order_with_or_score(action_goals, input_string):
    if len(action_goals) == 0:
        return -1
    cnt = 0
    tot = len(action_goals)
    start_index = 0
    unsatisfied_action_goals = []
    for goal_group in action_goals:
        options = goal_group.split("|")
        found = False
        for option in options:
            option = option.upper()
            option = option.replace(" ", "")
            index = input_string.find(option, start_index)
            if index != -1:
                start_index = index + len(option)
                found = True
                cnt += 1
                break
        if not found:
            unsatisfied_action_goals.append(goal_group)
            break
    return cnt, unsatisfied_action_goals


def json_to_action(action_list, relevant_name_to_id):
    actions = []
    # try:
    for action_json in action_list:
        for action, objects in action_json.items():
            if len(objects) == 0:
                actions.append(f"[{action}]")
            elif len(objects) == 1:
                obg_id1 = relevant_name_to_id[objects[0]]
                actions.append(f"[{action}] <{objects[0]}> ({obg_id1})")
            elif len(objects) == 2:
                obg_id1 = relevant_name_to_id[objects[0]]
                obg_id2 = relevant_name_to_id[objects[1]]
                actions.append(
                    f"[{action}] <{objects[0]}> ({obg_id1}) <{objects[1]}> ({obg_id2})"
                )
    return actions
    # except Exception as e:
    #     logger.info(f"Error in converting json to action: {action_json}")
    #     # raise e
    #     return []


def get_all_object_in_scene(data_dir, scene) -> str:
    graph_dir = os.path.join(
        data_dir,
        "init_and_final_graphs",
        f"TrimmedTestScene{scene}_graph",
        "results_intentions_march-13-18",
    )
    object_in_scene = ""
    for file in os.listdir(graph_dir):
        if file.endswith(".json"):
            graph_dict = json.load(open(os.path.join(graph_dir, file), "r"))
            for node in graph_dict["init_graph"]["nodes"]:
                object_in_scene += (
                    str(node["class_name"])
                    + ", id: "
                    + str(node["id"])
                    + ", properties: "
                    + str(node["properties"])
                )
                object_in_scene += "\n"
            object_in_scene += "-----------------\n"
            break
    return object_in_scene


def reformat_actions(commands):
    reformatted_commands = []
    relevant_id = []
    for command in commands:
        parts = command.split()
        # Assuming the format is consistent as described: [action] <object> (id) or [action] <object1> (id1) <object2> (id2)
        reformatted_command = parts[0]  # This should be [action_name]
        for part in parts[1:]:
            if "(" in part and ")" in part:
                id_number = part.split(".")[-1]
                id_number = "(" + id_number[:-1] + ")"
                reformatted_command += f" {id_number}"
                id_number = int(id_number.strip("(").strip(")"))
                relevant_id.append(id_number)
            else:
                # This is an object name or a part of it
                reformatted_command += f" {part}"
        reformatted_commands.append(reformatted_command)
    relevant_id = list(set(relevant_id))
    return reformatted_commands, relevant_id


def extract_script(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
        task_name = lines[0]
        task_description = lines[1]
        actions = [line.strip() for line in lines if line.startswith("[")]
    return task_name, task_description, actions


def get_from_dataset(dataset_root, scenegraph_id, script_id):
    scene_dir = os.path.join(
        dataset_root,
        "init_and_final_graphs",
        f"TrimmedTestScene{scenegraph_id}_graph",
        "results_intentions_march-13-18",
        f"file{script_id}.json",
    )
    graph_dict = json.load(open(scene_dir, "r"))
    init_scene_state = graph_dict["init_graph"]
    init_scene_graph = EnvironmentGraph(init_scene_state)
    final_state_dict = graph_dict["final_graph"]

    script_dir = os.path.join(
        dataset_root,
        "executable_programs",
        f"TrimmedTestScene{scenegraph_id}_graph",
        "results_intentions_march-13-18",
        f"file{script_id}.txt",
    )

    task_name, task_description, actions = extract_script(script_dir)
    return init_scene_graph, actions, final_state_dict, task_name, task_description


def construct_planner(
    name_equivalence,
    properties_data,
    object_placing,
    scenegraph_id=1,
    script_id="11_1",
    dataset_root="dataset/programs_processed_precond_nograb_morepreconds",
):
    acting_char_id = None
    if scenegraph_id == 1:
        acting_char_id = 65
    init_scene_graph, actions, final_state_dict, task_name, task_description = (
        get_from_dataset(dataset_root, scenegraph_id, script_id)
    )
    gd_actions, relevant_id = reformat_actions(actions)
    planner = MotionPlanner(
        init_scene_graph,
        final_state_dict,
        name_equivalence,
        properties_data,
        object_placing,
        acting_char_id=acting_char_id,
    )
    return planner, relevant_id, gd_actions, task_name, task_description


def scene_eval_on_diff(
    planner,
    pred_final_state_dict,
    gold_final_state_dict,
    selected_node_goals,
    selected_edge_goals,
    relevant_nodes_ids,
    character_id,
):
    _, gold_final_diff = planner.filter_unique_subdicts(
        planner.init_state.to_dict(), gold_final_state_dict
    )
    _, predict_final_diff = planner.filter_unique_subdicts(
        planner.init_state.to_dict(), pred_final_state_dict
    )
    selected_edge_state = copy.deepcopy(selected_edge_goals)
    selected_node_state = copy.deepcopy(selected_node_goals)
    id_2_name_dict = planner.id_to_name

    name_to_id = {}
    for tup in relevant_nodes_ids:
        name_to_id[tup[0]] = tup[1]

    node_metrics = [-1.0, -1.0, -1.0]
    edge_metrics = [-1.0, -1.0, -1.0]
    full_metrics = [-1.0, -1.0, -1.0]
    node_error_flag = False
    edge_error_flag = False

    node_relevant_ids = [character_id]
    # we first calculate node states precison/recall/f1
    for node_state_str in selected_node_state:
        if isinstance(node_state_str, str):
            node_state = eval(node_state_str)
        else:
            node_state = node_state_str
        relevant_id = name_to_id.get(node_state["name"], None)
        if relevant_id is None:
            logger.info(f'No candidate found for {node_state["name"]} DOUBLE CHECK GOALS!')
            node_error_flag = True
        node_relevant_ids.append(relevant_id)
    logger.info(f"{node_relevant_ids=}")
    if len(selected_node_state) == 0:
        node_error_flag = True
    if not node_error_flag:
        gold_final_diff_relevant = []
        for node in gold_final_diff["nodes"]:
            if node["id"] in node_relevant_ids:
                gold_final_diff_relevant.append(node)
        if len(gold_final_diff_relevant) == 0:
            logger.info(f"No relevant nodes found in gold final diff! DOUBLE CHECK GOALS!")
    if not node_error_flag and len(gold_final_diff_relevant) != 0:
        predict_final_diff_relevant = []
        for node in predict_final_diff["nodes"]:
            if node["id"] in node_relevant_ids:
                predict_final_diff_relevant.append(node)
        node_tp = 0
        logger.info(f"{predict_final_diff_relevant=}")
        logger.info(f"{gold_final_diff_relevant=}")
        for node in predict_final_diff_relevant:
            if node in gold_final_diff_relevant:
                node_tp += 1
        precision = (
            node_tp / len(predict_final_diff_relevant)
            if len(predict_final_diff_relevant) != 0
            else 0.0
        )
        recall = node_tp / len(gold_final_diff_relevant)
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall != 0
            else 0.0
        )
        node_metrics = [precision, recall, f1]

    # we then calculate edge states precison/recall/f1
    edge_relevant_ids = []
    for edge_state_str in selected_edge_state:
        if isinstance(edge_state_str, str):
            edge_state = eval(edge_state_str)
        else:
            edge_state = edge_state_str
        from_name, relation, to_name = (
            edge_state["from_name"],
            edge_state["relation"],
            edge_state["to_name"],
        )
        from_id = name_to_id.get(from_name, None)
        to_id = name_to_id.get(to_name, None)
        if from_id is None or to_id is None:
            logger.info(
                f"No candidate found for {from_name} or {to_name} DOUBLE CHECK GOALS!"
            )
            edge_error_flag = True
        edge_relevant_ids.append(from_id)
        edge_relevant_ids.append(to_id)
    logger.info(f"{edge_relevant_ids=}")
    if len(selected_edge_state) == 0:
        edge_error_flag = True
    if not edge_error_flag:
        gold_final_diff_relevant = []
        for edge in gold_final_diff["edges"]:
            if (
                edge["from_id"] in edge_relevant_ids
                or edge["to_id"] in edge_relevant_ids
            ):
                gold_final_diff_relevant.append(edge)
        if len(gold_final_diff_relevant) == 0:
            logger.info(f"No relevant edges found in gold final diff! DOUBLE CHECK GOALS!")
    if not edge_error_flag and len(gold_final_diff_relevant) != 0:
        predict_final_diff_relevant = []
        for edge in predict_final_diff["edges"]:
            if (
                edge["from_id"] in edge_relevant_ids
                or edge["to_id"] in edge_relevant_ids
            ):
                predict_final_diff_relevant.append(edge)
        edge_tp = 0
        for edge in predict_final_diff_relevant:
            if edge in gold_final_diff_relevant:
                edge_tp += 1
        precision = (
            edge_tp / len(predict_final_diff_relevant)
            if len(predict_final_diff_relevant) != 0
            else 0.0
        )
        recall = edge_tp / len(gold_final_diff_relevant)
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall != 0
            else 0.0
        )
        edge_metrics = [precision, recall, f1]

    if not node_error_flag and not edge_error_flag:
        full_precision = (node_tp + edge_tp) / (
            len(predict_final_diff_relevant) + len(gold_final_diff_relevant)
        )
        full_recall = (node_tp + edge_tp) / (
            len(gold_final_diff_relevant) + len(predict_final_diff_relevant)
        )
        full_f1 = 2 * full_precision * full_recall / (full_precision + full_recall)
        full_metrics = [full_precision, full_recall, full_f1]
    elif node_error_flag and not edge_error_flag:
        full_metrics = edge_metrics
    elif not node_error_flag and edge_error_flag:
        full_metrics = node_metrics
    else:
        full_metrics = [-1.0, -1.0, -1.0]

    return node_metrics, edge_metrics, full_metrics


def scene_evaluate(
    final_state_dict,
    selected_node_goals,
    selected_edge_goals,
    character_id,
    relevant_node_ids,
    action_seq=None,
    action_goals=None,
):
    name_equivalence = utils.load_name_equivalence()
    properties_data = utils.load_properties_data()
    object_placing = utils.load_object_placing()

    name_to_id = {}
    for tup in relevant_node_ids:
        name_to_id[tup[0]] = tup[1]
    logger.info(f"{name_to_id=}")

    final_scene_graph = EnvironmentGraph(final_state_dict)
    planner = MotionPlanner(
        final_scene_graph,
        final_state_dict,
        name_equivalence,
        properties_data,
        object_placing,
    )
    id_2_name_dict = planner.id_to_name

    node_match_num = 0
    edge_match_num = 0
    action_match_num = 0
    node_match_denom = len(selected_node_goals)
    edge_match_denom = len(selected_edge_goals)
    action_match_denom = len(action_goals)

    selected_edge_state = copy.deepcopy(selected_edge_goals)
    selected_node_state = copy.deepcopy(selected_node_goals)

    for node_state_str in selected_node_state:
        if isinstance(node_state_str, str):
            node_state = eval(node_state_str)
        else:
            node_state = node_state_str
        candidate_ids = get_object_id_goal(node_state["name"], id_2_name_dict)
        if len(candidate_ids) == 0:
            logger.info(f'No candidate found for {node_state["name"]}')
            node_match_num = 0
            continue
        for id in candidate_ids:
            obj = get_object_based_on_id(id, final_state_dict)
            if obj is None:
                continue
            if node_state["state"] in obj["states"]:
                node_match_num += 1
                break

    assert node_match_num <= node_match_denom, f"{node_match_num=}, {node_match_denom=}"

    candidate_edge_nodes = set()
    candidate_edge_relations = set()
    for edge_state_str in selected_edge_state:
        if isinstance(edge_state_str, str):
            edge_state = eval(edge_state_str)
        else:
            edge_state = edge_state_str
        goal_from_name, goal_relation, goal_to_name = (
            edge_state["from_name"],
            edge_state["relation"],
            edge_state["to_name"],
        )
        candidate_edge_nodes.add(goal_from_name)
        candidate_edge_nodes.add(goal_to_name)
        candidate_edge_relations.add(goal_relation)

    for real_edge_state in final_state_dict["edges"]:
        # below, we get the real edge state
        if (
            real_edge_state["relation_type"] == "CLOSE"
            and real_edge_state["from_id"] != character_id
            and real_edge_state["to_id"] != character_id
        ):
            continue
        from_id, relation, to_id = (
            real_edge_state["from_id"],
            real_edge_state["relation_type"],
            real_edge_state["to_id"],
        )
        from_name, to_name = id_2_name_dict[from_id], id_2_name_dict[to_id]
        if (
            from_name not in candidate_edge_nodes
            or to_name not in candidate_edge_nodes
            or relation not in candidate_edge_relations
        ):
            continue
        if from_id not in name_to_id.values() or to_id not in name_to_id.values():
            continue

        # below, we search in the goal edge states, to see if there is a match
        next_selected_edge_state = copy.deepcopy(selected_edge_state)
        for edge_state_str in selected_edge_state:
            if isinstance(edge_state_str, str):
                edge_state = eval(edge_state_str)
            else:
                edge_state = edge_state_str
            goal_from_name, goal_relation, goal_to_name = (
                edge_state["from_name"],
                edge_state["relation"],
                edge_state["to_name"],
            )
            if goal_relation != relation:
                continue
            if from_name == goal_from_name and to_name == goal_to_name:
                if edge_state_str not in next_selected_edge_state:
                    logger.info(f"Edge state {edge_state_str} is already matched!!!")
                    continue
                edge_match_num += 1
                logger.info(f"Matched edge state {edge_state_str} with {real_edge_state}")
                next_selected_edge_state.remove(edge_state_str)
                logger.info(f"{next_selected_edge_state=}")

    assert edge_match_num <= edge_match_denom, f"{edge_match_num=}, {edge_match_denom=}"

    if len(action_goals) > 0:
        action_str = " ".join(action_seq)
        action_match_num = check_order_with_or_score(action_goals, action_str)
        logger.info(f"{action_match_num=}")
        logger.info(f"{action_goals=}")
        logger.info(f"{action_str=}")
        assert (
            action_match_num <= action_match_denom
        ), f"{action_match_num=}, {action_match_denom=}"

    node_success_rate = (
        node_match_num / node_match_denom if node_match_denom != 0 else -1
    )
    edge_success_rate = (
        edge_match_num / edge_match_denom if edge_match_denom != 0 else -1
    )
    action_success_rate = (
        action_match_num / action_match_denom if action_match_denom != 0 else -1
    )
    full_success_rate = (
        (node_match_num + edge_match_num + action_match_num)
        / (node_match_denom + edge_match_denom + action_match_denom)
        if node_match_denom + edge_match_denom + action_match_denom != 0
        else -1
    )

    return node_success_rate, edge_success_rate, action_success_rate, full_success_rate


def scene_evaluate_wID(
    final_state_dict,
    accurate_node_goals,
    accurate_edge_goals,
    character_id,
    action_seq=[],
    action_goals=[],
):
    name_equivalence = utils.load_name_equivalence()
    properties_data = utils.load_properties_data()
    object_placing = utils.load_object_placing()

    final_scene_graph = EnvironmentGraph(final_state_dict)
    planner = MotionPlanner(
        final_scene_graph,
        final_state_dict,
        name_equivalence,
        properties_data,
        object_placing,
    )
    id_2_name_dict = planner.id_to_name

    node_match_num = 0
    edge_match_num = 0
    action_match_num = 0
    node_total_num = len(accurate_node_goals)
    edge_total_num = len(accurate_edge_goals)
    action_total_num = len(action_goals)
    unsatisfied_node_goals = []
    unsatisfied_edge_goals = []
    unsatisfied_action_goals = []

    for gd_node_goal in accurate_node_goals:
        id = gd_node_goal["id"]
        obj = get_object_based_on_id(id, final_state_dict)
        if obj is None:
            logger.info(f"GOAL FAIL! Not found: {gd_node_goal}")
            continue
        if gd_node_goal["state"] in obj["states"]:
            node_match_num += 1
        else:
            logger.info(f"GOAL FAIL! Not matched: {gd_node_goal}")
            unsatisfied_node_goals.append(gd_node_goal)

    # print found goals and not found goals
    assert node_match_num <= node_total_num, f"{node_match_num=}, {node_total_num=}"

    for gd_edge_goal in accurate_edge_goals:
        assert isinstance(gd_edge_goal, dict)
        if gd_edge_goal in final_state_dict["edges"]:
            edge_match_num += 1
            break
        else:
            logger.info(f"GOAL FAIL! Not found: {gd_edge_goal}")
            unsatisfied_edge_goals.append(gd_edge_goal)

    assert edge_match_num <= edge_total_num, f"{edge_match_num=}, {edge_total_num=}"

    if len(action_goals) > 0:
        action_str = " ".join(action_seq)
        action_match_num, unsatisfied_action_goals = check_order_with_or_score(
            action_goals, action_str
        )
        logger.info(f"{action_match_num=}")
        logger.info(f"{action_goals=}")
        logger.info(f"{action_str=}")
        assert (
            action_match_num <= action_total_num
        ), f"{action_match_num=}, {action_total_num=}"

    all_success = False
    if (
        node_match_num == node_total_num
        and edge_match_num == edge_total_num
        and action_match_num == action_total_num
    ):
        all_success = True

    return (
        node_match_num,
        edge_match_num,
        action_match_num,
        all_success,
        unsatisfied_node_goals,
        unsatisfied_edge_goals,
        unsatisfied_action_goals,
    )


def validate_programs_based_on_goal_states(
    final_state_dict, selected_node_goals, selected_edge_goals, character_id
):
    logger.info("\n\n=================Now starts validation=================\n\n")
    name_equivalence = utils.load_name_equivalence()
    properties_data = utils.load_properties_data()
    object_placing = utils.load_object_placing()

    success_list = []

    final_scene_graph = EnvironmentGraph(final_state_dict)
    planner = MotionPlanner(
        final_scene_graph,
        final_state_dict,
        name_equivalence,
        properties_data,
        object_placing,
    )
    id_2_name_dict = planner.id_to_name

    success = True
    selected_edge_state = copy.deepcopy(selected_edge_goals)
    selected_node_state = copy.deepcopy(selected_node_goals)
    # we first check node states
    for node_state_str in selected_node_state:
        if isinstance(node_state_str, str):
            node_state = eval(node_state_str)
        else:
            node_state = node_state_str
        candidate_ids = get_object_id_goal(node_state["name"], id_2_name_dict)
        if len(candidate_ids) == 0:
            logger.info(f'No candidate found for {node_state["name"]}')
            success = False
            break
        success = False
        for id in candidate_ids:
            obj = get_object_based_on_id(id, final_state_dict)
            if obj == None:
                continue
            if node_state["state"] in obj["states"]:
                success = True
                break
        if not success:
            logger.info(
                f"[Node Fail] state {node_state} not found in the final state in file."
            )
            break

    # we then check edge states
    if success:
        logger.info(f"[Node Success]: File passed the node state check.")
        success = False
        for real_edge_state in final_state_dict["edges"]:
            # below, we get the real edge state
            if (
                real_edge_state["relation_type"] == "CLOSE"
                and real_edge_state["from_id"] != character_id
                and real_edge_state["to_id"] != character_id
            ):
                continue
            from_id, relation, to_id = (
                real_edge_state["from_id"],
                real_edge_state["relation_type"],
                real_edge_state["to_id"],
            )
            from_name, to_name = id_2_name_dict[from_id], id_2_name_dict[to_id]
            get_from_properties = (
                properties_data[from_name] if from_name in properties_data else []
            )
            get_to_properties = (
                properties_data[to_name] if to_name in properties_data else []
            )
            get_from_properties = sorted(
                get_from_properties, key=lambda prop: prop.value
            )
            get_to_properties = sorted(get_to_properties, key=lambda prop: prop.value)

            next_selected_edge_state = copy.deepcopy(selected_edge_state)
            is_match = False
            # below, we search in the goal edge states, to see if there is a match
            for edge_state_str in selected_edge_state:
                if isinstance(edge_state_str, str):
                    edge_state = eval(edge_state_str)
                else:
                    edge_state = edge_state_str
                goal_from_name, goal_relation, goal_to_name = (
                    edge_state["from_name"],
                    edge_state["relation"],
                    edge_state["to_name"],
                )

                if goal_relation != relation:
                    continue
                pattern = r"\?.+?\?"
                if "?" in goal_from_name:
                    # from name is a wildcard
                    validation_from_name = (
                        f"?{str(get_from_properties)}?"
                        if from_name != "character"
                        else f"?character?"
                    )
                    goal_from_name_candidates = re.findall(pattern, goal_from_name)

                    if to_name == goal_to_name and at_least_one_matched(
                        validation_from_name, goal_from_name_candidates
                    ):
                        is_match = True
                        next_selected_edge_state.remove(edge_state_str)
                elif "?" in goal_to_name:
                    # to name is a wildcard
                    validation_to_name = (
                        f"?{str(get_to_properties)}?"
                        if to_name != "character"
                        else f"?character?"
                    )
                    goal_to_name_candidates = re.findall(pattern, goal_to_name)
                    if from_name == goal_from_name and at_least_one_matched(
                        validation_to_name, goal_to_name_candidates
                    ):
                        is_match = True
                        next_selected_edge_state.remove(edge_state_str)
                else:
                    if from_name == goal_from_name and to_name == goal_to_name:
                        is_match = True
                        next_selected_edge_state.remove(edge_state_str)
            if is_match:
                selected_edge_state = next_selected_edge_state

            if len(selected_edge_state) == 0:
                success = True
                break

    # now we check whether edge states are satisfied
    for edge_str in selected_edge_state:
        logger.info(f"[Edge Fail]: edge {edge_str} not found in the final state in file.")
    if success:
        logger.info(f"[Edge Success]: File passed the edge state check.")
        # logger.info(f"[Success]: File {file_id} passed all checks.")
        # success_list.append(file_id)
        return 1
    else:
        return 0


def find_node_and_edge_in_scene_exact(node_goals, edge_goals, planner):
    init_dict = planner.init_state.to_dict()
    final_state_dict = planner.final_state_dict
    id_2_name_dict = planner.id_to_name
    diff_in_init, diff_in_final = planner.filter_unique_subdicts(
        init_dict, final_state_dict
    )
    properties_data = utils.load_properties_data()

    node_goal_exact = []
    edge_goal_exact = []
    # selected_node_state, selected_edge_state, accurate_edge_state, actions = goal['selected_node_state'], goal['selected_edge_state'], goal['accurate_edge_state'], goal['actions']

    # logger.info('diff in node', diff_in_final['nodes'])

    for cur_node in diff_in_final["nodes"]:
        cur_id, cur_name, cur_states = (
            cur_node["id"],
            cur_node["class_name"],
            cur_node["states"],
        )
        # logger.info(f'{cur_node=}')
        for cur_state in cur_states:
            success = False
            for node_str in node_goals:
                if "|" in node_str:
                    node_str_candidates = node_str.split("|")
                    for node_candidate in node_str_candidates:
                        node_state = ast.literal_eval(node_candidate)
                        ground_node_name = node_state["name"]
                        ground_node_state = node_state["state"]
                        if (
                            cur_name == ground_node_name
                            and cur_state == ground_node_state
                        ):
                            success = True
                            break
                    if success:
                        break
                else:
                    try:
                        node_state = eval(node_str)
                    except:
                        node_state = node_str
                    # logger.info(f'{node_state=}')
                    ground_node_name = node_state["name"]
                    ground_node_state = node_state["state"]
                    if cur_name == ground_node_name and cur_state == ground_node_state:
                        success = True
                        break
                    if success:
                        break

            if success:
                node_goal_exact.append(
                    {"name": cur_name, "state": cur_state}
                )  # this can also be {'id': cur_id, 'class_name': cur_name, 'state': cur_state}, recommended
                # final_states.append({'id': cur_id, 'class_name': cur_name, 'state': cur_state})

    # logger.info('diff in edges', diff_in_final['edges'])
    for cur_edge in diff_in_final["edges"]:
        cur_from_id, cur_relation, cur_to_id = (
            cur_edge["from_id"],
            cur_edge["relation_type"],
            cur_edge["to_id"],
        )
        cur_from_name, cur_to_name = (
            id_2_name_dict[cur_from_id],
            id_2_name_dict[cur_to_id],
        )  # type: ignore

        # logger.info(f'{cur_from_name}, {cur_relation}, {cur_to_name}')

        # for edge_str, _ in accurate_edge_state.items():
        #     edge_state = ast.literal_eval(edge_str)
        #     goal_from_name, goal_relation, goal_to_name = edge_state['from_name'], edge_state['relation'], edge_state['to_name']
        #     if cur_from_name == goal_from_name and cur_to_name == goal_to_name and cur_relation == goal_relation:
        #         final_states.append(copy.deepcopy(cur_edge))

        get_cur_from_properties = (
            properties_data[cur_from_name] if cur_from_name in properties_data else []
        )
        get_cur_to_properties = (
            properties_data[cur_to_name] if cur_to_name in properties_data else []
        )
        get_cur_from_properties = sorted(
            get_cur_from_properties, key=lambda prop: prop.value
        )
        get_cur_to_properties = sorted(
            get_cur_to_properties, key=lambda prop: prop.value
        )
        for edge_str in edge_goals:
            try:
                edge_state = eval(edge_str)
            except:
                edge_state = edge_str
            goal_from_name, goal_relation, goal_to_name = (
                edge_state["from_name"],
                edge_state["relation"],
                edge_state["to_name"],
            )
            if "|" in goal_relation:
                goal_relation_candidates = goal_relation.split("|")
            else:
                goal_relation_candidates = [goal_relation]
            if cur_relation not in goal_relation_candidates:
                continue

            is_valid = False
            if "?" in goal_from_name:
                validation_from_name = (
                    f"?{str(get_cur_from_properties)}?"
                    if cur_from_name != "character"
                    else f"?character?"
                )
                goal_from_name_candidates = goal_from_name.split("|")
                if cur_to_name == goal_to_name and at_least_one_matched(
                    validation_from_name, goal_from_name_candidates
                ):
                    is_valid = True
            elif "?" in goal_to_name:
                validation_to_name = (
                    f"?{str(get_cur_to_properties)}?"
                    if cur_to_name != "character"
                    else f"?character?"
                )
                goal_to_name_candidates = goal_to_name.split("|")
                if cur_from_name == goal_from_name and at_least_one_matched(
                    validation_to_name, goal_to_name_candidates
                ):
                    is_valid = True
            else:
                if cur_from_name == goal_from_name and cur_to_name == goal_to_name:
                    is_valid = True

            if is_valid:
                tmp = {
                    "from_name": cur_from_name,
                    "relation": cur_relation,
                    "to_name": cur_to_name,
                }
                edge_goal_exact.append(tmp)

    return node_goal_exact, edge_goal_exact


def check_no_hallucination_in_action(action_list):
    for action_dict in action_list:
        for predicate_name, params in action_dict.items():
            predicate_name = predicate_name.upper()
            if predicate_name not in valid_actions.keys():
                logger.info(f"  Action {predicate_name} not in valid actions")
                return False
    return True


def check_no_hallucination_in_arg(action_list, relevant_id):
    for action_dict in action_list:
        for action, objects in action_dict.items():
            for obj in objects:
                if relevant_id.get(obj, None) is None:
                    return False
    return True


def check_action_grammar(action_list):
    for action_dict in action_list:
        for predicate_name, params in action_dict.items():
            params.remove("") if "" in params else None
            if len(params) != valid_actions[predicate_name][1]:
                logger.info(
                    f"Action {predicate_name} has {params} arguments, but expected number is {valid_actions[predicate_name][1]}"
                )
                return (
                    False,
                    f"Action {predicate_name} has {params} arguments, but expected number is {valid_actions[predicate_name][1]}",
                )
    return True, None


def set_error_type(error_dict, error_type):
    error_str = ""
    if error_type == 0:
        error_str = "wrong_order"
    elif error_type == 1:
        error_str = "missing_step"
    elif error_type == 2:
        error_str = "affordance"
    elif error_type == 3:
        error_str = "unseen"
    elif error_type == 4:
        error_str = "additional_step"
    elif error_type == 5:
        error_str = "other"
    else:
        assert False, f"Unknown Error Type: {error_type}"
    error_dict[error_str] += 1
    return error_str, error_dict


def check_fg_satisfied_in_prev_states(
    history_env_states_list,
    error_code,
    error_msg,
    node_goals,
    edge_goals,
    acting_char_id,
):
    if error_code == 1:
        logger.info("Check whether it is wrong order")
        found = False
        for history_env_states in history_env_states_list:
            if validate_programs_based_on_goal_states(
                history_env_states, node_goals, edge_goals, acting_char_id
            ):
                found = True
                break
        if found:
            error_code = 0
            error_msg = "Wrong temporal order. Found the final goal satisfied in previous states."
    return error_code, error_msg


def get_candidate_id(file_id, task_ans_list):
    ans_list = [ast.literal_eval(x) for x in task_ans_list]
    for f_id, ans in ans_list:
        if f_id == file_id:
            return ans
    assert False, f"file id {file_id} not found in task ans list"


def get_initial_states_and_final_goals_wo_id(planner, goal, relevant_nodes):
    room_nodes = [
        "bathroom",
        "kitchen",
        "living_room",
        "bedroom",
        "bathroom",
        "hallway",
        "dining_room",
    ]
    properties_data = utils.load_properties_data()
    init_dict = planner.init_state.to_dict()
    id_2_name_dict = planner.id_to_name
    diff_in_init, diff_in_final = planner.filter_unique_subdicts(
        init_dict, planner.final_state_dict
    )
    # logger.info(f'{id_2_name_dict=}')

    name2id = {}
    # first, we obtain the init states
    ## we first deal with nodes
    initial_states = []
    for node in diff_in_init["nodes"]:
        id, name, states = node["id"], node["class_name"], node["states"]
        name2id[name] = id
        real_obj_name = f"{name}"
        for s in states:
            predicate_name = state_transform_dictionary[s]
            predicate = f"{predicate_name}({real_obj_name})"
            initial_states.append(predicate)
        if name == "computer":
            if "PLUGGED_IN(computer)" not in predicate:
                initial_states.append("PLUGGED_OUT(computer)")
        if name == "floor_lamp":
            if "PLUGGED_IN(floor_lamp)" not in predicate:
                initial_states.append("PLUGGED_OUT(floor_lamp)")
        if name == "dishwasher":
            if "PLUGGED_IN(dishwasher)" not in predicate:
                initial_states.append("PLUGGED_OUT(dishwasher)")

    # logger.info(f'{relevant_nodes=}')
    relevant_node_set = set()
    for node_dict in relevant_nodes:
        obj_name = node_dict["obj_name"]
        property_list = node_dict["properties"]
        relevant_node_set.add(obj_name)
        for property_name in property_list:
            property_name = property_name.lower()
            predicate = f"{property_name}({obj_name})"
            # logger.info(f'{predicate=}')
            initial_states.append(predicate)

    logger.info(f"{relevant_node_set=}")
    relevant_edges = []
    for edge in init_dict["edges"]:
        from_id, relation, to_id = edge["from_id"], edge["relation_type"], edge["to_id"]
        from_name, to_name = id_2_name_dict[from_id], id_2_name_dict[to_id]
        if from_name in relevant_node_set and to_name in relevant_node_set:
            relevant_edges.append(edge)
    logger.info(f"{relevant_edges=}")

    relevant_edges += diff_in_init["edges"]

    ## we then deal with edges
    unpaired_between_list = []
    for edge in relevant_edges:
        from_id, relation, to_id = edge["from_id"], edge["relation_type"], edge["to_id"]
        from_name, to_name = id_2_name_dict[from_id], id_2_name_dict[to_id]

        # note that between is a special relation
        if relation == "BETWEEN":
            b_tuple = (from_id, to_id)
            tmp_between_list = copy.deepcopy(unpaired_between_list)
            for cur_from_id, cur_to_id in tmp_between_list:
                if cur_from_id == from_id:
                    cur_to_name = id_2_name_dict[cur_to_id]
                    name2id[cur_to_name] = cur_to_id
                    name2id[to_name] = to_id
                    name2id[from_name] = from_id
                    obj_1 = f"{from_name}"
                    obj_2 = f"{to_name}"
                    obj_3 = f"{cur_to_name}"
                    predicate = f"BETWEEN({obj_1}, {obj_2}, {obj_3})"
                    # logger.info(predicate)
                    initial_states.append(predicate)
                    unpaired_between_list.remove((cur_from_id, cur_to_id))
                elif cur_to_id == to_id:
                    cur_from_name = id_2_name_dict[cur_from_id]
                    name2id[cur_to_name] = cur_to_id
                    name2id[to_name] = to_id
                    name2id[from_name] = from_id
                    obj_1 = f"{to_name}"
                    obj_2 = f"{from_name}"
                    obj_3 = f"{cur_from_name}"
                    predicate = f"BETWEEN({obj_1}, {obj_2}, {obj_3})"
                    # logger.info(predicate)
                    initial_states.append(predicate)
                    unpaired_between_list.remove((cur_from_id, cur_to_id))
                else:
                    unpaired_between_list.append(b_tuple)
        else:
            if relation == "ON":
                if from_name == "character" and to_name != "character":
                    relation = "ONTOP"
                elif from_name != "character" and to_name == "character":
                    relation = "ON_CHAR"
                else:
                    relation = "OBJ_ONTOP"
            elif relation == "SITTING":
                relation = "SITTINGRELATION"
            elif relation == "INSIDE":
                if from_name == "character" or to_name == "character":
                    relation = "INSIDE"
                elif from_name in room_nodes or to_name in room_nodes:
                    relation = "INSIDE_ROOM"
                else:
                    relation = "OBJ_INSIDE"
            elif relation == "CLOSE":
                if from_name == "character" or to_name == "character":
                    relation = "NEXT_TO"
                else:
                    relation = "OBJ_NEXT_TO"
            logger.info(f"init: {from_name} {relation} {to_name}")
            name2id[to_name] = to_id
            name2id[from_name] = from_id
            obj_1 = f"{from_name}"
            obj_2 = f"{to_name}"
            predicate_name = state_transform_dictionary[relation]
            predicate = f"{predicate_name}({obj_1}, {obj_2})"
            # logger.info(predicate)
            initial_states.append(predicate)

    initial_states = list(set(initial_states))
    # then, we obtain the final state with wildcards being changed with realistic objects
    final_states = []
    # logger.info("==we then print out all final goal states==")
    selected_node_state, selected_edge_state, accurate_edge_state, actions = (
        goal["selected_node_state"],
        goal["selected_edge_state"],
        goal["accurate_edge_state"],
        goal["actions"],
    )

    ## we first deal with node states
    # @deprecated words: [we need a sign to rule out those same name (usually, same type of items should both be satisfied)]
    # @update words: [we do not need a sign. as long as a node is listed, it then must be satisfied, no matter what]
    for cur_node in diff_in_final["nodes"]:
        cur_id, cur_name, cur_states = (
            cur_node["id"],
            cur_node["class_name"],
            cur_node["states"],
        )
        for cur_state in cur_states:
            # as long as this state can match some success pattern, then this technically must be satisfied (remember 'three stacked plates' case)
            success = False
            for node_str, _ in selected_node_state.items():
                node_str_candidates = node_str.split("|")
                for node_candidate in node_str_candidates:
                    node_state = ast.literal_eval(node_candidate)
                    ground_node_name = node_state["name"]
                    ground_node_state = node_state["state"]
                    if cur_name == ground_node_name and cur_state == ground_node_state:
                        success = True
                        break
                if success:
                    break
            if success:
                name2id[cur_name] = cur_id
                real_obj_name = f"{cur_name}"
                predicate_name = state_transform_dictionary[cur_state]
                predicate = f"{predicate_name}({real_obj_name})"
                # logger.info(predicate)
                final_states.append(predicate)

    logger.info(f"goal node; {final_states}")
    ## we then deal with edge cases
    predicates = set()
    unpaired_between_list = []
    for cur_edge in diff_in_final["edges"]:
        cur_from_id, cur_relation, cur_to_id = (
            cur_edge["from_id"],
            cur_edge["relation_type"],
            cur_edge["to_id"],
        )
        cur_from_name, cur_to_name = (
            id_2_name_dict[cur_from_id],
            id_2_name_dict[cur_to_id],
        )

        # below is exact matching
        for edge_str, _ in accurate_edge_state.items():
            edge_state = ast.literal_eval(edge_str)
            goal_from_name, goal_relation, goal_to_name = (
                edge_state["from_name"],
                edge_state["relation"],
                edge_state["to_name"],
            )
            if (
                cur_from_name == goal_from_name
                and cur_to_name == goal_to_name
                and cur_relation == goal_relation
            ):
                if cur_relation == "BETWEEN":
                    b_tuple = (cur_from_id, cur_to_id)
                    tmp_between_list = copy.deepcopy(unpaired_between_list)
                    for tmp_from_id, tmp_to_id in tmp_between_list:
                        if tmp_from_id == cur_from_id:
                            tmp_to_name = id_2_name_dict[tmp_to_id]
                            name2id[cur_to_name] = cur_to_id
                            name2id[to_name] = to_id
                            name2id[from_name] = from_id
                            obj_1 = f"{from_name}"
                            obj_2 = f"{to_name}"
                            obj_3 = f"{cur_to_name}"
                            predicate = f"BETWEEN({obj_1}, {obj_2}, {obj_3})"
                            predicates.add(predicate)
                            unpaired_between_list.remove((tmp_from_id, tmp_to_id))
                        elif tmp_to_id == cur_to_id:
                            tmp_from_name = id_2_name_dict[tmp_from_id]
                            name2id[cur_to_name] = cur_to_id
                            name2id[to_name] = to_id
                            name2id[from_name] = from_id
                            obj_1 = f"{from_name}"
                            obj_2 = f"{to_name}"
                            obj_3 = f"{cur_to_name}"
                            predicate = f"BETWEEN({obj_1}, {obj_2}, {obj_3})"
                            predicates.add(predicate)
                            unpaired_between_list.remove((tmp_from_id, tmp_to_id))
                        else:
                            unpaired_between_list.append(b_tuple)
                else:
                    if cur_relation == "ON":
                        if cur_from_name == "character" and cur_to_name != "character":
                            cur_relation = "ONTOP"
                        elif (
                            cur_from_name != "character" and cur_to_name == "character"
                        ):
                            cur_relation = "ON_CHAR"
                        else:
                            cur_relation = "OBJ_ONTOP"
                    elif cur_relation == "SITTING":
                        cur_relation = "SITTINGRELATION"
                    elif cur_relation == "INSIDE":
                        if cur_from_name == "character" or cur_to_name == "character":
                            cur_relation = "INSIDE"
                        elif cur_from_name in room_nodes or cur_to_name in room_nodes:
                            cur_relation = "INSIDE_ROOM"
                        else:
                            cur_relation = "OBJ_INSIDE"
                    elif cur_relation == "CLOSE":
                        if cur_from_name == "character" or cur_to_name == "character":
                            cur_relation = "NEXT_TO"
                        else:
                            cur_relation = "OBJ_NEXT_TO"
                    logger.info(f"goals: {cur_from_name} {cur_relation} {cur_to_name}")
                    name2id[cur_to_name] = cur_to_id
                    name2id[cur_from_name] = cur_from_id
                    obj_1 = f"{cur_from_name}"
                    obj_2 = f"{cur_to_name}"
                    predicate_name = state_transform_dictionary[cur_relation]
                    predicate = f"{predicate_name}({obj_1}, {obj_2})"
                    predicates.add(predicate)

        # below is wildcard matching
        get_cur_from_properties = (
            properties_data[cur_from_name] if cur_from_name in properties_data else []
        )
        get_cur_to_properties = (
            properties_data[cur_to_name] if cur_to_name in properties_data else []
        )
        get_cur_from_properties = sorted(
            get_cur_from_properties, key=lambda prop: prop.value
        )
        get_cur_to_properties = sorted(
            get_cur_to_properties, key=lambda prop: prop.value
        )
        for edge_str, _ in selected_edge_state.items():
            edge_state = ast.literal_eval(edge_str)
            goal_from_name, goal_relation, goal_to_name = (
                edge_state["from_name"],
                edge_state["relation"],
                edge_state["to_name"],
            )
            goal_relation_candidates = goal_relation.split("|")
            if cur_relation not in goal_relation_candidates:
                continue

            is_valid = False
            if "?" in goal_from_name:
                validation_from_name = (
                    f"?{str(get_cur_from_properties)}?"
                    if cur_from_name != "character"
                    else f"?character?"
                )
                goal_from_name_candidates = goal_from_name.split("|")
                if cur_to_name == goal_to_name and at_least_one_matched(
                    validation_from_name, goal_from_name_candidates
                ):
                    is_valid = True
            elif "?" in goal_to_name:
                validation_to_name = (
                    f"?{str(get_cur_to_properties)}?"
                    if cur_to_name != "character"
                    else f"?character?"
                )
                goal_to_name_candidates = goal_to_name.split("|")
                if cur_from_name == goal_from_name and at_least_one_matched(
                    validation_to_name, goal_to_name_candidates
                ):
                    is_valid = True

            if is_valid:
                if cur_relation == "BETWEEN":
                    b_tuple = (cur_from_id, cur_to_id)
                    tmp_between_list = copy.deepcopy(unpaired_between_list)
                    for tmp_from_id, tmp_to_id in tmp_between_list:
                        if tmp_from_id == cur_from_id:
                            tmp_to_name = id_2_name_dict[tmp_to_id]
                            name2id[cur_from_name] = cur_from_id
                            name2id[cur_to_name] = cur_to_id
                            name2id[tmp_to_name] = tmp_to_id
                            obj_1 = f"{cur_from_name}"
                            obj_2 = f"{cur_to_name}"
                            obj_3 = f"{tmp_to_name}"
                            predicate = f"BETWEEN({obj_1}, {obj_2}, {obj_3})"
                            predicates.add(predicate)
                            unpaired_between_list.remove((tmp_from_id, tmp_to_id))
                        elif tmp_to_id == cur_to_id:
                            tmp_from_name = id_2_name_dict[tmp_from_id]
                            name2id[cur_from_name] = cur_from_id
                            name2id[cur_to_name] = cur_to_id
                            name2id[tmp_to_name] = tmp_to_id
                            obj_1 = f"{cur_to_name}.{cur_to_id}"
                            obj_2 = f"{cur_from_name}.{cur_from_id}"
                            obj_3 = f"{tmp_from_name}.{tmp_from_id}"
                            predicate = f"BETWEEN({obj_1}, {obj_2}, {obj_3})"
                            predicates.add(predicate)
                            unpaired_between_list.remove((tmp_from_id, tmp_to_id))
                        else:
                            unpaired_between_list.append(b_tuple)
                else:
                    if cur_relation == "ON":
                        if cur_from_name == "character" and cur_to_name != "character":
                            cur_relation = "ONTOP"
                        elif (
                            cur_from_name != "character" and cur_to_name == "character"
                        ):
                            cur_relation = "ON_CHAR"
                        else:
                            cur_relation = "OBJ_ONTOP"
                    elif cur_relation == "SITTING":
                        cur_relation = "SITTINGRELATION"
                    elif cur_relation == "INSIDE":
                        if cur_from_name == "character" or cur_to_name == "character":
                            cur_relation = "INSIDE"
                        elif cur_from_name in room_nodes or cur_to_name in room_nodes:
                            relation = "INSIDE_ROOM"
                        else:
                            cur_relation = "OBJ_INSIDE"
                    elif cur_relation == "CLOSE":
                        if cur_from_name == "character" or cur_to_name == "character":
                            cur_relation = "NEXT_TO"
                        else:
                            cur_relation = "OBJ_NEXT_TO"
                    logger.info(f"goals: {cur_from_name} {cur_relation} {cur_to_name}")
                    name2id[cur_from_name] = cur_from_id
                    name2id[cur_to_name] = cur_to_id
                    obj_1 = f"{cur_from_name}"
                    obj_2 = f"{cur_to_name}"
                    predicate_name = state_transform_dictionary[cur_relation]
                    predicate = f"{predicate_name}({obj_1}, {obj_2})"
                    predicates.add(predicate)
    ### output the predicates in edges
    for p in predicates:
        # logger.info(p)
        final_states.append(p)

    ## we then deal with actions
    actions_states = []
    # logger.info("==we then print out all final goal actions==")
    for action in actions:
        action_candidates = action.split("|")
        action_candidates = [f"{a.upper().replace(' ', '')}" for a in action_candidates]
        final_action_str = " or ".join(action_candidates)
        # logger.info(final_action_str)
        actions_states.append(final_action_str)
    return initial_states, final_states, actions_states, name2id


def transform_goal_states(goal_states):
    pddl_string = "(:goal\n    (and\n"
    for state in goal_states:
        predicate = state.split("(")[0].lower()
        arguments = state.split("(")[1].rstrip(")").replace(",", "")
        pddl_string += f"        ({predicate} {arguments})\n"
    pddl_string += "    )\n)"
    return pddl_string


def transform_initial_states(initial_states):
    pddl_string = "(:init\n"
    for state in initial_states:
        predicate = state.split("(")[0].lower()
        arguments = state.split("(")[1].rstrip(")").replace(",", "")
        pddl_string += f"    ({predicate} {arguments})\n"
    pddl_string += ")"
    return pddl_string


def transform_objects_to_pddl(relevant_nodes):
    characters = []
    objects = []
    for node in relevant_nodes:
        obj_name = node["obj_name"]
        if obj_name == "character":
            characters.append(obj_name)
        else:
            objects.append(obj_name)
    pddl_string = "(:objects\n"
    if characters:
        pddl_string += "    " + " ".join(set(characters)) + " - character\n"
    if objects:
        pddl_string += "    " + " ".join(set(objects)) + " - object\n"
    pddl_string += ")"
    return pddl_string


def create_pddl_problem(
    domain_path, initial_states, goal_states, relevant_nodes, task_name
):
    with open(domain_path, "r") as file:
        domain_content = file.read()
    objects_section = transform_objects_to_pddl(relevant_nodes)
    initial_state_section = transform_initial_states(initial_states)
    goal_section = transform_goal_states(goal_states)
    task_name_concat = "_".join(task_name.split())
    problem_content = f"""(define (problem {task_name_concat})
    (:domain virtualhome)
    {objects_section}
    {initial_state_section}
    {goal_section}
    )
    """
    return problem_content


def parse_pddl_plan(actions, pddl_plan):
    """
    Parses the PDDL plan and creates an ordered dictionary of actions with details.
    It replaces placeholders in preconditions and effects with actual parameters while keeping
    the 'parameters' part intact.
    Args:
    actions (dict): Dictionary of actions from the PDDL domain.
    pddl_plan (list of str): List of actions from the planner output.
    Returns:
    OrderedDict: Ordered dictionary where keys are actions and values are dictionaries of 'parameters', 'preconditions', and 'effects'.
    """
    plan_details = OrderedDict()
    for action_entry in pddl_plan:
        parts = action_entry.split()
        action_name = parts[0]
        parameters = parts[1:]
        if action_name in actions:
            action_def = actions[action_name]
            param_details = action_def["parameters"]
            precondition = action_def["precondition"]
            effect = action_def["effect"]
            param_placeholders = re.findall(r"\?(\w+)", param_details)
            param_map = {f"?{ph}": p for ph, p in zip(param_placeholders, parameters)}
            for placeholder, real_value in param_map.items():
                precondition = precondition.replace(placeholder, real_value)
                effect = effect.replace(placeholder, real_value)
            plan_details[action_entry] = {
                "parameters": param_details,
                "parameter_match": param_map,
                "preconditions": precondition,
                "effects": effect,
            }
    return plan_details


def extract_action_details(domain_file_path="", content=None):
    if content is None:
        with open(domain_file_path, "r") as file:
            content = file.read()
    content = re.sub(r";.*$", "", content, flags=re.MULTILINE)
    content = " ".join(content.split())

    def extract_block(content, start_idx):
        open_paren = 1
        i = start_idx
        if content[i] == ")":
            return ")"
        while open_paren > 0:
            i += 1
            if content[i] == "(":
                open_paren += 1
            elif content[i] == ")":
                open_paren -= 1
        return content[start_idx : i + 1]

    actions = {}
    action_pattern = re.compile(r"\(:action\s+(\w+)")
    idx = 0
    while True:
        action_match = action_pattern.search(content, idx)
        if not action_match:
            break
        action_name = action_match.group(1)
        start = action_match.end()
        # Locate the indices for parameters, precondition, and effect
        param_idx = content.find(":parameters", start)
        precon_idx = content.find(":precondition", start)
        effect_idx = content.find(":effect", start)
        if param_idx == -1 or precon_idx == -1 or effect_idx == -1:
            break
        # Extract the blocks based on balanced parentheses
        params = extract_block(content, content.find("(", param_idx) + 1)
        try:
            preconds = extract_block(content, content.find("(", precon_idx) + 1)
        except:
            preconds = "()"
        try:
            effects = extract_block(content, content.find("(", effect_idx) + 1)
        except:
            effects = "()"
        # Clean text and add to the actions dictionary
        action_param = "(" + " ".join(params.split())
        action_precond = "(" + " ".join(preconds.split())
        action_effects = "(" + " ".join(effects.split())
        action_param = action_param.replace(") )", "))")
        action_precond = action_precond.replace(") )", "))")
        action_effects = action_effects.replace(") )", "))")
        actions[action_name] = {
            "action_name": action_name,
            "action_parameters": action_param,
            "action_preconditions": action_precond,
            "action_effects": action_effects,
        }
        # Update the search index to continue past this action
        idx = effects.find(")") + effect_idx + 1
    return actions


def complete_pddl_domain(
    action_dict,
    gold_action_dict,
    domain_pd_path,
    file_id,
    domain_path,
    action_name_key=None,
):
    domain_pd = open(domain_pd_path, "r").read()
    # write each action into the pddl domain file
    if action_name_key is not None:
        domain_file = os.path.join(domain_path, f"{file_id}_{action_name_key}.pddl")
    else:
        domain_file = os.path.join(domain_path, f"{file_id}.pddl")
    for action_name in action_dict.keys():
        action = action_dict[action_name]
        domain_pd += f"\n\n    (:action {action_name}\n        :parameters {action['action_parameters']}\n        :precondition {action['action_preconditions']}\n        :effect {action['action_effects']}\n    )"
    unrelated_actions = set(gold_action_dict.keys()) - set(action_dict.keys())
    for action_name in unrelated_actions:
        action = gold_action_dict[action_name]
        domain_pd += f"\n\n    (:action {action_name}\n        :parameters {action['action_parameters']}\n        :precondition {action['action_preconditions']}\n        :effect {action['action_effects']}\n    )"
    domain_pd += ")"
    with open(domain_file, "w") as f:
        f.write(domain_pd)
    return domain_file


def get_relevant_nodes(planner: MotionPlanner):
    init_dict = planner.init_state.to_dict()
    diff_a, diff_b = planner.filter_unique_subdicts(init_dict, planner.final_state_dict)
    existing_ids = set()
    add_ids = set()
    for dic in [diff_a, diff_b]:
        for d in dic["nodes"]:
            existing_ids.add(d["id"])
        for d in dic["edges"]:
            add_ids.add(d["from_id"])
            add_ids.add(d["to_id"])
    all_ids = existing_ids.union(add_ids)

    all_nodes = []
    for node in init_dict["nodes"]:
        tmp = {}
        node_id = node["id"]
        if node_id in all_ids:
            tmp["id"] = node_id
            tmp["obj_name"] = node["class_name"]
            tmp["category"] = node["category"]
            tmp["properties"] = node["properties"]
            all_nodes.append(tmp)
    return all_nodes, all_ids


def group_by_value(d):
    from collections import defaultdict

    grouped_dict = defaultdict(list)
    for key, value in d.items():
        grouped_dict[value].append(key)
    grouped_dict = dict(grouped_dict)
    return grouped_dict


def group_by_index(input_list):
    result = {}
    for item in input_list:
        id_number, index_number = eval(item)
        if index_number == -1:
            continue
        if index_number in result:
            result[index_number].append(id_number)
        else:
            result[index_number] = [id_number]
    return result


def calculate_precision_recall_f1(d):
    new_d = {}
    for k in d.keys():
        if d[k] == [0, 0, 0]:
            continue
        TP = d[k][0]
        FP = d[k][1]
        FN = d[k][2]
        precision = TP / (TP + FP) if TP + FP != 0 else 0
        recall = TP / (TP + FN) if TP + FN != 0 else 0
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall != 0
            else 0
        )
        new_d[k] = [TP, FP, FN, precision, recall, f1]
    return new_d


def print_precision_recall_f1(d):
    for k in d.keys():
        logger.info(f"{k} precision: {d[k][3]:.2f}, recall: {d[k][4]:.2f}, f1: {d[k][5]:.2f}")


def calculate_success_rate(d):
    new_d = {}
    for k in d.keys():
        if d[k] == [0, 0]:
            continue
        success_rate = d[k][0] / d[k][1]
        new_d[k] = [d[k][0], d[k][1], success_rate]
    return new_d


def calculate_success_rate_by_category(d):
    new_d = {}
    for cat in d.keys():
        new_d[cat] = {}
        for k in d[cat].keys():
            if d[cat][k] == [0, 0]:
                continue
            success_rate = d[cat][k][0] / d[cat][k][1] if d[cat][k][1] != 0 else 0.0
            new_d[cat][k] = [d[cat][k][0], d[cat][k][1], success_rate]
    return new_d


def print_success_rate(d):
    for k in d.keys():
        logger.info(f"{k} success rate: {d[k][2]:.4f}")


def print_success_rate_by_category(d):
    for cat in d.keys():
        logger.info(f"{cat} success rate:")
        for k in d[cat].keys():
            logger.info(
                f"  {k} success rate: {d[cat][k][2]:.4f}, success: {d[cat][k][0]}, total: {d[cat][k][1]}"
            )


def precision_recall_f1(TP, FP, FN):
    precision = TP / (TP + FP) if TP + FP != 0 else 0.0
    recall = TP / (TP + FN) if TP + FN != 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall != 0
        else 0.0
    )
    return precision, recall, f1

def extract_model_names(llm_response_dir):
    model_names = []
    files = os.listdir(llm_response_dir)
    pattern = re.compile(r"^(.*?)_outputs\.json$")
    for file in files:
        match = pattern.match(file)
        if match:
            model_names.append(match.group(1))
    return model_names