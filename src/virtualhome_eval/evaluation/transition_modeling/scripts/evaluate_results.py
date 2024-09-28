import json
import copy
import os
import os.path as osp
import copy
from multiprocessing import Pool, Manager
from io import StringIO

from virtualhome_eval.simulation.evolving_graph.eval_utils import *
from virtualhome_eval.simulation.evolving_graph.pddlgym_planners.fd import FD
from virtualhome_eval.simulation.evolving_graph.logic_score import *

import logging
logger = logging.getLogger(__name__)


def worker_process(args):
    (
        output_dict,
        model_name,
        dataset,
        timeout,
        resource_root,
        pddl_root,
        pddl_problem_dir,
        id2action,
        id2category,
        id2task,
        success_file_id,
        pred2category,
        gold_action_dict,
        categories_set,
        action_set,
        predicate_set,
    ) = args

    # Set up a string buffer to capture log output
    log_capture_string = StringIO()
    ch = logging.StreamHandler(log_capture_string)
    ch.setLevel(logging.INFO)
    logger = logging.getLogger(f"worker_{os.getpid()}")
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)

    results = {
        "precond_predicate_type_res": {
            category: [0, 0, 0] for category in categories_set
        },
        "effect_predicate_type_res": {
            category: [0, 0, 0] for category in categories_set
        },
        "precond_action_type": {action: [0, 0, 0] for action in action_set},
        "effect_action_type": {action: [0, 0, 0] for action in action_set},
        "precond_predicate_score": {pred: [0, 0, 0] for pred in predicate_set},
        "effect_predicate_score": {pred: [0, 0, 0] for pred in predicate_set},
        "success_by_task_type": {category: [0, 0] for category in categories_set},
        "action_variate_control": {action: [0, 0] for action in action_set},
        "format_wrong_num": 0,
        "hallucination_num": 0,
        "total_predict_action_num": 0,
    }

    file_id = output_dict["identifier"]
    if file_id not in success_file_id:
        logger.info(f"{file_id} not in success file id!")
        return None, None

    task_name = id2task[file_id]
    logger.info(f"task name is {task_name}")

    task_name = "_".join(task_name.split())
    if dataset == "virtualhome":
        task_problem_dir = os.path.join(pddl_problem_dir, task_name)
    elif dataset == "behavior":
        task_problem_dir = pddl_problem_dir
    problem_path = os.path.join(task_problem_dir, f"{file_id}.pddl")

    category_name_list = id2category[file_id]
    logger.info(f"category names are {category_name_list}")

    predicted_action = output_dict["llm_output"]
    if predicted_action.startswith("```json"):
        predicted_action = predicted_action[7:]
        predicted_action = predicted_action.strip("```")
    predicted_action = predicted_action.strip().replace("\n", "")
    predicted_action = predicted_action.replace("'", '"')
    try:
        predicted_action = json.loads(predicted_action)
        predicted_action = predicted_action["output"]
    except Exception as e:
        logger.info(f"Error in parsing JSON: {e}")
        pass

    try:
        predicted_action = extract_action_details(content=predicted_action)
    except Exception as e:
        logger.info(f"Error in extracting action details: {e}")
        return {"format_wrong_num": 1}, "format wrong!"

    if predicted_action is None or predicted_action == "":
        logger.info("Predicted action is empty")
        return {"format_wrong_num": 1}, "format wrong!"

    predicted_domain_path = os.path.join(pddl_root, f"predicted_{model_name}")
    gold_domain_path = os.path.join(pddl_root, f"gold_{model_name}")
    os.makedirs(predicted_domain_path, exist_ok=True)
    os.makedirs(gold_domain_path, exist_ok=True)

    gold_actions = {}
    gold_actions_name = id2action[file_id]
    for action_name in gold_actions_name:
        gold_actions[action_name] = gold_action_dict[action_name]

    planner = FD()

    for action_name, action_dict in predicted_action.items():
        results["total_predict_action_num"] += 1
        if action_name not in gold_actions_name:
            results["hallucination_num"] += 1
            continue

        gold_action = gold_actions[action_name]

        # Calculate logic scores
        (
            precond_similarity_score,
            matched_precond,
            unmatched_pred_precond,
            unmatched_gold_precond,
        ) = calculate_logic_score(
            action_dict["action_preconditions"], gold_action["action_preconditions"]
        )
        (
            effect_similarity_score,
            matched_effect,
            unmatched_pred_effect,
            unmatched_gold_effect,
        ) = calculate_logic_score(
            action_dict["action_effects"], gold_action["action_effects"]
        )

        for pred in matched_precond:
            if pred == "()":
                continue
            results["precond_predicate_type_res"][pred2category[pred]][0] += 1
            results["precond_action_type"][action_name][0] += 1
            results["precond_predicate_score"][pred][0] += 1

        for pred in unmatched_pred_precond:
            if pred == "()":
                continue
            if pred not in pred2category.keys():
                continue
            results["precond_predicate_type_res"][pred2category[pred]][1] += 1
            results["precond_action_type"][action_name][1] += 1
            results["precond_predicate_score"][pred][1] += 1
        for pred in unmatched_gold_precond:
            if pred == "()":
                continue
            results["precond_predicate_type_res"][pred2category[pred]][2] += 1
            results["precond_action_type"][action_name][2] += 1
            results["precond_predicate_score"][pred][2] += 1

        # record effect
        for pred in matched_effect:
            if pred == "()":
                continue
            results["effect_predicate_type_res"][pred2category[pred]][0] += 1
            results["effect_action_type"][action_name][0] += 1
            results["effect_predicate_score"][pred][0] += 1
        for pred in unmatched_pred_effect:
            if pred == "()":
                continue
            if pred not in pred2category.keys():
                continue
            results["effect_predicate_type_res"][pred2category[pred]][1] += 1
            results["effect_action_type"][action_name][1] += 1
            results["effect_predicate_score"][pred][1] += 1
        for pred in unmatched_gold_effect:
            if pred == "()":
                continue
            results["effect_predicate_type_res"][pred2category[pred]][2] += 1
            results["effect_action_type"][action_name][2] += 1
            results["effect_predicate_score"][pred][2] += 1

    # Planner success rate and sensitivity analysis
    for category_name in category_name_list:
        results["success_by_task_type"][category_name][1] += 1

    for action in gold_actions_name:
        results["action_variate_control"][action][1] += 1

    # All action trial
    domain_file_path = complete_pddl_domain(
        predicted_action,
        gold_action_dict,
        os.path.join(resource_root, f"{dataset}_pd.pddl"),
        file_id,
        predicted_domain_path,
    )
    try:
        pddl_plan = planner.plan_from_pddl(
            domain_file_path, problem_path, timeout=timeout
        )
        for category_name in category_name_list:
            results["success_by_task_type"][category_name][0] += 1
        logger.info(f"Holistic test: task {file_id} succeeded")
    except Exception as e:
        logger.info(f"Holistic test: task {file_id} failed")
        logger.info(f"Error: {e}")

    # Return the results and log output
    return results, log_capture_string.getvalue()


