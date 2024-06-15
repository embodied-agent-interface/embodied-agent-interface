import sys
sys.path.append('F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\simulation')

import json
import os
import ast
import re

from simple_tl_parser import parse_simple_tl
from evolving_graph.eval_robots import MotionPlanner
from evolving_graph.execution import EnvironmentGraph
from evolving_graph.filter_relevant_info import get_final_goals_in_vh_format
from utils import vocab


# build a constant str value '<PARAM>' as placeholder
PARAM = 'xid'

def build_or_expression(predicates):
    exp = '(' + ' or '.join(predicates) + ')' if len(predicates) > 1 else predicates[0] if len(predicates) > 0 else None
    return exp

def build_and_expression(predicates):
    exp = '(' + ' and '.join(predicates) + ')' if len(predicates) > 1 else predicates[0] if len(predicates) > 0 else None
    return exp

def build_then_expression(predicates):
    exp = '(' + ' then '.join(predicates) + ')' if len(predicates) > 1 else predicates[0] if len(predicates) > 0 else None
    return exp

def build_not_expression(predicate):
    exp = f'not ({predicate})'
    return exp

def build_implication_expression(predicate1, predicate2):
    exp = f'(not {predicate1} or {predicate2})'
    return exp


def get_vh_tasks_state_file(file_path:str, scene_id:int):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    scene_str = f'scene_{scene_id}'
    tasks_state = data[scene_str]
    return tasks_state

def translate_actions_into_exists(actions_with_placeholders):
    last_level_expression = None
    max_valid_param_num = 2 if len(actions_with_placeholders[2]) > 0 else 1 if len(actions_with_placeholders[1]) > 0 else 0
    for i in range(max_valid_param_num, -1, -1): # start from 2 to 0, including 2, 1, 0
        current_level_expressions = []
        current_level_expressions.extend(actions_with_placeholders[i])
        if last_level_expression:
            current_level_expressions.append(last_level_expression)
        current_level_total_expression = build_or_expression(current_level_expressions)
        param_str = PARAM.replace('id', str(i-1))
        last_level_expression = f'exists {param_str}. ({current_level_total_expression})'

    return current_level_total_expression
    

# -------- Below is the wildcard translation area ------------
def get_actions_with_param_placeholder(actions_with_args):
    actions_with_placeholders = {
        0: [],
        1: [],
        2: []
    }
    for action_name, arg_num in actions_with_args:
        args = [PARAM.replace('id', str(i)) for i in range(arg_num)]
        tl_action_template = f'{action_name}({",".join(args)})'
        actions_with_placeholders[arg_num].append(tl_action_template)
    return actions_with_placeholders
    
def parse_wildcard_name_into_primitive(state_str):
    '''
    This function parses the wildcard name into primitive name.
    :return: a tuple of (type, value) where type is 'n' for name value and 'p' for property value list
    '''
    if state_str[0] == '?':
        if 'character' in state_str:
            return ('n', 'character')
        regex_pattern = r'<Property\.(\w+):'
        match = re.findall(regex_pattern, state_str)
        assert match
        return ('p', match)
    return ('n', state_str)

