import os
import json
import logging
logger = logging.getLogger(__name__)

from typing import Dict, List, Any, Union
from virtualhome_eval.evaluation.subgoal_decomposition.checkers import get_final_tl_goal, load_motion_planner, SubgoalSyntacticChecker, SubgoalSemanticChecker, SubgoalRuntimeChecker
from virtualhome_eval.evaluation.subgoal_decomposition.subgoal_plan import SubgoalPlanHalfJson
from virtualhome_eval.evaluation.subgoal_decomposition.subgoal_eval_utils import Vocabulary
from virtualhome_eval.tl_formula.simple_tl_parser import parse_simple_tl

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
                'info': None
            }
        return eval_dict
    
    def update_eval_rst_dict(self, task_name:str, success:bool, error_info:Union[str, None]):
        self.eval_rst_dict[task_name]['success'] = success
        self.eval_rst_dict[task_name]['info'] = error_info
    
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
    def __init__(self, vocab_path, scene_id, file_id, llm_output, args) -> None:
        self.vocab_path = vocab_path
        self.scene_id = scene_id
        self.file_id = file_id
        self.args = args
        self.subgoal_plan = SubgoalPlanHalfJson(scene_id, file_id, llm_output)
        self.planner = load_motion_planner(scene_id, file_id, args)
        self.vocab = Vocabulary(vocab_path, self.planner.id_to_name)
    
    def evaluate_subgoal_plan(self):
        syntactic_checker = SubgoalSyntacticChecker(self.subgoal_plan, self.vocab)
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
        semantic_checker = SubgoalSemanticChecker(self.subgoal_plan, self.vocab, tl_expression)
        semantic_rst = semantic_checker.run_result
        if not semantic_rst:
            semantic_report = semantic_checker.report()
            error_tuple = ('Hallucination', semantic_report, None)
            return error_tuple
        goal_tl_formula = get_final_tl_goal(self.scene_id, self.file_id, self.args)
        if not goal_tl_formula:
            assert False, 'Failed to get final goal formula'
        goal_tl_expression = parse_simple_tl(goal_tl_formula, self.vocab.get_tl_predicates(), self.vocab.get_subgoal_actions_in_list())
        runtime_checker = SubgoalRuntimeChecker(self.subgoal_plan, self.vocab, tl_expression, self.planner, goal_tl_expression, self.args)
        runtime_report = runtime_checker.report()
        runtime_rst = runtime_checker.run_result
        node_tot_num = runtime_checker.goal_info[0]
        node_success_num = runtime_checker.goal_info[1]
        edge_tot_num = runtime_checker.goal_info[2]
        edge_success_num = runtime_checker.goal_info[3]
        action_tot_num = runtime_checker.goal_info[4]
        action_success_num = runtime_checker.goal_info[5]
        full_tot_num = runtime_checker.goal_info[6]
        full_success_num = runtime_checker.goal_info[7]
        tmp = {
            'node_tot_num': node_tot_num,
            'node_success_num': node_success_num,
            'edge_tot_num': edge_tot_num,
            'edge_success_num': edge_success_num,
            'action_tot_num': action_tot_num,
            'action_success_num': action_success_num,
            'full_tot_num': full_tot_num,
            'full_success_num': full_success_num
        }
        if not runtime_rst:
            error_category = 'Runtime' if not runtime_checker.executable else 'GoalUnreachable'
            error_tuple = (error_category, runtime_checker.executable, runtime_report, tmp)
            return error_tuple
        return ('Correct', runtime_checker.executable, runtime_checker.feasible_action_seqs, runtime_report, tmp)

def evaluate_task(vocab_path, scene_id, file_id, llm_output, args):
    try:
        eval_subgoal_plan = EvalSubgoalPlan(vocab_path, scene_id, file_id, llm_output, args)
        report = eval_subgoal_plan.evaluate_subgoal_plan()
    except Exception as e:
        report = ('NotParseable', str(e), None)
    finally:
        return report

def get_scene_id_and_file_id(identifier):
    scene_id = int(identifier[6:7])
    file_id = identifier[8:]
    return scene_id, file_id

def get_llm_outputs_dict(llm_outputs_path):
    with open(llm_outputs_path, 'r') as f:
        llm_outputs = json.load(f)
    return llm_outputs

def get_llm_tasks_names(llm_outputs):
    task_name_list = [item['identifier'] for item in llm_outputs]
    return task_name_list