def evaluate_results(args):
    dataset = args.dataset
    num_workers = 32
    output_dir = args.output_dir

    if dataset == "virtualhome":
        timeout = 100
    elif dataset == "behavior":
        timeout = 200

    resource_root = osp.join(args.resource_dir, dataset)
    llm_response_path = args.llm_response_path

    # Load necessary data
    id2action = json.load(open(osp.join(resource_root, "id2action.json"), "r"))
    id2category = json.load(open(osp.join(resource_root, "id2category_2.json"), "r"))
    id2task = json.load(open(osp.join(resource_root, "id2task.json"), "r"))
    success_file_id = json.load(open(osp.join(resource_root, "success_task.json"), "r"))
    pred2category = json.load(
        open(osp.join(resource_root, "predicates_category.json"), "r")
    )
    gold_action_dict = json.load(open(osp.join(resource_root, "gold_action.json"), "r"))

    pddl_root = osp.join(resource_root, "pddl_files")
    pddl_problem_dir = osp.join(resource_root, "problem_pddl")
    os.makedirs(name=pddl_root, exist_ok=True)
    os.makedirs(pddl_problem_dir, exist_ok=True)

    categories_set = {
        "object_states",
        "object_affordance",
        "object_orientation",
        "spatial_relations",
        "non-spatial_relations",
        "object_tools",
    }
    action_set = set(action for actions in id2action.values() for action in actions)
    predicate_set = set(pred2category.keys())

    llm_response_path = osp.join(llm_response_path, dataset, "transition_modeling")
    logger.info(f"load llm response from {llm_response_path}")
    model_file = extract_model_names(llm_response_path)

    all_results = {}

    for model_name in model_file:
        llm_response_json = os.path.join(
            llm_response_path, f"{model_name}_outputs.json"
        )
        llm_response = json.load(open(llm_response_json, "r"))

        # Set up multiprocessing
        pool = Pool(processes=num_workers)

        # Prepare arguments for worker processes
        worker_args = [
            (
                output_dict,
                model_name,
                dataset,
                timeout,
                resource_root,
                pddl_root,
                pddl_problem_dir,
                id2action,
                id2category,
                id2task,
                success_file_id,
                pred2category,
                gold_action_dict,
                categories_set,
                action_set,
                predicate_set,
            )
            for output_dict in llm_response
        ]

        # Run worker processes
        results = pool.map(worker_process, worker_args)

        # Combine results and logs
        combined_log = StringIO()
        combined_results = {
            "precond_predicate_type_res": {
                category: [0, 0, 0] for category in categories_set
            },
            "effect_predicate_type_res": {
                category: [0, 0, 0] for category in categories_set
            },
            "precond_action_type": {action: [0, 0, 0] for action in action_set},
            "effect_action_type": {action: [0, 0, 0] for action in action_set},
            "precond_predicate_score": {pred: [0, 0, 0] for pred in predicate_set},
            "effect_predicate_score": {pred: [0, 0, 0] for pred in predicate_set},
            "success_by_task_type": {category: [0, 0] for category in categories_set},
            "action_variate_control": {action: [0, 0] for action in action_set},
            "format_wrong_num": 0,
            "hallucination_num": 0,
            "total_predict_action_num": 0,
        }

        for result, log_output in results:
            if result is not None:
                if result["format_wrong_num"] == 1:
                    combined_results["format_wrong_num"] += 1
                    continue
                # Aggregate results
                for key, value in result.items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            combined_results[key][subkey] = [
                                x + y
                                for x, y in zip(combined_results[key][subkey], subvalue)
                            ]
                    else:
                        combined_results[key] += value
            combined_log.write(log_output)

        # Close the pool
        pool.close()
        pool.join()

        # Process the combined results
        full_predicate_type_res_dict = {}
        full_action_type_dict = {}
        full_predicate_score_dict = {}

        full_predicate_type_res_dict["overall"] = [0, 0, 0]

        for category in categories_set:
            full_predicate_type_res_dict[category] = [
                combined_results["precond_predicate_type_res"][category][i]
                + combined_results["effect_predicate_type_res"][category][i]
                for i in range(3)
            ]
            for i in range(3):
                full_predicate_type_res_dict["overall"][i] += (
                    full_predicate_type_res_dict[category][i]
                )

        for action in action_set:
            full_action_type_dict[action] = [
                combined_results["precond_action_type"][action][i]
                + combined_results["effect_action_type"][action][i]
                for i in range(3)
            ]

        for pred in predicate_set:
            full_predicate_score_dict[pred] = [
                combined_results["precond_predicate_score"][pred][i]
                + combined_results["effect_predicate_score"][pred][i]
                for i in range(3)
            ]

        # Calculate precision, recall, and F1 scores
        precond_predicate_type_res_dict = calculate_precision_recall_f1(
            combined_results["precond_predicate_type_res"]
        )
        effect_predicate_type_res_dict = calculate_precision_recall_f1(
            combined_results["effect_predicate_type_res"]
        )
        full_predicate_type_res_dict = calculate_precision_recall_f1(
            full_predicate_type_res_dict
        )
        precond_action_type_dict = calculate_precision_recall_f1(
            combined_results["precond_action_type"]
        )
        effect_action_type_dict = calculate_precision_recall_f1(
            combined_results["effect_action_type"]
        )
        full_action_type_dict = calculate_precision_recall_f1(full_action_type_dict)
        precond_predicate_score_dict = calculate_precision_recall_f1(
            combined_results["precond_predicate_score"]
        )
        effect_predicate_score_dict = calculate_precision_recall_f1(
            combined_results["effect_predicate_score"]
        )
        full_predicate_score_dict = calculate_precision_recall_f1(
            full_predicate_score_dict
        )

        # Calculate success rates
        success_by_task_type_dict = calculate_success_rate(
            combined_results["success_by_task_type"]
        )

        present_categories = set(success_by_task_type_dict.keys())
        total_success = sum(
            success_by_task_type_dict[category][0] for category in present_categories
        )
        total_attempts = sum(
            success_by_task_type_dict[category][1] for category in present_categories
        )
        overall_success_rate = (
            total_success / total_attempts if total_attempts > 0 else 0
        )

        for category in present_categories:
            logger.info(
                f"ATTENTION! {category}: {success_by_task_type_dict[category][0]} / {success_by_task_type_dict[category][1]}"
            )

        # Add overall success rate to the dictionary
        success_by_task_type_dict["overall"] = [
            total_success,
            total_attempts,
            overall_success_rate,
        ]

        # Log the combined output
        logger.info(combined_log.getvalue())

        # Log results
        logger.info(f"Total tasks: {len(llm_response)}")
        logger.info(
            f"Format errors: {combined_results['format_wrong_num']}, rate={100.*combined_results['format_wrong_num']/len(llm_response):.2f}%"
        )
        logger.info(
            f"Hallucinations: {combined_results['hallucination_num']}, rate={100.*combined_results['hallucination_num']/combined_results['total_predict_action_num']:.2f}%"
        )

        logger.info("Precondition predicate type results:")
        print_precision_recall_f1(precond_predicate_type_res_dict)
        logger.info("Effect predicate type results:")
        print_precision_recall_f1(effect_predicate_type_res_dict)
        logger.info("Full predicate type results:")
        print_precision_recall_f1(full_predicate_type_res_dict)

        logger.info("Precondition action type results:")
        print_precision_recall_f1(precond_action_type_dict)
        logger.info("Effect action type results:")
        print_precision_recall_f1(effect_action_type_dict)
        logger.info("Full action type results:")
        print_precision_recall_f1(full_action_type_dict)

        logger.info("Success rates by task type:")
        print_success_rate(success_by_task_type_dict)

        # Prepare summary
        if dataset == "virtualhome":
            summary = {
                category: {
                    "precision": round(
                        100 * full_predicate_type_res_dict[category][3], 4
                    ),
                    "recall": round(100 * full_predicate_type_res_dict[category][4], 4),
                    "f1": round(100 * full_predicate_type_res_dict[category][5], 4),
                    "planner_success_rate": round(
                        100 * success_by_task_type_dict[category][2], 4
                    )
                    if category in success_by_task_type_dict
                    else 0,
                }
                for category in present_categories
            }
        elif dataset == "behavior":
            summary = {
                category: {
                    "precision": round(
                        100 * full_predicate_type_res_dict[category][3], 4
                    ),
                    "recall": round(100 * full_predicate_type_res_dict[category][4], 4),
                    "f1": round(100 * full_predicate_type_res_dict[category][5], 4),
                    "planner_success_rate": round(
                        100 * success_by_task_type_dict[category][2], 4
                    )
                    if category in success_by_task_type_dict
                    else 0,
                }
                for category in present_categories
            }
        summary["overall"] = {
            "precision": round(100 * full_predicate_type_res_dict["overall"][3], 4),
            "recall": round(100 * full_predicate_type_res_dict["overall"][4], 4),
            "f1": round(100 * full_predicate_type_res_dict["overall"][5], 4),
            "planner_success_rate": round(
                100 * success_by_task_type_dict["overall"][2], 4
            ),
        }

        # Save results
        all_results[model_name] = [summary, None]
        save_path = osp.join(output_dir, model_name)
        if not osp.exists(save_path):
            os.makedirs(save_path)
        with open(osp.join(save_path, "summary.json"), "w") as f:
            json.dump(summary, f, indent=4)
            logger.info(f"Evaluation results of {model_name} saved to {save_path}")

    return all_results


