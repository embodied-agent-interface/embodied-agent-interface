import os
import ast
import json
import behavior_eval
from typing import Optional, Union, Any
from behavior_eval.evaluation.subgoal_decomposition.resources.prompt_template.meta_prompt import get_meta_prompt_component
from behavior_eval.evaluation.action_sequencing.action_sequence_evaluator import ActionSequenceEvaluator
from behavior_eval.tl_formula.bddl_to_tl import translate_bddl_final_states_into_simplified_tl

def translate_addressable_obj_into_tl_obj(address_obj):
    if '_' not in address_obj:
        return address_obj
    address_obj = address_obj.replace('.', '_')
    parts = address_obj.split('_')
    assert len(parts) > 1, 'Invalid addressable object name: {}'.format(address_obj)
    tl_obj = '_'.join(parts[:-1]) + '.' + parts[-1]
    return tl_obj

def get_tl_category(obj_list):
    category_map = {}
    for obj in obj_list:
        category = obj['category']
        category_map[category] = category.replace('.', '_')
    return category_map


def convert_dict_to_list(dict_file_path, list_dict_path):
    with open(dict_file_path, 'r') as f:
        dict_data = json.load(f)
    list_data = []
    for task_name, task_info in dict_data.items():
        tmp = {
            "identifier": task_name,
            "llm_prompt": task_info['llm_prompt']
        }
        list_data.append(tmp)
    with open(list_dict_path, 'w') as f:
        json.dump(list_data, f, indent=4)

def get_subgoal_prompt(env: ActionSequenceEvaluator):
    # meta_prompt_file_path = os.path.join(behavior_eval.subgoal_dec_resources_path, 'prompts', 'meta_prompt.json')
    # generate_meta_prompt(meta_prompt_file_path)

    # with open(meta_prompt_file_path, 'r') as f:
    #     prompt_components = json.load(f)

    prompt_components = get_meta_prompt_component()

    task_name = env.transition_model.config['task']
    objects_str = env.get_objects_str().strip()
    initial_states_str = env.get_initial_state().strip()
    goal_states_str = env.get_target_state().strip()
    objects_in_scene = objects_str.split('\n')
    objects_in_scene = [ast.literal_eval(obj) for obj in objects_in_scene]
    initial_states = initial_states_str.split('\n')
    initial_states = [ast.literal_eval(state) for state in initial_states]
    goal_states = goal_states_str.split('\n')
    goal_states = [ast.literal_eval(state) for state in goal_states]
    name_mapping = env.name_mapping
    tl_category_map = get_tl_category(objects_in_scene)
    tl_objs = []
    for obj in objects_in_scene:
        obj_name = obj['name']
        obj_category = obj['category']
        tl_obj_name = translate_addressable_obj_into_tl_obj(obj_name)
        tl_obj_category = tl_category_map[obj_category]
        tl_obj = {'name': tl_obj_name, 'category': tl_obj_category}
        tl_objs.append(str(tl_obj))
    tl_exps = []
    for condition in initial_states:
        tl_condition = [translate_addressable_obj_into_tl_obj(obj) for obj in condition]
        primitive = tl_condition[0]
        if primitive == 'not':
            next_primitive = tl_condition[1]
            tl_exp = f'{next_primitive}({", ".join(tl_condition[2:])})' if len(tl_condition) > 2 else next_primitive
            tl_exp = f'not {tl_exp}'
        else:
            tl_exp = f'{primitive}({", ".join(tl_condition[1:])})' if len(tl_condition) > 1 else primitive
        tl_exps.append(tl_exp)
    s_tl_goal_conditions = []
    s_tl_goal_conditions = translate_bddl_final_states_into_simplified_tl(name_mapping, tl_category_map, env.task.goal_conditions)
    task_prompt = prompt_components['target_task']
    task_prompt = task_prompt.replace('<task_name>', task_name).replace('<relevant_objects>', '\n'.join(tl_objs)).replace('<initial_states>', '\n'.join(tl_exps)).replace('<goal_states>', '\n'.join(s_tl_goal_conditions))
    
    input_prompt = task_prompt
    return input_prompt

    
