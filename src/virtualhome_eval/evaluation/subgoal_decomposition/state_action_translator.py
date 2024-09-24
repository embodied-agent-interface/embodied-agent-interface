import copy
import os
import json
import logging
logger = logging.getLogger(__name__)

from virtualhome_eval.simulation.evolving_graph.motion_planner import MotionPlanner
from virtualhome_eval.tl_formula.simple_tl import SimpleTLExpression, Proposition, Action, SimpleTLPrimitive, SimpleTLNot
from virtualhome_eval.evaluation.subgoal_decomposition.subgoal_eval_utils import Vocabulary

from typing import List, Dict, Any, Tuple, Union
class StateActionTranslator:
    def __init__(self, subgoal_list: List[Union[SimpleTLNot, SimpleTLPrimitive]], planner: MotionPlanner, vocab:Vocabulary) -> None:
        self.subgoal_list = subgoal_list
        self.planner = planner
        self.vocab = vocab
        self.tl_to_vh_pred_dict = vocab.get_tl_to_vh_predicates_dict()
        assert all(isinstance(subgoal, (SimpleTLPrimitive, SimpleTLNot)) for subgoal in self.subgoal_list), 'Subgoal list contains non-primitive subgoals'
        self.actions_must_hold = ['DRINK', 'EAT', 'READ']

    @staticmethod
    def translate_zero_action(name):
        return f'[{name}]'
    
    @staticmethod
    def translate_single_action(name, obj_name, obj_id):
        return f'[{name}] <{obj_name}> ({obj_id})'
    
    def translate_action(self, name, params):
        action_str = f'[{name}]'
        for param in params:
            obj_name, obj_id = self.split_obj_pair(param)
            param_str = f' <{obj_name}> ({obj_id})'
            action_str += param_str
        return action_str

    @staticmethod
    def translate_double_action(name, obj1_name, obj1_id, obj2_name, obj2_id):
        return f'[{name}] <{obj1_name}> ({obj1_id}) <{obj2_name}> ({obj2_id})'
    
    @staticmethod
    def split_obj_pair(obj_pair):
        obj_name, obj_id = obj_pair.split('.')
        return obj_name, int(obj_id)
    
    def check_holding(self, obj_pair:str, planner:MotionPlanner, char_id=65):
        obj_name, obj_id = self.split_obj_pair(obj_pair)
        edges = planner.env_state.to_dict()['edges']
        right_holding = {"from_id": char_id, "relation_type": "HOLDS_RH", "to_id": obj_id}
        left_holding = {"from_id": char_id, "relation_type": "HOLDS_LH", "to_id": obj_id}
        return right_holding in edges or left_holding in edges

        
    def map_primitive_to_action_set(self, primitive:SimpleTLPrimitive, char_id=65) -> List[List[Any]]:
        action_set_candidates = []
        common_action_set = []
        predicate = primitive.prop_or_action
        primitive_name = predicate.name
        primitive_args = predicate.args
        
        if isinstance(predicate, Action):
            # perhaps need to add get char_id
            if primitive_name in self.actions_must_hold and not self.check_holding(primitive_args[0], self.planner, char_id):
                obj_pair = primitive_args[0]
                obj_name, obj_id = self.split_obj_pair(obj_pair)
                find_item_to_grab = self.translate_single_action('FIND', obj_name, obj_id)
                grab_item = self.translate_single_action('GRAB', obj_name, obj_id)
                common_action_set.append(find_item_to_grab)
                common_action_set.append(grab_item)
                common_action_set.append(self.translate_action(primitive_name, primitive_args))
            elif primitive_name == 'LOOKAT' or primitive_name == 'WATCH':
                obj_pair = primitive_args[0]
                obj_name, obj_id = self.split_obj_pair(obj_pair)
                find_item_to_look = self.translate_single_action('FIND', obj_name, obj_id)
                turnto_item = self.translate_single_action('TURNTO', obj_name, obj_id)
                common_action_set.append(find_item_to_look)
                common_action_set.append(turnto_item)
                common_action_set.append(self.translate_action(primitive_name, primitive_args))
            else:
                if primitive_args is None or primitive_args == []:
                    core_action = self.translate_zero_action(primitive_name)
                elif len(primitive_args) == 1:
                    obj_pair = primitive_args[0]
                    obj_name, obj_id = self.split_obj_pair(obj_pair)
                    find_item = self.translate_single_action('FIND', obj_name, obj_id)
                    common_action_set.append(find_item)
                    core_action = self.translate_single_action(primitive_name, obj_name, obj_id)
                elif len(primitive_args) == 2:
                    obj1_pair = primitive_args[0]
                    obj2_pair = primitive_args[1]
                    obj1_name, obj1_id = self.split_obj_pair(obj1_pair)
                    obj2_name, obj2_id = self.split_obj_pair(obj2_pair)
                    find_item1 = self.translate_single_action('FIND', obj1_name, obj1_id)
                    find_item2 = self.translate_single_action('FIND', obj2_name, obj2_id)
                    common_action_set.append(find_item1)
                    common_action_set.append(find_item2)
                    core_action = self.translate_double_action(primitive_name, obj1_name, obj1_id, obj2_name, obj2_id)
                common_action_set.append(core_action)
            action_set_candidates.append(common_action_set) 

        elif isinstance(predicate, Proposition):
            if len(primitive_args) == 1:
                obj_pair = primitive_args[0]
                obj_name, obj_id = self.split_obj_pair(obj_pair)
                if primitive_name == 'CLOSED':
                    find_item = self.translate_single_action('FIND', obj_name, obj_id)
                    close_item = self.translate_single_action('CLOSE', obj_name, obj_id)
                    common_action_set.append(find_item)
                    common_action_set.append(close_item)
                    action_set_candidates.append(common_action_set)
                elif primitive_name == 'OPEN':
                    find_item = self.translate_single_action('FIND', obj_name, obj_id)
                    open_item = self.translate_single_action('OPEN', obj_name, obj_id)
                    common_action_set.append(find_item)
                    common_action_set.append(open_item)
                    action_set_candidates.append(common_action_set)
                elif primitive_name == 'ON':
                    find_item = self.translate_single_action('FIND', obj_name, obj_id)
                    switch_on_item = self.translate_single_action('SWITCHON', obj_name, obj_id)
                    common_action_set.append(find_item)
                    common_action_set.append(switch_on_item)
                    action_set_candidates.append(common_action_set)
                elif primitive_name == 'OFF':
                    find_item = self.translate_single_action('FIND', obj_name, obj_id)
                    switch_off_item = self.translate_single_action('SWITCHOFF', obj_name, obj_id)
                    common_action_set.append(find_item)
                    common_action_set.append(switch_off_item)
                    action_set_candidates.append(common_action_set)
                elif primitive_name == 'SITTING' or primitive_name == 'LYING':
                    pass
                elif primitive_name == 'DIRTY':
                    # should be noticed here
                    pass
                elif primitive_name == 'CLEAN':
                    find_item = self.translate_single_action('FIND', obj_name, obj_id)
                    common_action_set.append(find_item)
                    ans_set_1 = copy.deepcopy(common_action_set)
                    ans_set_2 = copy.deepcopy(common_action_set)
                    wipe_item = self.translate_single_action('WIPE', obj_name, obj_id)
                    ans_set_1.append(wipe_item)
                    wash_item = self.translate_single_action('WASH', obj_name, obj_id)
                    ans_set_2.append(wash_item)
                    action_set_candidates.append(ans_set_1)
                    action_set_candidates.append(ans_set_2)
                elif primitive_name == 'PLUGGED_IN':
                    find_item = self.translate_single_action('FIND', obj_name, obj_id)
                    plug_item = self.translate_single_action('PLUGIN', obj_name, obj_id)
                    common_action_set.append(find_item)
                    common_action_set.append(plug_item)
                    action_set_candidates.append(common_action_set)
                elif primitive_name == 'PLUGGED_OUT':
                    find_item = self.translate_single_action('FIND', obj_name, obj_id)
                    unplug_item = self.translate_single_action('PLUGOUT', obj_name, obj_id)
                    common_action_set.append(find_item)
                    common_action_set.append(unplug_item)
                    action_set_candidates.append(common_action_set)
            elif len(primitive_args) == 2:
                obj_pair_1 = primitive_args[0]
                obj_pair_2 = primitive_args[1]
                obj1_name, obj1_id = self.split_obj_pair(obj_pair_1)
                obj2_name, obj2_id = self.split_obj_pair(obj_pair_2)
                if primitive_name == 'ONTOP':
                    if obj1_id == char_id:
                        find_item = self.translate_single_action('FIND', obj2_name, obj2_id)
                        common_action_set.append(find_item)
                        ans_set_1 = copy.deepcopy(common_action_set)
                        ans_set_2 = copy.deepcopy(common_action_set)
                        sit_on_item = self.translate_single_action('SIT', obj2_name, obj2_id)
                        ans_set_1.append(sit_on_item)
                        lie_on_item = self.translate_single_action('LIE', obj2_name, obj2_id)
                        ans_set_2.append(lie_on_item)
                        action_set_candidates.append(ans_set_1)
                        action_set_candidates.append(ans_set_2)
                    elif obj2_id == char_id:
                        put_on_item = self.translate_single_action('PUTON', obj1_name, obj1_id)
                        common_action_set.append(put_on_item)
                        action_set_candidates.append(common_action_set)
                    else:
                        if not self.check_holding(obj_pair_1, self.planner, char_id):
                            find_item = self.translate_single_action('FIND', obj1_name, obj1_id)
                            grab_item = self.translate_single_action('GRAB', obj1_name, obj1_id)
                            common_action_set.append(find_item)
                            common_action_set.append(grab_item)
                        find_item_2 = self.translate_single_action('FIND', obj2_name, obj2_id)
                        put_back_item = self.translate_double_action('PUTBACK', obj1_name, obj1_id, obj2_name, obj2_id)
                        common_action_set.append(find_item_2)
                        common_action_set.append(put_back_item)
                        action_set_candidates.append(common_action_set)
                elif primitive_name == 'INSIDE':
                    if obj1_id == char_id:
                        walk_to_item = self.translate_single_action('WALK', obj2_name, obj2_id)
                        common_action_set.append(walk_to_item)
                        action_set_candidates.append(common_action_set)
                    else:
                        if not self.check_holding(obj_pair_1, self.planner, char_id):
                            find_item = self.translate_single_action('FIND', obj1_name, obj1_id)
                            grab_item = self.translate_single_action('GRAB', obj1_name, obj1_id)
                            common_action_set.append(find_item)
                            common_action_set.append(grab_item)
                        find_item_2 = self.translate_single_action('FIND', obj2_name, obj2_id)
                        common_action_set.append(find_item_2)
                        ans_set_1 = copy.deepcopy(common_action_set)
                        ans_set_2 = copy.deepcopy(common_action_set)
                        put_in_item = self.translate_double_action('PUTIN', obj1_name, obj1_id, obj2_name, obj2_id)
                        ans_set_1.append(put_in_item)
                        pour_item = self.translate_double_action('POUR', obj1_name, obj1_id, obj2_name, obj2_id)
                        ans_set_2.append(pour_item)
                        action_set_candidates.append(ans_set_1)
                        action_set_candidates.append(ans_set_2)
                elif primitive_name == 'BETWEEN':
                    pass
                elif primitive_name == 'NEXT_TO':
                    if obj1_id == char_id:
                        find_item = self.translate_single_action('FIND', obj2_name, obj2_id)
                        common_action_set.append(find_item)
                        action_set_candidates.append(common_action_set)
                elif primitive_name == 'FACING':
                    find_item = self.translate_single_action('FIND', obj2_name, obj2_id)
                    turnto_item = self.translate_single_action('TURNTO', obj2_name, obj2_id)
                    common_action_set.append(find_item)
                    common_action_set.append(turnto_item)
                    action_set_candidates.append(common_action_set)
                elif primitive_name == 'HOLDS_RH' or primitive_name == 'HOLDS_LH':
                    find_item = self.translate_single_action('FIND', obj2_name, obj2_id)
                    grab_item = self.translate_single_action('GRAB', obj2_name, obj2_id)
                    common_action_set.append(find_item)
                    common_action_set.append(grab_item)
                    action_set_candidates.append(common_action_set)
        
        return action_set_candidates
    
    def map_subgoal_to_action_sequence_dynamic_verion(self, cur_primitive: SimpleTLPrimitive, new_planner: MotionPlanner) -> List[List[str]]:
        self.planner = new_planner
        action_set_candidates = self.map_primitive_to_action_set(cur_primitive, self.planner.acting_char_id)
        return action_set_candidates