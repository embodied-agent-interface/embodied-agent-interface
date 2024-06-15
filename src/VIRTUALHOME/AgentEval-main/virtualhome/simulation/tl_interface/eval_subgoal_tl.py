from collections import deque
import copy
import os
import sys
sys.path.append('F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\simulation')
sys.path.append("F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\simulation\\evolving_graph")
import json
import re
from simple_tl_parser import parse_simple_tl
from simple_tl import State, Proposition, Action, StateActionSequence, extract_propositions_and_actions, eval_simple_tl
from evolving_graph.filter_relevant_info import MotionPlanner, get_candidate_id
from evolving_graph.execution import EnvironmentGraph
from evolving_graph.eval_subgoal import translate_predicate_into_vh, get_final_goals_in_vh_format, parse_output_plan, set_error_type, print_execution_error_statistics

from utils import vocab
from typing import List, Dict

def print_error_type(error_type_dict):
    for error_type, program_ids in error_type_dict.items():
        print(f"Error type: {error_type}, program_ids: {program_ids}")

def parse_llm_output_into_tl_test(saved_file_path):
    with open(saved_file_path, 'r') as f:
        log_info = json.load(f)
    scene_str = 'scene_1'
    log_info = log_info[scene_str]
    vocab_predicates = vocab.get_tl_predicates()
    vocab_actions = vocab.get_subgoal_actions_in_list()
    error_type = {}
    total_num = 0
    wrong_num = 0
    for task_name, task_list in log_info.items():
        for program_id, program_info in task_list.items():
            original_output = program_info['original']
            tl_formula = program_info['tl_formula']
            total_num += 1
            try:
                parsed_tl = parse_simple_tl(tl_formula, vocab_predicates, vocab_actions)
                # print(f"program_id: {program_id} success")
            except Exception as e:
                wrong_num += 1
                if e.__class__.__name__ not in error_type:
                    error_type[e.__class__.__name__] = [program_id]
                else:
                    error_type[e.__class__.__name__].append(program_id)
                continue
    print_error_type(error_type)
    print(f"total_num: {total_num}, wrong_num: {wrong_num}, correct rate: {(total_num - wrong_num) / total_num}")

def get_exe_files_path():
    path = 'F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\dataset\\programs_processed_precond_nograb_morepreconds\\executable_programs\\TrimmedTestScene1_graph\\results_intentions_march-13-18'
    return path

def get_state_files_path():
    path = 'F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\dataset\\programs_processed_precond_nograb_morepreconds\\init_and_final_graphs\\TrimmedTestScene1_graph\\results_intentions_march-13-18'
    return path

def get_motion_planner(init_state, final_state):
    init_graph = EnvironmentGraph(init_state)
    planner = MotionPlanner(init_graph, final_state)
    return planner

def load_graph_state(state_file_path):
    with open(state_file_path, 'r') as f:
        state = json.load(f)
    init_state, final_state = state['init_graph'], state['final_graph']
    return init_state, final_state

def check_primitive_params_num(prop_or_action):
    tl_predicates_to_vh = vocab.get_tl_to_vh_predicates_dict()
    vh_states_to_tl = vocab.get_vh_states_to_tl_dict()
    vh_relations_to_tl = vocab.get_vh_relations_to_tl_dict()
    vh_properties, vh_states, vh_relations = vocab.get_vh_info()
    subgoal_actions = vocab.get_subgoal_actions()
    param_num = -1
    if isinstance(prop_or_action, Proposition):
        vh_predicate = tl_predicates_to_vh[prop_or_action.name]
        if vh_predicate in vh_properties:
            param_num = 1
        elif vh_predicate in vh_states and vh_states_to_tl[vh_predicate] == prop_or_action.name:
            param_num = 1
        elif vh_predicate in vh_relations and vh_relations_to_tl[vh_predicate] == prop_or_action.name:
            param_num = 2
    elif isinstance(prop_or_action, Action):
        param_num = subgoal_actions[prop_or_action.name]
    else:
        raise ValueError(f"Unknown type: {prop_or_action}")
    current_param_num = len(prop_or_action.args)
    rv = param_num == current_param_num
    if not rv:
        print(f'Current primitive: {prop_or_action}, expected param num: {param_num}, current param num: {current_param_num}')
    return rv

def check_object_name_id_pair(obj_pair, id_to_name_dict):
    if obj_pair == '<wildcard>':
        return True
    if '.' in obj_pair:
        obj_name, obj_id = obj_pair.split('.')
        obj_id = int(obj_id)
        rv = obj_id in id_to_name_dict
        if not rv:
            print(f'Object id: {obj_id} not in id_to_name_dict')
        rv = rv and id_to_name_dict[obj_id] == obj_name
        if not rv:
            print(f'Object id: {obj_id} and object name: {obj_name} not paired correctly, correct name: {id_to_name_dict[obj_id]}')
        return rv
    else:
        return obj_pair in id_to_name_dict.values()


def check_primitives(props, actions, id_to_name_dict):
    primitives = props + actions
    param_num_correct = True
    obj_name_id_pair_correct = True
    for primitive in primitives:
        if param_num_correct:
            param_num_correct = check_primitive_params_num(primitive)
        if obj_name_id_pair_correct:
            obj_name_id_pair_correct = all([check_object_name_id_pair(obj, id_to_name_dict) for obj in primitive.args])
        if not param_num_correct and not obj_name_id_pair_correct:
            break
    return param_num_correct, obj_name_id_pair_correct
    
