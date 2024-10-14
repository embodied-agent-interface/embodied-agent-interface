# Action Sequencing

## Description

The **action sequencing** module takes the task ⟨$s_0$, $g$⟩ as input, where:

- **$s_0$** represents the initial state of the environment.
- **$g$** is the task goal.

The module uses a transition model $\mathcal{M}$ specific to the simulator, which governs how the environment evolves based on actions. For more details on the transition model, refer to:

- `src/behavior_eval/evolving_graph/evolving_graph.py` for `Behavior`
- `src/virtualhome_eval/simulation/evolving_graph/environment.py` for `VirtualHome`

The module generates an action sequence $\bar{a} = \{a_i\}_{i=1}^{n}$, representing the actions required to move from the initial state toward achieving the task goal.

## Evaluation Details

### Evaluation Workflow

The evaluation of the action sequencing module involves two main components:

1. **Trajectory Evaluation**:
   - **Purpose**: To determine whether the generated action sequence $\bar{a}$ is executable in the simulator.
   - **Process**: Execute $\bar{a}$ to obtain the trajectory $T = ⟨\{s_i\}_{i=0}^{m}, \{a_i\}_{i=1}^{m}⟩$, e.g. `behavior_eval.evolving_graph.eval_evolving_graph_env.apply_action`.
   - **Outcome**: If an infeasible action occurs, execution may stop early. Execution failures are categorized into:
     - **Missing Steps**: Necessary actions that were omitted.
     - **Additional Steps**: Unnecessary actions that were included.
     - **Wrong Temporal Order**: Actions executed in an incorrect sequence.
     - **Affordance Errors**: Actions incompatible with the current state of objects (e.g., trying to "open" an object that cannot be opened).

2. **Goal Evaluation**:
   - **Purpose**: To assess if the task goal $g$ is satisfied after executing $\bar{a}$.
   - **Process**: Check for goal satisfaction, e.g. `behavior_eval.evolving_graph.evolving_graph.check_success`.
   - **Partial Goal Satisfaction Evaluation**:
     - Measures the percentage of subgoals in $g$ that are satisfied by $\bar{a}$.
     - **Process**:
       - Decompose $g$ into simple Linear Temporal Logic (LTL) goals $g_i$.
       - For each $g_i$:
         - Let $g_i = a₁ \overset{\text{then}}{\ldots} aₖ \textbf{~then~} (p₁ \land \ldots \land p_\ell)$.
         - Check if a subsequence in $\bar{a}$ matches $\{a_j\}_{j=1}^k$.
         - Evaluate the final state propositions $p_j$ in $s_m$.
       - Assign partial credits based on the number of propositions satisfied.
     - **Final Metric**: $\textit{PartialSucc}(\bar{a}, g) = \max_{g_i \in \mathcal{G}(g, \mathcal{U})} \textit{PartialSucc}(\bar{a}, g_i)$.

### Metrics

The evaluation metrics are divided into two categories:

1. **Trajectory Metrics**:
   - **Execution Success Rate**: The proportion of actions in $\bar{a}$ executed successfully without errors.
   - **Error Rates**:
     - **Parsing Errors**: Issues in interpreting the action sequence.
     - **Hallucination Errors**: Actions involving objects or states not present in the environment.
     - **Argument Errors**: Incorrect arguments provided for actions.
     - **Missing Steps**: Rate of necessary actions that were omitted.
     - **Additional Steps**: Rate of unnecessary actions included.
     - **Wrong Temporal Order**: Rate of actions executed in an incorrect sequence.
     - **Affordance Errors**: Rate of actions that cannot be performed due to object states.

2. **Goal Metrics**:
   - **Task Success Rate**: The proportion of tasks where the goal $g$ is fully satisfied after executing $\bar{a}$.
   - **Partial Goal Satisfaction Evaluation**:
        - **State Goal Satisfaction**: Success rate for satisfying state-based goals (e.g., object states).
        - **Relation Goal Satisfaction**: Success rate for satisfying relation-based goals (e.g., object relationships).
        - **Action Goal Satisfaction**: Success rate for achieving the specified action sequence.
        - **Total Goal Satisfaction**: Overall goal achievement rate, combining state, relation, and action goals.

### Output

The evaluation process produces several outputs:

- **Execution Information**:
  - Details for each action in $\bar{a}$, indicating whether it was executed successfully.
  - Error types encountered during execution (if any).
  - Step-by-step execution status.

- **Goal Satisfaction Results**:
  - Metrics indicating whether the goal was fully or partially satisfied.
  - Counts of total and satisfied predicates, including:
    - **Total Predicates**: Number of conditions evaluated.
    - **Satisfied Predicates**: Number of conditions that were satisfied.
    - Breakdown into edge and node predicates.

