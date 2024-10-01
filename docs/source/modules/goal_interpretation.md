# Goal Interpretation

## Description

**Goal Interpretation** aims to ground the natural language instruction to the environment representations of objects, states, relations, and actions. For example, the task instruction 

```python
"Use the rag to clean the trays, the bowl, and the refrigerator. When you are done, leave the rag next to the sink..."
```

can be grounded to specific objects with IDs, such as `fridge (ID: 97)`, `tray (ID: 1)`, `bowl (ID: 1)`, `rag (ID: 0)`, and `sink (ID: 82)`. Note that a simple natural language description can be grounded into a set of multiple goal conditions (object state and relation).


The goal interpretation module takes the state `**$s_0$**` and a natural language instruction `**$l_g$**` as input, and generates an LTL goal `**$\hat{g}_l$**` as a formal goal specification which a symbolic planner can conceivably take as input. In this paper, we only generate simple LTL goals formed by an ordered action sequence and a conjunction of propositions to be satisfied in the final state.


## Evaluation Details

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
