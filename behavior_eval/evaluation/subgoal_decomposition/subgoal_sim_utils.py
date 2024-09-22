import os
import json
import behavior_eval
from typing import List, Dict, Any, Optional, Tuple, Union
from behavior_eval.evolving_graph.eval_evolving_graph_env import EvalGraphEnv
from behavior_eval.evaluation.subgoal_decomposition.subgoal_plan import SubgoalPlan, SubgoalPlanHalfJson, SubgoalPlanJSON, SubgoalPlanPlain
from behavior_eval.evaluation.subgoal_decomposition.checkers import Vocab, SyntacticChecker, SemanticChecker, RuntimeChecker
from behavior_eval.evaluation.subgoal_decomposition.state_action_translator import StateActionTranslator
from behavior_eval.tl_formula.bddl_to_tl import translate_addressable_obj_into_tl_obj, translate_tl_obj_into_addressable_obj

class EvalStatistics:
    def __init__(self, task_list: List[str], log_path: str) -> None:
        self.task_list = task_list
        self.log_path = log_path
        self.eval_rst_dict = self.init_eval_rst_dict()
    
    def init_eval_rst_dict(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.log_path):
            with open(self.log_path, 'r') as f:
                eval_dict = json.load(f)
            return eval_dict
        
        eval_dict = {}
        for task_name in self.task_list:
            eval_dict[task_name] = {
                'success': False,
                'info': None,
                'goal_info': None
            }
        return eval_dict
    
    def update_eval_rst_dict(self, task_name:str, success:bool, error_info:Union[str, None], goal_info: Union[Dict[str, Any], None]=None):
        self.eval_rst_dict[task_name]['success'] = success
        self.eval_rst_dict[task_name]['info'] = error_info
        self.eval_rst_dict[task_name]['goal_info'] = goal_info
    
    def get_eval_rst_dict(self) -> Dict[str, Dict[str, Any]]:
        return self.eval_rst_dict
    
    def check_evaluated_task(self, task_name:str) -> bool:
        if self.eval_rst_dict[task_name]['success'] == False and self.eval_rst_dict[task_name]['info'] is None:
            return False
        return True
    
    def save_eval_rst_dict(self):
        with open(self.log_path, 'w') as f:
            json.dump(self.eval_rst_dict, f, indent=4)

class EvalSubgoalPlan:
    def __init__(self, demo_path:str, plan_path:str, json_format:Optional[bool]=False) -> None:
        self.env = EvalGraphEnv(demo_name=demo_path)
        self.igibson_name_mapping = self.env.get_name_mapping()
        self.igibson_relevant_objects = self.env.get_relevant_obj_list(self.igibson_name_mapping)
        self.category_map = self.get_tl_category(self.igibson_name_mapping) #type:ignore
        self.tl_name_mapping = self.get_tl_name_mapping(self.igibson_name_mapping, self.category_map) #type:ignore
        self.tl_relevant_objects = [obj['name'] for obj in self.tl_name_mapping]
        self.task_name = self.env.task.behavior_activity #type:ignore
        # self.subgoal_plan = SubgoalPlanPlain(plan_path, self.task_name) if not json_format else SubgoalPlanJSON(plan_path, self.task_name)
        try:
            self.subgoal_plan = SubgoalPlanHalfJson(plan_path, self.task_name)
        except Exception as e:
            raise e
    
    def get_tl_category(self, igibson_name_mapping:List[Dict[str, str]]) -> Dict[str, str]:
        category_map = {}
        for pair in igibson_name_mapping:
            category = pair['category']
            category_map[category] = category.replace('.', '_')
        return category_map


    def get_tl_name_mapping(self, igibson_name_mapping:List[Dict[str, str]], category_map: Dict[str, str]) -> List[Dict[str, str]]:
        tl_name_mapping = []
        for pair in igibson_name_mapping:
            obj_name = pair['name']
            obj_category = pair['category']
            tl_obj_name = translate_addressable_obj_into_tl_obj(obj_name)
            tl_obj_category = category_map[obj_category]
            tl_obj = {'name': tl_obj_name, 'category': tl_obj_category}
            tl_name_mapping.append(tl_obj)
        return tl_name_mapping
    
    def evaluate_subgoal_plan(self):
        vocab = Vocab(self.tl_name_mapping, self.tl_relevant_objects)
        syntactic_checker = SyntacticChecker(self.subgoal_plan, vocab)
        syntactic_rst = syntactic_checker.run_result
        if not syntactic_rst:
            syntactic_report = syntactic_checker.report()
            error_type = syntactic_report['error_type']
            error_category = ''
            if error_type == 'NotParseable':
                error_category = 'NotParseable'
            elif error_type == 'UnknownPrimitive':
                error_category = 'Hallucination'
            else:
                assert False, 'Unknown error type'
            error_tuple = (error_category, syntactic_report, None)
            return error_tuple
        tl_expression = syntactic_checker.get_parsed_tl_expression()
        semantic_checker = SemanticChecker(self.subgoal_plan, vocab, tl_expression, True)
        semantic_rst = semantic_checker.run_result
        if not semantic_rst:
            semantic_report = semantic_checker.report()
            error_tuple = ('Hallucination', semantic_report, None)
            return error_tuple
        runtime_checker = RuntimeChecker(self.env, self.subgoal_plan, vocab, tl_expression, True)
        runtime_report = runtime_checker.report()
        runtime_rst = runtime_checker.run_result
        if not runtime_rst:
            error_category = 'Runtime' if not runtime_checker.executable else 'GoalUnreachable'
            error_tuple = (error_category, runtime_checker.executable, runtime_report, runtime_checker.goal_info)
            return error_tuple
        return ('Correct', runtime_checker.executable, runtime_checker.feasible_action_seqs, runtime_report, runtime_checker.goal_info)

def evaluate_task(demo_name:str, plan_path):
    try:
        eval_subgoal_plan = EvalSubgoalPlan(demo_name, plan_path)
        report = eval_subgoal_plan.evaluate_subgoal_plan()
    except Exception as e:
        report = ('NotParseable', str(e), None)
    finally:
        # delete eval_subgoal_plan to clean memory
        if 'eval_subgoal_plan' in locals():
            eval_subgoal_plan.env.env.close()
        return report

def get_all_task_list():
    path = os.path.join(behavior_eval.demo_name_path)
    with open(path, 'r') as f:
        task_list = json.load(f)
    return task_list

def get_one_raw_task_goal(demo_name):
    env = EvalGraphEnv(demo_name)
    success_dict = env.action_env.cur_state.check_success(env.task)
    return success_dict


def get_all_raw_task_goal():
    error_list_dict_path = os.path.join(behavior_eval.subgoal_dec_resources_path, 'error_list_dict.json')
    if os.path.exists(error_list_dict_path):
        with open(error_list_dict_path, 'r') as f:
            error_list_dict = json.load(f)
    else:
        error_list_dict = {}
    task_list = get_all_task_list()
    real_task_list = [task_name for task_name in task_list if not task_name in error_list_dict.keys()]
    if len(real_task_list) == 0:
        return
    for task_name in real_task_list:
        error_list_dict[task_name] = get_one_raw_task_goal(task_name)
    with open(error_list_dict_path, 'w') as f:
        json.dump(error_list_dict, f, indent=4)