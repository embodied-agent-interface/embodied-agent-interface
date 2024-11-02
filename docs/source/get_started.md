# Installation
1. **Create and Activate a Conda Environment**:
   ```bash
   conda create -n eai-eval python=3.8 -y 
   conda activate eai-eval
   ```

2. **Install `eai`**:
   
   You can install it from pip:
   ```bash
   pip install eai-eval
   ```

   Or, install from source:
   ```bash
   git clone https://github.com/embodied-agent-interface/embodied-agent-interface.git
   cd embodied-agent-interface
   pip install -e .
   ```

3. **(Optional) Install iGibson for behavior evaluation**:
   
   If you need to use `behavior_eval`, install iGibson. Follow these steps to minimize installation issues:

   - Make sure you are using Python 3.8 and meet the minimum system requirements in the [iGibson installation guide](https://stanfordvl.github.io/iGibson/installation.html).
   
   - Install CMake using Conda (do not use pip):
     ```bash
     conda install cmake
     ```

   - Install `iGibson`:
     We provide an installation script:
     ```bash
     python -m behavior_eval.utils.install_igibson_utils
     ```
     Alternatively, install it manually:
     ```bash
     git clone https://github.com/embodied-agent-interface/iGibson.git --recursive
     cd iGibson
     pip install -e .
     ```

   - Download assets:
     ```bash
     python -m behavior_eval.utils.download_utils
     ```

   We have successfully tested installation on Linux, Windows 10+, and macOS.

# Quick Start

1. **Arguments**:
   ```bash
   eai-eval \
     --dataset {virtualhome,behavior} \
     --mode {generate_prompts,evaluate_results} \
     --eval-type {action_sequencing,transition_modeling,goal_interpretation,subgoal_decomposition} \
     --llm-response-path <path_to_responses> \
     --output-dir <output_directory> \
     --num-workers <number_of_workers>
   ```

   Run the following command for further information:
   ```bash
   eai-eval --help
   ```

2. **Examples**:

-  ***Evaluate Results***
   
   
   Make sure to download our results first if you don't want to specify <path_to_responses>
   ```bash
   python -m eai_eval.utils.download_utils
   ```

   Then, run the commands below:
   ```bash
   eai-eval --dataset virtualhome --eval-type action_sequencing --mode evaluate_results
   eai-eval --dataset virtualhome --eval-type transition_modeling --mode evaluate_results
   eai-eval --dataset virtualhome --eval-type goal_interpretation --mode evaluate_results
   eai-eval --dataset virtualhome --eval-type subgoal_decomposition --mode evaluate_results
   eai-eval --dataset behavior --eval-type action_sequencing --mode evaluate_results
   eai-eval --dataset behavior --eval-type transition_modeling --mode evaluate_results
   eai-eval --dataset behavior --eval-type goal_interpretation --mode evaluate_results
   eai-eval --dataset behavior --eval-type subgoal_decomposition --mode evaluate_results
   ```

-  ***Generate Pormpts***
   
   
   To generate prompts, you can run:
   ```bash
   eai-eval --dataset virtualhome --eval-type action_sequencing --mode generate_prompts
   eai-eval --dataset virtualhome --eval-type transition_modeling --mode generate_prompts
   eai-eval --dataset virtualhome --eval-type goal_interpretation --mode generate_prompts
   eai-eval --dataset virtualhome --eval-type subgoal_decomposition --mode generate_prompts
   eai-eval --dataset behavior --eval-type action_sequencing --mode generate_prompts
   eai-eval --dataset behavior --eval-type transition_modeling --mode generate_prompts
   eai-eval --dataset behavior --eval-type goal_interpretation --mode generate_prompts
   eai-eval --dataset behavior --eval-type subgoal_decomposition --mode generate_prompts
   ```

3. **Evaluate All Modules in One Command**


   To evaluate all modules with default parameters, use the command below:
   ```bash
   eai-eval --all
   ```
   This command will automatically traverse all unspecified parameter options.

   **Example Usage**:
   ```bash
   eai-eval --all --dataset virtualhome
   ```
   This will run both `generate_prompts` and `evaluate_results` for all modules in the `virtualhome` dataset. Make sure to download our results first if you don't want to specify <path_to_responses>

# Docker
We provide a ready-to-use Docker image for easy installation and usage.

First, pull the Docker image from Docker Hub:
```bash
docker pull jameskrw/eai-eval
```

Next, run the Docker container interactively:

```bash
docker run -it jameskrw/eai-eval
```

Test docker

```bash
eai-eval
```
By default, this will start generating prompts for goal interpretation in Behavior.