def check_missing_actions(actions: List[Action], required_actions: List[str], file_id: str):
    required_action_candidates = []
    for a in required_actions:
        required_action_candidates.append([a.upper().replace(' ', '') for a in a.split('|')])
    required_actions = copy.deepcopy(required_action_candidates)
    action_names = [a.name for a in actions]
    missing_action = False
    for ra_candidates in required_actions:
        if not any([ra in action_names for ra in ra_candidates]):
            missing_action = True
            print(f"File id: {file_id}")
            print(f"Missing action: {ra_candidates}")
            print(f"Current actions: {action_names}")
            break

    return missing_action

def split_original_output(original_output):
    raw_lines = original_output.split('\n')
    valid_lines = []
    for line in raw_lines:
        and_lines = line.strip().split(' and ')
        for and_line in and_lines:
           cur_lines = and_line.strip().split(' or ')
           valid_lines.append(cur_lines[0])
    return valid_lines

def get_root_exe_file_path():
    path = 'F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\dataset\\programs_processed_precond_nograb_morepreconds\\executable_programs\\TrimmedTestScene1_graph\\results_intentions_march-13-18'
    return path

def load_an_action_sequence(file_path):
    '''
    file is an txt file
    '''
    with open(file_path, 'r') as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines if line[0] == '[']
    # each line is similar to '[action] <item> (xxx.yyy)' or '[action] <item> (xxx.yyy) <item> (xxx.yyy)'
    # for format like 'xxx.yyy', use regex rule to extract yyy, where both xxx and yyy are numbers
    # then replace 'xxx.yyy' with 'yyy'
    pattern = re.compile(r'\((\d+\.\d+)\)')
    action_seq = []
    for line in lines:
        objs = line.split(' ')
        new_objs = []
        for obj in objs:
            if obj[0] == '(':
                match = pattern.search(obj)
                assert match, f'Failed to match pattern in {obj}'
                new_obj = obj.replace(match.group(1), match.group(1).split('.')[1])
                new_objs.append(new_obj)
            else:
                new_objs.append(obj)
        action_seq.append(' '.join(new_objs))

    return action_seq

def translate_states_into_tl_propositions(states_dict, id_2_name_dict):
    vh_states_to_tl_map = vocab.get_vh_states_to_tl_dict()
    vh_relations_to_tl_map = vocab.get_vh_relations_to_tl_dict()
    nodes = states_dict['nodes']
    edges = states_dict['edges']
    obj_name_list = []
    tl_prop_list = []
    for k, v in id_2_name_dict.items():
        obj_str = f'{v}.{k}'
        obj_name_list.append(obj_str)
    # we first translate all nodes
    for node in nodes:
        object_id = node['id']
        object_name = node['class_name']
        node_states = node['states']
        obj_str = f'{object_name}.{object_id}'
        for state in node_states:
            tl_state = vh_states_to_tl_map[state]
            params = [obj_str]
            prop = Proposition(tl_state, params)
            tl_prop_list.append(prop)

    # we then translate all edges
    for edge in edges:
        from_id = edge['from_id']
        relation = edge['relation_type']
        to_id = edge['to_id']
        from_obj_name = id_2_name_dict[from_id]
        to_obj_name = id_2_name_dict[to_id]
        from_obj_str = f'{from_obj_name}.{from_id}'
        to_obj_str = f'{to_obj_name}.{to_id}'
        tl_relation = vh_relations_to_tl_map[relation]
        params = [from_obj_str, to_obj_str]
        prop = Proposition(tl_relation, params)
        tl_prop_list.append(prop)
    
    return obj_name_list, tl_prop_list

def get_tl_states_seq(raw_states, id_2_name_dict):
    states_seq = []
    for raw_state in raw_states:
        obj_name_list, tl_prop_list = translate_states_into_tl_propositions(raw_state, id_2_name_dict)
        states_seq.append(State(obj_name_list, tl_prop_list))
    return states_seq

# [Warning] the following function only considers the direct object names, not nickname (objects appearing in executable scripts)
def translate_action_primitive_into_tl(action):
    action_line = MotionPlanner.parse_script_line(action, 0)
    action_name = action_line.action.name
    action_params = []
    for p in action_line.parameters:
        obj_str = f'{p.name}.{p.instance}'
        action_params.append(obj_str)
    action_line = Action(action_name, action_params)
    return action_line

def translate_actions_into_tl(action_seq):
    tl_action_seq = []
    for action in action_seq:
        tl_action = translate_action_primitive_into_tl(action)
        tl_action_seq.append(tl_action)
    return tl_action_seq

def get_tl_action_seq(raw_actions):
    return translate_actions_into_tl(raw_actions)

def get_trajectory(states:List[State], actions:List[Action]):
    return StateActionSequence(states, actions)

def assess_traj_with_expression(tl_states, tl_actions, tl_expression):
    trajectory = get_trajectory(tl_states, tl_actions)
    result = eval_simple_tl(tl_expression, trajectory)
    return result

