import os
import json
import re
import copy
import time
import ast

import evolving_graph.utils as utils
from evolving_graph.eval_robots import MotionPlanner, at_least_one_matched
from evolving_graph.execution import Relation, State
from evolving_graph.scripts import read_script, Action, ScriptObject, ScriptLine, ScriptParseException, Script
from evolving_graph.execution import ScriptExecutor
from evolving_graph.environment import EnvironmentGraph, EnvironmentState

name_equivalence = utils.load_name_equivalence()
properties_data = utils.load_properties_data()
object_placing = utils.load_object_placing()

# --------------------subgoal version---------------------------
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

def print_relevant_nodes(all_nodes):
    for node in all_nodes:
        print(node)
def get_formatted_relevant_nodes(all_nodes):
    relevant_nodes = []
    for node in all_nodes:
        id, obj_name, category, properties = node['id'], node['obj_name'], node['category'], node['properties']
        real_obj_name = f'{obj_name}.{id}'
        relevant_nodes.append(f'| {real_obj_name} | {category} | {properties} |')
    return relevant_nodes

def get_initial_states_and_final_goals(planner: MotionPlanner, goal:dict):
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
    selected_node_state, selected_edge_state, accurate_edge_state, actions = goal['selected_node_state'], goal['selected_edge_state'], goal['accurate_edge_state'], goal['actions']
    
    ## we first deal with node states
    # @deprecated words: [we need a sign to rule out those same name (usually, same type of items should both be satisfied)]
    # @update words: [we do not need a sign. as long as a node is listed, it then must be satisfied, no matter what]
    for cur_node in diff_in_final['nodes']:
        cur_id, cur_name, cur_states = cur_node['id'], cur_node['class_name'], cur_node['states']
        for cur_state in cur_states:
            # as long as this state can match some success pattern, then this technically must be satisfied (remember 'three stacked plates' case)
            success = False
            for node_str, _ in selected_node_state.items():
                node_str_candidates = node_str.split('|')
                for node_candidate in node_str_candidates:
                    node_state = ast.literal_eval(node_candidate)
                    ground_node_name = node_state['name']
                    ground_node_state = node_state['state']
                    if cur_name == ground_node_name and cur_state == ground_node_state:
                        success = True
                        break
                if success:
                    break
            if success:
                real_obj_name = f'{cur_name}.{cur_id}'
                predicate_name = state_transform_dictionary[cur_state]
                predicate = f'{predicate_name}({real_obj_name})'
                # print(predicate)
                final_states.append(predicate)

    ## we then deal with edge cases
    predicates = set()
    unpaired_between_list = []
    for cur_edge in diff_in_final['edges']:
        cur_from_id, cur_relation, cur_to_id = cur_edge['from_id'], cur_edge['relation_type'], cur_edge['to_id']
        cur_from_name, cur_to_name = id_2_name_dict[cur_from_id], id_2_name_dict[cur_to_id]
        
        # below is exact matching
        for edge_str, _ in accurate_edge_state.items():
            edge_state = ast.literal_eval(edge_str)
            goal_from_name, goal_relation, goal_to_name = edge_state['from_name'], edge_state['relation'], edge_state['to_name']
            if cur_from_name == goal_from_name and cur_to_name == goal_to_name and cur_relation == goal_relation:
                if cur_relation == 'BETWEEN':
                    b_tuple = (cur_from_id, cur_to_id)
                    tmp_between_list = copy.deepcopy(unpaired_between_list)
                    for tmp_from_id, tmp_to_id in tmp_between_list:
                        if tmp_from_id == cur_from_id:
                            tmp_to_name = id_2_name_dict[tmp_to_id]
                            obj_1 = f'{cur_from_name}.{cur_from_id}'
                            obj_2 = f'{cur_to_name}.{cur_to_id}'
                            obj_3 = f'{tmp_to_name}.{tmp_to_id}'
                            predicate = f'BETWEEN({obj_1}, {obj_2}, {obj_3})'
                            predicates.add(predicate)
                            unpaired_between_list.remove((tmp_from_id, tmp_to_id))
                        elif tmp_to_id == cur_to_id:
                            tmp_from_name = id_2_name_dict[tmp_from_id]
                            obj_1 = f'{cur_to_name}.{cur_to_id}'
                            obj_2 = f'{cur_from_name}.{cur_from_id}'
                            obj_3 = f'{tmp_from_name}.{tmp_from_id}'
                            predicate = f'BETWEEN({obj_1}, {obj_2}, {obj_3})'
                            predicates.add(predicate)
                            unpaired_between_list.remove((tmp_from_id, tmp_to_id))
                        else:
                            unpaired_between_list.append(b_tuple)
                else:
                    if cur_relation == 'ON':
                        cur_relation = 'ONTOP'
                    elif cur_relation == 'SITTING':
                        cur_relation = 'SITTINGRELATION'
                    obj_1 = f'{cur_from_name}.{cur_from_id}'
                    obj_2 = f'{cur_to_name}.{cur_to_id}'
                    predicate_name = state_transform_dictionary[cur_relation]
                    predicate = f'{predicate_name}({obj_1}, {obj_2})'
                    predicates.add(predicate)    

        # below is wildcard matching
        get_cur_from_properties = properties_data[cur_from_name] if cur_from_name in properties_data else []
        get_cur_to_properties = properties_data[cur_to_name] if cur_to_name in properties_data else []
        get_cur_from_properties = sorted(get_cur_from_properties, key=lambda prop: prop.value)
        get_cur_to_properties = sorted(get_cur_to_properties, key=lambda prop: prop.value)
        for edge_str, _ in selected_edge_state.items():
            edge_state = ast.literal_eval(edge_str)
            goal_from_name, goal_relation, goal_to_name = edge_state['from_name'], edge_state['relation'], edge_state['to_name']
            goal_relation_candidates = goal_relation.split('|')
            if cur_relation not in goal_relation_candidates:
                continue
            
            is_valid = False
            if '?' in goal_from_name:
                validation_from_name = f'?{str(get_cur_from_properties)}?' if cur_from_name != 'character' else f'?character?'
                goal_from_name_candidates = goal_from_name.split('|')
                if cur_to_name == goal_to_name and at_least_one_matched(validation_from_name, goal_from_name_candidates):
                    is_valid = True
            elif '?' in goal_to_name:
                validation_to_name = f'?{str(get_cur_to_properties)}?' if cur_to_name != 'character' else f'?character?'
                goal_to_name_candidates = goal_to_name.split('|')
                if cur_from_name == goal_from_name and at_least_one_matched(validation_to_name, goal_to_name_candidates):
                    is_valid = True
            
            if is_valid:
                if cur_relation == 'BETWEEN':
                    b_tuple = (cur_from_id, cur_to_id)
                    tmp_between_list = copy.deepcopy(unpaired_between_list)
                    for tmp_from_id, tmp_to_id in tmp_between_list:
                        if tmp_from_id == cur_from_id:
                            tmp_to_name = id_2_name_dict[tmp_to_id]
                            obj_1 = f'{cur_from_name}.{cur_from_id}'
                            obj_2 = f'{cur_to_name}.{cur_to_id}'
                            obj_3 = f'{tmp_to_name}.{tmp_to_id}'
                            predicate = f'BETWEEN({obj_1}, {obj_2}, {obj_3})'
                            predicates.add(predicate)
                            unpaired_between_list.remove((tmp_from_id, tmp_to_id))
                        elif tmp_to_id == cur_to_id:
                            tmp_from_name = id_2_name_dict[tmp_from_id]
                            obj_1 = f'{cur_to_name}.{cur_to_id}'
                            obj_2 = f'{cur_from_name}.{cur_from_id}'
                            obj_3 = f'{tmp_from_name}.{tmp_from_id}'
                            predicate = f'BETWEEN({obj_1}, {obj_2}, {obj_3})'
                            predicates.add(predicate)
                            unpaired_between_list.remove((tmp_from_id, tmp_to_id))
                        else:
                            unpaired_between_list.append(b_tuple)
                else:
                    if cur_relation == 'ON':
                        cur_relation = 'ONTOP'
                    elif cur_relation == 'SITTING':
                        cur_relation = 'SITTINGRELATION'
                    obj_1 = f'{cur_from_name}.{cur_from_id}'
                    obj_2 = f'{cur_to_name}.{cur_to_id}'
                    predicate_name = state_transform_dictionary[cur_relation]
                    predicate = f'{predicate_name}({obj_1}, {obj_2})'
                    predicates.add(predicate)
    ### output the predicates in edges
    for p in predicates:
        # print(p)
        final_states.append(p)

    ## we then deal with actions
    actions_states = []
    # print("==we then print out all final goal actions==")
    for action in actions:
        action_candidates = action.split('|')
        action_candidates = [f"{a.upper().replace(' ', '')}" for a in action_candidates]
        final_action_str = " or ".join(action_candidates)
        # print(final_action_str)
        actions_states.append(final_action_str)


    
    # !!!sth here can be introduced, that, we cannot simply search the id that first match some relationship, otherwise, it will introduce some bias, like put three blocks on top the other one.!!!
    # ## we first deal with node states
    # for node_str, _ in selected_node_state.items():
    #     node_str_candidates = node_str.split('|')
    #     predicate_candidates = []
    #     for node_candidate in node_str_candidates:
    #         node_state = ast.literal_eval(node_candidate)
    #         candidate_ids = get_object_id(node_state['name'], id_2_name_dict)
    #         real_id = None
    #         for id in candidate_ids:
    #             obj = get_object_based_on_id(id, final_state_dict)
    #             if obj == None:
    #                 continue
    #             if node_state['state'] in obj['states']:
    #                 real_id = id
    #                 break
    #         assert real_id is not None, f"no object found for {node_state['name']} with state {node_state['state']}"
    #         predicate_name = state_transform_dictionary[node_state['state']]
    #         real_obj_name = f'{node_state["name"]}.{real_id}'
    #         predicate = f'{predicate_name}({real_obj_name})'
    #         predicate_candidates.append(predicate)
    #     real_predicate = " or ".join(predicate_candidates)
    #     print(real_predicate)
    # ## we then deal with wildcard edge states
    # for id in related_ids:
    #     name = id_2_name_dict[id]
    #     get_properties = properties_data[name] if name in properties_data else []
    #     get_properties = sorted(get_properties, key=lambda prop: prop.value)
    #     for edge_str, _ in selected_edge_state.items():
    #         edge_state = ast.literal_eval(edge_str)
    #         goal_from_name, goal_relation, goal_to_name = edge_state['from_name'], edge_state['relation'], edge_state['to_name']
    #         goal_relation_candidates = goal_relation.split('|')
    #         if relation not in goal_relation_candidates:
    #             continue
    #         validation_name = f'?{str(get_properties)}?' if name != 'character' else f'?character?'
    #         if '?' in goal_from_name:
    #             goal_from_name_candidates = goal_from_name.split('|')
    #         ...
    return initial_states, final_states, actions_states
    ...

