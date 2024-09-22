<h1 align="center">  Embodied Agent Interface (EAgent): Benchmarking LLMs for Embodied Decision Making </h1>


[![](https://img.shields.io/badge/website-EAgent-purple?style=plastic&logo=Google%20chrome)](https://embodied-agent-eval.github.io/)
[![](https://img.shields.io/badge/dataset-download-yellow?style=plastic&logo=Data)](https://github.com/embodied-agent-eval/embodied-agent-eval/tree/main/dataset)
[![](https://img.shields.io/badge/docker-eval--embodied--agent-blue?style=plastic&logo=Docker)](https://hub.docker.com/r/jameskrw/eval-embodied-agent) 
[![](https://img.shields.io/badge/docs-online-blue?style=plastic&logo=Read%20the%20Docs)](https://embodied-agent-eval.readthedocs.io/en/latest/#)
[![](https://img.shields.io/badge/pip-behavior--eval-brightgreen?style=plastic&logo=Python)](https://pypi.org/project/behavior-eval/) 
[![](https://img.shields.io/badge/pip-virtualhome--eval-brightgreen?style=plastic&logo=Python)](https://pypi.org/project/virtualhome-eval/) 
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


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

- [Embodied Agent Interface (EAgent): Benchmarking LLMs for Embodied Decision Making](#embodied-agent-interface-eagent-benchmarking-llms-for-embodied-decision-making)
  - [:dizzy: Dataset Highlights](#dizzy-dataset-highlights)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Requirements](#requirements)
  - [Data](#data)
    - [VirtualHome original dataset (Optional)](#virtualhome-original-dataset-optional)
  - [Code](#code)
  - [Prompt](#prompt)
    - [Goal Interpretation](#goal-interpretation)
    - [Action Sequencing](#action-sequencing)
    - [Subgoal Decomposition](#subgoal-decomposition)
    - [Transition Modeling](#transition-modeling)
  - [Evaluation](#evaluation)
    - [Goal Interpretation](#goal-interpretation-1)
      - [Evaluation script](#evaluation-script)
    - [Action Sequencing](#action-sequencing-1)
      - [Evaluation script](#evaluation-script-1)
    - [Subgoal Decomposition](#subgoal-decomposition-1)
    - [Transition Modeling](#transition-modeling-1)
      - [Evaluation script](#evaluation-script-2)
  - [BEHAVIOR Symbolic Simulator Implementation](#behavior-symbolic-simulator-implementation)
    - [Evolving Graph](#evolving-graph)
    - [Transition Modeling](#transition-modeling-2)

<!-- <i> **please see [paper](https://arxiv.org/abs/2308.09126) for precise operationalizations. </i> -->

## Overview
We aim to evaluate Large Language Models (LLMs) for embodied decision making. While a significant body of work has been leveraging LLMs for decision making in embodied environments, we still lack a systematic understanding of their performance because they are usually applied in different domains, for different purposes, and built based on different inputs and outputs. Furthermore, existing evaluations tend to rely solely on a final success rate, making it difficult to pinpoint what ability is missing in LLMs and where the problem lies, which in turn blocks embodied agents from leveraging LLMs effectively and selectively.

To address these limitations, we propose a generalized interface, Embodied Agent Interface (EAgent), that supports the formalization of various types of tasks and input-output specifications of LLM-based modules. Specifically, it allows us to unify 1) a broad set of embodied decision-making tasks involving both state and temporally extended goals, 2) four commonly-used LLM-based modules for decision making: goal interpretation, subgoal decomposition, action sequencing, and transition modeling, and 3) a collection of fine-grained metrics which break down evaluation into various types of errors, such as hallucination errors, affordance errors, various types of planning errors, etc. Overall, our benchmark offers a comprehensive assessment of LLMs' performance for different subtasks, pinpointing the strengths and weaknesses in LLM-powered embodied AI systems and providing insights for effective and selective use of LLMs in embodied decision making. 

## Installation

To install the Embodied Agent Interface (EAgent) for benchmarking Large Language Models (LLMs) for embodied decision-making, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/embodied-agent-eval/embodied-agent-eval.git
   cd embodied-agent-eval
   ```

2. **Checkout the Development Branch**:
   ```bash
   git checkout dev
   ```

3. **Create and Activate a Conda Environment**:
   ```bash
   conda create -n eagent python=3.8 -y 
   conda activate eagent
   ```

4. **Install the Package**:
   ```bash
   pip install -e .
   ```

5. **(Optional) Install iGibson for behavior evaluation**:
   If you need to use `behavior_eval`, you must install iGibson.

   There might be issues during the installation of `iGibson`. 

    To minimize and identify potential issues, we recommend:
    
    1. Review the system requirements section of the [iGibson installation guide](https://stanfordvl.github.io/iGibson/installation.html).
    
    2. **Install CMake Using Conda (do not use pip)**: 
       ```
       conda install cmake
       ```
    
    3. **Install `iGibson`**: 
       We provided a script for automatically installing `iGibson`:
       ```
       python -m behavior_eval.utils.install_igibson_utils
       ```
       
       You can also do it on your own:
       ```
       git clone https://github.com/embodied-agent-eval/iGibson.git --recursive
       cd iGibson
       pip install -e .  # If you want to use editable mode
       # or
       pip install .  # Recommended
       ```
    
    We've successfully tested the installation on Linux servers, Windows 10+, and Mac OS X.



## Examples

Once the installation is complete, you can start using the Embodied Agent Interface (EAgent) for evaluation. Below are a few examples of how to run the evaluation.

1. **View Available Arguments**:
   ```bash
   eagent-eval --help
   ```

2. **Generate Prompts for Behavior Evaluation**:
   ```bash
   eagent-eval --dataset behavior --eval-type action_sequence --mode generate_prompts
   ```

3. **Evaluate Action Sequencing in VirtualHome Dataset**:
   ```bash
   eagent-eval --dataset virtualhome --eval-type action_sequence
   ```

4. **Evaluate Results in VirtualHome Dataset**:
   ```bash
   eagent-eval --dataset virtualhome --eval-type action_sequence --mode evaluate_results
   ```



