import igibson.object_states as object_states
import json
import behavior_eval
import os
import re


object_states = {
    "node_states": [
        "Cooked",
        "Dusty",
        "Frozen",
        "Open",  
        "Sliced",
        "Soaked",
        "Stained",
        "Toggled_On"
    ],
    "edge_states": [
        "Inside",
        "NextTo",
        "OnFloor",
        "OnTop",
        "Touching",
        "Under"
    ]
}
class goal_interpretation_data():
    def __init__(self):
        self.demo_to_conds_path = f"{behavior_eval.goal_int_resources_path}/data/all_conditions.json"
        self.demo_to_objs_path = f"{behavior_eval.goal_int_resources_path}/data/all_objects.json"
        self.task_to_instructions_path = f"{behavior_eval.goal_int_resources_path}/data/instructions_by_activity_name.json"
        self.prompt_path = f"{behavior_eval.goal_int_resources_path}/prompts/behavior_goal_interpretation.txt"
        self.task_to_demo_path = f"{behavior_eval.goal_int_resources_path}/data/task_to_demo.json"
        self.demo_to_prompt_path = f"{behavior_eval.goal_int_resources_path}/data/llm_prompts.json"
        
        with open(self.demo_to_conds_path, 'r') as json_file:
            self.demo_to_conds = json.load(json_file)

        with open(self.demo_to_objs_path, 'r') as json_file:
            self.demo_to_objs = json.load(json_file)

        with open(self.demo_to_prompt_path, 'r') as json_file:
            self.demo_to_prompt = json.load(json_file)

        with open(self.task_to_instructions_path, 'r') as json_file:
            self.task_to_instructions = json.load(json_file)
            
        with open(self.task_to_demo_path, 'r') as json_file:
            self.task_to_demos = json.load(json_file)

        with open(behavior_eval.demo_name_path, 'r') as file:
            self.demo_names = json.load(file)
            


import os
import re

def extract_model_names(llm_response_dir):
    # List to store the extracted model names
    model_names = []

    # Get all files in the directory
    files = os.listdir(llm_response_dir)
    
    # Define regex patterns to match both file naming conventions
    pattern1 = re.compile(r"^(.*?)_outputs\.json$")
    pattern2 = re.compile(r"^(.*?)\.json$")
    
    for file in files:
        match1 = pattern1.match(file)
        match2 = pattern2.match(file)
        
        if match1:
            # Extract the model name from filenames like "model-name_outputs.json"
            model_names.append(match1.group(1))
        elif match2 and not file.endswith("_outputs.json"):
            # Extract the model name from filenames like "model-name.json"
            # but exclude files that end with "_outputs.json" to avoid duplication
            model_names.append(match2.group(1))

    return model_names

def is_node_condition(condition):
    """check of a condition is a node condition."""
    
    # first check based on the state
    try:
        for state in object_states["node_states"]:
            if is_state_condition(state, condition):
                return True
    # if that does not work, check based on the length of the condition
    except:
        if condition[0] == "not":
            if len(condition[1]) == 2:
                return True
        else:
            if len(condition) == 2:
                return True
    return False
            
def is_edge_condition(condition):
    """check of a condition is an edge condition."""
    
    # first check based on the state
    try:
        for state in object_states["edge_states"]:
            if is_state_condition(state, condition):
                return True

    # if that does not work, check based on the length of the condition
    except:
        if condition[0] == "not":
            if len(condition[1]) == 3:
                return True
        else:
            if len(condition) == 3:
                return True
    return False
    

def is_state_condition(state, condition):
    """check if the given condition is about the given state."""
    if condition[0] == 'not':
        return condition[1][0] == state.lower()
    else:
        return condition[0] == state.lower()
    

            

