import os
import json
import ast
import re
import copy
import logging
logger = logging.getLogger(__name__)
from collections import OrderedDict

import virtualhome_eval.simulation.evolving_graph.utils as utils

class Vocabulary:
    def __init__(self, file_path, id_to_name_dict):
        self.vocab = self.load_vocab(file_path)
        self.state_param_dict = self.get_tl_predicates_param_dict()
        self.actio_param_dict = self.get_subgoal_actions()
        self.id_to_name_dict = id_to_name_dict
        
    def load_vocab(self, file_path):
        with open(file_path, 'r') as f:
            vocab = json.load(f)
        return vocab
    
    def get_vocab(self):
        return self.vocab
    
    def get_tl_predicates(self):
        return self.vocab['tl_predicates']
    
    def get_actions_all(self):
        return self.vocab['actions']
    
    def get_actions_all_in_list(self):
        return list(self.vocab['actions'].keys())
    
    def get_subgoal_actions(self):
        return self.vocab['subgoal_actions']
    
    def get_subgoal_actions_in_list(self):
        return list(self.vocab['subgoal_actions'].keys())
    
    def get_vh_info(self):
        '''
        Returns the vocabulary for properties, states and relations in VH
        '''
        return self.vocab['properties'], self.vocab['vh_states'], self.vocab['vh_relations']
    
    def get_tl_to_vh_predicates_dict(self):
        return self.vocab['tl_predicates_to_vh']
    
    def get_vh_states_to_tl_dict(self):
        return self.vocab['vh_states_to_tl']
    
    def get_vh_relations_to_tl_dict(self):
        return self.vocab['vh_relations_to_tl']
    
    def get_tl_predicates_param_dict(self):
        tl_predicates_to_vh = self.get_tl_to_vh_predicates_dict()
        vh_states_to_tl = self.get_vh_states_to_tl_dict()
        vh_relations_to_tl = self.get_vh_relations_to_tl_dict()
        vh_properties, vh_states, vh_relations = self.get_vh_info()
        param_dict = {}
        for tl_predicate in self.get_tl_predicates():
            vh_predicate = tl_predicates_to_vh[tl_predicate]
            param_num = -1
            if vh_predicate in vh_properties:
                param_num = 1
            elif vh_predicate in vh_states and vh_states_to_tl[vh_predicate] == tl_predicate:
                param_num = 1
            elif vh_predicate in vh_relations and vh_relations_to_tl[vh_predicate] == tl_predicate:
                param_num = 2
            param_dict[tl_predicate] = param_num
        return param_dict
    

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


def my_scene_evaluate(
    final_state_dict,
    selected_node_goals,
    selected_edge_goals,
    character_id,
    action_seq,
    action_goals,
):
    nodes = final_state_dict["nodes"]
    edges = final_state_dict["edges"]
    node_tot_num = len(selected_node_goals)
    node_success_num = 0
    edge_tot_num = len(selected_edge_goals)
    edge_success_num = 0
    action_tot_num = len(action_goals)
    action_success_num = 0
    for node_dict in nodes:
        cur_id = node_dict["id"]
        cur_class_name = node_dict["class_name"]
        cur_states = node_dict["states"]
        for node_goal in selected_node_goals:
            goal_id = node_goal["id"]
            goal_class_name = node_goal["class_name"]
            goal_state = node_goal["state"]
            if cur_id == goal_id and cur_class_name == goal_class_name and goal_state in cur_states:
                node_success_num += 1
    for edge_dict in edges:
        cur_from_id = edge_dict["from_id"]
        cur_to_id = edge_dict["to_id"]
        cur_relation = edge_dict["relation_type"]
        for edge_goal in selected_edge_goals:
            goal_from_id = edge_goal["from_id"]
            goal_to_id = edge_goal["to_id"]
            goal_relation = edge_goal["relation_type"]
            if cur_from_id == goal_from_id and cur_to_id == goal_to_id and cur_relation == goal_relation:
                edge_success_num += 1
                break
    if len(action_goals) > 0:
        for action_goal in action_goals:
            action_candidates = action_goal.split("|")
            success = False
            for action in action_candidates:
                found = False
                for action_instruction in action_seq:
                    if action in action_instruction:
                        found = True
                        break
                if found:
                    success = True
                    action_success_num += 1
                    break
            if not success:
                break
    tot_success_num = node_success_num + edge_success_num + action_success_num
    tot_num = node_tot_num + edge_tot_num + action_tot_num
    return node_tot_num, node_success_num, edge_tot_num, edge_success_num, action_tot_num, action_success_num, tot_num, tot_success_num


