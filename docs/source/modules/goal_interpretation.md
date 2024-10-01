# Goal Interpretation


Goal Interpretation aims to ground the natural language instruction to the environment representations of objects, states, relations, and actions. For example, the task instruction "Use the rag to clean the trays, the bowl, and the refrigerator. When you are done, leave the rag next to the sink..." can be grounded to specific objects with IDs, such as fridge (ID: 97), tray (ID: 1), bowl (ID: 1), rag (ID: 0), and sink (ID: 82). Note that a simple natural language description can be grounded into a set of multiple goal conditions (object state and relation).


The goal interpretation module takes the state \( s_0 \) and a natural language instruction \( l_g \) as input, and generates an LTL goal \( \hat{g}_l \) as a formal goal specification which a symbolic planner can conceivably take as input. In this paper, we only generate simple LTL goals formed by an ordered action sequence and a conjunction of propositions to be satisfied in the final state.
