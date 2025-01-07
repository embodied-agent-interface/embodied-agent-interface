from virtualhome_eval.simulation.evolving_graph.eval_utils import *
from virtualhome_eval.simulation.evolving_graph.pddlgym_planners.fd import FD
from virtualhome_eval.simulation.evolving_graph.logic_score import *


planner = FD()
domain_file_path = 'examples/virtualhome.pddl'
problem_path = 'examples/virtualhome_test.pddl'
timeout = 100

pddl_plan = planner.plan_from_pddl(
            domain_file_path, problem_path, timeout=timeout
        )

print('Results:')
print(pddl_plan)