- **Overall Evaluation Metrics**:
  - **Goal Evaluation**:
    - **Task Success Rate**: Overall success rate for completing the task.
    - **State Goal Satisfaction**: Success rate for satisfying state-based goals.
    - **Relation Goal Satisfaction**: Success rate for satisfying relation-based goals.
    - **Action Goal Satisfaction**: Success rate for achieving the specified action sequence.
    - **Total Goal Satisfaction**: Combined success rate across all goal types.
  - **Trajectory Evaluation**:
    - **Execution Success Rate**: Overall success rate of the action sequence execution.
    - **Grammar Errors**: Rates of parsing, hallucination, and predicate argument number errors.
    - **Runtime Errors**: Rates of wrong order, missing step, affordance, and additional step errors.

### Example

**Task**: `assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37`

**Model**: `o1-preview`

**Transition Model ($\mathcal{M}$)**: `Behavior` simulator

**Initial States ($s_0$)**:

```python
[
    "['onfloor', 'basket_0', 'room_floor_living_room_0']",
    "['onfloor', 'basket_1', 'room_floor_living_room_0']",
    "['onfloor', 'basket_2', 'room_floor_living_room_0']",
    "['onfloor', 'basket_3', 'room_floor_living_room_0']",
    "['ontop', 'candle_0', 'breakfast_table_13']",
    "['ontop', 'candle_1', 'breakfast_table_13']",
    "['ontop', 'candle_2', 'breakfast_table_13']",
    "['ontop', 'candle_3', 'breakfast_table_13']",
    "['ontop', 'cookie_0', 'breakfast_table_13']",
    "['ontop', 'cookie_1', 'breakfast_table_13']",
    "['ontop', 'cookie_2', 'breakfast_table_13']",
    "['ontop', 'cookie_3', 'breakfast_table_13']",
    "['ontop', 'cheese_0', 'coffee_table_12']",
    "['ontop', 'cheese_1', 'coffee_table_12']",
    "['ontop', 'cheese_2', 'coffee_table_12']",
    "['ontop', 'cheese_3', 'coffee_table_12']",
    "['ontop', 'bow_0', 'coffee_table_12']",
    "['ontop', 'bow_1', 'coffee_table_12']",
    "['ontop', 'bow_2', 'coffee_table_12']",
    "['ontop', 'bow_3', 'coffee_table_12']",
    "['onfloor', 'agent.n.01_1', 'room_floor_living_room_0']"
]
```

**Goal ($g$)**:

```python
[
    "['forpairs', 'basket.n.01', '-', 'basket.n.01', 'candle.n.01', '-', 'candle.n.01', 'inside', 'candle.n.01', 'basket.n.01']",
    "['forpairs', 'basket.n.01', '-', 'basket.n.01', 'cheese.n.01', '-', 'cheese.n.01', 'inside', 'cheese.n.01', 'basket.n.01']",
    "['forpairs', 'basket.n.01', '-', 'basket.n.01', 'cookie.n.01', '-', 'cookie.n.01', 'inside', 'cookie.n.01', 'basket.n.01']",
    "['forpairs', 'basket.n.01', '-', 'basket.n.01', 'bow.n.08', '-', 'bow.n.08', 'inside', 'bow.n.08', 'basket.n.01']"
]
```

**Output**:

```python
[
    {"action": "LEFT_GRASP", "object": "candle_0"},
    {"action": "RIGHT_GRASP", "object": "cookie_0"},
    {"action": "LEFT_PLACE_INSIDE", "object": "basket_0"},
    {"action": "RIGHT_PLACE_INSIDE", "object": "basket_0"},
    {"action": "LEFT_GRASP", "object": "cheese_0"},
    {"action": "RIGHT_GRASP", "object": "bow_0"},
    {"action": "LEFT_PLACE_INSIDE", "object": "basket_0"},
    {"action": "RIGHT_PLACE_INSIDE", "object": "basket_0"},
    {"action": "LEFT_GRASP", "object": "candle_1"},
    {"action": "RIGHT_GRASP", "object": "cookie_1"},
    {"action": "LEFT_PLACE_INSIDE", "object": "basket_1"},
    {"action": "RIGHT_PLACE_INSIDE", "object": "basket_1"},
    {"action": "LEFT_GRASP", "object": "cheese_1"},
    {"action": "RIGHT_GRASP", "object": "bow_1"},
    {"action": "LEFT_PLACE_INSIDE", "object": "basket_1"},
    {"action": "RIGHT_PLACE_INSIDE", "object": "basket_1"},
    {"action": "LEFT_GRASP", "object": "candle_2"},
    {"action": "RIGHT_GRASP", "object": "cookie_2"},
    {"action": "LEFT_PLACE_INSIDE", "object": "basket_2"},
    {"action": "RIGHT_PLACE_INSIDE", "object": "basket_2"},
    {"action": "LEFT_GRASP", "object": "cheese_2"},
    {"action": "RIGHT_GRASP", "object": "bow_2"},
    {"action": "LEFT_PLACE_INSIDE", "object": "basket_2"},
    {"action": "RIGHT_PLACE_INSIDE", "object": "basket_2"},
    {"action": "LEFT_GRASP", "object": "candle_3"},
    {"action": "RIGHT_GRASP", "object": "cookie_3"},
    {"action": "LEFT_PLACE_INSIDE", "object": "basket_3"},
    {"action": "RIGHT_PLACE_INSIDE", "object": "basket_3"},
    {"action": "LEFT_GRASP", "object": "cheese_3"},
    {"action": "RIGHT_GRASP", "object": "bow_3"},
    {"action": "LEFT_PLACE_INSIDE", "object": "basket_3"},
    {"action": "RIGHT_PLACE_INSIDE", "object": "basket_3"}
]
```

