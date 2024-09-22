
from typing import Optional
from behavior_eval.evaluation.action_sequence.scripts.evaluate_results import evaluate_results as action_sequence_evaluate_results
from behavior_eval.evaluation.action_sequence.scripts.generate_prompts import generate_prompts as action_sequence_generate_prompts
from behavior_eval.evaluation.goal_interpretation.scripts.evaluate_results import evaluate_results as goal_interpretation_evaluate_results
from behavior_eval.evaluation.goal_interpretation.scripts.generate_prompts import generate_prompts as goal_interpretation_generate_prompts
from behavior_eval.evaluation.subgoal_decomposition.scripts.generate_prompts import generate_prompts as subgoal_decomposition_generate_prompts
from behavior_eval.evaluation.subgoal_decomposition.scripts.evaluate_results import evaluate_results as subgoal_decomposition_evaluate_results
from behavior_eval.evaluation.transition_modeling.scripts.generate_prompts import generate_prompts as transition_modeling_generate_prompts
from virtualhome_eval.agent_eval import agent_evaluation as virtualhome_agent_evaluation
import os
import sys
def agent_evaluation(
        mode="generate_prompts",
        eval_type="goal_interpretation",
        output_dir='./output',
        num_workers=1,
        llm_response_path:Optional[str]=None,
    ):
    """
    eval_type: goal_interpretation,action_sequence,subgoal_decomposition,transition_modeling
    mode: evaluate_results,generate_prompts
    num_workers: number of workers for multiprocessing
    llm_response_dir: directory containing llm responses (helm outputs)
    output_dir: directory to store results
    output_dir: directory to store results
    """
    output_dir = os.path.join(output_dir, 'behavior',mode, eval_type)
    os.makedirs(output_dir,exist_ok=True)
    if eval_type=="evaluate_results":
        if llm_response_path is None:
            print("Error: llm_response_dir is required for evaluate_results")
            sys.exit(1)
    if mode not in ["evaluate_results","generate_prompts"]:
        print("Error: Invalid function, must be evaluate_results or generate_prompts")
        sys.exit(1)
    if eval_type not in ["goal_interpretation","action_sequence","subgoal_decomposition","transition_modeling"]:
        print(f"Invalid module {eval_type}, must be goal_interpretation,action_sequence,subgoal_decomposition,transition_modeling")
        sys.exit(1)
        
    if eval_type == "action_sequence":
        if mode == "evaluate_results":
            action_sequence_evaluate_results(os.path.join(llm_response_path,eval_type),num_workers,output_dir)
        elif mode == "generate_prompts":
            action_sequence_generate_prompts(num_workers,output_dir)
    elif eval_type == "goal_interpretation":
        if mode == "evaluate_results":
            goal_interpretation_evaluate_results(os.path.join(llm_response_path,eval_type), output_dir)
        elif mode == "generate_prompts":
            goal_interpretation_generate_prompts(output_dir)
    elif eval_type == "subgoal_decomposition":
        if mode == "evaluate_results":
            subgoal_decomposition_evaluate_results(os.path.join(llm_response_path,eval_type), num_workers, output_dir)
        elif mode == "generate_prompts":
            subgoal_decomposition_generate_prompts(num_workers, output_dir)
    elif eval_type == "transition_modeling":
        if mode == "evaluate_results":
            virtualhome_agent_evaluation(
                mode=mode,
                eval_type=eval_type,
                output_dir=output_dir,
                dataset="behavior",
            )
        elif mode == "generate_prompts":
            transition_modeling_generate_prompts(output_dir)
