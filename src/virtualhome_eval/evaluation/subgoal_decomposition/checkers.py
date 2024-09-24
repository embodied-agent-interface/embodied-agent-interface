import copy
import json
import os
import sys
import logging
logger = logging.getLogger(__name__)

from collections import deque
from typing import List, Dict, Any, Tuple, Union
from virtualhome_eval.simulation.evolving_graph.execution import ExecutionInfo, EnvironmentGraph
from virtualhome_eval.simulation.evolving_graph.scripts import parse_script_line
from virtualhome_eval.evaluation.subgoal_decomposition.subgoal_plan import SubgoalPlan, SubgoalPlanHalfJson
from virtualhome_eval.evaluation.subgoal_decomposition.subgoal_eval_utils import Vocabulary, my_scene_evaluate
from virtualhome_eval.simulation.evolving_graph.motion_planner import MotionPlanner
from virtualhome_eval.tl_formula.simple_tl_parser import parse_simple_tl
from virtualhome_eval.tl_formula.simple_tl import SimpleTLExpression, Proposition, Action, SimpleTLPrimitive, SimpleTLNot, State, StateActionSequence
from virtualhome_eval.tl_formula.simple_tl import extract_propositions_and_actions, extract_args, sample_a_determined_path_from_tl_expr, eval_simple_tl
from virtualhome_eval.evaluation.subgoal_decomposition.state_action_translator import StateActionTranslator


class TemporalOrderChecker:
    def __init__(self, error_info: ExecutionInfo, prev_states:List[Dict]) -> None:
        self.error_info = error_info
        self.prev_states = prev_states
        self.msg_list = []

    def check_edge_goal(self, edge_goal: Dict, edges: List[Dict]) -> bool:
        tar_from_id = edge_goal['from_id']
        tar_to_id = edge_goal['to_id']
        tar_relation = edge_goal['relation']
        is_from_id_matched = False
        is_to_id_matched = False
        is_relation_matched = False
        is_found = False
        for edge in edges:
            from_id = edge['from_id']
            to_id = edge['to_id']
            relation = edge['relation_type']

            is_from_id_matched = from_id == tar_from_id or tar_from_id == -1
            is_to_id_matched = to_id == tar_to_id or tar_to_id == -1
            is_relation_matched = tar_relation in relation

            is_found = is_from_id_matched and is_to_id_matched and is_relation_matched
            if is_found:
                return True
        return False
    
    def check_node_goal(self, node_goal: Dict, nodes: List[Dict]) -> bool:
        tar_id = node_goal['id']
        tar_state = node_goal['state']

        is_id_matched = False
        is_state_matched = False
        is_found = False
        for node in nodes:
            id = node['id']
            states = node['states']
            is_id_matched = id == tar_id
            is_state_matched = tar_state in states
            is_found = is_id_matched and is_state_matched
            if is_found:
                return True
        return False

    def get_precond_str(self, negate, precond) -> str:
        precondition_str = ''
        if 'relation' in precond:
            from_id = precond['from_id']
            to_id = precond['to_id']
            relation = precond['relation']
            precondition_str = f'{relation}({from_id}, {to_id})'
        else:
            id = precond['id']
            state = precond['state']
            precondition_str = f'{state}({id})'
        return f'not {precondition_str}' if negate else precondition_str

    def search_in_prev_states(self, precond_pair: Tuple[bool, Dict]) -> bool:
        negate, precond = precond_pair
        is_edge_goal = 'relation' in precond
        found_satisified = False
        for prev_state in self.prev_states:
            if is_edge_goal:
                edges = prev_state['edges']
                edge_found = self.check_edge_goal(precond, edges)
                found_satisified = edge_found if not negate else not edge_found
            else:
                nodes = prev_state['nodes']
                node_found = self.check_node_goal(precond, nodes)
                found_satisified = node_found if not negate else not node_found
            if found_satisified:
                error_msg = f'Precondition {self.get_precond_str(negate, precond)} is satisfied in previous states. '
                self.msg_list.append(error_msg)
                break
        return found_satisified

    def check_missing_preconds(self):
        self.missing_preconds = self.error_info.missing_preconds
        self.missing_connective = self.error_info.missing_connective
        preconds_found_list = []
        for precond_pair in self.missing_preconds:
            assert isinstance(precond_pair, tuple)
            precond_found = self.search_in_prev_states(precond_pair)
            preconds_found_list.append(precond_found)

        if self.missing_connective == 'and':
            return all(preconds_found_list)
        elif self.missing_connective == 'or':
            return any(preconds_found_list)
        else:
            return preconds_found_list[0]
        
    def run_checker(self) -> ExecutionInfo:
        if self.error_info.error_type != 1:
            return self.error_info
        rst = self.check_missing_preconds()
        if not rst:
            return self.error_info
        else:
            new_error_info = ExecutionInfo(True)
            error_msg = ' '.join(self.msg_list)
            new_error_info.messages = copy.deepcopy(self.error_info.messages)
            new_error_info.assign_error_type('time')
            new_error_info.error(error_msg)
            return new_error_info
        

