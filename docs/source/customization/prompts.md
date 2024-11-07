# Prompts

## Behavior

### Action Sequencing

#### Customize the Prompt Templates
- **Edit or Add Content**: Modify the prompt template in `behavior_eval.evaluation.action_sequencing.resources.prompt_templates.one_shot`.
- **Update Import Path**: In `behavior_eval.evaluation.action_sequencing.action_sequence_evaluator`, point the `prompt` path to your customized template.

#### Customize the Inputs to the Templates
- **Review Scene Information Collection**: Check how `init_state`, `target_state`, and `obj_list` are gathered in `action_sequence_evaluator.py`.
- **Adjust Input Logic**: Modify `action_sequence_evaluator.py` to change how inputs are generated or collected.

#### Useful Files for Reference
- **Scripts for Prompt Generation**: `behavior_eval.evaluation.action_sequencing.scripts.generate_prompts`
- **Prompt Template**: `behavior_eval.evaluation.action_sequencing.resources.prompt_templates.one_shot`
- **Prompt Generator**: `behavior_eval.evaluation.action_sequencing.action_sequence_evaluator`

---

### Goal Interpretation

*(No specific customization instructions provided)*

---

### Subgoal Decomposition

#### Customize the Prompt Templates
- **Edit or Add Content**: Modify the `system_prompt` and `target_task_info` in `behavior_eval.evaluation.subgoal_decomposition.resources.prompt_template.meta_prompt`.

#### Useful Files for Reference
- **Scripts for Prompt Generation**: `behavior_eval.evaluation.subgoal_decomposition.scripts.generate_prompts`
- **Prompt Template**: `behavior_eval.evaluation.subgoal_decomposition.resources.prompt_template.meta_prompt`
- **Prompt Generator**: `behavior_eval.evaluation.subgoal_decomposition.subgoal_prompts_utils` and `behavior_eval.evaluation.subgoal_decomposition.resources.prompt_template.meta_prompt`

---

### Transition Modeling

#### Customize the Prompt Templates
- **Edit or Add Content**: Modify the prompt template in `behavior_eval.evaluation.transition_modeling.resources.prompt_templates.prompts`.
- **Update Import Path**: In `behavior_eval.evaluation.transition_modeling.transition_modeling_evaluator`, point the `prompt` path to your custom template.

#### Useful Files for Reference
- **Scripts for Prompt Generation**: `behavior_eval.evaluation.transition_modeling.scripts.generate_prompts`
- **Prompt Template**: `behavior_eval.evaluation.transition_modeling.resources.prompt_templates.prompts`
- **Prompt Generator**: `behavior_eval.evaluation.transition_modeling.transition_modeling_evaluator`

---

## VirtualHome

For any module in VirtualHome, customize prompts by editing the corresponding files. Here, `{module}` could be `action_sequencing`, `goal_interpretation`, `subgoal_decomposition`, or `transition_modeling`.

#### Customize the Prompt Templates

To customize the prompt for a specific `{module}`:
- **Edit or Add Content**: Modify the prompt template in `virtualhome_eval.evaluation.{module}.prompts.one_shot.py`  
  *(For subgoal decomposition, use `virtualhome_eval.evaluation.{module}.prompts.meta_prompt`)*

#### Customize the Inputs to the Templates

To change the inputs passed to the template:
- **Edit Input Replacement Code**: In `virtualhome_eval.evaluation.{module}.scripts.generate_prompts.py`, update lines to replace the default input using `prompt = prompt.replace("<YOUR CUSTOM INPUT>", custom_input_variable)`.

#### Useful Files for Reference
- **Prompt Template**: `virtualhome_eval.evaluation.{module}.prompts.one_shot.py` (or `...meta_prompt.py` for subgoal decomposition)
- **Example Prompts**: `virtualhome_eval.evaluation.{module}.prompts.helm_prompts.json`
- **Scripts for Prompt Generation**: `virtualhome_eval.evaluation.{module}.scripts.generate_prompts.py`
- **Scripts for Module Evaluation**: `virtualhome_eval.evaluation.{module}.scripts.evaluate_results.py`

---
