"""General interface for a PDDL planner."""

import os
import time
import abc
import subprocess
import tempfile
import numpy as np
from pddlgym.spaces import LiteralSpace
from pddlgym.utils import nostdout
from pddlgym.parser import parse_plan_step, PDDLProblemParser
from virtualhome_eval.simulation.evolving_graph.pddlgym_planners.planner import (
    Planner,
    PlanningTimeout,
    PlanningFailure,
)


class PDDLPlanner(Planner):
    """Calls out to an external planner with constructed domain and problem
    files; parses the resulting plan.
    """

    def __call__(
        self,
        domain,
        state,
        horizon=np.inf,
        timeout=10,
        return_files=False,
        translate_separately=False,
    ):
        act_predicates = [domain.predicates[a] for a in list(domain.actions)]
        act_space = LiteralSpace(
            act_predicates, type_to_parent_types=domain.type_to_parent_types
        )
        dom_file = tempfile.NamedTemporaryFile(delete=False).name
        prob_file = tempfile.NamedTemporaryFile(delete=False).name
        domain.write(dom_file)
        lits = set(state.literals)
        if not domain.operators_as_actions:
            lits |= set(act_space.all_ground_literals(state, valid_only=False))
        PDDLProblemParser.create_pddl_file(
            prob_file,
            state.objects,
            lits,
            "myproblem",
            domain.domain_name,
            state.goal,
            fast_downward_order=True,
        )
        if translate_separately:
            # TODO: don't ignore timeout during translate phase
            from pddlgym_planners.FD.src.translate.translate import (
                main as downward_translate,
            )
            from pddlgym_planners.FD.src.translate.pddl_parser import (
                open as downward_open,
            )

            task = downward_open(domain_filename=dom_file, task_filename=prob_file)
            sas_file = tempfile.NamedTemporaryFile(delete=False).name
            with nostdout():
                downward_translate(task, sas_file)
            pddl_plan = self.plan_from_sas(sas_file, horizon=horizon, timeout=timeout)
            os.remove(dom_file)
            os.remove(prob_file)
            os.remove(sas_file)
        else:
            domain_content = open(dom_file, "r").read()
            problem_content = open(prob_file, "r").read()
            # print(f'{domain_content=}')
            # print(f'{problem_content=}')
            pddl_plan = self.plan_from_pddl(
                dom_file,
                prob_file,
                horizon=horizon,
                timeout=timeout,
                remove_files=(not return_files),
            )
            cmd_str = self._get_cmd_str(dom_file, prob_file, timeout)
            print(f"{pddl_plan=}")
            print(f"{cmd_str=}")
        plan = [
            self._plan_step_to_action(domain, state, act_predicates, plan_step)
            for plan_step in pddl_plan
        ]
        print(f"{plan=}")
        if return_files:
            return plan, dom_file, prob_file
        return plan

    def plan_from_pddl(
        self, dom_file, prob_file, horizon=np.inf, timeout=10, remove_files=False
    ):
        """PDDL-specific planning method."""
        cmd_str = self._get_cmd_str(dom_file, prob_file, timeout)
        print(f"{cmd_str=}")
        start_time = time.time()
        output = subprocess.getoutput(cmd_str)
        if remove_files:
            os.remove(dom_file)
            os.remove(prob_file)
        self._cleanup()
        if time.time() - start_time > timeout:
            raise PlanningTimeout("Planning timed out!")
        pddl_plan = self._output_to_plan(output)
        if len(pddl_plan) > horizon:
            raise PlanningFailure("PDDL planning failed due to horizon")
        return pddl_plan

    def plan_from_sas(self, sas_file, horizon=np.inf, timeout=10):
        """PDDL-specific planning method using SAS file."""
        cmd_str = self._get_cmd_str_searchonly(sas_file, timeout)
        start_time = time.time()
        output = subprocess.getoutput(cmd_str)
        self._cleanup()
        if time.time() - start_time > timeout:
            raise PlanningTimeout("Planning timed out!")
        pddl_plan = self._output_to_plan(output)
        if len(pddl_plan) > horizon:
            raise PlanningFailure("PDDL planning failed due to horizon")
        return pddl_plan

    @abc.abstractmethod
    def _get_cmd_str(self, dom_file, prob_file, timeout):
        raise NotImplementedError("Override me!")

    @abc.abstractmethod
    def _get_cmd_str_searchonly(self, sas_file, timeout):
        raise NotImplementedError("Override me!")

    @abc.abstractmethod
    def _output_to_plan(self, output):
        raise NotImplementedError("Override me!")

    def _cleanup(self):
        """Allow subclasses to run cleanup after planning"""
        pass

    @staticmethod
    def _plan_step_to_action(domain, state, act_predicates, plan_step):
        return parse_plan_step(
            plan_step,
            domain.operators.values(),
            act_predicates,
            state.objects,
            operators_as_actions=domain.operators_as_actions,
        )