def compute_confusion_metrics(all_satisfied_conditions, all_unsatisfied_conditions, all_false_positive_conditions, predicted_conditions, keep_conditions=True):
    
    # Compute evaluation metrics
    true_positives = len(all_satisfied_conditions)
    false_positives = len(all_false_positive_conditions)
    false_negatives = len(all_unsatisfied_conditions)
    accuracy = true_positives / len(predicted_conditions) if predicted_conditions else 0
    precision = true_positives / (true_positives + false_positives) if true_positives + false_positives > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if true_positives + false_negatives > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    
    if keep_conditions:
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'all_satisfied_conditions': all_satisfied_conditions,
            'all_unsatisfied_conditions': all_unsatisfied_conditions,
            'predicted_conditions': predicted_conditions,
            "false_positive_conditions": all_false_positive_conditions
        }
    else:
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        }
        
# Grammatical Error Checks

def is_of_correct_length(condition):
    """check if a condition is of correct length."""
    if condition[0] == "not":
        if len(condition[1]) == 2 or len(condition[1]) == 3:
            return True
    else:
        if len(condition) == 2 or len(condition) == 3:
            return True
    # if the condition length is neither 2 nor 3, return False
    return False

def contains_valid_state(condition):
    """check if a condition contains valid state."""
    for state in object_states["node_states"]:
        if is_state_condition(state, condition):
            return True
    for state in object_states["edge_states"]:
        if is_state_condition(state, condition):
            return True
    # if the state is neither a valid node state nor a valid edge state, return False
    return False

def contains_valid_objects(condition, demo, DATA):
    """check if a conditions contains valid objects from the demo"""
    legal_objects = list(DATA.demo_to_objs[demo].keys())
    used_objects = []
    if condition[0] == "not":
        if len(condition[1]) == 2:
            used_objects.append(condition[1][1])
        elif len(condition[1]) == 3:
            used_objects.append(condition[1][1])
            used_objects.append(condition[1][2])
        else:
            assert not is_of_correct_length(condition)
            pass
    else:
        if len(condition) == 2:
            used_objects.append(condition[1])
        elif len(condition) == 3:
            used_objects.append(condition[1])
            used_objects.append(condition[2])
    
    for obj in used_objects:
        if obj not in legal_objects:
            return False
    return True