def check_well_defined_subgoals(file_id, tl_expression, exe_file_root_path, state_file_root_path):
    exe_file_path = os.path.join(exe_file_root_path, f'file{file_id}.txt')
    state_file_path = os.path.join(state_file_root_path, f'file{file_id}.json')
    action_seq = load_an_action_sequence(exe_file_path)
    init_state, final_state = load_graph_state(state_file_path)
    planner = get_motion_planner(init_state, final_state)
    raw_actions = []
    raw_states = []

    current_state = copy.deepcopy(init_state)
    id_to_name_dict = planner.id_to_name
    raw_states.append(current_state)

    for action in action_seq:
        raw_actions.append(action)
        rv = planner.execute_primitive_action(action)
        if not rv:
            print(f"Failed to execute action: {action}")
            return None
        else:
            current_state = copy.deepcopy(planner.env_state.to_dict())
            raw_states.append(current_state)
    
    tl_states = get_tl_states_seq(raw_states, id_to_name_dict)
    tl_actions = get_tl_action_seq(raw_actions)

    # trajectory = get_trajectory(tl_states, tl_actions)
    # print(action_seq)
    # print(tl_expression)
    # result = eval_simple_tl(tl_expression, trajectory)
    result = assess_traj_with_expression(tl_states, tl_actions, tl_expression)
    return result

def check_state_satisfied(state_tuple, env_state_dict:dict):
    state_type, state_dict = state_tuple
    success = False
    if state_type == 's':
        id, class_name, state = state_dict['id'], state_dict['class_name'], state_dict['state']
        nodes = env_state_dict["nodes"] # type: ignore
        for node in nodes:
            s_id, s_name, s_states = node['id'], node['class_name'], node['states']
            if s_id == id and s_name == class_name and state in s_states:
                success = True
                break
            if state == 'SITTING' or state == 'LYING':
                success = True
                break
            
    elif state_type == 'r':
        from_id, relation, to_id = state_dict['from_id'], state_dict['relation_type'], state_dict['to_id']
        edges = env_state_dict["edges"] # type: ignore
        for edge in edges:
            e_from_id, e_relation, e_to_id = edge['from_id'], edge['relation_type'], edge['to_id']
            if e_from_id == from_id and e_relation == relation and e_to_id == to_id:
                success = True
                break
            elif e_from_id == from_id and 'HOLDS' in e_relation and e_to_id == to_id:
                success = True
                break
    return success

def check_satisfied_in_prev_states(cur_subgoal, history_env_states_list: list, error_code, error_msg):
    if error_code == 1:
        if cur_subgoal[0] == 'a':
            pass
        else:
            found = False
            for history_env_states in history_env_states_list:
                if check_state_satisfied(cur_subgoal, history_env_states):
                    found = True
                    break
            if found:
                error_code = 0
                error_msg = f'Wrong temporal order. Found the subgoal {cur_subgoal[1]} satisfied in previous states.'
    return error_code, error_msg

def check_final_goals_satisfied(final_state_dict, target_goals):
    success = True
    target_goals_copy = copy.deepcopy(target_goals)
    # go over nodes first
    for node in final_state_dict['nodes']:
        for state in node['states']:
            tmp = {'id': node['id'], 'state': state}
            for tg in target_goals:
                if 'id' in tg and 'state' in tg:
                    if tg['id'] == tmp['id'] and tg['state'] == tmp['state']:
                        target_goals_copy.remove(tg)
                        if len(target_goals_copy) == 0:
                            break


    # then go over edges
    for edge in final_state_dict['edges']:
        tmp = {'from_id': edge['from_id'], 'relation_type': "HOLDS" if "HOLDS" in edge['relation_type'] else edge['relation_type'], 'to_id': edge['to_id']}
        for tg in target_goals:
            if 'from_id' in tg and 'relation_type' in tg and 'to_id' in tg:
                if tg['from_id'] == tmp['from_id'] and ((tg['relation_type'] == tmp['relation_type']) or (tmp['relation_type'] in tg['relation_type'] and 'HOLDS' in tmp['relation_type'])) and tg['to_id'] == tmp['to_id']:
                    target_goals_copy.remove(tg)
                    if len(target_goals_copy) == 0:
                        break
    
    if len(target_goals_copy) > 0:
        print(f"Final goals not satisfied: {target_goals_copy}")
        success = False
    return success, target_goals_copy

def check_if_holding(obj_id, planner:MotionPlanner, char_id=65):
    edges = planner.env_state.to_dict()["edges"] # type: ignore
    right_holding = {"from_id": char_id, "relation_type": "HOLDS_RH", "to_id": obj_id}
    left_holding = {"from_id": char_id, "relation_type": "HOLDS_LH", "to_id": obj_id}
    if right_holding in edges or left_holding in edges:
        return True
    return False

def translate_single_action(name, obj_name, obj_id):
    return f'[{name}] <{obj_name}> ({obj_id})'

def translate_double_action(name, obj1_name, obj1_id, obj2_name, obj2_id):
    return f'[{name}] <{obj1_name}> ({obj1_id}) <{obj2_name}> ({obj2_id})'

def translate_action(name, params):
    action_str = f'[{name}]'
    for param in params:
        obj_name, obj_id = param
        param_str = f' <{obj_name}> ({obj_id})'
        action_str += param_str
    return action_str

actions_must_hold = ['DRINK', 'EAT', 'READ']