class SubgoalBaseChecker:
    def __init__(self, subgoal_plan: SubgoalPlan, vocab: Vocabulary) -> None:
        self.subgoal_plan = subgoal_plan
        self.vocab = vocab
        self.scene_id = subgoal_plan.scene_id
        self.file_id = subgoal_plan.file_id
        self.tl_formula = subgoal_plan.get_subgoal_plan_tl_formula()
    
    def run_checker(self) -> bool:
        '''This method runs the checker and returns True if the subgoal plan is correct.
        
        Returns:
            bool: True if the subgoal plan is correct
        '''
        raise NotImplementedError('This method should be implemented by the subclass')
    
    def update_statistics(self, error_info) -> None:
        '''This method updates the statistics based on the error_info
        
        Args:
            error_info: checking result of the subgoal plan
        
        Returns:
            None
        '''
        raise NotImplementedError('This method should be implemented by the subclass')
    
    def report(self) -> Dict[Any, Any]:
        '''This method reports the statistics of the subgoal plan.
        
        Args:
            None
        
        Returns:
            Dict[Any, Any]: statistics of the subgoal plan
        '''
        raise NotImplementedError('This method should be implemented by the subclass')
    

class SubgoalSyntacticChecker(SubgoalBaseChecker):
    def __init__(self, subgoal_plan: SubgoalPlan, vocab: Vocabulary) -> None:
        super().__init__(subgoal_plan, vocab)
        self.error_type = None
        self.error_info = None
        self.run_result = self.run_checker()
    
    def update_statistics(self, error_type, error_info) -> None:
        self.error_type = error_type
        self.error_info = error_info
    
    def run_checker(self) -> bool:
        try:
            self.parsed_tl_expression = parse_simple_tl(self.tl_formula, self.vocab.get_tl_predicates(), self.vocab.get_subgoal_actions_in_list())
        except Exception as e:
            error_type = str(e.__class__.__name__)
            error_info = str(e)
            if 'Unknown primitive' in error_info:
                error_type = 'UnknownPrimitive'
            else:
                error_type = 'NotParseable'
            self.update_statistics(error_type, error_info)
            return False
        return True
    
    def get_parsed_tl_expression(self) -> SimpleTLExpression:
        assert self.run_result, f'Cannot get parsed temporal logic expression for incorrect subgoal plan'
        return self.parsed_tl_expression
    
    def report(self) -> Dict[str, Any]:
        return {
            'scene_id': self.scene_id,
            'file_id': self.file_id,
            'syntactic_check': self.run_result,
            'error_type': self.error_type,
            'error_info': self.error_info
        }
    

