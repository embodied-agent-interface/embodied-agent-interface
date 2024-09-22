import os
import re
import ast
import json
import behavior_eval
import time
from typing import Dict, Any, List, Union, Tuple

class SimpleVocab:
    def __init__(self, vocab_path=os.path.join(behavior_eval.subgoal_dec_resources_path, 'base_vocabulary.json')):
        self.vocab_path = vocab_path
        self.vocab = self.load_vocab()
        self.predicate_list = self.get_predicate_list(self.vocab)
        self.state_param_dict = self.get_state_param_dict(self.vocab)
        self.quantifiers = ['forpairs', 'forn', 'exists', 'forall', 'fornpairs']
    
    def load_vocab(self):
        with open(self.vocab_path, 'r') as f:
            vocab = json.load(f)
        return vocab
    
    def get_predicate_list(self, vocab):
        states = self.get_states(vocab)
        return states
    
    def get_state_param_dict(self, vocab):
        return vocab['state_param']
    
    @staticmethod
    def get_states(vocab: Dict[str, Any]) -> List[str]:
        return vocab['states']
    
class GoalAnalyzer:
    def __init__(self, task_name:str, vocab:SimpleVocab, goal_info: Dict[str, Any]) -> None:
        self.task_name = task_name
        self.vocab = vocab
        self.goal_success = goal_info['success']
        self.subgoal_list = goal_info['subgoals']
        self.subgoal_states = goal_info['subgoal_success']
        self.special_states = {'toggled_on': 'toggledon'}
        pass
    
    def check_in_quantifiers(self, subgoal):
        for part in subgoal:
            if part.lower() in self.vocab.quantifiers:
                return True
        return False
    

    def check_goal_stats(self):
        tot_node_num_fail = 0
        tot_edge_num_fail = 0
        tot_node_num_success = 0
        tot_edge_num_success = 0
        for i, subgoal in enumerate(self.subgoal_list):
            # is_quantifier = self.check_in_quantifiers(subgoal)
            node_num = 0
            edge_num = 0
            is_node_goal = False
            is_edge_goal = False
            for part in subgoal:
                if part in self.special_states:
                    part = self.special_states[part]
                if part in self.vocab.state_param_dict:
                    param_num = self.vocab.state_param_dict[part]
                    if param_num == 1:
                        is_node_goal = True
                    elif param_num == 2:
                        is_edge_goal = True
            if is_node_goal and is_edge_goal:
                node_num += 0.5
                edge_num += 0.5
            elif is_edge_goal:
                edge_num += 1
            elif is_node_goal:
                node_num += 1
            if self.subgoal_states[i]:
                tot_node_num_success += node_num
                tot_edge_num_success += edge_num
            else:
                tot_node_num_fail += node_num
                tot_edge_num_fail += edge_num
                
        return tot_node_num_fail, tot_edge_num_fail, tot_node_num_success, tot_edge_num_success

def traj_eval_stats(eval_stat_path):
    model_name = os.path.basename(eval_stat_path).split('.')[0]
    with open(eval_stat_path, 'r') as f:
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
    for task, task_info in stats.items():
        success = task_info['success']
        if success:
            num_correct += 1
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
                    if not error_dict['IncorrectParamLength']:
                        incorrect_param_length_num += 1
                    if not error_dict['ObjectNotInScene']:
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
            runtime_report = info[-1]
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
            "affordance": round(affordance_errors/tot_num, 4) if tot_num > 0 else 0,
            "additional_step": round(additional_step_errors/tot_num, 4) if tot_num > 0 else 0,
        }
    }
    return traj_stats

def goal_eval_stats(eval_stat_path):
    error_list_path = os.path.join(behavior_eval.subgoal_dec_resources_path, 'error_list_dict.json')
    assert os.path.exists(error_list_path), f'Error list dict not found at {error_list_path}'
    with open(error_list_path, 'r') as f:
        error_list = json.load(f)
    model_name = os.path.basename(eval_stat_path).split('.')[0]
    with open(eval_stat_path, 'r') as f:
        stats = json.load(f)
    all_goal_statisfied_num = 0
    num_success = 0
    tot_num = 0
    tot_node_goals = 0
    tot_edge_goals = 0
    satified_goals = 0
    satisfied_nodes = 0
    satisfied_edges = 0
    vocab = SimpleVocab()
    for task_name, stat_info in stats.items():
        try:
            success = stat_info['success']
            if success:
                num_success += 1
            goal_info = stat_info['goal_info']
            if goal_info is not None :
                goal_analyzer = GoalAnalyzer(task_name, vocab, goal_info)
                node_num_fail, edge_num_fail, node_num_success, edge_num_success = goal_analyzer.check_goal_stats()
                tot_node_goals += node_num_fail + node_num_success
                tot_edge_goals += edge_num_fail + edge_num_success
                satified_goals += node_num_success + edge_num_success
                satisfied_nodes += node_num_success
                satisfied_edges += edge_num_success
            elif goal_info is None and task_name in error_list:
                goal_info = error_list[task_name]
                goal_analyzer = GoalAnalyzer(task_name, vocab, goal_info)
                node_num_fail, edge_num_fail, node_num_success, edge_num_success = goal_analyzer.check_goal_stats()
                tot_node_goals += node_num_fail + node_num_success
                tot_edge_goals += edge_num_fail + edge_num_success
                satified_goals += node_num_success + edge_num_success
                satisfied_nodes += node_num_success
                satisfied_edges += edge_num_success
            else:
                continue
            if goal_analyzer.goal_success:
                all_goal_statisfied_num += 1
        except Exception as e:
            print(f'Error in task: {task_name}\n')
            print(f'{e}\n')
            continue
    tot_num = tot_node_goals + tot_edge_goals
    node_goal_success_rate = (satisfied_nodes / tot_node_goals)
    edge_goal_success_rate = (satisfied_edges / tot_edge_goals)
    overall_goal_success_rate = ((satified_goals) / tot_num)
    goal_stats = {
        "task_success_rate": round(num_success/len(stats), 4) if len(stats) > 0 else 0,
        "state_goal": round(node_goal_success_rate, 4) if tot_node_goals > 0 else 0,
        "relation_goal": round(edge_goal_success_rate, 4) if tot_edge_goals > 0 else 0,
        "action_goal": round(0, 4),
        "total_goal": round(overall_goal_success_rate, 4) if tot_num > 0 else 0
    }
    return goal_stats

def extract_model_names(llm_response_dir):
    # List to store the extracted model names
    model_names = []
    assert os.path.exists(llm_response_dir), f"Directory {llm_response_dir} does not exist"
    # Get all files in the directory
    files = os.listdir(llm_response_dir)
    
    # Define a regex pattern to match the model name part of the filename
    pattern = re.compile(r"^(.*?)_outputs\.json$")
    
    for file in files:
        match = pattern.match(file)
        if match:
            # Extract the model name from the filename and add it to the list
            model_names.append(match.group(1))

    return model_names