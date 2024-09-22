"""Fast-downward planner.
http://www.fast-downward.org/ObtainingAndRunningFastDownward
"""

import re
import os
import sys
import subprocess
import tempfile
import numpy as np
import time
from virtualhome_eval.simulation.evolving_graph.pddlgym_planners.pddl_planner import (
    PDDLPlanner,
)
from virtualhome_eval.simulation.evolving_graph.pddlgym_planners.planner import (
    PlanningFailure,
)

FD_URL = "https://github.com/aibasel/downward.git"


class FD(PDDLPlanner):
    """Fast-downward planner."""

    def __init__(self, alias_flag="--alias lama-first", final_flags=""):
        super().__init__()
        dirname = os.path.dirname(os.path.realpath(__file__))
        self._exec = os.path.join(dirname, "FD/fast-downward.py")
        print("Instantiating FD", end=" ")
        if alias_flag:
            print("with", alias_flag, end=" ")
        if final_flags:
            print("with", final_flags, end=" ")
        print()
        self._alias_flag = alias_flag
        self._final_flags = final_flags
        if not os.path.exists(self._exec):
            self._install_fd()

    def plan_from_pddl(
        self, dom_file, prob_file, horizon=np.inf, timeout=100, remove_files=False
    ):
        """PDDL-specific planning method."""
        cmd_str = self._get_cmd_str(dom_file, prob_file, timeout)
        start_time = time.time()
        output = subprocess.getoutput(cmd_str)
        # print(f'{output=}')
        if remove_files:
            os.remove(dom_file)
            os.remove(prob_file)
        self._cleanup()
        if time.time() - start_time > timeout:
            print(
                f"Planning timed out! {time.time()-start_time} > {timeout}, started at {start_time}, current time {time.time()}"
            )
            raise Exception("Planning timed out!")
        pddl_plan = self._output_to_plan(output)
        if len(pddl_plan) > horizon:
            raise Exception("PDDL planning failed due to horizon")
        return pddl_plan

    def _get_cmd_str(self, dom_file, prob_file, timeout):
        sas_file = tempfile.NamedTemporaryFile(delete=False).name
        timeout_cmd = "gtimeout" if sys.platform == "darwin" else "timeout"
        cmd_str = "{} {} {} {} --sas-file {} {} {} {}".format(
            timeout_cmd,
            timeout,
            self._exec,
            self._alias_flag,
            sas_file,
            dom_file,
            prob_file,
            self._final_flags,
        )
        return cmd_str

    def _get_cmd_str_searchonly(self, sas_file, timeout):
        timeout_cmd = "gtimeout" if sys.platform == "darwin" else "timeout"
        cmd_str = "{} {} {} {} --search {} {}".format(
            timeout_cmd,
            timeout,
            self._exec,
            self._alias_flag,
            sas_file,
            self._final_flags,
        )
        return cmd_str

    def _cleanup(self):
        """Run FD cleanup"""
        cmd_str = "{} --cleanup".format(self._exec)
        subprocess.getoutput(cmd_str)

    def _output_to_plan(self, output):
        # Technically this is number of evaluated states which is always
        # 1+number of expanded states, but we report evaluated for consistency
        # with FF.
        num_node_expansions = re.findall(r"evaluated (\d+) state", output.lower())
        plan_length = re.findall(r"plan length: (\d+) step", output.lower())
        plan_cost = re.findall(r"] plan cost: (\d+)", output.lower())
        search_time = re.findall(r"] search time: (\d+\.\d+)", output.lower())
        total_time = re.findall(r"] total time: (\d+\.\d+)", output.lower())
        if "num_node_expansions" not in self._statistics:
            self._statistics["num_node_expansions"] = 0
        if len(num_node_expansions) == 1:
            assert int(num_node_expansions[0]) == float(num_node_expansions[0])
            self._statistics["num_node_expansions"] += int(num_node_expansions[0])
        if len(search_time) == 1:
            try:
                search_time_float = float(search_time[0])
                self._statistics["search_time"] = search_time_float
            except:
                raise PlanningFailure(
                    "Error on output's search time format: {}".format(search_time[0])
                )
        if len(search_time) == 1:
            try:
                total_time_float = float(total_time[0])
                self._statistics["total_time"] = total_time_float
            except:
                raise PlanningFailure(
                    "Error on output's total time format: {}".format(total_time[0])
                )
        if len(plan_length) == 1:
            try:
                plan_length_int = int(plan_length[0])
                self._statistics["plan_length"] = plan_length_int
            except:
                raise PlanningFailure(
                    "Error on output's plan length format: {}".format(plan_length[0])
                )
        if len(plan_cost) == 1:
            try:
                plan_cost_int = int(plan_cost[0])
                self._statistics["plan_cost"] = plan_cost_int
            except:
                raise PlanningFailure(
                    "Error on output's plan cost format: {}".format(plan_cost[0])
                )
        if "Solution found!" not in output:
            raise PlanningFailure("Plan not found with FD! Error: {}".format(output))
        if "Plan length: 0 step" in output:
            return []

        fd_plan = re.findall(r"(.+) \(\d+?\)", output.lower())
        if not fd_plan:
            raise PlanningFailure("Plan not found with FD! Error: {}".format(output))
        return fd_plan

    def _install_fd(self):
        loc = os.path.dirname(self._exec)
        # Install and compile FD.
        os.system("git clone {} {}".format(FD_URL, loc))
        os.system("cd {} && ./build.py && cd -".format(loc))
        assert os.path.exists(self._exec)
