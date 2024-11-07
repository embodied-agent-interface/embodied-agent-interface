import argparse
import os
import sys
from itertools import product

def main():
    parser = argparse.ArgumentParser(description="Embodied Evaluation CLI")
    parser.add_argument(
        "--mode",
        choices=["generate_prompts", "evaluate_results"],
        default="generate_prompts",
        help="Mode of operation (default: generate_prompts)",
    )
    parser.add_argument(
        "--eval-type",
        choices=[
            "action_sequencing",
            "transition_modeling",
            "goal_interpretation",
            "subgoal_decomposition",
        ],
        default="goal_interpretation",
        help="Type of evaluation (default: goal_interpretation)",
    )
    parser.add_argument(
        "--llm-response-path",
        type=str,
        help="Path to LLM response directory",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./output",
        help="Path to the output directory (default: output/)",
    )
    parser.add_argument(
        "--num-workers",
        type=int,
        default=4,
        help="Number of workers for multiprocessing (default: 4)",
    )
    parser.add_argument(
        "--dataset",
        choices=["virtualhome", "behavior"],
        default="behavior",
        help="The dataset to use (default: behavior)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="If specified, runs all combinations of unspecified arguments",
    )
    args = parser.parse_args()
    specified_args = get_specified_args(parser, sys.argv)
    print(args)
    print("Specified arguments:", specified_args)


    # Execute different arg combos sequentially
    # TODO: multiprocessing
    if args.all:
        args_to_consider = ["mode", "eval_type", "dataset"]
        arg_options = {
            "mode": ["generate_prompts", "evaluate_results"],
            "eval_type": [
                "action_sequencing",
                "transition_modeling",
                "goal_interpretation",
                "subgoal_decomposition",
            ],
            "dataset": ["virtualhome", "behavior"],
        }

        unspecified_args = [arg for arg in args_to_consider if arg not in specified_args]
        specified_args_dict = {arg: getattr(args, arg) for arg in args_to_consider if arg in specified_args}
        options_list = [arg_options[arg] for arg in unspecified_args]
        combinations = list(product(*options_list))

        for combo in combinations:
            combo_args = args.__dict__.copy()
            for arg, value in specified_args_dict.items():
                combo_args[arg] = value
            for arg, value in zip(unspecified_args, combo):
                combo_args[arg] = value

            print(f"Running with arguments: {combo_args}")

            if combo_args["dataset"] == "behavior":
                from behavior_eval.agent_eval import (
                    agent_evaluation as behavior_agent_evaluation,
                )

                behavior_agent_evaluation(
                    mode=combo_args["mode"],
                    eval_type=combo_args["eval_type"],
                    llm_response_path=combo_args["llm_response_path"],
                    output_dir=combo_args["output_dir"],
                    num_workers=combo_args["num_workers"],
                )
            elif combo_args["dataset"] == "virtualhome":
                from virtualhome_eval.agent_eval import (
                    agent_evaluation as virtualhome_agent_evaluation,
                )

                virtualhome_agent_evaluation(
                    mode=combo_args["mode"],
                    eval_type=combo_args["eval_type"],
                    llm_response_path=combo_args["llm_response_path"],
                    output_dir=combo_args["output_dir"],
                    dataset=combo_args["dataset"],
                    num_workers=combo_args["num_workers"],
                )
    else:
        if args.dataset == "behavior":
            from behavior_eval.agent_eval import agent_evaluation as behavior_agent_evaluation

            behavior_agent_evaluation(
                mode=args.mode,
                eval_type=args.eval_type,
                llm_response_path=args.llm_response_path,
                output_dir=args.output_dir,
                num_workers=args.num_workers,
            )
        elif args.dataset == "virtualhome":
            from virtualhome_eval.agent_eval import agent_evaluation as virtualhome_agent_evaluation

            virtualhome_agent_evaluation(
                mode=args.mode,
                eval_type=args.eval_type,
                llm_response_path=args.llm_response_path,
                output_dir=args.output_dir,
                dataset=args.dataset,
                num_workers=args.num_workers,
            )

def get_specified_args(parser, argv):
    specified_args = set()
    for action in parser._actions:
        if not action.option_strings:
            continue  
        for option_string in action.option_strings:
            if option_string in argv:
                specified_args.add(action.dest)
                break
    return specified_args

if __name__ == "__main__":
    main()