def parse_wildcard_vh_single_goal(goal:dict):
    selected_node_state, selected_edge_state, accurate_edge_state, actions = goal['selected_node_state'], goal['selected_edge_state'], goal['accurate_edge_state'], goal['actions']

    # parsing priority is 1. actions (with temporal order) 2. all other states (connected with and)
    ## we first parse the actions
    action_info_dict = vocab.get_actions_all()
    temporal_order_list = []
    for action_str in actions:
        action_candidates = action_str.split('|')
        actions = [a.replace(' ', '').upper().strip() for a in action_candidates]
        actions_with_args = [(a, action_info_dict[a]) for a in actions] 
        actions_with_placeholders = get_actions_with_param_placeholder(actions_with_args)
        total_action_expression = translate_actions_into_exists(actions_with_placeholders)
        temporal_order_list.append(total_action_expression)
       
    ## we then parse states and relations
    ### we first handle node states
    node_exp_list = []
    vh_states_to_tl_dict = vocab.get_vh_states_to_tl_dict()
    for node_str, _ in selected_node_state.items():
        node_str_candidates = node_str.split('|')
        node_state_candidates = [ast.literal_eval(node_s) for node_s in node_str_candidates]
        predicate_list = []
        for node_state in node_state_candidates:
            name, state = node_state['name'], node_state['state']
            tl_state = vh_states_to_tl_dict[state]
            tl_predicate = f'{tl_state}({name})'
            predicate_list.append(tl_predicate)
        cur_step_exp = build_or_expression(predicate_list)
        node_exp_list.append(cur_step_exp)
    
    ### we then handle edge states
    edge_exp_list = []
    vh_relations_to_tl_dict = vocab.get_vh_relations_to_tl_dict()
    #### we first handle accurate edge states
    for edge_str, _ in accurate_edge_state.items():
        edge_str_candidates = edge_str.split('|')
        edge_state_candidates = [ast.literal_eval(edge_s) for edge_s in edge_str_candidates]
        predicate_list = []
        for edge_state in edge_state_candidates:
            from_name, relation, to_name = edge_state['from_name'], edge_state['relation'], edge_state['to_name']
            tl_relation = vh_relations_to_tl_dict[relation]
            tl_predicate = f'{tl_relation}({from_name}, {to_name})'
            predicate_list.append(tl_predicate)
        cur_step_exp = build_or_expression(predicate_list)
        edge_exp_list.append(cur_step_exp)
    
    #### we then handle selected edge states
    for edge_str, _ in selected_edge_state.items():
        edge_state = ast.literal_eval(edge_str)
        from_name, relation, to_name = edge_state['from_name'], edge_state['relation'], edge_state['to_name']
        from_name_candidates_wildcard = from_name.split('|')
        relation_candidates = relation.split('|')
        to_name_candidates_wildcard = to_name.split('|')

        from_name_candidates = [parse_wildcard_name_into_primitive(from_name) for from_name in from_name_candidates_wildcard]
        to_name_candidates = [parse_wildcard_name_into_primitive(to_name) for to_name in to_name_candidates_wildcard]

        predicate_list = []
        for cur_from_name_type, cur_from_name in from_name_candidates:
            for cur_relation in relation_candidates:
                for cur_to_name_type, cur_to_name in to_name_candidates:
                    cur_tl_relation = vh_relations_to_tl_dict[cur_relation]
                    if cur_from_name_type == 'n' and cur_to_name_type == 'n':
                        tl_predicate = f'{cur_tl_relation}({cur_from_name}, {cur_to_name})'
                        predicate_list.append(tl_predicate)

                    elif cur_from_name_type == 'n' and cur_to_name_type == 'p':
                        to_properties_list = [f'{prop}(x)' for prop in cur_to_name]
                        tl_predicate = f'{cur_tl_relation}({cur_from_name}, x)'

                        # tl_total_expression = build_and_expression(to_properties_list + [tl_predicate]) this is a deprecated version, as we will introduce implication rule here
                        to_properties_and_str = build_and_expression(to_properties_list)
                        tl_total_expression = build_implication_expression(to_properties_and_str, tl_predicate)

                        tl_forall_expression = f'forall x. {tl_total_expression}'
                        predicate_list.append(tl_forall_expression)

                    elif cur_from_name_type == 'p' and cur_to_name_type == 'n':
                        from_properties_list = [f'{prop}(x)' for prop in cur_from_name]
                        tl_predicate = f'{cur_tl_relation}(x, {cur_to_name})'

                        # tl_total_expression = build_and_expression(from_properties_list + [tl_predicate]) this is a deprecated version
                        from_properties_and_str = build_and_expression(from_properties_list)
                        tl_total_expression = build_implication_expression(from_properties_and_str, tl_predicate)

                        tl_forall_expression = f'forall x. {tl_total_expression}'
                        predicate_list.append(tl_forall_expression)

                    elif cur_from_name_type == 'p' and cur_to_name_type == 'p':
                        from_properties_list = [f'{prop}(x)' for prop in cur_from_name]
                        to_properties_list = [f'{prop}(y)' for prop in cur_to_name]
                        tl_predicate = f'{cur_tl_relation}(x, y)'

                        from_properties_and_str = build_and_expression(from_properties_list)
                        to_properties_and_str = build_and_expression(to_properties_list)
                        
                        # tl_total_expression = build_and_expression(from_properties_list + to_properties_list + [tl_predicate]) this is a deprecated version
                        # tl_forall_expression = f'forall x. (forall y. ({tl_total_expression}))'
                        ### first build forall y
                        tl_total_expression_for_y = build_implication_expression(to_properties_and_str, tl_predicate)
                        tl_forall_expression_for_y = f'(forall y. {tl_total_expression_for_y})'
                        ### then build forall x
                        tl_total_expression = build_implication_expression(from_properties_and_str, tl_forall_expression_for_y)

                        tl_forall_expression = f'forall x. {tl_total_expression}'

                        predicate_list.append(tl_forall_expression)
        cur_step_exp = build_or_expression(predicate_list)
        edge_exp_list.append(cur_step_exp)

    ## we combine all the expressions
    complete_all_states_expression = build_and_expression(node_exp_list + edge_exp_list)

    temporal_order_list.append(complete_all_states_expression) if complete_all_states_expression and complete_all_states_expression != '' else None
    complete_expression = build_then_expression(temporal_order_list)
    return complete_expression

