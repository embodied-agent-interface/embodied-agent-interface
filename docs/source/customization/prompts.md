# Prompts

## Behavior

### Action Sequencing

You can customize the prompts for action sequencing in two ways: by modifying the prompt templates or by changing the inputs to the templates. Follow the steps below depending on your needs:

**Modify the Prompt Templates**

If you want to modify the prompt templates only:
1. Create your custom template by editing or adding new content to: `behavior_eval.evaluation.action_sequencing.resources.prompt_templates.one_shot`
   
2. Once your new template is ready, update the importing path for the `prompt` in the `behavior_eval.evaluation.action_sequencing` to point to your custom template. 

**Change the Inputs to the Template**

If you also want to change the inputs passed to the template:
1. Review how the scene information (`init_state`, `target_state`, and `obj_list`) is collected in the `action_sequence_evaluator.py` file. These inputs are essential for generating prompts and are gathered based on the current state of the scene.

2. Make adjustments to how these inputs are collected or generated. You can modify the logic in `action_sequence_evaluator.py` to use new input data or alter how the existing information is gathered.

**Useful Files for Reference:**

- **Scripts for prompt generation:**
  - `behavior_eval.evaluation.action_sequencing.scripts.generate_prompts`
  
- **Prompt template:**
  - `behavior_eval.evaluation.action_sequencing.resources.prompt_templates.one_shot`
  
- **Prompt generator:**
  - `behavior_eval.evaluation.action_sequencing.action_sequence_evaluator`

**Example Prompts:**
You can find example prompts used for action sequencing evaluation in:
- `behavior_eval.evaluation.action_sequencing.resources.prompts.helm_prompts`


### Goal Interpretation

### Subgoal Decomposition

To update subgoal decomposition prompt part, you can modify the file `behavior_eval.evaluation.subgoal_decomposition.resources.prompt_template.meta_prompt`, specifically `system_prompt` and `target_task_info` variables.

**Useful Files for Reference:**

- **Scripts for prompt generation:**
  - `behavior_eval.evaluation.subgoal_decomposition.scripts.generate_prompts`
- **Prompt template:**
  - `behavior_eval.evaluation.subgoal_decomposition.resources.prompt_template.meta_prompt`
- **Prompt generator:**
  - `behavior_eval.evaluation.subgoal_decomposition.subgoal_prompts_utils`

### Transition Modeling

## VirtualHome

For any of the four modules in VirtualHome, you can customize the prompt by editing the corresponding files. Here, `{module}` should be one of [`action_sequencing`, `goal_interpretation`, `subgoal_decomposition`, `transition_modeling`]

### Modify the Prompt Templates

You can customize the prompt for {module} by modifying the prompt template. Create your custom template by editing or adding new content to: `virtualhome_eval.evaluation.{module}.prompts.one_shot.py` with your customized input.

### Change the Inputs to the Template

You can change the inputs passed to the template. Go to `virtualhome_eval.evaluation.{module}.scripts.generate_prompts.py` and change lines `prompt = prompt.replace("<YOUR CUSTOM INPUT>", custom_input_variable)`

### Useful Files for Reference:
- **Prompt template:**
  - `virtualhome_eval.evaluation.{module}.prompts.one_shot.py`

- **Example Prompts:**
  - `virtualhome_eval.evaluation.{module}.prompts.helm_prompts.json`
  
- **Scripts for prompt generation:**
  - `virtualhome_eval.evaluation.{module}.scripts.generate_prompts.py`

- **Scripts for module evaluation:**
  - `virtualhome_eval.evaluation.{module}.scripts.evaluate_results.py`



