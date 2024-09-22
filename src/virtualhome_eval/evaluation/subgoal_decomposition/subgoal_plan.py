import os
import json
import random
import re
import logging
logger = logging.getLogger(__name__)
from typing import List, Dict, Any, Optional, Union

class SubgoalPlan:
    def __init__(self, scene_id: int, file_id: str, llm_output: str) -> None:
        self.scene_id = scene_id
        self.file_id = file_id
        self.llm_output = llm_output

    def __str__(self) -> str:
        raise NotImplementedError('This method should be implemented by the subclass')
    
    def get_subgoal_plan(self) -> List[str]:
        '''This method indicates preprocessed subgoal plan
        
        Args:
            None
            
        Returns:
            List[str]: Preprocessed subgoal plan
        '''
        raise NotImplementedError('This method should be implemented by the subclass')
    
    def get_subgoal_plan_tl_formula(self) -> str:
        '''This method indicates temporal logic formula of subgoal plan
        
        Args:
            None
            
        Returns:
            str: Temporal logic formula of subgoal plan
        '''
        raise NotImplementedError('This method should be implemented by the subclass')


class SubgoalPlanHalfJson(SubgoalPlan):
    def __init__(self, scene_id: int, file_id: str, llm_output: str) -> None:
        super().__init__(scene_id, file_id, llm_output)
        self.subgoal_plan = self.get_subgoal_plan()
        self.subgoal_plan_tl_formula = self.get_subgoal_plan_tl_formula()
        self.simple_subgoal_plan = self.get_simple_subgoal_plan()
    

    def __str__(self) -> str:
        return '\n'.join(self.subgoal_plan)

    @staticmethod
    def extract_json_obj(plan_str: str) -> Union[Dict[str, Any], None]:
        raw_plan_str = plan_str.strip().replace('}}', '}')
        match = re.search(r"{[^{}]*}", raw_plan_str, re.DOTALL)
        if match:
            result = match.group(0)
            try:
                json_obj = json.loads(result)
                assert 'output' in json_obj, 'output key is not in json_obj'
                assert isinstance(json_obj['output'], list), 'output value is not list'
            except Exception as e:
                return None
            return json_obj
        return None

    @staticmethod
    def sample_state_from_compound_state(compound_state: str) -> Union[str, None]:
        # compound state must contain str format like "<predicate name>([params])"
        # e.g., "is_open(door1)", ONTOP(object1, object2)
        if compound_state == 'SLEEP' or compound_state == 'WAKEUP' or compound_state == 'STANDUP':
            return f'{compound_state}()'
        match = re.search(r"\w+\(.*?\)", compound_state)
        if not match:
            return None
        states_or = compound_state.split(' or ')
        sampled_state = random.choice(states_or)
        return sampled_state
        

    @staticmethod
    def preprocess_raw_plan_obj(raw_plan_list: List[str]) -> List[str]:
        subgoal_plan_list = []
        for state in raw_plan_list:
            state = state.strip()
            if state != '':
                sampled_state = SubgoalPlanHalfJson.sample_state_from_compound_state(state)
                if sampled_state is not None:
                    subgoal_plan_list.append(sampled_state)
        return subgoal_plan_list
    
    def get_subgoal_plan(self) -> List[str]:
        raw_plan_str = self.llm_output
        json_obj = self.extract_json_obj(raw_plan_str)
        if json_obj is None:
            raise Exception(f'Failed to extract json object from the plan string: {raw_plan_str}')
        plan_list = json_obj['output']
        subgoal_plan_list = self.preprocess_raw_plan_obj(plan_list)
        return subgoal_plan_list
    
    def get_subgoal_plan_tl_formula(self) -> str:
        return ' then '.join(self.subgoal_plan)
    
    def get_simple_subgoal_plan(self) -> List[str]:
        simple_subgoal_plan = []
        for state in self.subgoal_plan:
            states_and = state.split(' and ')
            simple_subgoal_plan.extend(states_and)
        return simple_subgoal_plan
    


# ========================================
# ============== Unit Tests ==============
# ========================================

# def test_subgoal_object():
#     llm_outputs_path = './virtualhome/simulation/evaluation/eval_subgoal_plan/llm_output/llama-3-8b-chat_outputs.json'
#     with open(llm_outputs_path, 'r') as f:
#         llm_outputs = json.load(f)
#     error_num = 0
#     # now iterate all
#     for llm_output in llm_outputs:
#         identifier = llm_output['identifier']
#         llm_output = llm_output['llm_output']
#         scene_id = int(identifier[6:7])
#         file_id = identifier[8:]
#         try:
#             subgoal_plan = SubgoalPlanHalfJson(scene_id, file_id, llm_output)
#         except Exception as e:
#             error_num += 1
#     print(f'Error num: {error_num}')


# if __name__ == '__main__':
#     test_subgoal_object()