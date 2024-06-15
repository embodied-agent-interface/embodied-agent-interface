from collections import deque
import json
import re
import copy
from matplotlib import pyplot as plt
import openai
import os
import time
import ast
import tqdm
import sys
sys.path.append('F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\simulation')
import evolving_graph.utils as utils
from evolving_graph.execution import Relation, State
from evolving_graph.scripts import read_script, Action, ScriptObject, ScriptLine, ScriptParseException, Script
from evolving_graph.execution import ExecutionInfo
from evolving_graph.environment import EnvironmentGraph, EnvironmentState
from evolving_graph.filter_relevant_info import get_formatted_relevant_nodes, get_initial_states_and_final_goals, get_candidate_id, MotionPlanner, name_equivalence, object_placing, properties_data, get_relevant_nodes, get_final_goals_in_vh_format

prompt_root_dir = '../../prompts'
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10809'
client = openai.OpenAI(api_key=os.environ.get('MANLING_OPENAI_KEY'))

state_from_predicate_2_vh = {
    "CLOSED": ("CLOSED", 1, 's'),
    "OPEN": ("OPEN", 1, 's'),
    "ON": ("ON", 1, 's'),
    "OFF": ("OFF", 1, 's'),
    "SITTING": ("SITTING", 1, 's'),
    "DIRTY": ("DIRTY", 1, 's'),
    "CLEAN": ("CLEAN", 1, 's'),
    "LYING": ("LYING", 1, 's'),
    "PLUGGED_IN": ("PLUGGED_IN", 1, 's'),
    "PLUGGED_OUT": ("PLUGGED_OUT", 1, 's'),
    "ONTOP": ("ON", 2, 'r'),
    "INSIDE": ("INSIDE", 2, 'r'),
    "BETWEEN": ("BETWEEN", 3, 'r'),
    "NEXT_TO": ("CLOSE", 2, 'r'),
    "FACING": ("FACING", 2, 'r'),
    "HOLDS_RH": ("HOLDS_RH", 2, 'r'),
    "HOLDS_LH": ("HOLDS_LH", 2, 'r'),
}

valid_actions = {
    "DRINK": ("DRINK", 1),
    "EAT": ("EAT", 1),
    "CUT": ("CUT", 1),
    "TOUCH": ("TOUCH", 1),
    "LOOKAT": ("LOOKAT", 1),
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
    "SWITCHOFF": ("SWITCHOFF", 1)
}

actions_must_hold = ['DRINK', 'EAT', 'READ']

def get_openai_output(messages:list, model="gpt-3.5-turbo", temperature=0.7, max_tokens=3000):
    isFail = False
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
    except openai.APITimeoutError as e:
        #Handle timeout error, e.g. retry or log
        print(f"OpenAI API request timed out: {e}")
        pass
    except openai.APIConnectionError as e:
        #Handle connection error, e.g. check network or log
        print(f"OpenAI API request failed to connect: {e}")
        pass
    except openai.AuthenticationError as e:
        #Handle authentication error, e.g. check credentials or log
        print(f"OpenAI API request was not authorized: {e}")
        pass
    except openai.BadRequestError as e:
        #Handle bad request error, e.g. check request body or log
        print(f"OpenAI API request was invalid: {e}")
        isFail = True
        pass
    except openai.PermissionDeniedError as e:
        #Handle permission error, e.g. check scope or log
        print(f"OpenAI API request was not permitted: {e}")
        pass
    except openai.RateLimitError as e:
        #Handle rate limit error, e.g. wait or log
        print(f"OpenAI API request exceeded rate limit: {e}")
        pass
    except Exception as e:
        #Handle other errors, e.g. log or raise
        print(f"OpenAI API request failed: {e}")
        isFail = True
        pass
    return completion.choices[0].message.content if not isFail else None