def dataset_error_analysis(all_satisfied_conditions: list, all_unsatisfied_conditions: list, all_false_positive_conditions: list, predicted_conditions: list, num_object_hallucinations: int):
    """Compute metrics for node and edge conditions separately."""
    
    grammatically_valid_predicted_conditions = []
    format_error = []
    state_hallucination = []
    for condition in predicted_conditions:
        if contains_valid_state(condition) and is_of_correct_length(condition):
            grammatically_valid_predicted_conditions.append(condition)
        if not is_of_correct_length(condition):
            format_error.append(condition)
        if not contains_valid_state(condition):
            state_hallucination.append(condition)
    
            
    node_predicted_conditions = [condition for condition in predicted_conditions if is_node_condition(condition)]
    node_satisfied_conditions = [condition for condition in all_satisfied_conditions if is_node_condition(condition)]
    node_unsatisfied_conditions = [condition for condition in all_unsatisfied_conditions if is_node_condition(condition)]
    node_false_positive_conditions = [condition for condition in all_false_positive_conditions if is_node_condition(condition)]
    edge_predicted_conditions = [condition for condition in predicted_conditions if is_edge_condition(condition)]
    edge_satisfied_conditions = [condition for condition in all_satisfied_conditions if is_edge_condition(condition)]
    edge_unsatisfied_conditions = [condition for condition in all_unsatisfied_conditions if is_edge_condition(condition)]
    edge_false_positive_conditions = [condition for condition in all_false_positive_conditions if is_edge_condition(condition)]
    
    overall_confusion = compute_confusion_metrics(all_satisfied_conditions, all_unsatisfied_conditions, all_false_positive_conditions, predicted_conditions, keep_conditions=False)
    state_confusion = compute_confusion_metrics(node_satisfied_conditions, node_unsatisfied_conditions, node_false_positive_conditions, node_predicted_conditions, keep_conditions=False)
    relation_goal_confusion = compute_confusion_metrics(edge_satisfied_conditions, edge_unsatisfied_conditions, edge_false_positive_conditions, edge_predicted_conditions, keep_conditions=False)
    
    return {
        'overall': 
            {
                "num_predicted_conditions": len(predicted_conditions),
                "num_GT_conditions": len(all_satisfied_conditions) + len(all_unsatisfied_conditions),
                "num_satisfied_conditions": len(all_satisfied_conditions),
                "num_unsatisfied_conditions": len(all_unsatisfied_conditions),
                "num_false_positive_conditions": len(all_false_positive_conditions),
                'overall_confusion_metrics': overall_confusion,
            },
        "state_goal":
            {
                "num_predicted_conditions": len(node_predicted_conditions),
                "num_GT_conditions": len(node_satisfied_conditions) + len(node_unsatisfied_conditions),
                "num_satisfied_conditions": len(node_satisfied_conditions),
                "num_unsatisfied_conditions": len(node_unsatisfied_conditions),
                "num_false_positive_conditions": len(node_false_positive_conditions),
                'state_goal_confusion_metrics': state_confusion,
            },
        "relation_goal":
            {
                "num_predicted_conditions": len(edge_predicted_conditions),
                "num_GT_conditions": len(edge_satisfied_conditions) + len(edge_unsatisfied_conditions),
                "num_satisfied_conditions": len(edge_satisfied_conditions),
                "num_unsatisfied_conditions": len(edge_unsatisfied_conditions),
                "num_false_positive_conditions": len(edge_false_positive_conditions),
                'relation_goal_confusion_metrics': relation_goal_confusion,
            },
        'grammatical_errors': 
            {
                "grammatically_valid_num": len(grammatically_valid_predicted_conditions),
                "grammatically_valid_rate": len(grammatically_valid_predicted_conditions) / len(predicted_conditions) if len(predicted_conditions) > 0 else 0,
                "format_error_num": len(format_error),
                "format_error_rate": len(format_error) / len(predicted_conditions) if len(predicted_conditions) > 0 else 0,
                "state_hallucination_num": len(state_hallucination),
                "state_hallucination_rate": len(state_hallucination) / len(predicted_conditions) if len(predicted_conditions) > 0 else 0,
                "object_hallucination_num": num_object_hallucinations,
                "object_hallucination_rate": num_object_hallucinations / len(predicted_conditions) if len(predicted_conditions) > 0 else 0,
            },
    }




