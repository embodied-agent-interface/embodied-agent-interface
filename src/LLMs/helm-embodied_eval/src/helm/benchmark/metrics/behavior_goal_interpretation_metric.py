import json
from typing import List, Optional
import re
import yaml

from sklearn.metrics import f1_score
from sklearn.preprocessing import MultiLabelBinarizer

from helm.benchmark.adaptation.request_state import RequestState
from helm.benchmark.metrics.evaluate_instances_metric import EvaluateInstancesMetric
from helm.benchmark.metrics.evaluate_reference_metrics import normalize_text
from helm.benchmark.metrics.metric import MetricName
from helm.benchmark.metrics.statistic import Stat
from helm.benchmark.scenarios.scenario import Reference
from helm.common.request import GeneratedOutput
from helm.common.request import RequestResult



def evaluate_goals(predicted_goals, ground_truth_goals):
    """Evaluate predicted goals against ground truth goals."""
    # Flatten the predicted goals
    predicted_conditions = flatten_goals(predicted_goals)
    
    
    all_satisfied_conditions = []
    all_unsatisfied_conditions = []
    
    # check each goal in ground_truth_goals
    for key, value in ground_truth_goals.items():
        # if there is only one way to satisfy the goal
        if len(value) == 1:
            satisfied_conditions, unsatisfied_conditions = check_satisfaction(predicted_conditions, value[0])
        # if there are multiple ways to satisfy the goal, choose the one that satisfies the most number of conditions
        else:
            satisfied_nums = [len([cond for cond in option if cond in predicted_conditions]) for option in value]
            max_satisfied_option = value[satisfied_nums.index(max(satisfied_nums))]
            satisfied_conditions, unsatisfied_conditions = check_satisfaction(predicted_conditions, max_satisfied_option)
        
        all_satisfied_conditions.extend(satisfied_conditions)
        all_unsatisfied_conditions.extend(unsatisfied_conditions) 
    
    return compute_breakdown_metrics(all_satisfied_conditions, all_unsatisfied_conditions, predicted_conditions)
    

def evaluate_dataset(result_reference_list):
    all_satisfied_conditions = []
    all_unsatisfied_conditions = []
    all_predicted_conditions = []

    # model_results_evaluated = {}
    
    for tuple in result_reference_list:
        goal_conds = tuple["reference"]
        model_pred = tuple["llm_output"]
        eval_result = evaluate_goals(model_pred, goal_conds)
        
        all_satisfied_conditions.extend(eval_result['complete_metrics']['all_satisfied_conditions'])
        all_unsatisfied_conditions.extend(eval_result['complete_metrics']['all_unsatisfied_conditions'])
        all_predicted_conditions.extend(flatten_goals(model_pred))
        # model_results_evaluated[demo] = eval_result

    # sorted_model_results_evaluated  = {key: model_results_evaluated [key] for key in sorted(model_results_evaluated)}

    dataset_results_evaluated = compute_breakdown_metrics(all_satisfied_conditions, all_unsatisfied_conditions, all_predicted_conditions, keep_conditions=False)
    # node_state_results, edge_state_results = compute_metrics_by_state(all_satisfied_conditions, all_unsatisfied_conditions, all_predicted_conditions)
    
    return dataset_results_evaluated


def flatten_goals(goal_data):
    """Flatten goal data into a single list of conditions."""
    return [condition for goal_type in goal_data.values() for condition in goal_type]

def check_satisfaction(predicted_conditions, ground_truth_conditions):
    """check which of the conditions in the ground truth are satisfied by the predicted conditions."""
    satisfied_conditions = []
    unsatisfied_conditions = []
    for condition in ground_truth_conditions:
        if condition in predicted_conditions:
            satisfied_conditions.append(condition)
        else:
            unsatisfied_conditions.append(condition)
    return satisfied_conditions, unsatisfied_conditions


def is_node_condition(condition):
    """check of a condition is a node condition or an edge condition."""
    
    # first check based on the state
    try:
        for state in object_states["node_states"]:
            if is_state_condition(state, condition):
                return True
        for state in object_states["edge_states"]:
            if is_state_condition(state, condition):
                return False
        print("cannot check based on state", condition)
        assert(0 == 1)
            
    # if that does not work, check based on the length of the condition
    except:
        if condition[0] == "not":
            if len(condition[1]) == 2:
                return True
            elif len(condition[1]) == 3:
                return False
            else:
                return False
                # TODO will fix this later
                raise ValueError("Invalid condition", condition)
        else:
            if len(condition) == 2:
                return True
            elif len(condition) == 3:
                return False
            else:
                return False
                # TODO will fix this later
                raise ValueError("Invalid condition", condition)

def is_state_condition(state, condition):
    """check if the given condition is about the given state."""
    if condition[0] == 'not':
        return condition[1][0] == state.lower()
    else:
        return condition[0] == state.lower()