class SubgoalSemanticChecker(SubgoalBaseChecker):
    def __init__(self, subgoal_plan: SubgoalPlan, vocab: Vocabulary, parsed_tl_expression:SimpleTLExpression) -> None:
        super().__init__(subgoal_plan, vocab)
        self.tl_expression = parsed_tl_expression
        self.error_dict = {
            "scene_id": self.scene_id,
            "file_id": self.file_id,
            "result": True,
            "IncorrectParamLength": False,
            "ObjectNotInScene": False,
            "error_info": ""
        }
        self.run_result = self.run_checker()
    
    def update_statistics(self, error_type, error_info) -> None:
        assert error_type in self.error_dict, f'Unknown error type {error_type}'
        self.error_dict['result'] = False
        self.error_dict[error_type] = True
        self.error_dict["error_info"] += f'{error_info}\n'
    
    def check_param_length(self) -> bool:
        propostions, actions = extract_propositions_and_actions(self.tl_expression)
        primitives = propostions + actions
        for primitive in primitives:
            try:
                if isinstance(primitive, Proposition):
                    state_name = primitive.name
                    grounded_param_num = self.vocab.state_param_dict[state_name]
                    cur_param_num = len(primitive.args) if primitive.args else 0
                elif isinstance(primitive, Action):
                    action_name = primitive.name
                    grounded_param_num = self.vocab.actio_param_dict[action_name]
                    cur_param_num = len(primitive.args) if primitive.args else 0
                else:
                    raise Exception()
                if cur_param_num != grounded_param_num:
                    self.update_statistics('IncorrectParamLength', f'Primitive {primitive} has incorrect number of parameters')
                    return False
            except Exception as e:
                raise ValueError(f'Unknown primitive type {primitive}')
        return True
    
    def check_objects_in_scene(self) -> bool:
        cur_objects = extract_args(self.tl_expression)
        for obj in cur_objects:
            if '.' in obj:
                obj_name, obj_id = obj.split('.')
                obj_id = int(obj_id)
                rv = self.vocab.id_to_name_dict.get(obj_id, None)
                if not rv:
                    error_type = 'ObjectNotInScene'
                    error_info = f'Object {obj} is not in the scene'
                    self.update_statistics(error_type, error_info)
                    return False
                rv = self.vocab.id_to_name_dict[obj_id] == obj_name
                if not rv:
                    error_type = 'ObjectNotInScene'
                    error_info = f'Object {obj} is not in the scene'
                    self.update_statistics(error_type, error_info)
                    return False
            else:
                rv = obj in self.vocab.id_to_name_dict.values()
                if not rv:
                    error_type = 'ObjectNotInScene'
                    error_info = f'Object {obj} is not in the scene'
                    self.update_statistics(error_type, error_info)
                    return False
        return True
    
    def run_checker(self) -> bool:
        param_check_rst = self.check_param_length()
        obj_check_rst = self.check_objects_in_scene()
        return param_check_rst and obj_check_rst
    
    def report(self) -> Dict[str, Any]:
        return self.error_dict
    
