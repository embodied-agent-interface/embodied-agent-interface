Embodied Agent Interface
========================

Welcome! **``Embodied Agent Interface``** is a single-line evaluation
pipeline to evaluate LLMs for embodied agents, which aims to tackle the
following challenges in building embodied decision-making agents:

-  Standardization of goal specifications.
-  Standardization of modules and interfaces.
-  Broad coverage of evaluation and fine-grained metrics.

The code is `hosted on GitHub
here <https://github.com/embodied-agent-eval/embodied-agent-eval>`__.

The project website can be found `here <https://embodied-agent-eval.github.io/>`__.


Overview
========

We aim to evaluate Large Language Models (LLMs) for embodied decision
making. While a significant body of work has been leveraging LLMs for
decision making in embodied environments, we still lack a systematic
understanding of their performance because they are usually applied in
different domains, for different purposes, and built based on different
inputs and outputs. Furthermore, existing evaluations tend to rely
solely on a final success rate, making it difficult to pinpoint what
ability is missing in LLMs and where the problem lies, which in turn
blocks embodied agents from leveraging LLMs effectively and selectively.

To address these limitations, we propose a generalized interface,
Embodied Agent Interface (EAgent), that supports the formalization of
various types of tasks and input-output specifications of LLM-based
modules. Specifically, it allows us to unify 1) a broad set of embodied
decision-making tasks involving both state and temporally extended
goals, 2) four commonly-used LLM-based modules for decision making: goal
interpretation, subgoal decomposition, action sequencing, and transition
modeling, and 3) a collection of fine-grained metrics which break down
evaluation into various types of errors, such as hallucination errors,
affordance errors, various types of planning errors, etc. Overall, our
benchmark offers a comprehensive assessment of LLMs' performance for
different subtasks, pinpointing the strengths and weaknesses in
LLM-powered embodied AI systems and providing insights for effective and
selective use of LLMs in embodied decision making.

Dataset
=======

The dataset is publicly available at `BEHAVIOR Annotations <https://github.com/embodied-agent-eval/embodied-agent-eval/blob/main/dataset/behavior_data.json>`__ and `VirtualHome Annotations <https://github.com/embodied-agent-eval/embodied-agent-eval/blob/main/dataset/virtualhome_data.json>`__.

The dataset is in JSON format. Here's an example entry:

.. code-block:: json

    {
      "1057_1": {
        "task_name": "Watch TV",
        "natural_language_description": "Go to the living room, sit on the couch, find the remote, switch on the TV and watch",
        "vh_goal": {
          "actions": [
            "LOOKAT|WATCH"
          ],
          "goal": [
            {
              "id": 410,
              "class_name": "television",
              "state": "ON"
            },
            {
              "id": 410,
              "class_name": "television",
              "state": "PLUGGED_IN"
            },
            {
              "from_id": 65,
              "relation_type": "FACING",
              "to_id": 410
            }
          ]
        },
        "tl_goal": "(exists x0. ((LOOKAT(x0) or WATCH(x0))) then (ON(television.410) and PLUGGED_IN(television.410) and FACING(character.65, television.410)))",
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
        "transition_model": "<pddl_definition>"
      }
    }

    
Installation and Usage Guide for ``behavior-eval``
==================================================

Installation
------------

Step 1: Create a Conda Virtual Environment for ``behavior-eval``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   conda create -n behavior-eval python=3.8 -y
   conda activate behavior-eval

Step 2: Install ``behavior-eval``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can install from pip:

::

   pip install behavior-eval

You can also install from source and use editable mode if you want to
modify the source files:

::

   git clone https://github.com/embodied-agent-eval/behavior-eval.git
   cd behavior-eval
   pip install -e .

Step 3: Install ``iGibson``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

There might be issues during the installation of ``iGibson``.

To minimize and identify potential issues, we recommend:

1. Review the system requirements section of the `iGibson installation
   guide <https://stanfordvl.github.io/iGibson/installation.html>`__.

2. **Install CMake Using Conda (do not use pip)**:

   ::

      conda install cmake

