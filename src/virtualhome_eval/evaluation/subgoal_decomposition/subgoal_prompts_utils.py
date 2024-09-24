import os
import ast
import json
import copy
import logging
logger = logging.getLogger(__name__)
from virtualhome_eval.simulation.evolving_graph.eval_utils import *
from virtualhome_eval.simulation.evolving_graph.motion_planner import MotionPlanner

name_equivalence = utils.load_name_equivalence()
properties_data = utils.load_properties_data()
object_placing = utils.load_object_placing()

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
    "ONTOP": "ONTOP", # relation on should be converted into ontop
    "INSIDE": "INSIDE",
    "BETWEEN": "BETWEEN",
    "CLOSE": "NEXT_TO",
    "FACING": "FACING",
    "HOLDS_RH": "HOLDS_RH",
    "HOLDS_LH": "HOLDS_LH",
    "SITTINGRELATION": "ONTOP", # relation sitting should be converted into ontop
}

def prompt_generated(helm_prompt_list, scene_str, file_id):
    for helm_prompt in helm_prompt_list:
        if helm_prompt['identifier'] == f'{scene_str}_{file_id}':
            return True
    return False

def get_relevant_nodes(planner: MotionPlanner):
    init_dict = planner.init_state.to_dict()
    diff_a, diff_b = planner.filter_unique_subdicts(init_dict, planner.final_state_dict)
    existing_ids = set()
    add_ids = set()
    for dic in [diff_a, diff_b]:
        for d in dic['nodes']:
            existing_ids.add(d['id'])
        for d in dic['edges']:
            add_ids.add(d['from_id'])
            add_ids.add(d['to_id'])
    all_ids = existing_ids.union(add_ids)

    all_nodes = []
    for node in init_dict['nodes']:
        tmp = {}
        node_id = node['id']
        if node_id in all_ids:
            tmp['id'] = node_id
            tmp['obj_name'] = node['class_name']
            tmp['category'] = node['category']
            tmp['properties'] = node['properties']
            all_nodes.append(tmp)
    return all_nodes, all_ids


def get_formatted_relevant_nodes(all_nodes):
    relevant_nodes = []
    for node in all_nodes:
        id, obj_name, category, properties = node['id'], node['obj_name'], node['category'], node['properties']
        real_obj_name = f'{obj_name}.{id}'
        relevant_nodes.append(f'| {real_obj_name} | {category} | {properties} |')
    return relevant_nodes