class SubgoalRuntimeChecker(SubgoalBaseChecker):
    def __init__(self, subgoal_plan: SubgoalPlan, vocab: Vocabulary, tl_expression: SimpleTLExpression, planner: MotionPlanner, goal_tl_expression: SimpleTLExpression, args) -> None:
        super().__init__(subgoal_plan, vocab)
        self.tl_expression = tl_expression
        self.planner = planner
        self.det_subgoal_tl_list = sample_a_determined_path_from_tl_expr(self.tl_expression)
        self.state_action_translator = StateActionTranslator(self.det_subgoal_tl_list, self.planner, self.vocab)
        self.feasible_action_seqs = []
        self.error_info = []
        self.executable = False
        self.goal_tl_expression = goal_tl_expression
        self.args = args
        self.vh_goal = self.get_vh_goal()
        self.error_code_to_type = self.get_error_code_to_error_type_dict()
        self.run_result = self.run_checker()
    
    @staticmethod
    def get_error_code_to_error_type_dict():
        return {
            0: 'WRONG_TEMPORAL_ORDER',
            1: 'MISSING_STEP',
            2: 'AFFORDANCE_ERROR',
            3: 'UNSEEN_OBJECT',
            4: 'ADDITIONAL_STEP',
            5: 'UNKNOWN_ERROR',
        }

    @staticmethod
    def translate_states_into_tl_propositions(states_dict, id_2_name_dict, vocab):
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
    
    def get_tl_states_seq(self, raw_states, id_2_name_dict):
        states_seq = []
        for raw_state in raw_states:
            obj_name_list, tl_prop_list = SubgoalRuntimeChecker.translate_states_into_tl_propositions(raw_state, id_2_name_dict, self.vocab)
            states_seq.append(State(obj_name_list, tl_prop_list))
        return states_seq
    
    # [Warning] the following function only considers the direct object names, not nickname (objects appearing in executable scripts)
    @staticmethod
    def translate_action_primitive_into_tl(action):
        action_line = parse_script_line(action, 0)
        action_name = action_line.action.name
        action_params = []
        for p in action_line.parameters:
            obj_str = f'{p.name}.{p.instance}'
            action_params.append(obj_str)
        action_line = Action(action_name, action_params)
        return action_line
    
    @staticmethod
    def translate_actions_into_tl(action_seq):
        tl_action_seq = []
        for action in action_seq:
            tl_action = SubgoalRuntimeChecker.translate_action_primitive_into_tl(action)
            tl_action_seq.append(tl_action)
        return tl_action_seq
    
    def get_tl_action_seq(self, raw_actions):
        return self.translate_actions_into_tl(raw_actions)

    def check_tl_final_goal(self, raw_states, raw_actions_list):
        raw_actions = []
        for action in raw_actions_list:
            raw_actions.append(action)
        tl_states = self.get_tl_states_seq(raw_states, self.planner.id_to_name)
        tl_actions = self.get_tl_action_seq(raw_actions)
        trajectory = StateActionSequence(tl_states, tl_actions)
        result = eval_simple_tl(self.goal_tl_expression, trajectory)
        return result

    def execute_subgoal_plan(self):
        prev_action_env_state = copy.deepcopy(self.planner.env_state)
        prev_saved_history_state = [copy.deepcopy(prev_action_env_state.to_dict())]
        prev_executed_action_list = []
        prev_error_info_list = []
        remained_subgoals = copy.deepcopy(self.det_subgoal_tl_list)
        level = 0

        exec_queue = deque()
        prev = (prev_action_env_state, prev_executed_action_list, remained_subgoals, prev_saved_history_state, prev_error_info_list, level)
        exec_queue.append(prev)

        feasible_action_seqs = []
        failed_action_seqs = []
        correct_plan = False
        executable = False

        while exec_queue:
            cur_action_env_state, cur_executed_action_list, cur_remained_subgoals, cur_saved_history_state, cur_error_info_list, cur_level = exec_queue.popleft()
            prev_action_env_state = copy.deepcopy(cur_action_env_state)
            prev_saved_history_state = copy.deepcopy(cur_saved_history_state)
            prev_error_info_list = copy.deepcopy(cur_error_info_list)

            if len(cur_remained_subgoals) == 0:
                executable = True
                self.executable = True
                success = self.check_tl_final_goal(cur_saved_history_state, cur_executed_action_list)
                if success:
                    feasible_action_seqs.append((cur_executed_action_list, cur_error_info_list))
                    correct_plan = True
                else:
                    error_type = ['GOAL_FAILED']
                    error_info = ['Final goal not satisfied']
                    error_dict = {
                        'error_type': error_type,
                        'error_info': error_info
                    }
                    cur_error_info_list.append([error_dict, None, None])
                    failed_action_seqs.append((cur_executed_action_list, cur_error_info_list))
            else:
                cur_subgoal = cur_remained_subgoals[0]
                self.planner.env_state = copy.deepcopy(cur_action_env_state)
                action_candidates = self.state_action_translator.map_subgoal_to_action_sequence_dynamic_verion(cur_subgoal, self.planner)
                if len(action_candidates) == 0:
                    new_action_env_state = copy.deepcopy(self.planner.env_state)
                    new_executed_action_list = copy.deepcopy(cur_executed_action_list)
                    new_remained_subgoals = copy.deepcopy(cur_remained_subgoals[1:])
                    new_saved_history_state = copy.deepcopy(cur_saved_history_state)
                    new_level = cur_level + 1
                    new_tuple = (new_action_env_state, new_executed_action_list, new_remained_subgoals, new_saved_history_state, cur_error_info_list, new_level)
                    exec_queue.append(new_tuple)
                for action_set in action_candidates:
                    self.planner.env_state = copy.deepcopy(cur_action_env_state)
                    cur_error_info_list = copy.deepcopy(prev_error_info_list)
                    success = True
                    tmp_executed_action_list = []
                    tmp_history_state = []
                    for action_instruction in action_set:
                        rst, my_info = self.planner.my_execute_primitive_action_eval(action_instruction)
                        if not rst:
                            formal_info_checker = TemporalOrderChecker(my_info, prev_saved_history_state+tmp_history_state)
                            formal_info = formal_info_checker.run_checker()
                            failed_error_code = formal_info.get_error_type()
                            failed_error_seq = formal_info.get_error_string()
                            ADDITIONAL_ERRROR_CODE = 4
                            assert failed_error_code in self.error_code_to_type, f'Unknown error code {failed_error_code}'
                            error_dict_new = {
                                'error_type': [self.error_code_to_type[failed_error_code]],
                                'error_info': [failed_error_seq]
                            }
                            cur_error_info_list.append([error_dict_new, str(cur_subgoal), action_instruction])
                            if failed_error_code != ADDITIONAL_ERRROR_CODE:
                                success = False
                                failed_action_seq = copy.deepcopy(cur_executed_action_list) + tmp_executed_action_list
                                failed_error_info_list = copy.deepcopy(cur_error_info_list)
                                failed_action_seqs.append((failed_action_seq, failed_error_info_list))
                                break
                        else:
                            tmp_executed_action_list.append(action_instruction)
                            tmp_history_state.append(copy.deepcopy(self.planner.env_state.to_dict()))
                    if success:
                        new_action_env_state = copy.deepcopy(self.planner.env_state)
                        new_executed_action_list = copy.deepcopy(cur_executed_action_list) + tmp_executed_action_list
                        new_remained_subgoals = copy.deepcopy(cur_remained_subgoals[1:])
                        new_saved_history_state = copy.deepcopy(prev_saved_history_state) + tmp_history_state
                        new_level = cur_level + 1
                        new_tuple = (new_action_env_state, new_executed_action_list, new_remained_subgoals, new_saved_history_state, cur_error_info_list, new_level)
                        exec_queue.append(new_tuple)
            
        return executable, correct_plan, feasible_action_seqs, failed_action_seqs
    

    def get_activated_failed_action_seqs(self, failed_action_seqs:List[Tuple[List, List]]):
        new_failed_action_seqs = []
        for failed_info in failed_action_seqs:
            failed_error_info_list = failed_info[1]
            end_goal = False
            for failed_error_info_dict in failed_error_info_list:
                failed_error_info = failed_error_info_dict[0]
                error_type = failed_error_info['error_type']
                if 'GOAL_FAILED' in error_type:
                    end_goal = True
                    break
            if end_goal:
                new_failed_action_seqs.append(failed_info)
        return new_failed_action_seqs
    
    def get_vh_goal(self):
        resource_dir = self.args.resource_dir
        ltl_formula_accurate_base_root = os.path.join(resource_dir, 'task_state_LTL_formula_accurate.json')
        with open(ltl_formula_accurate_base_root, 'r') as f:
            task_obj = json.load(f)
        scene_str = f'scene_{self.scene_id}'
        task_obj = task_obj[scene_str]
        for task_name, task_info in task_obj.items():
            for file_id, file_info in task_info.items():
                if file_id == self.file_id:
                    return file_info['vh_goal']
        return {
            'actions': [],
            'goal': []
        }

    def get_action_seq_rst(self, action_seq:List[str]):
        self.planner.reset()
        char_id = self.planner.acting_char_id
        node_goals = []
        edge_goals = []
        action_goals = self.vh_goal['actions']
        for goal in self.vh_goal['goal']:
            if 'id' in goal and 'class_name' in goal and 'state' in goal:
                node_goals.append(goal)
            elif 'from_id' in goal and 'to_id' in goal and 'relation_type' in goal:
                if goal not in edge_goals:
                    edge_goals.append(goal)
        for action in action_seq:
            rst, info =self.planner.my_execute_primitive_action_eval(action)
            if not rst:
                logger.info(f'Action {action} failed')
        final_state_dict = self.planner.env_state.to_dict()
        return my_scene_evaluate(final_state_dict, node_goals, edge_goals, char_id,  action_seq, action_goals)




    def run_checker(self) -> bool:
        executable, correct_plan, feasible_action_seqs, failed_action_seqs = self.execute_subgoal_plan()
        if correct_plan:
            # self.feasible_action_seqs = [seq for seq, _ in feasible_action_seqs]
            min_errors = float('inf')
            min_failed_action_seq = None
            min_failed_error_info = None
            for success_info in feasible_action_seqs:
                success_action_seq = success_info[0]
                success_error_info_list = success_info[1]
                num_errors = len(success_error_info_list)
                if num_errors < min_errors:
                    min_errors = num_errors
                    min_failed_action_seq = success_action_seq
                    min_failed_error_info = success_error_info_list
            if min_failed_action_seq is not None:
                for success_error_info_dict in min_failed_error_info:
                    success_subgoal = success_error_info_dict[1]
                    success_action = success_error_info_dict[2]
                    tmp_dict = {
                        'failed_action_sequence': min_failed_action_seq,
                        'failed_subgoal': str(success_subgoal),
                        'failed_action': success_action,
                        'error_info': success_error_info_dict[0]
                    }

                    self.update_statistics(tmp_dict)
                self.goal_info = self.get_action_seq_rst(min_failed_action_seq)
            self.feasible_action_seqs = [min_failed_action_seq]
            return executable and correct_plan and len(self.feasible_action_seqs) > 0
        new_failed_action_seqs = self.get_activated_failed_action_seqs(failed_action_seqs)
        failed_action_seqs = new_failed_action_seqs if len(new_failed_action_seqs) > 0 else failed_action_seqs
        if len(failed_action_seqs) > 0:
            min_errors = float('inf')
            min_failed_action_seq = None
            min_failed_action_seq_len = 0
            min_failed_error_info = None

            for fail_info in failed_action_seqs:
                failed_action_seq = fail_info[0]
                failed_error_info_list = fail_info[1]
                failed_action_seq_len = len(failed_action_seq)
                num_errors = len(failed_error_info_list)
                if num_errors < min_errors or (num_errors == min_errors and failed_action_seq_len > min_failed_action_seq_len): # we prefer longer action sequence
                    min_errors = num_errors
                    min_failed_action_seq = failed_action_seq
                    min_failed_action_seq_len = failed_action_seq_len
                    min_failed_error_info = failed_error_info_list

            if min_failed_action_seq is not None:
                for failed_error_info_dict in min_failed_error_info:
                    failed_subgoal = failed_error_info_dict[1]
                    failed_action = failed_error_info_dict[2]
                    tmp_dict = {
                        'failed_action_sequence': min_failed_action_seq,
                        'failed_subgoal': str(failed_subgoal),
                        'failed_action': failed_action,
                        'error_info': failed_error_info_dict[0]
                    }
                    self.update_statistics(tmp_dict)
                self.goal_info = self.get_action_seq_rst(min_failed_action_seq)
        self.feasible_action_seqs = []
        return executable and correct_plan and len(self.feasible_action_seqs) > 0


    def update_statistics(self, error_info) -> None:
        self.error_info.append(error_info)
    
    def report(self) -> List[Dict[str, Any]]:
        return self.error_info