def per_demo_error_analysis(demo, all_satisfied_conditions, all_unsatisfied_conditions, all_false_positive_conditions, predicted_conditions, DATA):
    """Compute metrics for node and edge conditions separately."""
    
    grammatically_valid_predicted_conditions = []
    format_error = []
    state_hallucination = []
    object_hallucination = []
    for condition in predicted_conditions:
        if contains_valid_state(condition) and is_of_correct_length(condition) and contains_valid_objects(condition, demo, DATA):
            grammatically_valid_predicted_conditions.append(condition)
        if not is_of_correct_length(condition):
            format_error.append(condition)
        if not contains_valid_state(condition):
            state_hallucination.append(condition)
        if not contains_valid_objects(condition, demo, DATA):
            object_hallucination.append(condition)
            
    
            
    node_predicted_conditions = [condition for condition in predicted_conditions if is_node_condition(condition)]
    node_satisfied_conditions = [condition for condition in all_satisfied_conditions if is_node_condition(condition)]
    node_unsatisfied_conditions = [condition for condition in all_unsatisfied_conditions if is_node_condition(condition)]
    node_false_positive_conditions = [condition for condition in all_false_positive_conditions if is_node_condition(condition)]
    edge_predicted_conditions = [condition for condition in predicted_conditions if is_edge_condition(condition)]
    edge_satisfied_conditions = [condition for condition in all_satisfied_conditions if is_edge_condition(condition)]
    edge_unsatisfied_conditions = [condition for condition in all_unsatisfied_conditions if is_edge_condition(condition)]
    edge_false_positive_conditions = [condition for condition in all_false_positive_conditions if is_edge_condition(condition)]
    
    overall_confusion = compute_confusion_metrics(all_satisfied_conditions, all_unsatisfied_conditions, all_false_positive_conditions, predicted_conditions, keep_conditions=True)
    state_confusion = compute_confusion_metrics(node_satisfied_conditions, node_unsatisfied_conditions, node_false_positive_conditions, node_predicted_conditions, keep_conditions=True)
    relation_goal_confusion = compute_confusion_metrics(edge_satisfied_conditions, edge_unsatisfied_conditions, edge_false_positive_conditions, edge_predicted_conditions, keep_conditions=True)
    
    return {
        'overall': 
            {
                "num_predicted_conditions": len(predicted_conditions),
                "num_GT_conditions": len(all_satisfied_conditions) + len(all_unsatisfied_conditions),
                "num_satisfied_conditions": len(all_satisfied_conditions),
                "num_unsatisfied_conditions": len(all_unsatisfied_conditions),
                "num_false_positive_conditions": len(all_false_positive_conditions),
                'overall_confusion_metrics': overall_confusion,
            },
        "state_goal":
            {
                "num_predicted_conditions": len(node_predicted_conditions),
                "num_GT_conditions": len(node_satisfied_conditions) + len(node_unsatisfied_conditions),
                "num_satisfied_conditions": len(node_satisfied_conditions),
                "num_unsatisfied_conditions": len(node_unsatisfied_conditions),
                "num_false_positive_conditions": len(node_false_positive_conditions),
                'state_goal_confusion_metrics': state_confusion,
            },
        "relation_goal":
            {
                "num_predicted_conditions": len(edge_predicted_conditions),
                "num_GT_conditions": len(edge_satisfied_conditions) + len(edge_unsatisfied_conditions),
                "num_satisfied_conditions": len(edge_satisfied_conditions),
                "num_unsatisfied_conditions": len(edge_unsatisfied_conditions),
                "num_false_positive_conditions": len(edge_false_positive_conditions),
                'relation_goal_confusion_metrics': relation_goal_confusion,
            },
        'grammatical_errors': 
            {
                "grammatically_valid_num": len(grammatically_valid_predicted_conditions),
                "grammatically_valid_rate": len(grammatically_valid_predicted_conditions) / len(predicted_conditions) if len(predicted_conditions) > 0 else 0,
                "format_error_num": len(format_error),
                "format_error_rate": len(format_error) / len(predicted_conditions) if len(predicted_conditions) > 0 else 0,
                "state_hallucination_num": len(state_hallucination),
                "state_hallucination_rate": len(state_hallucination) / len(predicted_conditions) if len(predicted_conditions) > 0 else 0,
                "object_hallucination_num": len(object_hallucination),
                "object_hallucination_rate": len(object_hallucination) / len(predicted_conditions) if len(predicted_conditions) > 0 else 0,
            },
    }
    


# Evaluate goals per demo

def evaluate_goals(predicted_goals, ground_truth_goals):
    """This function is in charge of figuring out the satisfied, unsatisfied, and false positive conditions"""
    # Flatten the predicted goals
    flattened_predicted_conditions = flatten_goals(predicted_goals)
    
    all_satisfied_conditions = []
    all_unsatisfied_conditions = []
    
    # check each goal in ground_truth_goals
    for key, value in ground_truth_goals.items():
        # if there is only one way to satisfy the goal
        if len(value) == 1:
            satisfied_conditions, unsatisfied_conditions = check_satisfaction(flattened_predicted_conditions, value[0])
        # if there are multiple ways to satisfy the goal, choose the one that satisfies the most number of conditions
        else:
            satisfied_nums = [len([cond for cond in option if cond in flattened_predicted_conditions]) for option in value]
            max_satisfied_option = value[satisfied_nums.index(max(satisfied_nums))]
            satisfied_conditions, unsatisfied_conditions= check_satisfaction(flattened_predicted_conditions, max_satisfied_option)
        
        all_satisfied_conditions.extend(satisfied_conditions)
        all_unsatisfied_conditions.extend(unsatisfied_conditions) 
    
    all_false_positive_conditions = [condition for condition in flattened_predicted_conditions if condition not in all_satisfied_conditions]
    
    return all_satisfied_conditions, all_unsatisfied_conditions, all_false_positive_conditions, flattened_predicted_conditions


