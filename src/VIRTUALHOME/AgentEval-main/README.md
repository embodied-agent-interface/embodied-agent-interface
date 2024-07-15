# Installation and Usage Guide for virtualhome-eval


## Install dependencies
```
pip install pddlgym
```

## Usage
To run `virtualhome_eval`, use the following commands with arguments
```
python -m virtualhome_eval.agent_eval --mode [generate_prompts, evaluate_results] --eval_type [goal_interpretation, action_sequence, transition_modeling] --model_name [YOUR MODEL NAME]  > [YOUR LOG PATH] 2>&1
```
### Parameters
- `mode`: Specifies either generate prompts or evaluate results. Options are:
  - `generate_prompts` 
  - `evaluate_results`
- `eval_type`: Specifies the evaluation task type. Options are:
  - `goal_interpretation`
  - `action_sequence`
  - `subgoal_decomposition`
  - `transition_modeling`
- `model_name`: Name of LLM to be evaluated, served as an identifier.
- `llm_response_path`: The path of LLM output to be evaluated. It is `""` by default, using the existing outputs at directory `virtualhome_eval/llm_response/`. 
- `dataset`: The dataset type. Options:
  - `virtualhome`
  - `behavior`
- `output_dir`: The directory to store the output results. By default, it is at `virtualhome_eval/output/`

### Example usage
1. To generate prompts for `goal_interpretation`:
```
python -m virtualhome_eval.agent_eval --mode generate_prompts --eval_type goal_interpretation > goal_eval_vh_prompt.log 2>&1
```
2. To evaluate LLM outputs for `goal_interpretation`:
```
python -m virtualhome_eval.agent_eval --mode evaluate_results --eval_type goal_interpretation --model_name gpt-4o-2024-05-13 > goal_eval_vh_eval.log 2>&1
```
3. To generate prompts for `action_sequence`:
```
python -m virtualhome_eval.agent_eval --mode generate_prompts --eval_type action_sequence > action_eval_vh_prompt.log 2>&1
```
4. To evaluate LLM outputs for `action_sequence`:
```
python -m virtualhome_eval.agent_eval --mode evaluate_results --eval_type action_sequence --model_name gpt-4o-2024-05-13 > action_eval_vh_eval.log 2>&1
```
5. To generate Virtualhome prompts for `transition_modeling`:
```
python -m virtualhome_eval.agent_eval --mode generate_prompts --eval_type transition_model --dataset virtualhome > transition_vh_prompt.log 2>&1
```
6. To evaluate LLM outputs on BEHAVIOR for `transition_modeling`:
```
python -m virtualhome_eval.agent_eval --mode evaluate_results --eval_type transition_model --model_name gpt-4o-2024-05-13 --dataset behavior  > transition_bh_eval.log 2>&1
```