def get_action_solution_candidates(core_action, planner:MotionPlanner, char_id=65):
    solution_candidates = []
    core_action_name, params = core_action['name'], core_action['params']
    solution_actions = []
    if len(params) > 0:
        obj_name = params[0][0]
        obj_id = params[0][1]
        if core_action_name in actions_must_hold and not check_if_holding(obj_id, planner, char_id):
            # first find and grab core_action_name
            find_item_to_grab = translate_single_action('FIND', obj_name, obj_id)
            grab_item = translate_single_action('GRAB', obj_name, obj_id)
            solution_actions.append(find_item_to_grab)
            solution_actions.append(grab_item)
        elif core_action_name == 'LOOKAT' or core_action_name == 'WATCH':
            find_item_to_look = translate_single_action('FIND', obj_name, obj_id)
            turnto_item = translate_single_action('TURNTO', obj_name, obj_id)
            solution_actions.append(find_item_to_look)
            solution_actions.append(turnto_item)
        else:
            find_item = translate_single_action('FIND', obj_name, obj_id)
            solution_actions.append(find_item)
    solution_actions.append(translate_action(core_action_name, params))
    solution_candidates.append(solution_actions)
    return solution_candidates


def get_state_solution_candidates(state_tuple, planner: MotionPlanner, char_id=65):
    solution_candidates = []
    state_type, state_dict = state_tuple
    id_2_name_dict = planner.id_to_name

    # otherwise, search all possible solution candidates
    if state_type == 's':
        id, class_name, state = state_dict['id'], state_dict['class_name'], state_dict['state']
        if state == 'CLOSED':
            ans_set = []
            find_item = translate_single_action('FIND', class_name, id)
            close_item = translate_single_action('CLOSE', class_name, id)
            ans_set.append(find_item)
            ans_set.append(close_item)
            solution_candidates.append(ans_set)
        elif state == 'OPEN':
            ans_set = []
            find_item = translate_single_action('FIND', class_name, id)
            open_item = translate_single_action('OPEN', class_name, id)
            ans_set.append(find_item)
            ans_set.append(open_item)
            solution_candidates.append(ans_set)
        elif state == 'ON': # sth is activated
            ans_set = []
            find_item = translate_single_action('FIND', class_name, id)
            switchon_item = translate_single_action('SWITCHON', class_name, id)
            ans_set.append(find_item)
            ans_set.append(switchon_item)
            solution_candidates.append(ans_set)
        elif state == 'OFF': # sth is deactivated
            ans_set = []
            find_item = translate_single_action('FIND', class_name, id)
            switchoff_item = translate_single_action('SWITCHOFF', class_name, id)
            ans_set.append(find_item)
            ans_set.append(switchoff_item)
            solution_candidates.append(ans_set)
        elif state == 'SITTING' or state == 'LYING':
            pass # this is a tricky part to deal with, simply pass!!!!
        elif state == 'DIRTY':
            return None # now, vh does not support turning sth dirty. if this state is not previously satisfied, then it is not possible to satisfy it
        elif state == 'CLEAN': # STATE
            ans_set_1 = []
            ans_set_2 = []
            find_item = translate_single_action('FIND', class_name, id)
            wipe_item = translate_single_action('WIPE', class_name, id)
            wash_item = translate_single_action('WASH', class_name, id)
            ans_set_1.append(find_item)
            ans_set_1.append(wipe_item)
            ans_set_2.append(find_item)
            ans_set_2.append(wash_item)
            solution_candidates.append(ans_set_1)
            solution_candidates.append(ans_set_2)
        elif state == 'PLUGGED_IN':
            ans_set = []
            find_item = translate_single_action('FIND', class_name, id)
            plug_in_item = translate_single_action('PLUGIN', class_name, id)
            ans_set.append(find_item)
            ans_set.append(plug_in_item)
            solution_candidates.append(ans_set)
        elif state == 'PLUGGED_OUT':
            ans_set = []
            find_item = translate_single_action('FIND', class_name, id)
            plug_out_item = translate_single_action('PLUGOUT', class_name, id)
            ans_set.append(find_item)
            ans_set.append(plug_out_item)
            solution_candidates.append(ans_set)
        
    elif state_type == 'r':
        from_id, relation, to_id = state_dict['from_id'], state_dict['relation_type'], state_dict['to_id']
        from_name, to_name = id_2_name_dict[int(from_id)], id_2_name_dict[int(to_id)] # type: ignore
        if relation == 'ON': # spatial relationship, ontop
            if from_id == char_id: # this is a tricky part to deal with, either sleep or sit
                ans_set_1 = []
                ans_set_2 = []
                find_item = translate_single_action('FIND', to_name, to_id)
                sit_on_item = translate_single_action('SIT', to_name, to_id)
                lie_on_item = translate_single_action('LIE', to_name, to_id)
                ans_set_1.append(find_item)
                ans_set_1.append(sit_on_item)
                ans_set_2.append(find_item)
                ans_set_2.append(lie_on_item)
                solution_candidates.append(ans_set_1)
                solution_candidates.append(ans_set_2)
            elif to_id == char_id: # put on clothes
                ans_set = []
                put_on_item = translate_single_action('PUTON', from_name, from_id)
                ans_set.append(put_on_item)
                solution_candidates.append(ans_set)
            else:
                ans_set = []
                if not check_if_holding(from_id, planner, char_id):
                    find_item = translate_single_action('FIND', from_name, from_id)
                    grab_item = translate_single_action('GRAB', from_name, from_id)
                    ans_set.append(find_item)
                    ans_set.append(grab_item)
                find_item_2 = translate_single_action('FIND', to_name, to_id)
                put_back_item = translate_double_action('PUTBACK', from_name, from_id, to_name, to_id)
                ans_set.append(find_item_2)
                ans_set.append(put_back_item)
                solution_candidates.append(ans_set)
        elif relation == 'INSIDE':
            if from_id == char_id:
                ans_set = []
                walk_to_item = translate_single_action('WALK', to_name, to_id)
                ans_set.append(walk_to_item)
                solution_candidates.append(ans_set)
            else:
                ans_set_1 = []
                ans_set_2 = []
                if not check_if_holding(from_id, planner, char_id):
                    find_item = translate_single_action('FIND', from_name, from_id)
                    grab_item = translate_single_action('GRAB', from_name, from_id)
                    ans_set_1.append(find_item)
                    ans_set_1.append(grab_item)
                    ans_set_2.append(find_item)
                    ans_set_2.append(grab_item)
                find_item_2 = translate_single_action('FIND', to_name, to_id)
                put_in_item = translate_double_action('PUTIN', from_name, from_id, to_name, to_id)
                pour_in_item = translate_double_action('POUR', from_name, from_id, to_name, to_id)
                ans_set_1.append(find_item_2)
                ans_set_1.append(put_in_item)
                ans_set_2.append(find_item_2)
                ans_set_2.append(pour_in_item)
                solution_candidates.append(ans_set_1)
                solution_candidates.append(ans_set_2)
        elif relation == 'BETWEEN':
            pass # this is a tricky part to deal with, simply pass!!!!
        elif relation == 'CLOSE' and char_id == from_id:
            ans_set = []
            find_item = translate_single_action('FIND', to_name, to_id)
            ans_set.append(find_item)
            solution_candidates.append(ans_set)
        elif relation == 'FACING':
            ans_set = []
            find_item = translate_single_action('FIND', to_name, to_id)
            turn_to_item = translate_single_action('TURNTO', to_name, to_id)
            ans_set.append(find_item)
            ans_set.append(turn_to_item)
            solution_candidates.append(ans_set)
        elif relation == 'HOLDS_RH' or relation == 'HOLDS_LH':
            if not check_if_holding(to_id, planner, char_id):
                ans_set = []
                find_item = translate_single_action('FIND', to_name, to_id)
                grab_item = translate_single_action('GRAB', to_name, to_id)
                ans_set.append(find_item)
                ans_set.append(grab_item)
                solution_candidates.append(ans_set)
            else:
                return None
    
    
    return solution_candidates