# Basic Helper Methods

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



# define the evaluate dataset function
def evaluate_dataset(result_reference_list, DATA):
    all_satisfied_conditions = []
    all_unsatisfied_conditions = []
    all_predicted_conditions = []
    all_false_positive_conditions = []
    
    # because it is not possible to check illegal objects for each condition without demo name
    num_object_hallucination = 0

    # this is to store results for each individual demo
    model_results_evaluated = {}
    
    for tuple in result_reference_list:
        demo = tuple["identifier"]
        goal_conds = tuple["reference"]
        model_pred = tuple["llm_output"]
        
        satisfied_conditions, unsatisfied_conditions, false_positive_conditions, flattened_predicted_conditions = evaluate_goals(model_pred, goal_conds)
        model_results_evaluated[demo] = per_demo_error_analysis(demo, satisfied_conditions, unsatisfied_conditions, false_positive_conditions, flattened_predicted_conditions, DATA)
        num_object_hallucination += model_results_evaluated[demo]["grammatical_errors"]["object_hallucination_num"]
        
        all_satisfied_conditions.extend(satisfied_conditions)
        all_unsatisfied_conditions.extend(unsatisfied_conditions)
        all_false_positive_conditions.extend(false_positive_conditions)
        all_predicted_conditions.extend(flattened_predicted_conditions)
        
        
    # save results for each individual demo
    sorted_model_results_evaluated  = {key: model_results_evaluated [key] for key in sorted(model_results_evaluated)}
    

    # this is to obtain error analysis results for the complete dataset
    dataset_results_evaluated = dataset_error_analysis(all_satisfied_conditions, all_unsatisfied_conditions, all_false_positive_conditions, all_predicted_conditions, num_object_hallucination)
    
    return dataset_results_evaluated, sorted_model_results_evaluated 




def parse_json(raw_llm_output, model_name):
    '''
    This function takes in the raw output from an LLM model and parses it into JSON format.
    
    ----------------------------Required Inputs----------------------------
    raw_llm_output (str): the raw output from the LLM model
    model_name (str): the name of the LLM model
    -----------------------------------------------------------------------
    
    ----------------------------Produced Outputs----------------------------
    parsed_output (dict): the parsed output in JSON format
    error_message (str): an error message if the raw output could not be parsed
    ------------------------------------------------------------------------
    
    '''
    # Replace single quotes with double quotes
    raw_llm_output = raw_llm_output.lower().replace("'", '"').replace("toggledon", "toggled_on")
    
    # Extract the substring between the first { and the first } after it
    match = re.search(r"{[^{}]*}", raw_llm_output, re.DOTALL)

    if match:
        result = match.group(0)

        # Print the final cleaned result
        try:
            parsed_result = json.loads(result)
            return parsed_result, None
        except:
            error_message = f"{model_name} produced valid JSON-like content but did not follow the designated format. This example will have score 0."
    else:
        error_message = f"{model_name} did not produce valid JSON-like content. This example will have score 0."
    
    # For either error case, treat as if model predicted nothing
    return {"node goals": [], "edge goals": []}, error_message