def traj_eval_stats(eval_stat_path):
    model_name = os.path.basename(eval_stat_path).split("_")[0]
    with open(eval_stat_path, "r") as f:
        stats = json.load(f)
    num_correct = 0
    parse_errors = 0
    hallucination_errors = 0
    runtime_errors = 0
    goal_errors = 0
    incorrect_param_length_num = 0
    obj_not_in_scene_num = 0
    unknown_primitive_num = 0
    executable_num = 0
    tot_runtime_errors = 0
    missing_step_errors = 0
    additional_step_errors = 0
    affordance_errors = 0
    wrong_temporal_order_errors = 0

    tmp_list = []
    for task, task_info in stats.items():
        success = task_info['success']
        if success:
            num_correct += 1
            tmp_list.append(task.replace('scene_1_',''))
        info = task_info['info']
        assert info is not None, f'info is None for task {task}'
        info = ast.literal_eval(info)
        error_type = info[0]
        if error_type == 'NotParseable' or error_type == 'Hallucination':
            if error_type == 'NotParseable':
                parse_errors += 1
            elif error_type == 'Hallucination':
                hallucination_errors += 1
                error_dict = info[1]
                if 'error_type' in error_dict and error_dict['error_type'] == 'UnknownPrimitive':
                    unknown_primitive_num += 1
                else:
                    if error_dict['IncorrectParamLength']:
                        incorrect_param_length_num += 1
                    if error_dict['ObjectNotInScene']:
                        obj_not_in_scene_num += 1
        elif error_type == 'GoalUnreachable':
            goal_errors += 1
            executable_num += 1
        
        else:
            if error_type == 'Runtime':
                runtime_errors += 1
                executable = info[1]
                if executable:
                    executable_num += 1
            else:
                executable_num += 1
            runtime_report = info[-2]
            get_one_additional = False
            for error in runtime_report:
                error_info = error['error_info']
                error_type = error_info['error_type']
                real_info = error_info['error_info']
                tot_runtime_errors += len(error_type)
                for t in error_type:
                    if 'missing_step' in t.lower():
                        missing_step_errors += 1
                    elif 'additional_step' in t.lower():
                        if not get_one_additional:
                            additional_step_errors += 1
                            get_one_additional = True
                    elif 'affordance' in t.lower():
                        affordance_errors += 1
                    elif 'wrong_temporal_order' in t.lower():
                        wrong_temporal_order_errors += 1
    tot_num = len(stats)
    traj_stats = {
        "execution_success_rate": round(executable_num/tot_num, 4) if tot_num > 0 else 0,
        "grammar_error": {
            "parsing": round(parse_errors/tot_num, 4) if tot_num > 0 else 0,
            "hallucination": round((hallucination_errors-incorrect_param_length_num)/tot_num, 4) if tot_num > 0 else 0,
            "predicate_argument_number": round(incorrect_param_length_num/tot_num, 4) if tot_num > 0 else 0,
        }, 
        "runtime_error": {
            "wrong_order": round(wrong_temporal_order_errors/tot_num, 4) if tot_num > 0 else 0,
            "missing_step": round(missing_step_errors/tot_num, 4) if tot_num > 0 else 0,
            "additional_step": round(additional_step_errors/tot_num, 4) if tot_num > 0 else 0,
            "affordance": round(affordance_errors/tot_num, 4) if tot_num > 0 else 0,
        },
    }
    return traj_stats