def check_tl_final_goal_satisfied(tl_final_goal, raw_states, raw_actions_list, id_to_name_dict):
    raw_actions = []
    # print(f'len of states: {len(raw_states)}, len of actions: {len(raw_actions_list)}')
    for action_list in raw_actions_list:
        raw_actions.append(action_list[-1])
    # print(f"Final goal: {tl_final_goal}")
    # print(f'raw_actions: {raw_actions}')
    tl_states = get_tl_states_seq(raw_states, id_to_name_dict)
    tl_actions = get_tl_action_seq(raw_actions)
    trajectory = get_trajectory(tl_states, tl_actions)
    result = eval_simple_tl(tl_final_goal, trajectory)
    return result

def execute_subgoal_sequence(subgoals, final_goals, parsed_tl_final_goal, planner:MotionPlanner):

    prev_env_states = copy.deepcopy(planner.env_state)
    history_env_states = [copy.deepcopy(prev_env_states.to_dict())] # type: ignore
    level = 0

    queue = deque()
    prev = (prev_env_states, [], subgoals, level, history_env_states)
    queue.append(prev)
    
    feasible_solutions = []
    failed_actions_candidates = []
    executable = 0
    while queue:
        cur_env_states, cur_executed_actions, cur_subgoals, cur_level, cur_history_env_states = queue.popleft()
        prev_env_states = copy.deepcopy(cur_env_states)

        if len(cur_subgoals) == 0:
            executable = 1
            # check whether final goals are satisfied
            success = check_tl_final_goal_satisfied(parsed_tl_final_goal, cur_history_env_states, cur_executed_actions, planner.id_to_name)
            if success:
                feasible_solutions.append(cur_executed_actions)
            else:
                failed_error_code = 1
                failed_error_seq = f'Final goals not satisfied. Target goals: {parsed_tl_final_goal}'
                failed_actions_candidates.append((failed_error_code, cur_executed_actions, failed_error_seq))
            '''
            success, remaining_goals = check_final_goals_satisfied(prev_env_states.to_dict(), final_goals)
            if success:
                feasible_solutions.append(cur_executed_actions)
            else:
                failed_error_code = 1
                failed_error_seq = 'Missing steps: ' + str(remaining_goals)
                for remaining_goal in remaining_goals:
                    if "relation_type" in remaining_goal and "HOLDS" in remaining_goal['relation_type']:
                        state_type = 'r'
                        remaining_goal_right = {'from_id': remaining_goal['from_id'], 'relation_type': 'HOLDS_RH', 'to_id': remaining_goal['to_id']}
                        remaining_goal_left = {'from_id': remaining_goal['from_id'], 'relation_type': 'HOLDS_LH', 'to_id': remaining_goal['to_id']}
                        r_goal_1 = ('r', remaining_goal_right)
                        r_goal_2 = ('r', remaining_goal_left)
                        tmp_failed_error_code, tmp_failed_error_seq = check_satisfied_in_prev_states(r_goal_1, cur_history_env_states, failed_error_code, failed_error_seq)
                        tmp_failed_error_code_1, tmp_failed_error_seq_1 = check_satisfied_in_prev_states(r_goal_2, cur_history_env_states, failed_error_code, failed_error_seq)
                        if tmp_failed_error_code_1 == 0:
                            failed_error_code = 0
                            failed_error_seq = tmp_failed_error_seq_1
                            break
                    elif "relation_type" in remaining_goal:
                        r_goal = ('r', remaining_goal)
                        tmp_failed_error_code, tmp_failed_error_seq = check_satisfied_in_prev_states(r_goal, cur_history_env_states, failed_error_code, failed_error_seq)
                    else:
                        tmp = {'id': remaining_goal['id'], 'class_name': planner.id_to_name[remaining_goal['id']],'state': remaining_goal['state']} # type: ignore
                        s_goal = ('s', tmp)
                        tmp_failed_error_code, tmp_failed_error_seq = check_satisfied_in_prev_states(s_goal, cur_history_env_states, failed_error_code, failed_error_seq)
                    if tmp_failed_error_code == 0:
                        failed_error_code = 0
                        failed_error_seq = tmp_failed_error_seq
                        break
                failed_actions_candidates.append((failed_error_code, cur_executed_actions, failed_error_seq))
            '''
                
        else:
            cur_subgoal = cur_subgoals[0] # cur_subgoal = ('type', content)
            if cur_subgoal[0] == 'a':
                solution_candidates = get_action_solution_candidates(cur_subgoal[1], planner, planner.acting_char_id)
                for action_seq in solution_candidates:
                    planner.env_state = copy.deepcopy(prev_env_states)
                    success = True
                    for action_instruction in action_seq:
                        success, my_info = planner.my_execute_primitive_action_eval(action_instruction)
                        if not success:
                            failed_error_code = my_info.get_error_type()
                            failed_error_seq = my_info.get_error_string()
                            failed_error_code, failed_error_seq = check_satisfied_in_prev_states(cur_subgoal, cur_history_env_states, failed_error_code, failed_error_seq)
                            failed_action_seq = cur_executed_actions + action_seq
                            failed_actions_candidates.append((failed_error_code, failed_action_seq, failed_error_seq))
                            break
                    if success:
                        new_executed_actions = copy.deepcopy(cur_executed_actions)
                        new_executed_actions.append(action_seq)
                        new_subgoals = copy.deepcopy(cur_subgoals[1:]) if len(cur_subgoals) > 1 else []
                        new_level = cur_level + 1
                        new_env_state = copy.deepcopy(planner.env_state)
                        new_history_env_states = copy.deepcopy(cur_history_env_states)
                        new_history_env_states.append(copy.deepcopy(new_env_state.to_dict()))
                        queue.append((new_env_state, new_executed_actions, new_subgoals, new_level, new_history_env_states))
                    
            else: 
                # node state, relation state (edge)
                # if this state is now satisfied, then this state is deemed as valid
                rv = check_state_satisfied(cur_subgoal, planner.env_state.to_dict()) # type: ignore
                if rv: 
                    new_executed_actions = copy.deepcopy(cur_executed_actions)
                    new_subgoals = copy.deepcopy(cur_subgoals[1:]) if len(cur_subgoals) > 1 else []
                    new_level = cur_level + 1
                    new_env_state = copy.deepcopy(cur_env_states)
                    new_history_env_states = copy.deepcopy(cur_history_env_states)
                    queue.append((new_env_state, new_executed_actions, new_subgoals, new_level, new_history_env_states))
                    # continue
                else:
                    solution_candidates = get_state_solution_candidates(cur_subgoal, planner, planner.acting_char_id)
                    if solution_candidates is None:
                        continue
                    for action_seq in solution_candidates:
                        planner.env_state = copy.deepcopy(prev_env_states)
                        success = True
                        for action_instruction in action_seq:
                            success, my_info = planner.my_execute_primitive_action_eval(action_instruction)
                            if not success:
                                failed_error_code = my_info.get_error_type()
                                failed_error_seq = my_info.get_error_string()
                                failed_error_code, failed_error_seq = check_satisfied_in_prev_states(cur_subgoal, cur_history_env_states, failed_error_code, failed_error_seq)
                                failed_action_seq = cur_executed_actions + action_seq
                                failed_actions_candidates.append((failed_error_code, failed_action_seq, failed_error_seq))
                                break
                        if success:
                            new_executed_actions = copy.deepcopy(cur_executed_actions)
                            new_executed_actions.append(action_seq)
                            new_subgoals = copy.deepcopy(cur_subgoals[1:]) if len(cur_subgoals) > 1 else []
                            new_level = cur_level + 1
                            new_env_state = copy.deepcopy(planner.env_state)
                            new_history_env_states = copy.deepcopy(cur_history_env_states)
                            new_history_env_states.append(copy.deepcopy(new_env_state.to_dict()))
                            queue.append((new_env_state, new_executed_actions, new_subgoals, new_level, new_history_env_states))


        # if current is action, then first produce its side_effect actions, then execute them, and consume current action

        # if current is a state/relation, first check whether it is satisfied
        ## if this state/relation is satisfied, then consume it
        ## else, find action sequence candidates to satisfy this state/relation, then append them to the queue as a list, where we would iterate all possible candidates
    return feasible_solutions, executable, failed_actions_candidates