def evaluate_results(llm_response_dir, result_dir):
    '''
    This script is used to evaluate performance of the 15 LLMs in the Embodied Agents Eval Paper.
    
    ----------------------------Required Inputs----------------------------
    base prompt to be modified (prompt_path)
    relevant objects (with all possible states) (demo_to_objs_path)
    initial and goal conditions (demo_to_conds_path)
    task instructions (task_to_instructions_path)
    list of demo names (demo_names_path)
    mapping from task name to demo name (task_to_demo_path)
    -----------------------------------------------------------------------
    
    ----------------------------Produced Outputs----------------------------
    error analysis for all 15 models ({model_name}_outputs.json)
    parsing error analysis for all 15 models ({model_name}_non_parsable_outputs.json)
    ------------------------------------------------------------------------
    
    '''
        
        
    DATA = goal_interpretation_data()
    DATA.all_models = extract_model_names(llm_response_dir)

    ALL_RESULTS = {}

    for model_name in DATA.all_models:
        
        # save_path = f"{llm_response_dir}/{model_name}_outputs.json"
        try:
            save_path = [i for i in os.listdir(llm_response_dir) if model_name in i][0]
            save_path=os.path.join(llm_response_dir, save_path)
            assert save_path.endswith(".json")
        except:
            print(f"Error: {model_name} does not have a corresponding json output file in {llm_response_dir}")
            exit(1)
        
        with open(save_path, 'r') as json_file:
            raw_llm_outputs = json.load(json_file)

        llm_results_list = {}
        error_cases = []

        for item in raw_llm_outputs:
            
            # parse the raw llm output and save it to the llm_results_list
            parsed_output, error_message = parse_json(item["llm_output"], model_name)
            llm_results_list[item["identifier"]] = parsed_output
            
            # if error message is not None, save the error case
            if error_message:
                error_cases.append({
                    "identifier": item["identifier"],
                    "output": item["llm_output"],
                    "error_message": error_message
                })
        
        if error_cases != []:
            parsing_errors_save_path = f"{result_dir}/log/parsing_errors/{model_name}_non_parsable_outputs.json"
            os.makedirs(os.path.dirname(parsing_errors_save_path), exist_ok=True)
            with open(parsing_errors_save_path, "w") as file:
                    json.dump(error_cases, file, indent=4)
                    
            # print(f"\n{model_name} made one or more format errors in its raw response, error cases and details are saved to {parsing_errors_save_path} \n")

        ALL_RESULTS[model_name] = llm_results_list

    
    ALL_METRICS = {}

    for model_name in DATA.all_models:
        model_results = ALL_RESULTS[model_name]
        
        result_reference_list = []
        for demo in DATA.demo_names:
            goal_conds = DATA.demo_to_conds[demo]['goal_conditions']
            model_pred = model_results[demo]
            result_reference_list.append(
                {   
                    "identifier": demo,
                    "llm_output": model_pred,
                    "reference": goal_conds,
                }
            )    
        
        
        ALL_METRICS[model_name], sorted_model_results_evaluated = evaluate_dataset(result_reference_list, DATA)
        
        performance_scores_save_path = f"{result_dir}/summary/{model_name}_performance_scores.json"
        os.makedirs(os.path.dirname(performance_scores_save_path), exist_ok=True)
        with open(performance_scores_save_path, 'w') as json_file:
            json.dump(ALL_METRICS[model_name], json_file, indent=4)
        
        
        error_analysis_save_path = f"{result_dir}/log/detailed_analyses/{model_name}_detailed_analysis.json"
        os.makedirs(os.path.dirname(error_analysis_save_path), exist_ok=True)
        with open(error_analysis_save_path, 'w') as json_file:
            json.dump(sorted_model_results_evaluated, json_file, indent=4)
    
    print("\n--------------------------------------------------------------------------------------")
    print(f"* If LMs have format issues, see details -> {result_dir}/log/parsing_errors/\n")
    print(f"* Detailed sample error analyses -> {result_dir}/log/detailed_analyses/\n")
    print(f"* Final model performance scores -> {result_dir}/summary/")
    print("--------------------------------------------------------------------------------------")
    print(f"Success! All models have been evaluated.")