def compute_metrics(all_satisfied_conditions, all_unsatisfied_conditions, predicted_conditions, keep_conditions=True):
    
    # Compute evaluation metrics
    true_positives = len(all_satisfied_conditions)
    false_positives = len(predicted_conditions) - true_positives
    false_negatives = len(all_unsatisfied_conditions)
    accuracy = true_positives / len(predicted_conditions) if predicted_conditions else 0
    precision = true_positives / (true_positives + false_positives) if true_positives + false_positives > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if true_positives + false_negatives > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    
    if keep_conditions:
        return {
            # 'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'all_satisfied_conditions': all_satisfied_conditions,
            'all_unsatisfied_conditions': all_unsatisfied_conditions,
            'predicted_conditions': predicted_conditions
        }
    else:
        return {
            # 'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        }


def compute_breakdown_metrics(all_satisfied_conditions, all_unsatisfied_conditions, predicted_conditions, keep_conditions=True):
    """Compute metrics for node and edge conditions separately."""
    node_predicted_conditions = [condition for condition in predicted_conditions if is_node_condition(condition)]
    node_satisfied_conditions = [condition for condition in all_satisfied_conditions if is_node_condition(condition)]
    node_unsatisfied_conditions = [condition for condition in all_unsatisfied_conditions if is_node_condition(condition)]
    edge_predicted_conditions = [condition for condition in predicted_conditions if not is_node_condition(condition)]
    edge_satisfied_conditions = [condition for condition in all_satisfied_conditions if not is_node_condition(condition)]
    edge_unsatisfied_conditions = [condition for condition in all_unsatisfied_conditions if not is_node_condition(condition)]
    
    
    complete_metrics = compute_metrics(all_satisfied_conditions, all_unsatisfied_conditions, predicted_conditions, keep_conditions)
    node_metrics = compute_metrics(node_satisfied_conditions, node_unsatisfied_conditions, node_predicted_conditions, keep_conditions)
    edge_metrics = compute_metrics(edge_satisfied_conditions, edge_unsatisfied_conditions, edge_predicted_conditions, keep_conditions)
    
    return {
        'complete_metrics': complete_metrics,
        'node_metrics': node_metrics,
        'edge_metrics': edge_metrics
    }

def parse_json(raw_llm_output):
    
    # Replace single quotes with double quotes
    raw_llm_output = raw_llm_output.replace("'", '"')
    
    # Extract the substring between the first { and the first } after it
    match = re.search(r"{[^{}]*}", raw_llm_output, re.DOTALL)

    if match:
        result = match.group(0)

        # Print the final cleaned result
        try:
            parsed_result = json.loads(result)
            with open('intermediate_outputs/success.txt', 'a') as file:
                file.write(str(result)+"\n\n")
            return parsed_result
        except:
            print("Error parsing JSON-like content.")
            with open('intermediate_outputs/fail.txt', 'a') as file:
                file.write(str(result)+"\n\n")
            return None
    else:
        print("No valid JSON-like content found.")



class Behavior_Goal_Interpretation_Metric(EvaluateInstancesMetric):
    """
    Defines metrics for the Behavior_Goal_Interpretation scenario.
    """

    def __init__(self, delimiter: Optional[str] = None):
        self.delimiter = delimiter
        with open('intermediate_outputs/success.txt', 'w') as file:
                file.write(str(""))
        with open('intermediate_outputs/fail.txt', 'w') as file:
            file.write(str(""))

    def evaluate_instances(self, request_states: List[RequestState], eval_cache_path: str) -> List[Stat]:
        
        result_reference_list = []
        
        for request_state in request_states:
            goal_conds = request_state.instance.references[0].output.text['goal_conditions']
            raw_llm_output = request_state.result.completions[0].text + "}"
            
            # print("------------------------------------------------------------------")
            # print("type(request_state.result.completions):", type(request_state.result.completions))
            # print("len(request_state.result.completions):", len(request_state.result.completions))
            # print("type(request_state.result.completions[0]):", type(request_state.result.completions[0]))
            # print("dir(request_state.result.completions[0]):", dir(request_state.result.completions[0]))
            # print("request_state.result.completions[0].text + '}':", request_state.result.completions[0].text + "}")
            # print("------------------------------------------------------------------")
            
            
            # with open('intermediate_outputs/request_state.txt', 'w') as file:
            #     file.write(str(request_state))
            # with open('intermediate_outputs/goal_conds.txt', 'w') as file:
            #     file.write(str(goal_conds))
            # with open('intermediate_outputs/raw_llm_output.txt', 'w') as file:
            #     file.write(raw_llm_output)
            model_pred = parse_json(raw_llm_output)
            
            result_reference_list.append(
                {
                    "llm_output": model_pred,
                    "reference": goal_conds
                }
            )
            
        
        evaluation_results = evaluate_dataset(result_reference_list)
        
        # print("----------------------------------------------------------------------------------------")
        # print("evaluation_results:", evaluation_results)
        # print("----------------------------------------------------------------------------------------")
            
        precision = Stat(MetricName("precision"))
        precision.add(evaluation_results['complete_metrics']['precision'])

        recall = Stat(MetricName("recall"))
        recall.add(evaluation_results['complete_metrics']['recall'])
        
        f1_score = Stat(MetricName("f1_score"))
        f1_score.add(evaluation_results['complete_metrics']['f1_score'])
        
        node_f1_score = Stat(MetricName("node_f1_score"))
        node_f1_score.add(evaluation_results['node_metrics']['f1_score'])
        
        edge_f1_score = Stat(MetricName("edge_f1_score"))
        edge_f1_score.add(evaluation_results['edge_metrics']['f1_score'])
        
        stats = [precision, recall, f1_score, node_f1_score, edge_f1_score]
        
        return stats