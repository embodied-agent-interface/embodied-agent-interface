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

Our metrics are broken down into 4 primary categories:

1. **Grammatical Errors**:
   - state_hallucination
   - object_hallucination
   - wrong_length

2. **Object States**:
   - Number of satisfied conditions (TP)
   - Number of unsatisfied conditions (FN)
   - Number of false positive conditions (FP)
   - Confusion matrix (Precision/Recall/F1 Score)

3. **Object Relations**:
      - Number of satisfied conditions (TP)
   - Number of unsatisfied conditions (FN)
   - Number of false positive conditions (FP)
   - Confusion matrix (Precision/Recall/F1 Score)

4. **Overall Performance**:
      - Number of satisfied conditions (TP)
   - Number of unsatisfied conditions (FN)
   - Number of false positive conditions (FP)
   - Confusion matrix (Precision/Recall/F1 Score)