def read_from_scratch_prompt(prompt_file_path):
    with open(prompt_file_path, 'r') as f:
        prompts = json.load(f)
    
    info_prompt = prompts['Background'] + prompts['StateInfo'] + prompts['ActionInfo'] + prompts['SupplementInfo'] + "\n".join(prompts['GoldExamples'])

    task_prompt = prompts['TaskInfo']
    return info_prompt, task_prompt

def add_task_info_into_prompt(prompt, task_name, relv_objs, init_states, final_states, final_actions, necessity):
    return prompt.replace("<task_name>", task_name).replace("<relevant_objects>", relv_objs).replace("<initial_states>", init_states).replace("<final_states>", final_states).replace("<final_actions>", final_actions).replace("<necessity>", necessity)


def connection_test():
    messages = [
                {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
                {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
            ]
    return_message = get_openai_output(messages, max_tokens=100)
    print(return_message)

def scratch_generation_example(prompt_file_path):
    model = "gpt-3.5-turbo"
    temperature = 0.7
    max_tokens = 4000

    info_prompt, task_prompt = read_from_scratch_prompt(prompt_file_path)

    task_name = "Turn on light"
    relv_objs = '''| character.65 | Characters | [] |\n| bedroom.67 | Rooms | [] |\n| dining_room.201 | Rooms | [] |\n| floor_lamp.1000 | placable_objects | ['HAS_SWITCH', 'MOVABLE'] |'''
    init_states = '''CLEAN(floor_lamp.1000)\nOFF(floor_lamp.1000)\nINSIDE(character.65, dining_room.201)'''
    final_states = '''ON(floor_lamp.1000)'''
    final_actions = "None"

    #     task_name = "Write an email"
    #     relv_objs = '''| character.65 | Characters | [] |
    # | bedroom.67 | Rooms | [] |
    # | floor.208 | Floor | ['SURFACES'] |
    # | wall.213 | Walls | [] |
    # | home_office.319 | Rooms | [] |
    # | floor.325 | Floors | ['SURFACES'] |
    # | floor.326 | Floors | ['SURFACES'] |
    # | wall.330 | Walls | [] |
    # | wall.331 | Walls | [] |
    # | doorjamb.346 | Doors | [] |
    # | walllamp.351 | Lamps | [] |
    # | chair.356 | Furniture | ['GRABBABLE', 'MOVABLE', 'SITTABLE', 'SURFACES'] |
    # | desk.357 | Furniture | ['MOVABLE', 'SURFACES'] |
    # | powersocket.412 | Electronics | [] |
    # | mouse.413 | Electronics | ['GRABBABLE', 'HAS_PLUG', 'MOVABLE'] |
    # | mousepad.414 | Electronics | ['MOVABLE', 'SURFACES'] |
    # | keyboard.415 | Electronics | ['GRABBABLE', 'HAS_PLUG', 'MOVABLE'] |
    # | cpuscreen.416 | Electronics | [] |
    # | computer.417 | Electronics | ['HAS_SWITCH', 'LOOKABLE'] |'''
    #     init_states = '''ONTOP(keyboard.415, desk.357)
    # ONTOP(mouse.413, mousepad.414)
    # INSIDE(character.65, bedroom.67)
    # ONTOP(mouse.413, desk.357)'''
    #     final_states = '''None'''
    #     final_actions = '''[TYPE]
    # [SWITCHOFF]'''
    necessity = 'yes' if final_actions != "None" else 'no'

    task_prompt = add_task_info_into_prompt(task_prompt, task_name, relv_objs, init_states, final_states, final_actions, necessity)

    messages = [
        {"role": "system", "content": info_prompt},
        {"role": "user", "content": task_prompt}
    ]

    print("Input:")
    print(info_prompt + task_prompt)
    output = get_openai_output(messages, model, temperature, max_tokens)
    print("====================")
    print("Output:")
    print(output)

def scracth_all_cases_generation(prompt_file_path, log_dir_path, model='gpt-3.5-turbo'):
    temperature = 0.7
    max_tokens = 4000

    data_dir = 'F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\dataset\\programs_processed_precond_nograb_morepreconds'
    task_dict_dir = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\resources\\task_state_updated.json"
    task_dict = json.load(open(task_dict_dir, 'r'))
    scene_str = "scene_1"
    task_dict = task_dict[scene_str]

    # we use current time str as the log file name, to input as a json
    log_file_name = time.strftime("%Y%m%d%H%M%S", time.localtime())
    log_file_path = os.path.join(log_dir_path, f"{log_file_name}.json")

    log_info = {}
    log_info[scene_str] = {}

    info_prompt, task_prompt_template = read_from_scratch_prompt(prompt_file_path)

    for task_name, task_detail in task_dict.items():
        graph_path = task_detail['graph_state_path']
        task_list = task_detail['task_file_list']
        task_list_ans_list = task_detail['task_file_list_with_ans']
        goal_candidates = task_detail['goal_candidates']

        log_info[scene_str][task_name] = {}

        for file_id in task_list:
            ans_id = get_candidate_id(file_id, task_list_ans_list)
            if ans_id == -1:
                continue
            
            log_info[scene_str][task_name][file_id] = {
                "system_input": "",
                "user_input": "",
                "output": ""
            }

            goal = goal_candidates[ans_id]
            state_file_path = os.path.join(graph_path, f'file{file_id}.json')
            state_dict = json.load(open(state_file_path, 'r'))
            init_state_dict = state_dict['init_graph']
            final_state_dict = state_dict['final_graph']

            init_scene_graph = EnvironmentGraph(init_state_dict)
            planner = MotionPlanner(init_scene_graph, final_state_dict, name_equivalence, properties_data, object_placing)

            relevant_nodes, related_ids = get_relevant_nodes(planner)
            relevant_nodes = get_formatted_relevant_nodes(relevant_nodes)
            init_states, final_states, action_states = get_initial_states_and_final_goals(planner, goal)
            relevent_nodes_str = "\n".join(relevant_nodes) if len(relevant_nodes) > 0 else "None"
            init_states_str = "\n".join(init_states) if len(init_states) > 0 else "None"
            final_states_str = "\n".join(final_states) if len(final_states) > 0 else "None"
            action_states_str = "\n".join(action_states) if len(action_states) > 0 else "None"
            
            necessity = 'yes' if action_states_str != "None" else 'no'
            task_prompt = add_task_info_into_prompt(task_prompt_template, task_name, relevent_nodes_str, init_states_str, final_states_str, action_states_str, necessity)

            messages = [
                {"role": "system", "content": info_prompt},
                {"role": "user", "content": task_prompt}
            ]

            output = get_openai_output(messages, model, temperature, max_tokens)

            print(f"==[Task is {task_name}, file_id is {file_id}]")
            print(f"Input:")
            print(info_prompt+task_prompt)
            print("Output:")
            print(output)

            log_info[scene_str][task_name][file_id]["system_input"] = info_prompt
            log_info[scene_str][task_name][file_id]["user_input"] = task_prompt
            log_info[scene_str][task_name][file_id]["output"] = output
    
    with open(log_file_path, 'w') as f:
        json.dump(log_info, f, indent=2)


def display_all_outputs(log_file_path=""):
    assert os.path.exists(log_file_path), "Log path does not exist"
    with open(log_file_path, 'r') as f:
        log_info = json.load(f)
    scene_str = "scene_1"
    tasks = log_info[scene_str]
    for task_name, files in tasks.items():
        print(f"Task is {task_name}")
        for file_id, file_info in files.items():
            print(f"File id is {file_id}")
            print("Output:")
            print(file_info["output"])
            print("=========================")

def parse_output_plan(raw_output):
    def match_string(input_string):
        pattern = r'([A-Z_]+)(?:\(([^)]*)\))?'
        matches = re.findall(pattern, input_string)
        return matches
    matches = match_string(raw_output)
    matching_list = []
    for match in matches:
        if match[1] == "" and match[0] not in valid_actions and match[0] not in state_from_predicate_2_vh:
            continue
        matching_list.append((match[0], match[1].split(",")))
    return matching_list

def get_param_name_and_id(param):
    tmp = param.split('.')
    name, id = tmp[0].strip(), tmp[1]
    return name, id
    ...

def translate_action(name, params):
    action_str = f'[{name}]'
    for param in params:
        obj_name, obj_id = param
        param_str = f' <{obj_name}> ({obj_id})'
        action_str += param_str
    return action_str


def translate_predicate_into_vh(parsed_lines):
    translated_lines = []
    for line in parsed_lines:
        predicate_name, params = line
        params.remove('') if '' in params else None
        if predicate_name in state_from_predicate_2_vh:
            vh_name, _, state_type = state_from_predicate_2_vh[predicate_name]
            if state_type == 's': # node 
                obj_name, obj_id = get_param_name_and_id(params[0])
                cur_state = {'id': int(obj_id), 'class_name': obj_name, 'state': vh_name}
                translated_lines.append(('s', cur_state))
            elif state_type == 'r': # edge
                if predicate_name == 'BETWEEN':
                    obj1_name, obj1_id = get_param_name_and_id(params[0])
                    obj2_name, obj2_id = get_param_name_and_id(params[1])
                    obj3_name, obj3_id = get_param_name_and_id(params[2])
                    cur_relation = {'from_id': obj1_id, 'relation_type': vh_name, 'to_id': obj3_id}
                    translated_lines.append(cur_relation)
                else:
                    obj1_name, obj1_id = get_param_name_and_id(params[0])
                    obj2_name, obj2_id = get_param_name_and_id(params[1])
                cur_relation = {'from_id': int(obj1_id), 'relation_type': vh_name, 'to_id': int(obj2_id)}
                translated_lines.append(('r', cur_relation))
        elif predicate_name in valid_actions: # action
            # action_str = translate_action(predicate_name, params) # this is not a flexible version
            name_id_pairs = [get_param_name_and_id(param) for param in params]
            cur_action = {"name": predicate_name, "params": name_id_pairs}
            translated_lines.append(('a', cur_action))
    return translated_lines



def incremental_subgoal_plan():
    ...

def is_goal_achieved():
    ...

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
    return success

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
    
    
    return solution_candidates



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

def execute_subgoal_sequence(subgoals, final_goals, planner:MotionPlanner):

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
                        break
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

def check_id_correctness(program_lines, planner: MotionPlanner):
    invalid_ids = []
    for line in program_lines:
        _, params = line
        params.remove('') if '' in params else None
        id_2_name_dict = planner.id_to_name
        for param in params:
            obj_name, obj_id = get_param_name_and_id(param)
            if obj_name != id_2_name_dict[int(obj_id)]: # type: ignore
                invalid_ids.append((obj_name, obj_id))
                print(f"false name: {obj_name}, id: {obj_id}, real name: {id_2_name_dict[int(obj_id)]}") # type: ignore
    return invalid_ids

def set_error_type(error_dict, error_type):
    error_str = ''
    if error_type == 0:
        error_str = 'wrong_order'
    elif error_type == 1:
        error_str = 'missing_step'
    elif error_type == 2:
        error_str = 'affordance'
    elif error_type == 3:
        error_str = 'unseen'
    elif error_type == 4:
        error_str = 'additional_step'
    elif error_type == 5:
        error_str = 'other'
    else:
        assert False, f"Unknown Error Type: {error_type}"
    error_dict[error_str] += 1
    return error_str

def print_execution_error_statistics(task_num, error_dict):
    wrong_order_num = 0
    missing_step_num = 0
    affordance_num = 0
    unseen_num = 0
    additional_step_num = 0
    other_num = 0
    for task_name, error_info in error_dict.items():
        wrong_order_num += error_info['wrong_order']
        missing_step_num += error_info['missing_step']
        affordance_num += error_info['affordance']
        unseen_num += error_info['unseen']
        additional_step_num += error_info['additional_step']
        other_num += error_info['other']
    print(f"Task number is {task_num}, wrong order number is {wrong_order_num}, missing step number is {missing_step_num}, affordance number is {affordance_num}, unseen number is {unseen_num}, additional step number is {additional_step_num}, other number is {other_num}")
    

def eval_subgoal_plan(log_file_path, task_state_file_path, data_root_path):
    with open(task_state_file_path, 'r') as f:
        task_state_dict = json.load(f)
    with open(log_file_path, 'r') as f:
        log_info = json.load(f)
    scene_str = "scene_1"
    tasks = log_info[scene_str]
    task_state_dict = task_state_dict[scene_str]

    total_num = 0
    grammar_correct = 0
    actions_correct = 0
    syntactic_correct_dict = {}
    semantic_correct_dict = {}
    valid_correct_dict = {}
    grammar_correct_dict = {}
    actions_correct_dict = {}
    obj_mapping_correct_dict = {}
    executable_plan_dict = {}
    correct_plan_dict = {}
    task_num_dict = {}
    total_task_error_dict = {}
    for task_name, files in tasks.items():
        # ---------------
        task_syntactic_correct = 0
        task_semantic_correct = 0
        task_correct_plan = 0
        # ---------------

        task_valid_correct = 0
        task_grammar_correct = 0
        task_actions_correct = 0
        task_obj_mapping_correct = 0
        task_executable_plan = 0

        # ---------Error Types---------
        task_error_dict = {
            "wrong_order": 0,
            "missing_step": 0,
            "affordance": 0,
            "unseen": 0,
            "additional_step": 0,
            "other": 0
        }
        # -----------------------------

        for file_id, file_info in files.items():
            # if file_id != '188_1':
            #     continue
            task_num_dict[task_name] = task_num_dict.get(task_name, 0) + 1
            total_num += 1
            # if file_id != '496_1':
            #     continue
            llm_output = file_info["output"]
            parsed_output = parse_output_plan(llm_output)

            ans_id = get_candidate_id(file_id, task_state_dict[task_name]['task_file_list_with_ans'])
            ans = task_state_dict[task_name]['goal_candidates'][ans_id]
            syntatic_error = False
            semantic_error = False
            runtime_error = False

            if len(parsed_output) == 0:
                print(f"Task {task_name}, file {file_id} has no valid output")
                syntatic_error = True
            else:
                task_valid_correct += 1
            if not check_output_grammar(parsed_output):
                print(f"Task {task_name}, file {file_id} has grammar error")
                syntatic_error = True
            else:
                task_grammar_correct += 1

            if syntatic_error:
                continue
            task_syntactic_correct += 1


            valid_lines, action_pass = check_actions(parsed_output, ans)
            if not action_pass:
                print(f"Task {task_name}, file {file_id} has wrong actions")
                semantic_error = True
                # continue
            else:
                task_actions_correct += 1
            state_file_path = os.path.join(task_state_dict[task_name]['graph_state_path'], f'file{file_id}.json')
            state_dict = json.load(open(state_file_path, 'r'))
            init_state_dict = state_dict['init_graph']
            final_state_dict = state_dict['final_graph']
            init_scene_graph = EnvironmentGraph(init_state_dict)
            
            planner = MotionPlanner(init_scene_graph, final_state_dict)
            false_ids = check_id_correctness(valid_lines, planner)

            if len(false_ids) > 0:
                # currently, if there exists wrong id, we assume it cannot handle it correctly
                print(f"Task {task_name}, file {file_id} has wrong ids")
                semantic_error = True
                # continue
            else:
                task_obj_mapping_correct += 1

            if semantic_error:
                continue
            task_semantic_correct += 1

            translated_lines = translate_predicate_into_vh(valid_lines)
            
            target_goals = get_final_goals_in_vh_format(planner, ans)
            result, executable, failed_info = execute_subgoal_sequence(translated_lines, target_goals, planner)
            result_success = False
            if executable == 1:
                task_executable_plan += 1
                print(f"Task {task_name}, file {file_id} has executable plan")
                if len(result) > 0:
                    task_correct_plan += 1
                    print(f"Task {task_name}, file {file_id} has correct plan")
                    result_success = True
            else:
                print(f"Task {task_name}, file {file_id} has no executable plan")
            if not result_success:   
                print(f"  Fail Plan is:")
                for translated_line in valid_lines:
                    print("  -", translated_line)
                print(f"  Fail Final goals are:")
                for target_goal in target_goals:
                    print("  -", target_goal)

                # two options: first is, calc all statistics; second is, only get the first one
                ## we get the first one
                if len(failed_info) > 0:
                    failed_first_item = failed_info[0]
                    error_type, failed_exe_action_seq, failed_error_seq = failed_first_item
                    error_str = set_error_type(task_error_dict, error_type)
                    print(f"  Wrong Error Type: {error_str}")
                    print(f"  Wrong Action Sequence: {failed_exe_action_seq}")
                    print(f"  Wrong Error Sequence: {failed_error_seq}")
                else:
                    print(f"  We confront an unknown error!")
                    task_error_dict['other'] += 1
                
            # exit()
        syntactic_correct_dict[task_name] = task_syntactic_correct
        semantic_correct_dict[task_name] = task_semantic_correct
        valid_correct_dict[task_name] = task_valid_correct
        grammar_correct_dict[task_name] = task_grammar_correct
        actions_correct_dict[task_name] = task_actions_correct
        obj_mapping_correct_dict[task_name] = task_obj_mapping_correct
        executable_plan_dict[task_name] = task_executable_plan
        correct_plan_dict[task_name] = task_correct_plan
        total_task_error_dict[task_name] = task_error_dict

    print(f"Total number of tasks is {total_num}, syntactic correct number is {sum(syntactic_correct_dict.values())}")
    print(f"Total number of tasks is {total_num}, semantic correct number is {sum(semantic_correct_dict.values())}")

    print(f"Total number of tasks is {total_num}, valid correct number is {sum(valid_correct_dict.values())}")
    print(f"Total number of tasks is {total_num}, grammar correct number is {sum(grammar_correct_dict.values())}")

    print(f"Total number of syntactic correct tasks is {sum(syntactic_correct_dict.values())}, obj mapping correct number is {sum(obj_mapping_correct_dict.values())}")
    print(f"Total number of syntactic correct tasks is {sum(syntactic_correct_dict.values())}, actions correct number is {sum(actions_correct_dict.values())}")

    print(f"Total number of semantic correct tasks is {sum(semantic_correct_dict.values())}, executable plan number is {sum(executable_plan_dict.values())}")
    print(f"Total number of semantic correct tasks is {sum(semantic_correct_dict.values())}, correct plan number is {sum(correct_plan_dict.values())}")
    print_execution_error_statistics(total_num, total_task_error_dict)
    
    
    return total_num, syntactic_correct_dict, semantic_correct_dict, task_num_dict, grammar_correct_dict, actions_correct_dict, obj_mapping_correct_dict, executable_plan_dict, correct_plan_dict, total_task_error_dict, valid_correct_dict


def check_output_grammar(parsed_lines):
    for line in parsed_lines:
        predicate_name, params = line
        params.remove('') if '' in params else None
        if predicate_name in valid_actions:
            if len(params) != valid_actions[predicate_name][1]:
                print(f"  Action {predicate_name} has wrong number of parameters")
                return False
        elif predicate_name in state_from_predicate_2_vh:
            if len(params) != state_from_predicate_2_vh[predicate_name][1]:
                print(f"  State {predicate_name} has wrong number of parameters")
                return False
        else:
            print(f"  Predicate {predicate_name} is not valid")
            return False
    return True


def check_actions(parsed_lines, ans):
    tmp_actions = ans['actions']
    action_candidates = []
    for a in tmp_actions:
        action_candidates.append([element.upper().replace(" ", '') for element in a.split("|")])
    actions = copy.deepcopy(action_candidates)
    valid_lines = []
    for line in parsed_lines:
        predicate_name, params = line
        if predicate_name in valid_actions:
            found = False
            for a in action_candidates:
                if predicate_name in a:
                    found = True
                    break
            if found:
                valid_lines.append(line)
            else:
                print(f"  Action {predicate_name} not in the answer")
                return [], False
            for a in action_candidates:
                if predicate_name in a:
                    actions.remove(a) if a in actions else None
                    break
        else:
            valid_lines.append(line)
    return valid_lines, True if len(actions) == 0 else False



## Above is old virtualhome version

## Below is temporal logic version


def translate_llm_simplified_tl_into_tl(llm_output_goal:str):
    predicate_candidates = llm_output_goal.strip().split('\n')
    predicates = []
    for p in predicate_candidates:
        if '(' not in p or ')' not in p:
            continue
        else:
            predicates.append(p.strip())
    return ' then '.join(predicates)

def translate_llm_outputs_into_tl(log_file_path, saved_file_path):
    with open(log_file_path, 'r') as f:
        log_info = json.load(f)
    result = {
        "scene_1": {}
    }
    scene_str = "scene_1"
    tasks = log_info[scene_str]
    for task_name, task_list in tasks.items():
        result[scene_str][task_name] = {}
        for program_id, program_info in task_list.items():
            llm_output = program_info['output']
            result[scene_str][task_name][program_id] = {}
            try:
                tl_formula = translate_llm_simplified_tl_into_tl(llm_output)
                result[scene_str][task_name][program_id]['original'] = llm_output
                result[scene_str][task_name][program_id]['tl_formula'] = tl_formula
            except Exception as e:
                print(f"Error: {e}")
                
    with open(saved_file_path, 'w') as f:
        json.dump(result, f, indent=4)







def main_test_translate_llm_outputs_into_tl():
    log_fil_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\log\\eval_subgoal\\20240430232232_gpt4.json"
    saved_file_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\log\\eval_subgoal\\20240430232232_gpt4_translated.json"
    translate_llm_outputs_into_tl(log_fil_path, saved_file_path)


def plt_the_figure(task_list, success_rate_list, title_name, file_name="", metric_name="Success Rates"):
    base_pic_dir = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\pics"
    pic_path = os.path.join(base_pic_dir, f"{file_name}.png")
    plt.figure(figsize=(26, 10))
    plt.bar(task_list, success_rate_list, width=0.8)
    plt.xticks(rotation=45, ha='right')
    plt.tick_params(axis='x', which='major', labelsize=14)
    plt.tick_params(axis='y', which='major', labelsize=12)
    plt.grid(axis='y')
    plt.xlabel('Tasks', fontsize=16)
    plt.ylabel(f'{metric_name}', fontsize=16)
    plt.title(f'{title_name} {metric_name}', fontsize=18)
    plt.tight_layout()
    plt.savefig(pic_path, dpi=500)

def plot_grammar(task_num_dict, grammar_dict):
    task_list = []
    success_rate_list = []
    for task_name, num in grammar_dict.items():
        task_list.append(task_name)
        success_rate_list.append(num/task_num_dict[task_name] if task_num_dict[task_name] != 0 else 0)
    plt_the_figure(task_list, success_rate_list, "Grammar", "grammar")




def plot_actions(task_num_dict, actions_dict):
    task_list = []
    success_rate_list = []
    for task_name, num in actions_dict.items():
        task_list.append(task_name)
        success_rate_list.append(num/task_num_dict[task_name] if task_num_dict[task_name] != 0 else 0)
    plt_the_figure(task_list, success_rate_list, "Actions", "actions_1")

def plot_general(task_num_dict, general_dict, title_name):
    task_list = []
    success_rate_list = []
    for task_name, num in general_dict.items():
        task_list.append(task_name)
        success_rate_list.append(num/task_num_dict[task_name] if task_num_dict[task_name] != 0 else 0)
    plt_the_figure(task_list, success_rate_list, title_name, title_name.lower().replace(" ", "_"))

def plot_error_type_num(total_error_dict, error_name):
    task_list = []
    error_list = []
    for task_name, error_dict in total_error_dict.items():
        task_list.append(task_name)
        error_list.append(error_dict[error_name])
    plt_the_figure(task_list, error_list, error_name, error_name.lower().replace(" ", "_"), 'Number')


def test_field(file_id="417_1"):
    graph_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\dataset\\programs_processed_precond_nograb_morepreconds\\init_and_final_graphs\\TrimmedTestScene1_graph\\results_intentions_march-13-18"
    file_name = f'file{file_id}.json'
    state_file_path = os.path.join(graph_path, file_name)
    state_dict = json.load(open(state_file_path, 'r'))
    init_state_dict = state_dict['init_graph']
    final_state_dict = state_dict['final_graph']
    init_scene_graph = EnvironmentGraph(init_state_dict)
    planner = MotionPlanner(init_scene_graph, final_state_dict)
    action_seq = ['[FIND] <clothes_pants> (1002)', '[GRAB] <clothes_pants> (1002)', '[FIND] <washing_machine> (1000)', '[PUTBACK] <clothes_pants> (1002) <washing_machine> (1000)']
    success = False

    for action in action_seq:
        success = planner.my_execute_primitive_action(action)
        if not success:
            print(f'Action {action} fails.')

def main_draw_statistics_plot():
    prompt_file_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\prompts\\subgoal_plan_scratch_version.json"
    eval_subgoal_log_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\log\\eval_subgoal"
    log_file_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\log\\eval_subgoal\\20240408011211.json"
    task_state_file_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\resources\\task_state_updated.json"
    data_root_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\dataset\\programs_processed_precond_nograb_morepreconds\\init_and_final_graphs\\TrimmedTestScene1_graph\\results_intentions_march-13-18"
    total, syntactic_correct_dict, sementic_correct_dict, task_num_dict, grammar_dict, action_dict, obj_mapping_dict, executable_dict, correct_dict, error_dict, valid_correct_dict = eval_subgoal_plan(log_file_path, task_state_file_path, data_root_path)
    # test_field()


    # plot_general(task_num_dict, syntactic_correct_dict, "Syntactic")
    # plot_general(task_num_dict, sementic_correct_dict, "Semantic")
    # plot_general(task_num_dict, valid_correct_dict, "Valid Plan")
    # plot_general(task_num_dict, grammar_dict, "Grammar")
    # plot_general(task_num_dict, action_dict, "Actions")
    # plot_general(task_num_dict, obj_mapping_dict, "Object Mapping")
    # plot_general(task_num_dict, executable_dict, "Executable Plan")
    # plot_general(task_num_dict, correct_dict, "Correct Plan")
    # plot_error_type_num(error_dict, "wrong_order")
    # plot_error_type_num(error_dict, "missing_step")
    # plot_error_type_num(error_dict, "affordance")
    # plot_error_type_num(error_dict, "unseen")
    # plot_error_type_num(error_dict, "additional_step")
    # plot_error_type_num(error_dict, "other")

def main_vh_llm_output_generation():
    prompt_file_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\prompts\\subgoal_plan_scratch_version.json"
    eval_subgoal_log_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\log\\eval_subgoal"
    connection_test()
    scratch_generation_example(prompt_file_path)
    scracth_all_cases_generation(prompt_file_path, eval_subgoal_log_path)
    # display_all_outputs(log_file_path=log_file_path)

def main_tl_llm_output_generation():
    prompt_file_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\prompts\\subgoal_plan_scratch_tl.json"
    eval_subgoal_log_path = "F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\log\\eval_subgoal"
    # scratch_generation_example(prompt_file_path)
    # connection_test()
    scracth_all_cases_generation(prompt_file_path, eval_subgoal_log_path)
    # scracth_all_cases_generation(prompt_file_path, eval_subgoal_log_path, model='gpt-4-turbo')

if __name__ == '__main__':
    # main_tl_llm_output_generation()
    # main_draw_statistics_plot()
    # connection_test()
    # main_test_translate_llm_outputs_into_tl()