def get_all_scene_goal_stats(args):
    resource_dir = args.resource_dir
    task_dict_path = os.path.join(resource_dir, "task_state_LTL_formula_accurate.json")
    task_dict = json.load(open(task_dict_path, 'r'))
    scene_str = 'scene_1'
    task_dict = task_dict[scene_str]
    stat_dict = {}
    for task_name, task_info in task_dict.items():
        for file_id, file_info in task_info.items():
            file_info = file_info['vh_goal']
            action_goal_num = len(file_info['actions'])
            node_goal_num = 0
            edge_goal_num = 0
            
            identifier = scene_str + '_' + file_id
            goals = file_info['goal']
            for goal in goals:
                if 'id' in goal and 'class_name' in goal and 'state' in goal:
                    node_goal_num += 1
                elif 'from_id' in goal and 'to_id' in goal and 'relation_type' in goal:
                    edge_goal_num += 1
            
            stat_dict[identifier] = {
                'node_tot_num': node_goal_num,
                'edge_tot_num': edge_goal_num,
                'action_tot_num': action_goal_num,
            }
            # if '258_2' in identifier:
            #     print(stat_dict[identifier])
    return stat_dict

def goal_eval_stats(eval_stat_path, args):
    model_name = os.path.basename(eval_stat_path).split("_")[0]
    with open(eval_stat_path, "r") as f:
        stats = json.load(f)
    num_success = 0
    node_tot_num = 0
    node_success_num = 0
    edge_tot_num = 0
    edge_success_num = 0
    action_tot_num = 0
    action_success_num = 0
    full_tot_num = 0
    full_success_num = 0

    tot_stat_dict = get_all_scene_goal_stats(args)

    for id, info in stats.items():
        success = info['success']
        if success:
            num_success += 1
        info = ast.literal_eval(info['info'])
        stat_dict = info[-1]
        if isinstance(stat_dict, dict):
            node_tot_num += stat_dict['node_tot_num']
            node_success_num += stat_dict['node_success_num']
            edge_tot_num += stat_dict['edge_tot_num']
            edge_success_num += stat_dict['edge_success_num']
            action_tot_num += stat_dict['action_tot_num']
            action_success_num += stat_dict['action_success_num']
            full_tot_num += stat_dict['full_tot_num']
            full_success_num += stat_dict['full_success_num']
        else:
            node_tot_num += tot_stat_dict[id]['node_tot_num']
            edge_tot_num += tot_stat_dict[id]['edge_tot_num']
            action_tot_num += tot_stat_dict[id]['action_tot_num']
            full_tot_num += tot_stat_dict[id]['node_tot_num'] + tot_stat_dict[id]['edge_tot_num'] + tot_stat_dict[id]['action_tot_num']
    node_goal_success_rate = (node_success_num / node_tot_num) if node_tot_num > 0 else 0
    edge_goal_success_rate = (edge_success_num / edge_tot_num) if edge_tot_num > 0 else 0
    action_goal_success_rate = (action_success_num / action_tot_num) if action_tot_num > 0 else 0
    overall_goal_success_rate = ((full_success_num) / full_tot_num) if full_tot_num > 0 else 0
    goal_stats = {
        "task_success_rate": round(num_success/len(stats), 4) if len(stats) > 0 else 0,
        "state_goal": round(node_goal_success_rate, 4),
        "relation_goal": round(edge_goal_success_rate, 4),
        "action_goal": round(action_goal_success_rate, 4),
        "overall_goal": round(overall_goal_success_rate, 4)
    }
    return goal_stats


def extract_model_names(llm_response_dir):
    model_names = []
    files = os.listdir(llm_response_dir)
    pattern = re.compile(r"^(.*?)_outputs\.json$")
    for file in files:
        match = pattern.match(file)
        if match:
            model_names.append(match.group(1))
    return model_names