3. **Install ``iGibson``**: We provided a script for automatically
   installing ``iGibson``:

   ::

      python -m behavior_eval.utils.install_igibson_utils

   You can also do it on your own:

   ::

      git clone https://github.com/embodied-agent-eval/iGibson.git --recursive
      cd iGibson
      pip install -e .  # If you want to use editable mode
      # or
      pip install .  # Recommended

We've successfully tested the installation on Linux servers, Windows
10+, and Mac OS X.

Step 4: Download Assets for ``iGibson``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   python -m behavior_eval.utils.download_utils

Usage
-----

To run ``behavior-eval``, use the following command:

::

   python -m behavior_eval.main

(By default, this will generate the prompts for action sequencing.)

Parameters:
~~~~~~~~~~~

-  ``module``: Specifies the module to use. Options are:

   -  ``goal_interpretation``
   -  ``action_sequence``
   -  ``subgoal_decomposition``
   -  ``transition_modeling``

-  ``func``: Specifies the function to execute. Options are:

   -  ``evaluate_results``
   -  ``generate_prompts``

-  ``worker_num``: Number of workers for multiprocessing.
-  ``llm_response_dir``: Directory containing LLM responses (HELM
   outputs).
-  ``result_dir``: Directory to store results.

Example Usage:
~~~~~~~~~~~~~~

1. To generate prompts using the ``action_sequence`` module:

   ::

      python -m behavior_eval.main --module=action_sequence --func=generate_prompts

2. To evaluate results using the ``action_sequence`` module:

   ::

      python -m behavior_eval.main --module=action_sequence --func=evaluate_results --llm_response_dir=<your_llm_response_dir>

Replace ``<your_llm_response_dir>`` with the path to your LLM response
directory.

Installation and Usage Guide for virtualhome-eval
=================================================

Install dependencies
--------------------

::

   pip install virtualhome_eval

Usage
-----

To run ``virtualhome_eval``, use the following commands with arguments

::

   from virtualhome_eval.agent_eval import agent_evaluation
   agent_evaluation(mode=[generate_prompts, evaluate_results], eval_type=[goal_interpretation, action_sequence, transition_modeling], llm_response_path=[YOUR LLM OUTPUT DIR])

Parameters
~~~~~~~~~~

-  ``mode``: Specifies either generate prompts or evaluate results.
   Options are:

   -  ``generate_prompts``
   -  ``evaluate_results``

-  ``eval_type``: Specifies the evaluation task type. Options are:

   -  ``goal_interpretation``
   -  ``action_sequence``
   -  ``subgoal_decomposition``
   -  ``transition_model``

-  ``llm_response_path``: The path of LLM output directory to be
   evaluated. It is ``""`` by default, using the existing outputs at
   directory ``virtualhome_eval/llm_response/``. The function will
   evaluate all LLM outputs under the directory.
-  ``dataset``: The dataset type. Options:

   -  ``virtualhome``
   -  ``behavior``

-  ``output_dir``: The directory to store the output results. By
   default, it is at ``output/`` of current path.

Example usage
~~~~~~~~~~~~~

1. To generate prompts for ``goal_interpretation``:

::

   agent_evaluation(mode='generate_prompts',  eval_type='goal_interpretation')

2. To evaluate LLM outputs for ``goal_interpretation``:

::

   results = agent_evaluation(mode='evaluate_results', eval_type='goal_interpretation')

3. To generate prompts for ``action_sequence``:

::

   agent_evaluation(mode='generate_prompts',  eval_type='action_sequence')

4. To evaluate LLM outputs for ``action_sequence``:

::

   results = agent_evaluation(mode='evaluate_results', eval_type='action_sequence')

5. To generate Virtualhome prompts for ``transition_model``:

::

   agent_evaluation(mode='generate_prompts',  eval_type='transition_model')

6. To evaluate LLM outputs on Virtualhome for ``transition_model``:

::

   results = agent_evaluation(mode='evaluate_results', eval_type='transition_model')

7. To generate prompts for ``subgoal_decomposition``:

::

   agent_evaluation(mode='generate_prompts',  eval_type='subgoal_decomposition')

8. To evaluate LLM outputs for ``subgoal_decomposition``:

::

   results = agent_evaluation(mode='evaluate_results', eval_type='subgoal_decomposition')