**Results**:

```python
"llm_rst": {
    "error_type": {
        "parsing": null,            # No parsing errors occurred
        "hallucination": null,      # No hallucination errors occurred (no false information)
        "arguments": null,          # No argument errors occurred
        "execution_success": true   # Execution was successful
    },
    "goal_rst": {
        "all_goal_satisfied_ig": true,       # All goals were satisfied according to the internal graph (IG)
        "all_goal_satisfied_graph": true,    # All goals were satisfied according to the external goal graph
        "tot_predicates": 4.0,               # Total number of predicates (conditions) evaluated
        "tot_edge_predicates": 4.0,          # Total number of edge predicates (relationships between entities)
        "tot_node_predicates": 0.0,          # Total number of node predicates (properties of entities)
        "satisfied_predicates": 4.0,         # Number of predicates that were satisfied
        "satisfied_edge_predicates": 4.0,    # Number of satisfied edge predicates
        "satisfied_node_predicates": 0.0,    # Number of satisfied node predicates
        "pure_edge_predicates": 4,           # Number of pure edge predicates (without involving nodes)
        "pure_node_predicates": 0,           # Number of pure node predicates
        "mixed_predicates": 0,               # Number of mixed predicates (involving both edges and nodes)
        "satisfied_pure_edge_predicates": 4, # Number of satisfied pure edge predicates
        "satisfied_pure_node_predicates": 0, # Number of satisfied pure node predicates
        "satisfied_mixed_predicates": 0      # Number of satisfied mixed predicates
    },
    "execution_info": [
        {
            "action": "LEFT_GRASP",
            "object": "candle_0",
            "execution_success": True,
            "step": 0
        },
        {
            "action": "RIGHT_GRASP",
            "object": "cookie_0",
            "execution_success": True,
            "step": 1
        },
        {
            "action": "LEFT_PLACE_INSIDE",
            "object": "basket_0",
            "execution_success": True,
            "step": 2
        },
        {
            "action": "RIGHT_PLACE_INSIDE",
            "object": "basket_0",
            "execution_success": True,
            "step": 3
        },
        ...
        {
            "action": "RIGHT_PLACE_INSIDE",
            "object": "basket_3",
            "execution_success": True,
            "step": 31
        }
    ]
}
```

**Overall Results Across Tasks**

```python
{
    "goal_evaluation": {
        "task_success_rate": 0.81,    # Overall success rate for completing the task
        "state_goal": 0.895,          # Success rate for satisfying state-based goals
        "relation_goal": 0.844,       # Success rate for satisfying relation-based goals
        "action_goal": 0,             # Success rate for achieving the specified action sequence
        "total_goal": 0.8579          # Combined goal achievement rate
    },
    "trajectory_evaluation": {
        "execution_success_rate": 0.91,   # Overall success rate of action sequence execution
        "grammar_error": {
            "parsing": 0.0,               # No parsing errors
            "hallucination": 0.0,         # No hallucination errors
            "predicate_argument_number": 0.0  # No predicate argument number errors
        },
        "runtime_error": {
            "wrong_order": 0.0,           # No wrong order errors
            "missing_step": 0.06,         # 6% of sequences had missing steps
            "affordance": 0.02,           # 2% had affordance errors
            "additional_step": 0.03       # 3% had additional steps
        }
    }
}
```

## Usage

To evaluate the action sequencing module, use the following commands:

```bash
eai-eval --dataset virtualhome --eval-type action_sequencing --mode evaluate_results
eai-eval --dataset behavior --eval-type action_sequencing --mode evaluate_results
eai-eval --dataset virtualhome --eval-type action_sequencing --mode generate_prompts
eai-eval --dataset behavior --eval-type action_sequencing --mode generate_prompts
```