def eval_subgoal_plan_tl(log_file_path, task_state_file_path, task_state_per_prog_file_path):
    with open(log_file_path, 'r') as f:
        gen_subgoal_dict = json.load(f)
    with open(task_state_file_path, 'r') as f:
        task_state_dict = json.load(f)
    with open(task_state_per_prog_file_path, 'r') as f:
        task_state_per_prog_dict = json.load(f)
    
    scene_str = 'scene_1'
    tasks = gen_subgoal_dict[scene_str]
    task_states = task_state_dict[scene_str]
    task_states_per_prog = task_state_per_prog_dict[scene_str]

    vocab_predicates = vocab.get_tl_predicates()
    vocab_actions = vocab.get_subgoal_actions_in_list()
    # vocab_actions = vocab.get_actions_all_in_list()
    exe_files_path = get_exe_files_path()
    state_files_path = get_state_files_path()

    total_num = 0
    grammar_wrong = 0
    grammar_correct = 0
    grammar_error_dict = {}

    semantic_correct = 0
    semantic_wrong_predicates_dict = {}
    semantic_unpaired_objs_dict = {}
    
    runtime_correct = 0
    runtime_missing_action_dict = {}
    runtime_executable_plan_dict = {}
    runtime_well_defined_subgoals_dict = {}
    runtime_correct_plan_dict = {}
    total_task_error_dict = {}
    for task_name, files in tasks.items():
        semantic_wrong_predicates_dict[task_name] = []
        semantic_unpaired_objs_dict[task_name] = []
        runtime_missing_action_dict[task_name] = []
        runtime_executable_plan_dict[task_name] = []
        runtime_correct_plan_dict[task_name] = []
        runtime_well_defined_subgoals_dict[task_name] = []
        task_error_dict = {
            "wrong_order": 0,
            "missing_step": 0,
            "affordance": 0,
            "unseen": 0,
            "additional_step": 0,
            "other": 0
        }
        for file_id, file_info in files.items():
            if file_id != '988_1':
                continue
            assert file_id in task_states_per_prog[task_name], f"File id: {file_id} not in task_states_per_prog"
            original_output = file_info['original']
            tl_formula = file_info['tl_formula']
            tl_final_goal = task_states_per_prog[task_name][file_id]['tl_goal']
            if tl_final_goal == None:
                print(f"Task {task_name}, file {file_id} has no valid final goal")
                continue

            total_num += 1
            # Below is the grammar parsing and checking part
            try:
                # translate all actions into tl actions, then combine them with connective 'then' to form a ltl formula 
                parsed_tl_expression = parse_simple_tl(tl_formula, vocab_predicates, vocab_actions)
                grammar_correct += 1
            except Exception as e:
                grammar_wrong += 1
                if e.__class__.__name__ not in grammar_error_dict:
                    grammar_error_dict[e.__class__.__name__] = [file_id]
                else:
                    grammar_error_dict[e.__class__.__name__].append(file_id)
                continue

            # Below is the semantic checking part
            props, actions = extract_propositions_and_actions(parsed_tl_expression)
            state_file_path = f"{state_files_path}\\file{file_id}.json"
            init_state, final_state = load_graph_state(state_file_path)
            planner = get_motion_planner(init_state, final_state)
            id_2_name_dict = planner.id_to_name
            ## First, we need to check objects number is correct for all predicates
            ## Second, we need to check the object name and object id are paired correctly
            param_num_correct, obj_name_id_pair_correct = check_primitives(props, actions, id_2_name_dict)
            if param_num_correct and obj_name_id_pair_correct:
                semantic_correct += 1
            else:
                if not param_num_correct:
                    semantic_wrong_predicates_dict[task_name].append(file_id)
                else:
                    semantic_unpaired_objs_dict[task_name].append(file_id)
                continue

            
            # Below is the runtime checking part
            ans_id = get_candidate_id(file_id, task_states[task_name]['task_file_list_with_ans'])
            ans = task_states[task_name]['goal_candidates'][ans_id]
            required_actions = ans['actions']
            missing_action = check_missing_actions(actions, required_actions, file_id)
            if missing_action:
                runtime_missing_action_dict[task_name].append(file_id)
                continue

            unparsed_valid_lines = split_original_output(original_output)
            unparsed_output = '\n'.join(unparsed_valid_lines)
            valid_lines = parse_output_plan(unparsed_output)
            translated_lines = translate_predicate_into_vh(valid_lines)
            target_goals = get_final_goals_in_vh_format(planner, ans)
            # print(f"Target goals: {target_goals}")
            
            parsed_tl_final_goal = parse_simple_tl(tl_final_goal, vocab_predicates, vocab_actions)
        

            result, executable, failed_info = execute_subgoal_sequence(translated_lines, target_goals, parsed_tl_final_goal, planner)
            result_success = False
            if executable == 1:
                print(f"Task {task_name}, file {file_id} has executable plan")
                runtime_executable_plan_dict[task_name].append(file_id)
                if len(result) > 0:
                    runtime_correct += 1
                    runtime_correct_plan_dict[task_name].append(file_id)
                    print(f"Task {task_name}, file {file_id} has correct plan")
                    result_success = True
                    well_defined_check = check_well_defined_subgoals(file_id, parsed_tl_expression, exe_files_path, state_files_path)
                    print(original_output)
                    print(result)
                    if well_defined_check is None:
                        pass
                    elif well_defined_check is True:
                        runtime_well_defined_subgoals_dict[task_name].append(file_id)
                        print(f"Task {task_name}, file {file_id} has well defined subgoals")
                    else:
                        print(f"Task {task_name}, file {file_id} has ill defined subgoals")
            else:
                print(f"Task {task_name}, file {file_id} has no executable plan")
            if not result_success:
                print(f"  Fail Plan is:")
                for translated_line in valid_lines:
                    print("  -", translated_line)
                print(f"  Fail Final goals are:")
                for target_goal in target_goals:
                    print("  -", target_goal)
                
                if len(failed_info) > 0:
                    failed_first_item = failed_info[0]
                    error_type, failed_exe_action_seq, failed_error_seq = failed_first_item
                    error_str = set_error_type(task_error_dict, error_type)
                    print(f"  Wrong Error Type: {error_str}")
                    print(f"  Wrong Action Sequence: {failed_exe_action_seq if executable == 0 else result}")
                    print(f"  Wrong Error Sequence: {failed_error_seq}")
                else:
                    print(f"  An unknown error occured!")
                    task_error_dict['other'] += 1
        total_task_error_dict[task_name] = task_error_dict
        ...
    print(f"Total number of tasks: {total_num}")
    print(f"Grammar correct: {grammar_correct}, Grammar wrong: {grammar_wrong}")
    print(f"Semantic correct: {semantic_correct}")
    print(f"Runtime correct: {runtime_correct}")
    print_error_type(grammar_error_dict)
    print(f'Statistics for semantic wrong predicates num: {sum([len(v) for v in semantic_wrong_predicates_dict.values()])}')
    print(f'Statistics for semantic unpaired objects num: {sum([len(v) for v in semantic_unpaired_objs_dict.values()])}')
    print(f'Statistics for runtime missing action num: {sum([len(v) for v in runtime_missing_action_dict.values()])}')
    print(f'Statistics for runtime executable plan num: {sum([len(v) for v in runtime_executable_plan_dict.values()])}')
    print(f'Statistics for runtime correct plan num: {sum([len(v) for v in runtime_correct_plan_dict.values()])}')
    print(f'Statistics for runtime well defined subgoals num: {sum([len(v) for v in runtime_well_defined_subgoals_dict.values()])}')
    print_execution_error_statistics(total_num, total_task_error_dict)