def get_final_goals_in_vh_format(planner: MotionPlanner, goal:dict):
    init_dict = planner.init_state.to_dict()
    final_state_dict = planner.final_state_dict
    id_2_name_dict = planner.id_to_name
    diff_in_init, diff_in_final = planner.filter_unique_subdicts(init_dict, final_state_dict)

    final_states = []
    selected_node_state, selected_edge_state, accurate_edge_state, actions = goal['selected_node_state'], goal['selected_edge_state'], goal['accurate_edge_state'], goal['actions']

    for cur_node in diff_in_final['nodes']:
        cur_id, cur_name, cur_states = cur_node['id'], cur_node['class_name'], cur_node['states']
        for cur_state in cur_states:
            success = False
            for node_str, _ in selected_node_state.items():
                node_str_candidates = node_str.split('|')
                for node_candidate in node_str_candidates:
                    node_state = ast.literal_eval(node_candidate)
                    ground_node_name = node_state['name']
                    ground_node_state = node_state['state']
                    if cur_name == ground_node_name and cur_state == ground_node_state:
                        success = True
                        break
                if success:
                    break
            if success:
                # final_states.append({'id': cur_id, 'state': cur_state})
                final_states.append({'id': cur_id, 'class_name': cur_name, 'state': cur_state})
    
    for cur_edge in diff_in_final['edges']:
        cur_from_id, cur_relation, cur_to_id = cur_edge['from_id'], cur_edge['relation_type'], cur_edge['to_id']
        cur_from_name, cur_to_name = id_2_name_dict[cur_from_id], id_2_name_dict[cur_to_id] # type: ignore

        for edge_str, _ in accurate_edge_state.items():
            edge_state = ast.literal_eval(edge_str)
            goal_from_name, goal_relation, goal_to_name = edge_state['from_name'], edge_state['relation'], edge_state['to_name']
            if cur_from_name == goal_from_name and cur_to_name == goal_to_name and cur_relation == goal_relation:
                final_states.append(copy.deepcopy(cur_edge))
        
        get_cur_from_properties = properties_data[cur_from_name] if cur_from_name in properties_data else []
        get_cur_to_properties = properties_data[cur_to_name] if cur_to_name in properties_data else []
        get_cur_from_properties = sorted(get_cur_from_properties, key=lambda prop: prop.value)
        get_cur_to_properties = sorted(get_cur_to_properties, key=lambda prop: prop.value)
        for edge_str, _ in selected_edge_state.items():
            edge_state = ast.literal_eval(edge_str)
            goal_from_name, goal_relation, goal_to_name = edge_state['from_name'], edge_state['relation'], edge_state['to_name']
            goal_relation_candidates = goal_relation.split('|')
            if cur_relation not in goal_relation_candidates:
                continue

            is_valid = False
            if '?' in goal_from_name:
                validation_from_name = f'?{str(get_cur_from_properties)}?' if cur_from_name != 'character' else f'?character?'
                goal_from_name_candidates = goal_from_name.split('|')
                if cur_to_name == goal_to_name and at_least_one_matched(validation_from_name, goal_from_name_candidates):
                    is_valid = True
            elif '?' in goal_to_name:
                validation_to_name = f'?{str(get_cur_to_properties)}?' if cur_to_name != 'character' else f'?character?'
                goal_to_name_candidates = goal_to_name.split('|')
                if cur_from_name == goal_from_name and at_least_one_matched(validation_to_name, goal_to_name_candidates):
                    is_valid = True

            if is_valid:
                tmp = {'from_id': cur_from_id, 'relation_type': cur_relation if "HOLDS" not in cur_relation else "HOLDS", 'to_id': cur_to_id}
                # tmp = {'from_id': cur_from_id, 'relation_type': cur_relation, 'to_id': cur_to_id}
                # final_states.append(tmp)

    return final_states