def get_initial_states_and_final_goals(planner: MotionPlanner, node_goals: list, edge_goals:list, action_goals:list):
    init_dict = planner.init_state.to_dict()
    final_state_dict = planner.final_state_dict
    id_2_name_dict = planner.id_to_name
    diff_in_init, diff_in_final = planner.filter_unique_subdicts(init_dict, planner.final_state_dict)
    

    # first, we obtain the init states
    ## we first deal with nodes
    initial_states = []
    # print("==we first print out all initial node states==")
    for node in diff_in_init['nodes']:
        id, name, states = node['id'], node['class_name'], node['states']
        real_obj_name = f'{name}.{id}'
        for s in states:
            predicate_name = state_transform_dictionary[s]
            predicate = f'{predicate_name}({real_obj_name})'
            initial_states.append(predicate)
    ## we then deal with edges
    unpaired_between_list = []
    for edge in diff_in_init['edges']:
        from_id, relation, to_id = edge['from_id'], edge['relation_type'], edge['to_id']
        from_name, to_name = id_2_name_dict[from_id], id_2_name_dict[to_id]
        
        # note that between is a special relation
        if relation == 'BETWEEN':
            b_tuple = (from_id, to_id)
            tmp_between_list = copy.deepcopy(unpaired_between_list)
            for cur_from_id, cur_to_id in tmp_between_list:
                if cur_from_id == from_id:
                    cur_to_name = id_2_name_dict[cur_to_id]
                    obj_1 = f'{from_name}.{from_id}'
                    obj_2 = f'{to_name}.{to_id}'
                    obj_3 = f'{cur_to_name}.{cur_to_id}'
                    predicate = f'BETWEEN({obj_1}, {obj_2}, {obj_3})'
                    # print(predicate)
                    initial_states.append(predicate)
                    unpaired_between_list.remove((cur_from_id, cur_to_id))
                elif cur_to_id == to_id:
                    cur_from_name = id_2_name_dict[cur_from_id]
                    obj_1 = f'{to_name}.{to_id}'
                    obj_2 = f'{from_name}.{from_id}'
                    obj_3 = f'{cur_from_name}.{cur_from_id}'
                    predicate = f'BETWEEN({obj_1}, {obj_2}, {obj_3})'
                    # print(predicate)
                    initial_states.append(predicate)
                    unpaired_between_list.remove((cur_from_id, cur_to_id))
                else:
                    unpaired_between_list.append(b_tuple)
        else:
            if relation == 'ON':
                relation = 'ONTOP'
            elif relation == 'SITTING':
                relation = 'SITTINGRELATION'
            elif relation == 'CLOSE':
                continue
            obj_1 = f'{from_name}.{from_id}'
            obj_2 = f'{to_name}.{to_id}'
            predicate_name = state_transform_dictionary[relation]
            predicate = f'{predicate_name}({obj_1}, {obj_2})'
            # print(predicate)
            initial_states.append(predicate)
        
    # then, we obtain the final state with wildcards being changed with realistic objects
    final_states = []
    # print("==we then print out all final goal states==")
    for node in node_goals:
        id, name, state = node['id'], node['class_name'], node['state']
        real_obj_name = f'{name}.{id}'
        predicate_name = state_transform_dictionary[state]
        predicate = f'{predicate_name}({real_obj_name})'
        final_states.append(predicate)

    ## we then deal with edges
    predicates = set()
    unpaired_between_list = []
    for edge in edge_goals:
        from_id, relation, to_id = edge['from_id'], edge['relation_type'], edge['to_id']
        from_name, to_name = id_2_name_dict[from_id], id_2_name_dict[to_id]
        
        # note that between is a special relation
        if relation == 'BETWEEN':
            b_tuple = (from_id, to_id)
            tmp_between_list = copy.deepcopy(unpaired_between_list)
            for cur_from_id, cur_to_id in tmp_between_list:
                if cur_from_id == from_id:
                    cur_to_name = id_2_name_dict[cur_to_id]
                    obj_1 = f'{from_name}.{from_id}'
                    obj_2 = f'{to_name}.{to_id}'
                    obj_3 = f'{cur_to_name}.{cur_to_id}'
                    predicate = f'BETWEEN({obj_1}, {obj_2}, {obj_3})'
                    predicates.add(predicate)
                    unpaired_between_list.remove((cur_from_id, cur_to_id))
                elif cur_to_id == to_id:
                    cur_from_name = id_2_name_dict[cur_from_id]
                    obj_1 = f'{to_name}.{to_id}'
                    obj_2 = f'{from_name}.{from_id}'
                    obj_3 = f'{cur_from_name}.{cur_from_id}'
                    predicate = f'BETWEEN({obj_1}, {obj_2}, {obj_3})'
                    predicates.add(predicate)
                    unpaired_between_list.remove((cur_from_id, cur_to_id))
                else:
                    unpaired_between_list.append(b_tuple)
        else:
            if relation == 'ON':
                relation = 'ONTOP'
            elif relation == 'SITTING':
                relation = 'SITTINGRELATION'
            obj_1 = f'{from_name}.{from_id}'
            obj_2 = f'{to_name}.{to_id}'
            predicate_name = state_transform_dictionary[relation]
            predicate = f'{predicate_name}({obj_1}, {obj_2})'
            predicates.add(predicate)
    ### output the predicates in edges
    for p in predicates:
        # print(p)
        final_states.append(p)

    ## we then deal with actions
    actions_states = []
    # print("==we then print out all final goal actions==")
    for action in action_goals:
        action_candidates = action.split('|')
        action_candidates = [f"{a.upper().replace(' ', '')}" for a in action_candidates]
        final_action_str = " or ".join(action_candidates)
        # print(final_action_str)
        actions_states.append(final_action_str)
    return initial_states, final_states, actions_states

def add_task_info_into_prompt(prompt_path, task_name, relv_objs, init_states, final_states, final_actions, necessity):
    prompt = json.load(open(prompt_path, 'r'))['target_task']
    return prompt.replace("<task_name>", task_name).replace("<relevant_objects>", relv_objs).replace("<initial_states>", init_states).replace("<final_states>", final_states).replace("<final_actions>", final_actions).replace("<necessity>", necessity)

def add_task_info_into_prompt_component(template_prompt, task_name, relv_objs, init_states, final_states, final_actions, necessity):
    target_task = template_prompt['target_task']
    return target_task.replace("<task_name>", task_name).replace("<relevant_objects>", relv_objs).replace("<initial_states>", init_states).replace("<final_states>", final_states).replace("<final_actions>", final_actions).replace("<necessity>", necessity)