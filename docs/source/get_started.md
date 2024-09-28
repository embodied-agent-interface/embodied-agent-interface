
# Installation

To install **Embodied Agent Interface (EAgent)** for benchmarking LLMs in embodied decision-making:

1. **Create and Activate a Conda Environment**:
   ```bash
   conda create -n eagent python=3.8 -y 
   conda activate eagent
   ```

2. **Install `eagent-eval`**:
   You can install it from pip:
   ```bash
   pip install eagent-eval
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
   eagent-eval \
     --dataset {virtualhome,behavior} \
     --mode {generate_prompts,evaluate_results} \
     --eval-type {action_sequencing,transition_modeling,goal_interpretation,subgoal_decomposition} \
     --llm-response-path <path_to_responses> \
     --output-dir <output_directory> \
     --num-workers <number_of_workers>
   ```

   Run the following command for further information:
   ```bash
   eagent-eval --help
   ```

2. **Reproduce Our Results**:

   Download helm outputs:
   ```bash
   python -m eagent_eval.utils.download_utils
   ```

   Then, traverse the arguments in the command below to get all the results:
   ```bash
   eagent-eval \
     --dataset {virtualhome,behavior} \
     --eval-type {action_sequencing,transition_modeling,goal_interpretation,subgoal_decomposition} \
     --mode evaluate_results
   ```

4. **Prompt Generation**:


   To generate prompts, run in the command below (pick up arguments from ):
   ```bash
   eagent-eval \
     --dataset {virtualhome,behavior} \
     --eval-type {action_sequencing,transition_modeling,goal_interpretation,subgoal_decomposition} \
     --mode generate_prompts
   ```

6. **Examples**:
   - ***Generate Prompts***

      To generate prompts for the **VirtualHome** dataset with **action sequencing** evaluation type:

      ```bash
      eagent-eval --dataset virtualhome --eval-type action_sequencing --mode generate_prompts
      ```

      To generate prompts for the **Behavior** dataset with **goal interpretation** evaluation type:

      ```bash
      eagent-eval --dataset behavior --eval-type goal_interpretation --mode generate_prompts
      ```

   -  ***Evaluate Results***
      
      Make sure to download our results first if you don't want to specify <path_to_responses>

      ```bash
      python -m eagent_eval.utils.download_utils
      ```
      To evaluate the results for the **VirtualHome** dataset with **subgoal decomposition** evaluation type:

      ```bash
      eagent-eval --dataset virtualhome --eval-type subgoal_decomposition --mode evaluate_results
      ```

      To evaluate the results for the **Behavior** dataset with **transition modeling** evaluation type:

      ```bash
      eagent-eval --dataset behavior --eval-type transition_modeling --mode evaluate_results
      ```


# Docker
We provide a ready-to-use Docker image for easy installation and usage.

First, pull the Docker image from Docker Hub:
```bash
docker pull jameskrw/eagent-eval
```

Next, run the Docker container interactively:

```bash
docker run -it jameskrw/eagent-eval
```

When inside the container, make sure you remain in the `/opt/iGibson` directory (do not change to other directories).

To check the available arguments for the `eagent-eval` CLI, use the following command:

```bash
python3 -m eagent_eval.cli --help
```

You can run:

```bash
python3 -m eagent_eval.cli
```

By default, this will start generating prompts for goal interpretation in Behavior.

The command `python3 -m eagent_eval.cli` is equivalent to `eagent-eval` as introduced above, although currently only `python3 -m eagent_eval.cli` is supported in the docker.