# =================================
# ============= Tests =============
# =================================

def load_graph_state(state_file_path):
    with open(state_file_path, 'r') as f:
        state = json.load(f)
    init_state, final_state = state['init_graph'], state['final_graph']
    return init_state, final_state

def load_motion_planner(scene_id: int, file_id:str, args) -> MotionPlanner:
    dataset_dir = args.dataset_dir
    state_root_path =  os.path.join(dataset_dir, f'programs_processed_precond_nograb_morepreconds/init_and_final_graphs/TrimmedTestScene{scene_id}_graph/results_intentions_march-13-18')
    state_file_path = os.path.join(state_root_path, f'file{file_id}.json')
    init_state, final_state = load_graph_state(state_file_path)
    init_graph = EnvironmentGraph(init_state)
    return MotionPlanner(init_graph, final_state)




# def get_example_subgoal_case():
#     llm_output_path = './virtualhome/simulation/evaluation/eval_subgoal_plan/llm_output/gpt-4o-2024-05-13_outputs.json'
#     with open(llm_output_path, 'r') as f:
#         llm_outputs = json.load(f)
#     identifier = llm_outputs[0]['identifier']
#     llm_output = llm_outputs[0]['llm_output']
#     scene_id = int(identifier[6:7])
#     file_id = identifier[8:]
#     return SubgoalPlanHalfJson(scene_id, file_id, llm_output)