def get_candidate_id(file_id, task_ans_list):
    ans_list = [ast.literal_eval(x) for x in task_ans_list]
    for f_id, ans in ans_list:
        if f_id == file_id:
            return ans
    assert False, f"file id {file_id} not found in task ans list"
# --------------------------------------------------------------



def main_filter():
    data_dir = 'F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\dataset\\programs_processed_precond_nograb_morepreconds'
    task_dict_dir = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\resources\\task_state_updated.json"

    task_dict = json.load(open(task_dict_dir, 'r'))
    scene_str = "scene_1"
    task_dict = task_dict[scene_str]

    

    for task_name, task_detail in task_dict.items():
        print(f"task name is {task_name}")
        graph_path = task_detail['graph_state_path']
        task_list = task_detail['task_file_list']
        task_list_ans_list = task_detail['task_file_list_with_ans']
        goal_candidates = task_detail['goal_candidates']
        for fild_id in task_list:
            # we first get candidate num
            ans_id = get_candidate_id(fild_id, task_list_ans_list)
            if ans_id == -1:
                continue
            # if task_name != 'Write an email':
            #     continue
            goal = goal_candidates[ans_id]

            state_file_path = os.path.join(graph_path, f'file{fild_id}.json')
            state_dict = json.load(open(state_file_path, 'r'))
            init_state_dict = state_dict['init_graph']
            final_state_dict = state_dict['final_graph']

            init_scene_graph = EnvironmentGraph(init_state_dict)
            planner = MotionPlanner(init_scene_graph, final_state_dict, name_equivalence, properties_data, object_placing)

            relevant_nodes, related_ids = get_relevant_nodes(planner)
            get_formatted_relevant_nodes(relevant_nodes)

            get_initial_states_and_final_goals(planner, goal)
            return

if __name__ == '__main__':
    main_filter()