def get_raw_states_and_actions(action_seq, planner:MotionPlanner):
    '''
    Args:
        action_seq: a list of actions, should be processed before. Can be obtained from the function load_an_action_sequence or generated by the model
        planner: a motion planner'''
    raw_actions = []
    raw_states = []
    current_states = copy.deepcopy(planner.env_state.to_dict())
    raw_states.append(current_states)
    for action in action_seq:
        raw_actions.append(action)
        rv, my_info = planner.my_execute_primitive_action_eval(action)
        if not rv:
            print(f"Failed to execute action: {action}")
            failed_error_code = my_info.get_error_type()
            failed_error_seq = my_info.get_error_string()
            error_info_list = (failed_error_code, failed_error_seq, raw_actions)
            raise Exception(str(error_info_list))
        else:
            current_states = copy.deepcopy(planner.env_state.to_dict())
            raw_states.append(current_states)
    return raw_states, raw_actions

def eval_tl_final_goal_operator(raw_states, raw_actions, id_to_name_dict, tl_final_goal):
    '''
    Args:
        raw_states: a list of states, each state is a dictionary
        raw_actions: a list of actions, each action is a dictionary
        id_to_name_dict: a dictionary mapping object id to object name
        tl_final_goal: parsed version. A string representing the final goal in temporal logic.
    '''
    tl_states = get_tl_states_seq(raw_states, id_to_name_dict)
    tl_actions = get_tl_action_seq(raw_actions)
    trajectory = get_trajectory(tl_states, tl_actions)
    result = eval_simple_tl(tl_final_goal, trajectory)
    return result

if __name__ == '__main__':
    saved_file_path = 'F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\log\\eval_subgoal\\20240430232232_gpt4_translated.json' # gpt 4
    # saved_file_path = 'F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\log\\eval_subgoal\\20240430213941_translated.json' # gpt 3.5
    task_state_dict_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\resources\\task_state_updated.json"
    task_state_dict_per_prog_path = 'F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\resources\\task_state_LTL_formula_accurate.json'
    # parse_llm_output_into_tl_test(saved_file_path)
    eval_subgoal_plan_tl(saved_file_path, task_state_dict_path, task_state_dict_per_prog_path)
