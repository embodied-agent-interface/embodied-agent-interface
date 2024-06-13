# Embodied Agent Interface (eAgent): Benchmarking LLMs for Embodied Decision Making
 
<h2 align="center">  Embodied Agent Interface (EAgent): Benchmarking LLMs for Embodied Decision Making </h2>

<p align="center">
    <a href="https://limanling.github.io/">Manling Li</a>, <a href="https://www.linkedin.com/in/shiyu-zhao-1124a0266/">Shiyu Zhao</a>, <a href="https://github.com/QinengWang-Aiden">Qineng Wang</a>, <a href="https://jameskrw.github.io/">Kangrui Wang</a>, <a href="https://bryanzhou008.github.io/">Yu Zhou</a>, <a href="https://example.com/sanjana-srivastava">Sanjana Srivastava</a>, <a href="https://example.com/cem-gokmen">Cem Gokmen</a>, <a href="https://example.com/tony-lee">Tony Lee</a>, <a href="https://sites.google.com/site/lieranli/">Li Erran Li</a>, <a href="https://example.com/ruohan-zhang">Ruohan Zhang</a>, <a href="https://example.com/weiyu-liu">Weiyu Liu</a>, <a href="https://cs.stanford.edu/~pliang/">Percy Liang</a>, <a href="https://profiles.stanford.edu/fei-fei-li">Li Fei-Fei</a>, <a href="https://jiayuanm.com/">Jiayuan Mao</a>, <a href="https://jiajunwu.com/">Jiajun Wu</a>
</p>
<p align="center"> Stanford Vision and Learning Lab, Stanford University </p>

