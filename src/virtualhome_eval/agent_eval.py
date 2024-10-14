import os
import os.path as osp
import logging
from virtualhome_eval.log_config import setup_logging
from virtualhome_eval.evaluation.goal_interpretation.scripts.generate_prompts import (
    generate_prompts as goal_input_preparation,
)
from virtualhome_eval.evaluation.transition_modeling.scripts.generate_prompts import (
    generate_prompts as tm_input_preparation,
)
from virtualhome_eval.evaluation.action_sequencing.scripts.generate_prompts import (
    generate_prompts as action_input_preparation,
)
from virtualhome_eval.evaluation.subgoal_decomposition.scripts.generate_prompts import (
    generate_prompts as subgoal_input_preparation,
)
from virtualhome_eval.evaluation.goal_interpretation.scripts.evaluate_results import (
    evaluate_results as goal_output_evaluation,
)
from virtualhome_eval.evaluation.transition_modeling.scripts.evaluate_results import (
    evaluate_results as tm_output_evaluation,
)
from virtualhome_eval.evaluation.action_sequencing.scripts.evaluate_results import (
    evaluate_results as action_output_evaluation,
)
from virtualhome_eval.evaluation.subgoal_decomposition.scripts.evaluate_results import (
    evaluate_results as subgoal_output_evaluation,
)

import eai_eval

package_path = os.path.dirname(os.path.abspath(__file__))
default_resource_dir = os.path.join(package_path, "resources")
default_dataset_dir = os.path.join(package_path, "dataset")
default_evaluation_dir = os.path.join(package_path, "evaluation")
default_llm_response_path = eai_eval.helm_output_path

def agent_evaluation(
    mode="generate_prompts",
    eval_type="goal_interpretation",
    output_dir="./output",
    dataset="virtualhome",
    llm_response_path=None,
    scene_id=1,
    num_workers=1,
    resource_dir=default_resource_dir,
    dataset_dir=default_dataset_dir,
    evaluation_dir=default_evaluation_dir,
):
    """
    Perform agent evaluation based on the specified parameters.

    Args:
        mode (str): The evaluation mode ('generate_prompts' or 'evaluate_results').
        eval_type (str): The type of evaluation ('action_sequencing', 'transition_model', 'goal_interpretation', or 'subgoal_decomposition').
        resource_dir (str): Path to the resources directory.
        llm_response_path (str): Path to the LLM response directory.
        dataset_dir (str): Path to the dataset directory.
        dataset (str): The dataset to use ('virtualhome' or 'behavior').
        output_dir (str): Path to the output directory.
        scene_id (int): The VirtualHome scene ID.

    Returns:
        dict or None: Evaluation results if mode is 'evaluate_results', None otherwise.
    """
    if llm_response_path is None:
        llm_response_path = default_llm_response_path

    # Create output directory if it doesn't exist
    output_dir=os.path.join(output_dir, f"{dataset}", mode, eval_type)
    if not osp.exists(output_dir):
        os.makedirs(output_dir)

    # Create a class to mimic the structure of args
    class Args:
        pass

    args = Args()
    args.mode = mode
    args.eval_type = eval_type
    args.resource_dir = resource_dir
    args.llm_response_path = llm_response_path
    args.dataset_dir = dataset_dir
    args.dataset = dataset
    args.output_dir = output_dir
    args.scene_id = scene_id
    args.evaluation_dir = evaluation_dir
    args.num_workers = num_workers

    if mode == "generate_prompts":
        if eval_type == "action_sequencing":
            log_file = setup_logging(function_name="action_sequencing_prompts")
            logger = logging.getLogger(__name__)
            prompt_path = action_input_preparation(args)
        elif eval_type == "transition_modeling":
            log_file = setup_logging(function_name="transition_model_prompts")
            logger = logging.getLogger(__name__)
            prompt_path = tm_input_preparation(args)
        elif eval_type == "goal_interpretation":
            log_file = setup_logging(function_name="goal_interpretation_prompts")
            logger = logging.getLogger(__name__)
            prompt_path = goal_input_preparation(args)
        elif eval_type == "subgoal_decomposition":
            log_file = setup_logging(function_name="subgoal_decomposition_prompts")
            logger = logging.getLogger(__name__)
            prompt_path = subgoal_input_preparation(args)
        print(f"Prompts generated and saved to {prompt_path}")
        return None
    elif mode == "evaluate_results":
        if eval_type == "action_sequencing":
            log_file = setup_logging(function_name="action_sequencing_eval")
            logger = logging.getLogger(__name__)
            all_results = action_output_evaluation(args)
        elif eval_type == "transition_modeling":
            log_file = setup_logging(function_name="transition_model_eval")
            logger = logging.getLogger(__name__)
            all_results = tm_output_evaluation(args)
        elif eval_type == "goal_interpretation":
            log_file = setup_logging(function_name="goal_interpretation_eval")
            logger = logging.getLogger(__name__)
            all_results = goal_output_evaluation(args)
        elif eval_type == "subgoal_decomposition":
            log_file = setup_logging(function_name="subgoal_decomposition_eval")
            logger = logging.getLogger(__name__)
            all_results = subgoal_output_evaluation(args)
        print(f"All results saved to {output_dir}")
        return all_results
    else:
        raise ValueError(f"Invalid mode: {mode}")