def evaluate_results_sequential(args):
    dataset = args.dataset
    output_dir = args.output_dir

    if dataset == "virtualhome":
        timeout = 100
    elif dataset == "behavior":
        timeout = 200

    resource_root = osp.join(args.resource_dir, dataset)
    llm_response_path = args.llm_response_path
    # indexing path
    id2action_path = osp.join(resource_root, "id2action.json")
    id2category_path = osp.join(resource_root, "id2category_2.json")
    id2task_path = osp.join(resource_root, "id2task.json")
    success_dict_path = osp.join(resource_root, "success_task.json")

    # evaluation path
    domain_pd_path = osp.join(resource_root, f"{dataset}_pd.pddl")
    gold_action_path = osp.join(resource_root, "gold_action.json")
    pred2category_path = osp.join(resource_root, "predicates_category.json")

    pddl_root = osp.join(resource_root, "pddl_files")
    pddl_problem_dir = osp.join(resource_root, "problem_pddl")
    os.makedirs(name=pddl_root, exist_ok=True)
    os.makedirs(pddl_problem_dir, exist_ok=True)

    # load indexing dict
    id2action = json.load(open(id2action_path, "r"))
    id2category = json.load(open(id2category_path, "r"))
    id2task = json.load(open(id2task_path, "r"))
    success_file_id = json.load(open(success_dict_path, "r"))
    pred2category = json.load(open(pred2category_path, "r"))

    categories_set = {
        "object_states",
        "object_affordance",
        "object_orientation",
        "spatial_relations",
        "non-spatial_relations",
        "object_tools",
    }
    action_set = set()
    for action_list in id2action.values():
        action_set.update(action_list)
    predicate_set = set()
    for predicate in pred2category.keys():
        predicate_set.add(predicate)

    # load evaluation dict
    gold_action_dict = json.load(open(gold_action_path, "r"))

    output_dir = args.output_dir
    if not osp.exists(output_dir):
        os.makedirs(output_dir)

    llm_response_path = osp.join(llm_response_path, dataset, "transition_modeling")
    logger.info(f"load llm response from {llm_response_path}")
    model_file = extract_model_names(llm_response_path)

    all_results = {}

    for model_name in model_file:
        llm_response_json = os.path.join(
            llm_response_path, f"{model_name}_outputs.json"
        )
        llm_response = json.load(open(llm_response_json, "r"))

        # logical score (precison, recall, f1)
        # 1. precond logical score based on type
        # 2. effect logical score based on type
        # 3. precond logical score per action (fig)
        # 4. effect logical score per action (fig)
        # potentially record score for each predicate

        precond_predicate_type_res_dict = {}
        effect_predicate_type_res_dict = {}
        full_predicate_type_res_dict = {}
        precond_action_type_dict = {}
        effect_action_type_dict = {}
        full_action_type_dict = {}

        precond_predicate_score_dict = {}
        effect_predicate_score_dict = {}
        full_predicate_score_dict = {}

        # 5. success rate by planner on task type
        success_by_task_type_dict = {}

        # sensitivity analysis
        # 6. action success rate by planner on task type (precond, effect) -- change all operators/precond/effect by predicted in task
        task_variate_control_by_type = {}  # all
        task_variate_control_precond_by_type = {}  # precond
        task_variate_control_effect_by_type = {}  # effect
        # 7. action success rate by planner for all action (precond, effect)
        action_variate_control = {}  # all

        for category_type in categories_set:
            # [success(TP), precond false positive fail(FP), missing fail(FN)]
            precond_predicate_type_res_dict[category_type] = [0, 0, 0]
            effect_predicate_type_res_dict[category_type] = [0, 0, 0]
            success_by_task_type_dict[category_type] = [0, 0]  # [success, total]
            task_variate_control_by_type[category_type] = {}
            task_variate_control_precond_by_type[category_type] = {}
            task_variate_control_effect_by_type[category_type] = {}

        # micro avg
        for action in action_set:
            # [success(TP), precond false positive fail(FP), missing fail(FN)]
            precond_action_type_dict[action] = [0, 0, 0]
            effect_action_type_dict[action] = [0, 0, 0]
            action_variate_control[action] = [0, 0]  # [success, total]


        for pred in predicate_set:
            precond_predicate_score_dict[pred] = [0, 0, 0]
            effect_predicate_score_dict[pred] = [0, 0, 0]

        planner = FD()
        total_num = 0
        format_wrong_num = 0
        hallucination_num = 0
        total_predict_action_num = 0

        logger.info("start evaluation")

        for output_dict in llm_response:
            file_id = output_dict["identifier"]
            if file_id not in success_file_id:
                logger.info(f"{file_id} not in success file id!")
                continue

            total_num += 1

            task_name = id2task[file_id]
            logger.info(f"task name is {task_name}")

            task_name = "_".join(task_name.split())
            if dataset == "virtualhome":
                task_problem_dir = os.path.join(pddl_problem_dir, task_name)
            elif dataset == "behavior":
                task_problem_dir = pddl_problem_dir
            problem_path = os.path.join(task_problem_dir, f"{file_id}.pddl")

            category_name_list = id2category[file_id]
            logger.info(f"category names are {category_name_list}")

            predicted_action = output_dict["llm_output"]
            # if llm output starts with ```json
            if predicted_action.startswith("```json"):
                predicted_action = predicted_action[7:]
                predicted_action = predicted_action.strip("```")
            predicted_action = predicted_action.strip().replace("\n", "")
            predicted_action = predicted_action.replace("'", '"')
            try:
                predicted_action = json.loads(predicted_action)
                predicted_action = predicted_action["output"]
            except Exception as e:
                pass
            # logger.info(predicted_action)

            try:
                predicted_action = extract_action_details(content=predicted_action)
            except Exception as e:
                format_wrong_num += 1
                logger.info(f"Error in extracting action details: {e}")
                logger.info(f"format wrong num is {format_wrong_num}")
                continue

            logger.info("GPT predicted action body:")
            if predicted_action is None or predicted_action == "":
                continue

            predicted_domain_path = os.path.join(pddl_root, f"predicted_{model_name}")
            gold_domain_path = os.path.join(pddl_root, f"gold_{model_name}")
            os.makedirs(predicted_domain_path, exist_ok=True)
            os.makedirs(gold_domain_path, exist_ok=True)

            gold_actions = {}
            gold_actions_name = id2action[file_id]
            for action_name in gold_actions_name:
                gold_actions[action_name] = gold_action_dict[action_name]

            # start eval
            for action_name, action_dict in predicted_action.items():
                total_predict_action_num += 1
                if action_name not in gold_actions_name:
                    hallucination_num += 1
                    continue

                gold_action = gold_actions[action_name]

                # print predicted action
                pred_str = ""
                pred_str += f":action {action_name}\n"
                pred_str += f'  :parameters {action_dict["action_parameters"]}\n'
                pred_str += f'  :preconditions {action_dict["action_preconditions"]}\n'
                pred_str += f'  :effects {action_dict["action_effects"]}\n'

                gold_str = ""
                gold_str += f":action {action_name}\n"
                gold_str += f'  :parameters {gold_action["action_parameters"]}\n'
                gold_str += f'  :preconditions {gold_action["action_preconditions"]}\n'
                gold_str += f'  :effects {gold_action["action_effects"]}\n'

                logger.info("Gold action:")
                logger.info(gold_str)
                logger.info("GPT predicted action")
                logger.info(pred_str)

                # logical score
                gold_action = gold_action_dict[action_name]

                # match preconditions and effects
                (
                    precond_similarity_score,
                    matched_precond,
                    unmatched_pred_precond,
                    unmatched_gold_precond,
                ) = calculate_logic_score(
                    action_dict["action_preconditions"],
                    gold_action["action_preconditions"],
                )
                (
                    effect_similarity_score,
                    matched_effect,
                    unmatched_pred_effect,
                    unmatched_gold_effect,
                ) = calculate_logic_score(
                    action_dict["action_effects"], gold_action["action_effects"]
                )

                # record precondition
                for pred in matched_precond:
                    if pred == "()":
                        continue
                    precond_predicate_type_res_dict[pred2category[pred]][0] += 1
                    precond_action_type_dict[action_name][0] += 1
                    precond_predicate_score_dict[pred][0] += 1
                logger.info(f"{unmatched_pred_precond=}")
                for pred in unmatched_pred_precond:
                    if pred == "()":
                        continue
                    if pred not in pred2category.keys():
                        continue
                    precond_predicate_type_res_dict[pred2category[pred]][1] += 1
                    precond_action_type_dict[action_name][1] += 1
                    precond_predicate_score_dict[pred][1] += 1
                for pred in unmatched_gold_precond:
                    if pred == "()":
                        continue
                    precond_predicate_type_res_dict[pred2category[pred]][2] += 1
                    precond_action_type_dict[action_name][2] += 1
                    precond_predicate_score_dict[pred][2] += 1

                # record effect
                for pred in matched_effect:
                    if pred == "()":
                        continue
                    effect_predicate_type_res_dict[pred2category[pred]][0] += 1
                    effect_action_type_dict[action_name][0] += 1
                    effect_predicate_score_dict[pred][0] += 1
                for pred in unmatched_pred_effect:
                    if pred == "()":
                        continue
                    if pred not in pred2category.keys():
                        continue
                    effect_predicate_type_res_dict[pred2category[pred]][1] += 1
                    effect_action_type_dict[action_name][1] += 1
                    effect_predicate_score_dict[pred][1] += 1
                for pred in unmatched_gold_effect:
                    if pred == "()":
                        continue
                    effect_predicate_type_res_dict[pred2category[pred]][2] += 1
                    effect_action_type_dict[action_name][2] += 1
                    effect_predicate_score_dict[pred][2] += 1

            predicted_action_copy = copy.deepcopy(predicted_action)
            # success rate by planner & sensitivity analysis
            # partial operator trials
            # category_name_list = id2category[file_id]

            # increase tot number for success rate
            for category_name in category_name_list:
                success_by_task_type_dict[category_name][1] += 1
                # increase tot number for sensitivity analysis
                for action in gold_actions_name:
                    if action not in task_variate_control_by_type[category_name].keys():
                        task_variate_control_by_type[category_name][action] = [0, 1]
                    else:
                        task_variate_control_by_type[category_name][action][1] += 1
                    if action not in task_variate_control_precond_by_type[category_name]:
                        task_variate_control_precond_by_type[category_name][action] = [0, 1]
                    else:
                        task_variate_control_precond_by_type[category_name][action][1] += 1
                    if action not in task_variate_control_effect_by_type[category_name]:
                        task_variate_control_effect_by_type[category_name][action] = [0, 1]
                    else:
                        task_variate_control_effect_by_type[category_name][action][1] += 1

            for action in gold_actions_name:
                action_variate_control[action][1] += 1

            # per action trial
            for action_name in predicted_action.keys():
                assert predicted_action_copy == predicted_action
                if action_name not in gold_actions_name:
                    logger.info(f"{action_name} not in gold! Hallucination!")
                    continue
                single_variate_action = {}
                gold_action_dict_copy = copy.deepcopy(gold_action_dict)
                for gd_action_name in gold_actions_name:
                    single_variate_action[gd_action_name] = copy.deepcopy(
                        gold_action_dict_copy[gd_action_name]
                    )
                single_variate_action[action_name] = copy.deepcopy(
                    predicted_action_copy[action_name]
                )
                # logger.info(f"{single_variate_action=}")
                domain_file_path = complete_pddl_domain(
                    single_variate_action,
                    gold_action_dict,
                    domain_pd_path,
                    file_id,
                    predicted_domain_path,
                    action_name_key=action_name,
                )
                try:
                    pddl_plan = planner.plan_from_pddl(
                        domain_file_path, problem_path, timeout=timeout
                    )
                    for category_name in category_name_list:
                        task_variate_control_by_type[category_name][action_name][0] += 1
                    action_variate_control[action_name][0] += 1
                    logger.info(f"Action test: task {file_id}'s {action_name} succeeded")
                except Exception as e:
                    logger.info(f"Action test: task {file_id}'s {action_name} failed")
                    logger.info(f"Test error: {e}")


            # all action trial
            domain_file_path = complete_pddl_domain(
                predicted_action,
                gold_action_dict,
                domain_pd_path,
                file_id,
                predicted_domain_path,
            )
            try:
                pddl_plan = planner.plan_from_pddl(
                    domain_file_path, problem_path, timeout=timeout
                )
                for category_name in category_name_list:
                    success_by_task_type_dict[category_name][0] += 1
                logger.info(f"Holistic test: task {file_id} succeeded")
            except Exception as e:
                logger.info(f"Holistic test: task {file_id} failed")
        
        # maintain an overall cnt for all categories for success_by_task_type_dict
        success_by_task_type_dict['overall'] = [0, 0]
        for category_name in category_name_list:
            success_by_task_type_dict['overall'][0] += success_by_task_type_dict[category_name][0]
            success_by_task_type_dict['overall'][1] += success_by_task_type_dict[category_name][1]

        # full is the sum of precond and effect
        for category_type in categories_set:
            full_predicate_type_res_dict[category_type] = [
                precond_predicate_type_res_dict[category_type][0]
                + effect_predicate_type_res_dict[category_type][0],
                precond_predicate_type_res_dict[category_type][1]
                + effect_predicate_type_res_dict[category_type][1],
                precond_predicate_type_res_dict[category_type][2]
                + effect_predicate_type_res_dict[category_type][2],
            ]
        
        # maintain an overall cnt for all categories
        full_predicate_type_res_dict['overall'] = [0, 0, 0]
        for category_type in categories_set:
            full_predicate_type_res_dict['overall'][0] += full_predicate_type_res_dict[category_type][0]
            full_predicate_type_res_dict['overall'][1] += full_predicate_type_res_dict[category_type][1]
            full_predicate_type_res_dict['overall'][2] += full_predicate_type_res_dict[category_type][2]

        # full is the sum of precond and effect
        for action in action_set:
            full_action_type_dict[action] = [
                precond_action_type_dict[action][0] + effect_action_type_dict[action][0],
                precond_action_type_dict[action][1] + effect_action_type_dict[action][1],
                precond_action_type_dict[action][2] + effect_action_type_dict[action][2],
            ]

        # full is the sum of precond and effect
        for pred in predicate_set:
            full_predicate_score_dict[pred] = [
                precond_predicate_score_dict[pred][0]
                + effect_predicate_score_dict[pred][0],
                precond_predicate_score_dict[pred][1]
                + effect_predicate_score_dict[pred][1],
                precond_predicate_score_dict[pred][2]
                + effect_predicate_score_dict[pred][2],
            ]

        # precond logical score based on type
        precond_predicate_type_res_dict = calculate_precision_recall_f1(
            precond_predicate_type_res_dict
        )

        # effect logical score based on type
        effect_predicate_type_res_dict = calculate_precision_recall_f1(
            effect_predicate_type_res_dict
        )

        full_predicate_type_res_dict = calculate_precision_recall_f1(
            full_predicate_type_res_dict
        )

        # precond logical score per action
        precond_action_type_dict = calculate_precision_recall_f1(precond_action_type_dict)

        # effect logical score per action
        effect_action_type_dict = calculate_precision_recall_f1(effect_action_type_dict)

        full_action_type_dict = calculate_precision_recall_f1(full_action_type_dict)

        # precondition predicate score per predicate
        precond_predicate_score_dict = calculate_precision_recall_f1(
            precond_predicate_score_dict
        )

        # effect predicate score per predicate
        effect_predicate_score_dict = calculate_precision_recall_f1(
            effect_predicate_score_dict
        )

        # full predicate score per predicate
        full_predicate_score_dict = calculate_precision_recall_f1(full_predicate_score_dict)

        logger.info(f"Format wrong num is {format_wrong_num}!!!")
        # print out precision recall f1
        logger.info("Precondition predicate type res dict:")
        print_precision_recall_f1(precond_predicate_type_res_dict)
        logger.info("Effect predicate type res dict:")
        print_precision_recall_f1(effect_predicate_type_res_dict)

        logger.info("Precondition action type dict:")
        print_precision_recall_f1(precond_action_type_dict)
        logger.info("Effect action type dict:")
        print_precision_recall_f1(effect_action_type_dict)
        logger.info("Full action type dict:")
        print_precision_recall_f1(full_action_type_dict)
        logger.info("Precondition predicate score dict:")
        print_precision_recall_f1(precond_predicate_score_dict)
        logger.info("Effect predicate score dict:")
        print_precision_recall_f1(effect_predicate_score_dict)
        logger.info("Full predicate score dict:")
        print_precision_recall_f1(full_predicate_score_dict)

        # post-process sensitivity analysis
        task_variate_control_by_type = calculate_success_rate_by_category(
            task_variate_control_by_type
        )
        task_variate_control_precond_by_type = calculate_success_rate_by_category(
            task_variate_control_precond_by_type
        )
        task_variate_control_effect_by_type = calculate_success_rate_by_category(
            task_variate_control_effect_by_type
        )

        logger.info("Task variate control by type:")
        print_success_rate_by_category(task_variate_control_by_type)
        logger.info("Task variate control precond by type:")
        print_success_rate_by_category(task_variate_control_precond_by_type)
        logger.info("Task variate control effect by type:")
        print_success_rate_by_category(task_variate_control_effect_by_type)
        logger.info("Action variate control:")
        logger.info(action_variate_control)

        # post-process success rate by planner on task type
        logger.info("\n")
        logger.info(f"{total_num=}")
        logger.info(f"{format_wrong_num=}, rate={100.*format_wrong_num/total_num:.2f}")
        logger.info(
            f"{hallucination_num=}, rate={100.*hallucination_num/total_predict_action_num:.2f}"
        )
        success_by_task_type_dict = calculate_success_rate(success_by_task_type_dict)
        logger.info("MODEL NAME!!! %s", model_name)
        logger.info("\n")
        logger.info("Success by task type dict:")
        print_success_rate(success_by_task_type_dict)
        logger.info("\n")
        logger.info("Full predicate type res dict:")
        print_precision_recall_f1(full_predicate_type_res_dict)

        for category in categories_set:
            if category not in success_by_task_type_dict:
                continue
            logger.info(
                f"ATTENTION {category}: {success_by_task_type_dict[category][0]} / {success_by_task_type_dict[category][1]}"
            )
            print(success_by_task_type_dict["overall"][0])
            print(success_by_task_type_dict["overall"][1])
            print(success_by_task_type_dict["overall"][2])

        if dataset == "virtualhome":
            summary = {
                "object_states": {
                    "precision": round(
                        100 * full_predicate_type_res_dict["object_states"][3], 4
                    ),
                    "recall": round(
                        100 * full_predicate_type_res_dict["object_states"][4], 4
                    ),
                    "f1": round(
                        100 * full_predicate_type_res_dict["object_states"][5], 4
                    ),
                    "planner_success_rate": round(
                        100 * success_by_task_type_dict["object_states"][2], 4
                    ),
                },
                "object_affordance": {
                    "precision": round(
                        100 * full_predicate_type_res_dict["object_affordance"][3], 4
                    ),
                    "recall": round(
                        100 * full_predicate_type_res_dict["object_affordance"][4], 4
                    ),
                    "f1": round(
                        100 * full_predicate_type_res_dict["object_affordance"][5], 4
                    ),
                    "planner_success_rate": round(
                        100 * success_by_task_type_dict["object_affordance"][2], 4
                    ),
                },
                "object_orientation": {
                    "precision": round(
                        100 * full_predicate_type_res_dict["object_orientation"][3], 4
                    ),
                    "recall": round(
                        100 * full_predicate_type_res_dict["object_orientation"][4], 4
                    ),
                    "f1": round(
                        100 * full_predicate_type_res_dict["object_orientation"][5], 4
                    ),
                    "planner_success_rate": round(
                        100 * success_by_task_type_dict["object_orientation"][2], 4
                    ),
                },
                "spatial_relations": {
                    "precision": round(
                        100 * full_predicate_type_res_dict["spatial_relations"][3], 4
                    ),
                    "recall": round(
                        100 * full_predicate_type_res_dict["spatial_relations"][4], 4
                    ),
                    "f1": round(
                        100 * full_predicate_type_res_dict["spatial_relations"][5], 4
                    ),
                    "planner_success_rate": round(
                        100 * success_by_task_type_dict["spatial_relations"][2], 4
                    ),
                },
                "non-spatial_relations": {
                    "precision": round(
                        100 * full_predicate_type_res_dict["non-spatial_relations"][3],
                        4,
                    ),
                    "recall": round(
                        100 * full_predicate_type_res_dict["non-spatial_relations"][4],
                        4,
                    ),
                    "f1": round(
                        100 * full_predicate_type_res_dict["non-spatial_relations"][5],
                        4,
                    ),
                    "planner_success_rate": round(
                        100 * success_by_task_type_dict["non-spatial_relations"][2], 4
                    ),
                },
                "overall": {
                    "precision": round(
                        100 * full_predicate_type_res_dict["overall"][3], 4
                    ),
                    "recall": round(
                        100 * full_predicate_type_res_dict["overall"][4], 4
                    ),
                    "f1": round(100 * full_predicate_type_res_dict["overall"][5], 4),
                    "planner_success_rate": round(
                        100 * success_by_task_type_dict["overall"][2], 4
                    ),
                },
            }
        elif dataset == "behavior":
            summary = {
                "object_states": {
                    "precision": round(
                        100 * full_predicate_type_res_dict["object_states"][3], 4
                    ),
                    "recall": round(
                        100 * full_predicate_type_res_dict["object_states"][4], 4
                    ),
                    "f1": round(
                        100 * full_predicate_type_res_dict["object_states"][5], 4
                    ),
                    "planner_success_rate": round(
                        100 * success_by_task_type_dict["object_states"][2], 4
                    ),
                },
                "spatial_relations": {
                    "precision": round(
                        100 * full_predicate_type_res_dict["spatial_relations"][3], 4
                    ),
                    "recall": round(
                        100 * full_predicate_type_res_dict["spatial_relations"][4], 4
                    ),
                    "f1": round(
                        100 * full_predicate_type_res_dict["spatial_relations"][5], 4
                    ),
                    "planner_success_rate": round(
                        100 * success_by_task_type_dict["spatial_relations"][2], 4
                    ),
                },
                "non-spatial_relations": {
                    "precision": round(
                        100 * full_predicate_type_res_dict["non-spatial_relations"][3],
                        4,
                    ),
                    "recall": round(
                        100 * full_predicate_type_res_dict["non-spatial_relations"][4],
                        4,
                    ),
                    "f1": round(
                        100 * full_predicate_type_res_dict["non-spatial_relations"][5],
                        4,
                    ),
                    "planner_success_rate": round(
                        100 * success_by_task_type_dict["non-spatial_relations"][2], 4
                    ),
                },
                "overall": {
                    "precision": round(
                        100 * full_predicate_type_res_dict["overall"][3], 4
                    ),
                    "recall": round(
                        100 * full_predicate_type_res_dict["overall"][4], 4
                    ),
                    "f1": round(100 * full_predicate_type_res_dict["overall"][5], 4),
                    "planner_success_rate": round(
                        100 * success_by_task_type_dict["overall"][2], 4
                    ),
                },
            }
        all_results[model_name] = [summary, None]
        save_path = osp.join(output_dir, model_name)
        if not osp.exists(save_path):
            os.makedirs(save_path)
        with open(osp.join(save_path, "summary.json"), "w") as f:
            json.dump(summary, f, indent=4)
            logger.info(f"Evaluate results of {model_name} saved to {save_path}")

    return all_results
