import fire
from typing import Optional
from behavior_eval.evaluation.action_sequencing.scripts.evaluate_results import evaluate_results as action_sequence_evaluate_results
from behavior_eval.evaluation.action_sequencing.scripts.generate_prompts import generate_prompts as action_sequence_generate_prompts
from behavior_eval.evaluation.goal_interpretation.scripts.evaluate_results import evaluate_results as goal_interpretation_evaluate_results
from behavior_eval.evaluation.goal_interpretation.scripts.generate_prompts import generate_prompts as goal_interpretation_generate_prompts
from behavior_eval.evaluation.subgoal_decomposition.scripts.generate_prompts import generate_prompts as subgoal_decomposition_generate_prompts
from behavior_eval.evaluation.subgoal_decomposition.scripts.evaluate_results import evaluate_results as subgoal_decomposition_evaluate_results
import os
def main(module:str="action_sequence",func:str="generate_prompts",worker_num:int=1,llm_response_dir:Optional[str]=None,result_dir:str='./results'):
    """
    module: goal_interpretation,action_sequence,subgoal_decomposition,transition_modeling
    func: evaluate_results,generate_prompts
    worker_num: number of workers for multiprocessing
    llm_response_dir: directory containing llm responses (helm outputs)
    result_dir: directory to store results
    result_dir: directory to store results
    """
    result_dir = os.path.join(result_dir, module, func)
    os.makedirs(result_dir,exist_ok=True)
    if func=="evaluate_results":
        if llm_response_dir is None:
            return "llm_response_dir is required for evaluate_results"
    if func not in ["evaluate_results","generate_prompts"]:
        return "Invalid function, must be evaluate_results or generate_prompts"
    if module not in ["goal_interpretation","action_sequence","subgoal_decomposition","transition_modeling"]:
        return f"Invalid module {module}, must be goal_interpretation,action_sequence,subgoal_decomposition,transition_modeling"
    if module == "action_sequence":
        if func == "evaluate_results":
            action_sequence_evaluate_results(llm_response_dir,worker_num,result_dir)
            action_sequence_evaluate_results(llm_response_dir,worker_num,result_dir)
        elif func == "generate_prompts":
            action_sequence_generate_prompts(worker_num,result_dir)
    elif module == "goal_interpretation":
        if func == "evaluate_results":
            goal_interpretation_evaluate_results(llm_response_dir, result_dir)
        elif func == "generate_prompts":
            goal_interpretation_generate_prompts(result_dir)
    elif module == "subgoal_decomposition":
        if func == "evaluate_results":
            subgoal_decomposition_evaluate_results(llm_response_dir, worker_num, result_dir)
        elif func == "generate_prompts":
            subgoal_decomposition_generate_prompts(worker_num, result_dir)


if __name__ == '__main__':
    fire.Fire(main)