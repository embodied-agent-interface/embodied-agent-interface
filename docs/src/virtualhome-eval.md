# Installation and Usage Guide for virtualhome-eval


## Install dependencies
```
pip install virtualhome_eval
```

## Usage
To run `virtualhome_eval`, use the following commands with arguments
```
from virtualhome_eval.agent_eval import agent_evaluation
agent_evaluation(mode=[generate_prompts, evaluate_results], eval_type=[goal_interpretation, action_sequence, transition_modeling], llm_response_path=[YOUR LLM OUTPUT DIR])
```

### Parameters
- `mode`: Specifies either generate prompts or evaluate results. Options are:
  - `generate_prompts` 
  - `evaluate_results`
- `eval_type`: Specifies the evaluation task type. Options are:
  - `goal_interpretation`
  - `action_sequence`
  - `subgoal_decomposition`
  - `transition_model`
- `llm_response_path`: The path of LLM output directory to be evaluated. It is `""` by default, using the existing outputs at directory `virtualhome_eval/llm_response/`. The function will evaluate all LLM outputs under the directory.
- `dataset`: The dataset type. Options:
  - `virtualhome`
  - `behavior`
- `output_dir`: The directory to store the output results. By default, it is at `output/` of current path.

### Example usage
1. To generate prompts for `goal_interpretation`:
```
agent_evaluation(mode='generate_prompts',  eval_type='goal_interpretation')
```
2. To evaluate LLM outputs for `goal_interpretation`:
```
results = agent_evaluation(mode='evaluate_results', eval_type='goal_interpretation')
```
3. To generate prompts for `action_sequence`:
```
agent_evaluation(mode='generate_prompts',  eval_type='action_sequence')
```
4. To evaluate LLM outputs for `action_sequence`:
```
results = agent_evaluation(mode='evaluate_results', eval_type='action_sequence')
```
5. To generate Virtualhome prompts for `transition_model`:
```
agent_evaluation(mode='generate_prompts',  eval_type='transition_model')
```
6. To evaluate LLM outputs on Virtualhome for `transition_model`:
```
results = agent_evaluation(mode='evaluate_results', eval_type='transition_model')
```
7. To generate prompts for `subgoal_decomposition`:
```
agent_evaluation(mode='generate_prompts',  eval_type='subgoal_decomposition')
```
8. To evaluate LLM outputs for `subgoal_decomposition`:
```
results = agent_evaluation(mode='evaluate_results', eval_type='subgoal_decomposition')