def get_final_tl_goal(scene_id, file_id, args):
    resource_dir = args.resource_dir
    final_goal_file_path = os.path.join(resource_dir, 'task_state_LTL_formula_accurate.json')
    scene_str = f'scene_{scene_id}'
    with open(final_goal_file_path, 'r') as f:
        final_goal_dict = json.load(f)
    final_goal_dict = final_goal_dict[scene_str]
    for task_name, p_list in final_goal_dict.items():
        p_list_keys = list(p_list.keys())
        if file_id in p_list_keys:
            return p_list[file_id]['tl_goal']
    return None


# def test_checkers():
#     vocab_path = 'virtualhome_eval/resources/vocabulary.json'
#     subgoal_plan = get_example_subgoal_case()
#     scene_id = subgoal_plan.scene_id
#     file_id = subgoal_plan.file_id
#     planner = load_motion_planner(scene_id, file_id)
#     id_to_name_dict = planner.id_to_name
#     vocab = Vocabulary(vocab_path, id_to_name_dict)
#     syntactic_checker = SubgoalSyntacticChecker(subgoal_plan, vocab)
#     print(syntactic_checker.report())
#     if not syntactic_checker.run_result:
#         return
#     tl_expression = syntactic_checker.get_parsed_tl_expression()
#     semantic_checker = SubgoalSemanticChecker(subgoal_plan, vocab, tl_expression)
#     print(semantic_checker.report())
#     if not semantic_checker.run_result:
#         return
#     goal_tl_formula = get_final_tl_goal(scene_id, file_id)
#     if goal_tl_formula is None:
#         print('Final goal not found')
#         return
#     goal_tl_expression = parse_simple_tl(goal_tl_formula, vocab.get_tl_predicates(), vocab.get_subgoal_actions_in_list())
#     runtime_checker = SubgoalRuntimeChecker(subgoal_plan, vocab, tl_expression, planner, goal_tl_expression)
#     print(runtime_checker.report())
#     print(runtime_checker.run_result)
#     if not runtime_checker.run_result:
#         return

    

# if __name__ == '__main__':
#     test_checkers()