<!-- :globe_with_meridians: [Webpage](https://egoschema.github.io/)  | :book: [Paper](https://arxiv.org/abs/2308.09126)  | :movie_camera: [Teaser Video](https://youtu.be/_VVoiSzb5E4)  | :microphone: [4-min Podcast](https://www.podbean.com/media/share/pb-sj7gk-148d8bc?)  |  :speaking_head: [Overview Talk Video]() | :bar_chart: [Statistics Dashboard](https://public.tableau.com/views/EgoSchema/EGOSchema?:showVizHome=no)| :crossed_swords: [Kaggle](https://www.kaggle.com/competitions/egoschema-public/overview) -->

<br/>

<p align="center">
<a href="https://cs.stanford.edu/~manlingl/projects/embodied-eval" target="_blank"><img src="./EAgent.png" alt="EAgent" width="80%" height="80%" border="10" /></a>
</p>
<!-- <p align="center" style="color: #87CEEB"> Click for the youtube teaser video </p> -->

## :dizzy: Dataset Highlights 

:exclamation: Standardization of goal specifications.<br/><br/>
:exclamation: Standardization of modules and interfaces.<br/><br/>
:exclamation: Broad coverage of evaluation and fine-grained metrics.  <br/><br/>

## Table of Contents

  * [Overview](#overview)
  * [Requirements](#requirements)
  * [Data](#data)
  * [Code](#code)
  * [Prompt](#prompt)
      * [Goal Interpretation](#)
      * [Action Sequencing](#)
      * [Subgoal Decomposition](#)
      * [Transition Modeling](#)
  * [Evaluation](#evaluation)
      * [Goal Interpretation](#)
      * [Action Sequencing](#)
      * [Subgoal Decomposition](#)
      * [Transition Modeling](#)
  * [BEHAVIOR Symbolic Simulator Implementation](#behavior)
      * [Evolving Graph](#)
      * [Transition Modeling](#)

<!-- <i> **please see [paper](https://arxiv.org/abs/2308.09126) for precise operationalizations. </i> -->

## Overview
We aim to evaluate Large Language Models (LLMs) for embodied decision making. While a significant body of work has been leveraging LLMs for decision making in embodied environments, we still lack a systematic understanding of their performance because they are usually applied in different domains, for different purposes, and built based on different inputs and outputs. Furthermore, existing evaluations tend to rely solely on a final success rate, making it difficult to pinpoint what ability is missing in LLMs and where the problem lies, which in turn blocks embodied agents from leveraging LLMs effectively and selectively.

To address these limitations, we propose a generalized interface, Embodied Agent Interface (EAgent), that supports the formalization of various types of tasks and input-output specifications of LLM-based modules. Specifically, it allows us to unify 1) a broad set of embodied decision-making tasks involving both state and temporally extended goals, 2) four commonly-used LLM-based modules for decision making: goal interpretation, subgoal decomposition, action sequencing, and transition modeling, and 3) a collection of fine-grained metrics which break down evaluation into various types of errors, such as hallucination errors, affordance errors, various types of planning errors, etc. Overall, our benchmark offers a comprehensive assessment of LLMs' performance for different subtasks, pinpointing the strengths and weaknesses in LLM-powered embodied AI systems and providing insights for effective and selective use of LLMs in embodied decision making. 

## Requirements


To run the code, first set up the simulators: 

[VirtualHome](https://github.com/zsyJosh/AgentEval/tree/main) 
```bash
pip install virtualhome
```
[BEHAVIOR](https://github.com/StanfordVL/iGibson)
```bash
# Install miniconda
curl -LO http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
bash Miniconda-latest-Linux-x86_64.sh
rm Miniconda-latest-Linux-x86_64.sh

# Add conda to your PATH
echo "export PATH=$HOME/.miniconda/bin:$PATH" >> .bashrc 

# Update conda and create a virtual environment for iGibson
conda update -y conda
conda create -y -n igibson python=3.8
conda activate igibson
```
[HELM](https://github.com/stanford-crfm/helm)
```bash
# Create a virtual environment.
# Only run this the first time.
conda create -n crfm-helm python=3.8 pip

# Activate the virtual environment.
conda activate crfm-helm

pip install crfm-helm
```

## Data

The dataset is publicly available at [BEHAVIOR Annotations](https://github.com/embodied-agent-eval/embodied-agent-eval/blob/main/dataset/behavior_data.json) and [VirtualHome Annotations](https://github.com/embodied-agent-eval/embodied-agent-eval/blob/main/dataset/virtualhome_data.json).

The dataset is in JSON format:
```"1057_1": {
  "task_name": "Watch TV",
  "natural_language_description": "Go to the living room, sit on the couch, find the 
    remote, switch on the TV and watch",
  "vh_goal": {
    "actions": [
      "LOOKAT|WATCH"
    ],
    "goal": [{
        "id": 410,
        "class_name": "television",
        "state": "ON"
      }, {
        "id": 410,
        "class_name": "television",
        "state": "PLUGGED_IN"
      }, {
        "from_id": 65,
        "relation_type": "FACING",
        "to_id": 410
    }]
  },
  "tl_goal": "(exists x0. ((LOOKAT(x0) or WATCH(x0))) then (ON(television.410) and 
    PLUGGED_IN(television.410) and FACING(character.65, television.410)))",
  "action_trajectory": [
    "[WALK] <home_office> (319)",
    "[WALK] <couch> (352)",
    "[FIND] <couch> (352)",
    "[SIT] <couch> (352)",
    "[FIND] <remote_control> (1000)",
    "[FIND] <television> (410)",
    "[SWITCHON] <television> (410)",
    "[TURNTO] <television> (410)",
    "[WATCH] <television> (410)"
  ],
  "transition_model": <pddl_definition>
}
```

## Code

The code structure for `EAgent` is as follows:
```
---- src
------------ BEHAVIOR  # Evaluator on BEHAVIOR
---------------- igibson/evaluation
-------------------- goal_interpretation
------------------------ prompts
------------------------ scripts
-------------------- action_sequence
------------------------ prompts
------------------------ scripts
-------------------- eval_subgoal_plan
------------------------ prompts
------------------------ scripts
-------------------- transition_modeling
------------------------ prompts
------------------------ scripts
---------------- igibson/evolving_graph
---------------- igibson/transition_model
------------ VirtualHome  # Evaluator on VirtualHome
---------------- virtualhome/simulation/evolving_graph
-------------------- motion_planner.py
-------------------- eval_goal.py
-------------------- eval_action.py
-------------------- eval_subgoal.py
-------------------- eval_transition.py
------------------------ logic_score.py
------------------------ planner_test.py
------------------------ pddlgym_planners
-------------------- virtualhome/prompts
------------ HELM  # Running LLMs
---------------- scripts
```

## Prompt

### Goal Interpretation
```
---- src
------------ BEHAVIOR  # Evaluator on BEHAVIOR
---------------- igibson/evaluation
-------------------- goal_interpretation
------------------------ prompts
------------ VirtualHome  # Evaluator on VirtualHome
-------------------- virtualhome/prompts
```

### Action Sequencing
```
---- src
------------ BEHAVIOR  # Evaluator on BEHAVIOR
---------------- igibson/evaluation
-------------------- action_sequence
------------------------ prompts
------------ VirtualHome  # Evaluator on VirtualHome
-------------------- virtualhome/prompts
```

### Subgoal Decomposition
```
---- src
------------ BEHAVIOR  # Evaluator on BEHAVIOR
---------------- igibson/evaluation
-------------------- eval_subgoal_plan
------------------------ prompts
------------ VirtualHome  # Evaluator on VirtualHome
-------------------- virtualhome/prompts
```

### Transition Modeling
```
---- src
------------ BEHAVIOR  # Evaluator on BEHAVIOR
---------------- igibson/evaluation
-------------------- transition_modeling
------------------------ prompts
------------ VirtualHome  # Evaluator on VirtualHome
-------------------- virtualhome/prompts
```

## Evaluation

### Goal Interpretation
```
---- src
------------ BEHAVIOR  # Evaluator on BEHAVIOR
---------------- igibson/evaluation
-------------------- goal_interpretation
------------------------ prompts
------------------------ scripts
------------ VirtualHome  # Evaluator on VirtualHome
---------------- virtualhome/simulation/evolving_graph
-------------------- motion_planner.py
-------------------- eval_goal.py
```

### Action Sequencing
```
---- src
------------ BEHAVIOR  # Evaluator on BEHAVIOR
---------------- igibson/evaluation
-------------------- action_sequence
------------------------ scripts
---------------- igibson/evolving_graph
---------------- igibson/transition_model
------------ VirtualHome  # Evaluator on VirtualHome
---------------- virtualhome/simulation/evolving_graph
-------------------- motion_planner.py
-------------------- eval_action.py
```

### Subgoal Decomposition
```
---- src
------------ BEHAVIOR  # Evaluator on BEHAVIOR
---------------- igibson/evaluation
-------------------- eval_subgoal_plan
------------------------ scripts
---------------- igibson/evolving_graph
---------------- igibson/transition_model
------------ VirtualHome  # Evaluator on VirtualHome
---------------- virtualhome/simulation/evolving_graph
-------------------- motion_planner.py
-------------------- eval_subgoal.py
```

### Transition Modeling
```
---- src
------------ BEHAVIOR  # Evaluator on BEHAVIOR
---------------- igibson/evaluation
-------------------- transition_modeling
------------------------ scripts
---------------- igibson/evolving_graph
---------------- igibson/transition_model
------------ VirtualHome  # Evaluator on VirtualHome
---------------- virtualhome/simulation/evolving_graph
-------------------- motion_planner.py
-------------------- eval_transition.py
------------------------ logic_score.py
------------------------ planner_test.py
------------------------ pddlgym_planners
```

## BEHAVIOR Symbolic Simulator Implementation

### Evolving Graph

We implement the evolving graph at `src/BEHAVIOR/igibson/evolving_graph`.

### Transition Modeling

We implement the evolving graph at `src/BEHAVIOR/igibson/transition_model`.
