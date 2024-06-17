import argparse
import os
import os.path as osp
from simulation.evolving_graph.eval_action import *
from simulation.evolving_graph.eval_transition import *
from simulation.evolving_graph.eval_goal import *
from simulation.evolving_graph.eval_utils import *


def parse_args():
    parser = argparse.ArgumentParser(description="Agent evaluation")
    parser.add_argument('--mode', type=str, default='output', help='input, output')
    parser.add_argument(
        "--eval_type",
        type=str,
        default="transition",
        help="action, transition, goal, subgoal",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="gpt-4o-2024-05-13",
        help="gemini-1.5-pro-preview-0409, gpt-4o-2024-05-13, llama-3-70b-chat, mistral-large-2402,mixtral-8x22b-instruct-v0.1, gpt-4-turbo-2024-04-09, gpt-3.5-turbo-0125,llama-3-8b-chat, claude-3-haiku-20240307, claude-3-opus-20240229,claude-3-sonnet-2024022, cohere-command-r, cohere-command-r-plus, gemini-1.0-pro, gemini-1.5-flash-preview-0514",
    )
    parser.add_argument(
        "--resource_dir",
        type=str,
        default='resources/',
        help="resources directory",
    )
    parser.add_argument('--helm_dir', type=str, default='helm2/', help='output directory')
    parser.add_argument(
        "--dataset", type=str, default="virtualhome", help="virtualhome, behavior"
    )
    parser.add_argument(
        "--dataset_dir",
        type=str,
        default="dataset/",
        help="dataset directory",
    )
    parser.add_argument(
        "--prompt_dir", type=str, default='prompts/', help="prompt directory"
    )
    parser.add_argument(
        "--output_dir", type=str, default='output/', help="output directory"
    )

    # virtualhoome
    parser.add_argument(
        "--scene_id", type=int, default=1, help="virtualhome scene id"
    )
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    eval_type = args.eval_type
    mode = args.mode

    # create dir
    if not osp.exists(args.helm_dir):
        os.makedirs(args.helm_dir)
    helm_prompt = osp.join(args.helm_dir, "helm_prompt")
    helm_output = osp.join(args.helm_dir, "helm_output")
    if not osp.exists(helm_prompt):
        os.makedirs(helm_prompt)
    if not osp.exists(helm_output):
        os.makedirs(helm_output)
    if not osp.exists(args.prompt_dir):
        os.makedirs(args.prompt_dir)
    if mode == 'input':
        if eval_type == 'action':
            action_input_preparation(args)
        elif eval_type == 'transition':
            tm_input_preparation(args)
        elif eval_type == 'goal':
            goal_input_preparation(args)
    elif mode == 'output':
        if eval_type == 'action':
            action_output_evaluation(args)
        elif eval_type == 'transition':
            tm_output_evaluation(args)
        elif eval_type == 'goal':
            goal_output_evaluation(args)
    else:
        raise ValueError(f"Invalid mode: {mode}")