def parse_wildcard_vh_goals(goal_candidates):
    '''
    Parses the wildcard goals for VH tasks
    '''
    goal_expression_list = []
    for goal in goal_candidates:
        exp = parse_wildcard_vh_single_goal(goal)
        goal_expression_list.append(exp)
    return ' or '.join(goal_expression_list)

def parse_vh_tasks(task_state_file_path:str, scene_id:int):
    '''
    Parses the VH tasks state file and returns the tasks state dictionary
    '''
    tasks_state_dict = get_vh_tasks_state_file(task_state_file_path, scene_id)
    new_tasks_state_dict = {}

    for task_name, task_info in tasks_state_dict.items():
        # print(task_name)
        goal_candidates = task_info['goal_candidates']
        goal_candidates_exp = parse_wildcard_vh_goals(goal_candidates)
        print(goal_candidates_exp)
        new_tasks_state_dict[task_name] = {
            'task_file_list': task_info['task_file_list'],
            'goal_candidates': goal_candidates_exp
        }
    
    new_tasks_state_file = {
        f"scene_{scene_id}": new_tasks_state_dict
    }

    return new_tasks_state_file


def generate_new_state_dict():
    file_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\resources\\task_state_updated.json"
    new_file_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\resources\\task_state_LTL_formula_ir.json"
    scene_id = 1
    new_task_state_dict = parse_vh_tasks(file_path, scene_id)
    with open(new_file_path, 'w', encoding='utf-8') as f:
        json.dump(new_task_state_dict, f, indent=2)

