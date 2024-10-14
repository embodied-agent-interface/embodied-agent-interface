# Overview

We aim to evaluate Large Language Models (LLMs) for embodied decision-making. While many works leverage LLMs for decision-making in embodied environments, a systematic understanding of their performance is still lacking. These models are applied in different domains, for various purposes, and with diverse inputs and outputs. Current evaluations tend to rely on final success rates alone, making it difficult to pinpoint where LLMs fall short and how to leverage them effectively in embodied AI systems.

To address this gap, we propose the **Embodied Agent Interface (EAI)**, which unifies:
1. A broad set of embodied decision-making tasks involving both state and temporally extended goals.
2. Four commonly used LLM-based modules: goal interpretation, subgoal decomposition, action sequencing, and transition modeling.
3. Fine-grained evaluation metrics, identifying errors such as hallucinations, affordance issues, and planning mistakes.

Our benchmark provides a comprehensive assessment of LLM performance across different subtasks, identifying their strengths and weaknesses in embodied decision-making contexts.