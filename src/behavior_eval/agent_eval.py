
from typing import Optional
from behavior_eval.evaluation.action_sequencing.scripts.evaluate_results import evaluate_results as action_sequence_evaluate_results
from behavior_eval.evaluation.action_sequencing.scripts.generate_prompts import generate_prompts as action_sequence_generate_prompts
from behavior_eval.evaluation.goal_interpretation.scripts.evaluate_results import evaluate_results as goal_interpretation_evaluate_results
from behavior_eval.evaluation.goal_interpretation.scripts.generate_prompts import generate_prompts as goal_interpretation_generate_prompts
from behavior_eval.evaluation.subgoal_decomposition.scripts.generate_prompts import generate_prompts as subgoal_decomposition_generate_prompts
from behavior_eval.evaluation.subgoal_decomposition.scripts.evaluate_results import evaluate_results as subgoal_decomposition_evaluate_results
from behavior_eval.evaluation.transition_modeling.scripts.generate_prompts import generate_prompts as transition_modeling_generate_prompts
from virtualhome_eval.agent_eval import agent_evaluation as virtualhome_agent_evaluation
import os
import sys
import eai_eval
def agent_evaluation(
        mode="generate_prompts",
        eval_type="goal_interpretation",
        output_dir='./output',
        num_workers=1,
        llm_response_path:Optional[str]=None,
    ):
    """
    eval_type: goal_interpretation,action_sequencing,subgoal_decomposition,transition_modeling
    mode: evaluate_results,generate_prompts
    num_workers: number of workers for multiprocessing
    llm_response_dir: directory containing llm responses (helm outputs)
    output_dir: directory to store results
    output_dir: directory to store results
    """
    output_dir_for_tm=output_dir
    output_dir = os.path.join(output_dir, 'behavior',mode, eval_type)
    os.makedirs(output_dir,exist_ok=True)
    if mode=="evaluate_results":
        if llm_response_path is None:
            print(f"did not provide llm_response_path, set to default: {eai_eval.helm_output_path}")
            llm_response_path=eai_eval.helm_output_path
        
        
        llm_response_path_eval_type=os.path.join(llm_response_path,'behavior',eval_type)
        if os.path.exists(llm_response_path_eval_type) is False:
            print(f"Error: eval-type dir {llm_response_path_eval_type} under {llm_response_path} does not exist")
            print("Please run python -m eagent_eval.utils.download_utils to download the data \n or provide the correct path")
            
            
            
    if mode not in ["evaluate_results","generate_prompts"]:
        print("Error: Invalid mode {mode}, must be evaluate_results or generate_prompts")
        sys.exit(1)
    if eval_type not in ["goal_interpretation","action_sequencing","subgoal_decomposition","transition_modeling"]:
        print(f"Invalid eval_type {eval_type}, must be goal_interpretation,action_sequencing,subgoal_decomposition,transition_modeling")
        sys.exit(1)
        
    if eval_type == "action_sequencing":
        if mode == "evaluate_results":
            action_sequence_evaluate_results(llm_response_path_eval_type,num_workers,output_dir)
        elif mode == "generate_prompts":
            action_sequence_generate_prompts(num_workers,output_dir)
    elif eval_type == "goal_interpretation":
        if mode == "evaluate_results":
            goal_interpretation_evaluate_results(llm_response_path_eval_type, output_dir)
        elif mode == "generate_prompts":
            goal_interpretation_generate_prompts(output_dir)
    elif eval_type == "subgoal_decomposition":
        if mode == "evaluate_results":
            subgoal_decomposition_evaluate_results(llm_response_path_eval_type, num_workers, output_dir)
        elif mode == "generate_prompts":
            subgoal_decomposition_generate_prompts(num_workers, output_dir)
    elif eval_type == "transition_modeling":
        if mode == "evaluate_results":
            virtualhome_agent_evaluation(
                mode=mode,
                eval_type=eval_type,
                output_dir=output_dir_for_tm,
                dataset="behavior",
                llm_response_path=os.path.join(llm_response_path),
            )
        elif mode == "generate_prompts":
            transition_modeling_generate_prompts(output_dir)