def check_new_state_validity():
    new_file_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\resources\\task_state_LTL_formula.json"
    with open(new_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    tasks_state_dict = data['scene_1']

    tl_predicates_vocab = vocab.get_tl_predicates()
    tl_actions_vocab = vocab.get_actions_all_in_list()
    
    success = True
    for task_name, task_info in tasks_state_dict.items():
        text = task_info['goal_candidates']
        try:
            rv = parse_simple_tl(text, tl_predicates_vocab, tl_actions_vocab)
            if rv is None:
                raise ValueError('Invalid LTL formula')
        except Exception as e:
            success = False
            print(f'Error in task: {task_name}')
            print(e)
    
    if success:
        print('All translated wildcard tasks are valid!')
# -------- End of the wildcard translation area ------------

# -------- Below is the accurate translation area ------------
def generate_accurate_goal():
    file_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\resources\\task_state_updated.json"
    tasks_state_dict = get_vh_tasks_state_file(file_path, 1)
    new_accurate_task_dict = {}
    for task_name, task_info in tasks_state_dict.items():
        task_file_list_with_ans = task_info['task_file_list_with_ans']
        goal_candidates = task_info['goal_candidates']
        for file_info_str in task_file_list_with_ans:
            file_id, ans_id = ast.literal_eval(file_info_str)
            if ans_id == -1:
                continue

            cur_goal = goal_candidates[ans_id]
            actions = cur_goal['actions']

            state_file_path = os.path.join(tasks_state_dict[task_name]['graph_state_path'], f'file{file_id}.json')
            state_dict = json.load(open(state_file_path, 'r'))
            init_state_dict = state_dict['init_graph']
            final_state_dict = state_dict['final_graph']
            init_scene_graph = EnvironmentGraph(init_state_dict)

            planner = MotionPlanner(init_scene_graph, final_state_dict)
            id_2_name_dict = planner.id_to_name

            cur_file_final_states = get_final_goals_in_vh_format(planner, cur_goal)
            
            temporal_order_list = []
            action_info_dict = vocab.get_actions_all()
            for action_str in actions:
                action_candidates = action_str.split('|')
                actions = [a.replace(' ', '').upper().strip() for a in action_candidates]
                actions_with_args = [(a, action_info_dict[a]) for a in actions]
                actions_with_placeholders = get_actions_with_param_placeholder(actions_with_args)
                total_action_expression = translate_actions_into_exists(actions_with_placeholders)
                temporal_order_list.append(total_action_expression)
            
            predicate_list = []
            vh_states_to_tl_dict = vocab.get_vh_states_to_tl_dict()
            vh_relations_to_tl_dict = vocab.get_vh_relations_to_tl_dict()
            for final_state in cur_file_final_states:
                if 'class_name' in final_state:
                    cur_state = final_state['state']
                    cur_state = vh_states_to_tl_dict[cur_state]
                    obj_name = f"{final_state['class_name']}.{final_state['id']}"
                    tl_predicate = f'{cur_state}({obj_name})'
                    predicate_list.append(tl_predicate)
                else:
                    from_id, relation, to_id = final_state['from_id'], final_state['relation_type'], final_state['to_id']
                    from_name = id_2_name_dict[from_id] # type: ignore
                    to_name = id_2_name_dict[to_id] # type: ignore
                    from_obj_name = f"{from_name}.{from_id}"
                    to_obj_name = f"{to_name}.{to_id}"
                    tl_relation = vh_relations_to_tl_dict[relation]
                    tl_predicate = f'{tl_relation}({from_obj_name}, {to_obj_name})'
                    predicate_list.append(tl_predicate)

            cur_step_exp = build_and_expression(predicate_list)
            temporal_order_list.append(cur_step_exp) if cur_step_exp and cur_step_exp != '' else None
            complete_expression = build_then_expression(temporal_order_list)
            if task_name not in new_accurate_task_dict:
                new_accurate_task_dict[task_name] = {}
            new_accurate_task_dict[task_name][file_id] = {}
            new_accurate_task_dict[task_name][file_id]['vh_goal'] = {
                "actions": [a.replace(' ', '').upper() for a in cur_goal['actions']],
                "goal": cur_file_final_states,
            }
            new_accurate_task_dict[task_name][file_id]['tl_goal'] = complete_expression
    new_accurate_tasks_dict = {
        'scene_1': new_accurate_task_dict
    }
    return new_accurate_tasks_dict

def generate_accurate_goal_dict():
    new_accurate_tasks_dict = generate_accurate_goal()
    new_file_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\resources\\task_state_LTL_formula_accurate.json"
    with open(new_file_path, 'w', encoding='utf-8') as f:
        json.dump(new_accurate_tasks_dict, f, indent=2)

def check_new_accurate_validity():
    new_file_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\resources\\task_state_LTL_formula_accurate.json"
    with open(new_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    tasks_state_dict = data['scene_1']
    success = True
    for task_name, files in tasks_state_dict.items():
        for file_id, file_info in files.items():
            tl_goal = file_info['tl_goal']
            if tl_goal is not None:
                try:
                    parse_simple_tl(tl_goal, vocab.get_tl_predicates(), vocab.get_actions_all_in_list())
                except Exception as e:
                    success = False
                    print(f'Error in task: {task_name} file: {file_id}')
                    print(e)
            else:
                print(f'Error in task: {task_name} file: {file_id}')
                print('TL goal is None')
    if success:
        print('All translated accurate goals tasks are valid!')

# -------- End of the accurate translation area ------------

if __name__ == '__main__':
    # generate_new_state_dict()
    # check_new_state_validity()
    # generate_accurate_goal_dict()
    check_new_accurate_validity()