import argparse
import os
import os.path as osp
import json

from virtualhome_eval.evaluation.goal_interpretation.scripts.generate_prompts import (
    generate_prompts as goal_input_preparation,
)
from virtualhome_eval.evaluation.transition_modeling.scripts.generate_prompts import (
    generate_prompts as tm_input_preparation,
)
from virtualhome_eval.evaluation.action_sequence.scripts.generate_prompts import (
    generate_prompts as action_input_preparation,
)
from virtualhome_eval.evaluation.goal_interpretation.scripts.evaluate_results import (
    evaluate_results as goal_output_evaluation,
)
from virtualhome_eval.evaluation.transition_modeling.scripts.evaluate_results import (
    evaluate_results as tm_output_evaluation,
)
from virtualhome_eval.evaluation.action_sequence.scripts.evaluate_results import (
    evaluate_results as action_output_evaluation,
)

def parse_args():
    parser = argparse.ArgumentParser(description="Agent evaluation")
    parser.add_argument(
        "--mode",
        type=str,
        default="evaluate_results",
        help="generate_prompts, evaluate_results",
    )
    parser.add_argument(
        "--eval_type",
        type=str,
        default="action_sequence",
        help="action_sequence, transition_model, goal_interpretation, subgoal_decomposition",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="gpt-4o-2024-05-13",
        help="model name will be used as directory name to store results: gemini-1.5-pro-preview-0409, gpt-4o-2024-05-13, llama-3-70b-chat, mistral-large-2402,mixtral-8x22b-instruct-v0.1, gpt-4-turbo-2024-04-09, gpt-3.5-turbo-0125,llama-3-8b-chat, claude-3-haiku-20240307, claude-3-opus-20240229,claude-3-sonnet-2024022, cohere-command-r, cohere-command-r-plus, gemini-1.0-pro, gemini-1.5-flash-preview-0514",
    )
    parser.add_argument(
        "--resource_dir",
        type=str,
        default="virtualhome_eval/resources/",
        help="resources directory",
    )
    parser.add_argument(
        "--llm_response_path", type=str, default="", help="your llm response path"
    )
    parser.add_argument(
        "--dataset_dir",
        type=str,
        default="virtualhome_eval/dataset/",
        help="dataset directory, necessary only when generating prompts",
    )
    parser.add_argument(
        "--dataset", type=str, default="virtualhome", help="virtualhome, behavior"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="virtualhome_eval/output/",
        help="output directory",
    )
    # virtualhoome
    parser.add_argument("--scene_id", type=int, default=1, help="virtualhome scene id")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    eval_type = args.eval_type
    mode = args.mode
    model_name = args.model_name

    output_dir = args.output_dir
    if not osp.exists(output_dir):
        os.makedirs(output_dir)
    if mode == "generate_prompts":
        if eval_type == "action_sequence":
            action_input_preparation(args)
        elif eval_type == "transition_model":
            tm_input_preparation(args)
        elif eval_type == "goal_interpretation":
            goal_input_preparation(args)
    elif mode == "evaluate_results":
        if eval_type == "action_sequence":
            output_dir = osp.join(output_dir, "action_sequence")
            if not osp.exists(output_dir):
                os.makedirs(output_dir)
            summary, error_info = action_output_evaluation(args)
        elif eval_type == "transition_model":
            output_dir = osp.join(output_dir, "transition_modeling")
            if not osp.exists(output_dir):
                os.makedirs(output_dir)
            summary, error_info = tm_output_evaluation(args)
        elif eval_type == "goal_interpretation":
            output_dir = osp.join(output_dir, "goal_interpretation")
            if not osp.exists(output_dir):
                os.makedirs(output_dir)
            summary, error_info = goal_output_evaluation(args)
    else:
        raise ValueError(f"Invalid mode: {mode}")

    # save summary results and intermediate results
    if mode == "evaluate_results":
        output_dir = osp.join(output_dir, model_name)
        if not osp.exists(output_dir):
            os.makedirs(output_dir)
        with open(osp.join(output_dir, "summary.json"), "w") as f:
            json.dump(summary, f, indent=4)
            print(f'Evaluate results saved to {osp.join(output_dir, "summary.json")}')
        if error_info is not None:
            with open(osp.join(output_dir, "error_info.json"), "w") as f:
                json.dump(error_info, f, indent=4)
                print(f'Error info saved to {osp.join(output_dir, "error_info.json")}')
    elif mode == "generate_prompts":
        print(f"Prompts generated in {output_dir}")
