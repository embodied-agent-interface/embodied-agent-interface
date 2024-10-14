# Transition Modeling

## Description

**Transition Modeling** evaluates LLMs' ability to predict the preconditions and effects of operators. In `EAgent`, evaluation of transition modeling incorporates two parts: `generate_prompts` and `evaluate_results`. With annotated data, running EAgent with the `generate_prompts` option will generate a JSON file of LLM prompts, asking LLM to predict the relevant operators for each task. You can provide your LLM with the prompts and generate outputs. After specifying `llm-response-path`, running EAgent with the `evaluate_results` option provides evaluation results in two perspectives: *logic matching score* and *planner success rate*.

## Evaluation Details

### Meta data

Some meta data are necessary for evaluation. The raw meta data is provided under `resources/{dataset}`.

- `id2action`: A map from `task_id` to a list of operators involved for the task. Only relevant operator names will be provided to LLM for prediction.
- `id2category_2`: A map from `task_id` to its categories. Each task is categorized into 2 out of 5 (VirtualHome) or 3 (BEHAVIOR) classes.
- `id2task`: A map from `task_id` to its task name.
- `gold_action`: Annotated ground truth PDDL operators.
- `predicates_category`: A map from operator name to a category.
- `{dataset}_pd.pddl`: PDDL domain file without operator definitions, only including predicates list.

### Evaluation Workflow

The evaluation process is primarily handled by the `evaluate_results` function. Key steps include:

1. **Data Loading**:
   - Load necessary meta data and configurations.
   - Load LLM responses from the specified path.

2. **Evaluation Loop**:
   - For each LLM response:
     - Extract predicted operator definitions.
     - Compare predicted preconditions and effects with ground truth.
     - Calculate logic matching scores.
     - Attempt to generate a plan using the predicted operators.

3. **Metric Calculation**:
   - Compute precision, recall, and F1 scores for preconditions and effects.
   - Calculate planning success rates.

4. **Results Aggregation**:
   - Aggregate results by predicate type, action type, and task type.

5. **Output Generation**:
   - Generate summary statistics and save results to JSON files.

### Metrics

Several key metrics are used in the evaluation:

1. **Logic Matching Score**:
   - Calculated for preconditions and effects separately.
   - Broken down by predicate type (e.g., object_states, spatial_relations).
   - Reported as precision, recall, and F1 score.
   - Variables: `precond_predicate_type_res_dict`, `effect_predicate_type_res_dict`, `full_predicate_type_res_dict`.

2. **Planning Success Rate**:
   - Measures the ability to generate a valid plan using predicted operators.
   - Calculated per task type.
   - Variable: `success_by_task_type_dict`.

3. **Action-specific Metrics**:
   - Logic matching scores calculated per action.
   - Variables: `precond_action_type_dict`, `effect_action_type_dict`, `full_action_type_dict`.

4. **Predicate-specific Metrics**:
   - Logic matching scores calculated per predicate.
   - Variables: `precond_predicate_score_dict`, `effect_predicate_score_dict`, `full_predicate_score_dict`.

5. **Sensitivity Analysis**:
   - Measures the impact of individual operator predictions on overall task success.
   - Variables: `task_variate_control_by_type`, `task_variate_control_precond_by_type`, `task_variate_control_effect_by_type`, `action_variate_control`.

### Output

The evaluation generates a summary JSON file for each model, containing:

- Precision, recall, and F1 scores for each predicate type.
- Planning success rates for each task type.
- Overall scores across all categories.

These results are saved in the specified output directory, providing a comprehensive view of the LLM's performance in transition modeling.

## Usage

To run the evaluation:

1. Ensure all LLM responses are in place.
2. Run the `eai-eval` command with appropriate arguments:

   ```bash
   eai-eval --dataset [virtualhome, behavior] --eval-type transition_modeling --mode evaluate_results
   ```

3. The function will process all LLM responses, calculate metrics, and save results to the specified output directory.

## Customization

The evaluation framework is designed to work with both VirtualHome and BEHAVIOR datasets. The code automatically adjusts based on the specified dataset, handling differences in categories and evaluation criteria. For adding new datasets or metrics, modify the relevant sections in the `evaluate_results` function and ensure appropriate meta data is provided.