"""Fast-forward planner.
https://fai.cs.uni-saarland.de/hoffmann/ff.html
"""

import re
import os
import sys
import numpy as np
import time
import subprocess
from pddlgym_planners.pddl_planner import PDDLPlanner
from pddlgym_planners.planner import PlanningFailure

FF_URL = "https://fai.cs.uni-saarland.de/hoffmann/ff/FF-v2.3.tgz"
FF_MAC_URL = "https://github.com/ronuchit/FF.git"


class FF(PDDLPlanner):
    """Fast-forward planner.
    """
    def __init__(self):
        super().__init__()
        dirname = os.path.dirname(os.path.realpath(__file__))
        self._exec = os.path.join(dirname, "FF-v2.3/ff")
        print("Instantiating FF")
        if not os.path.exists(self._exec):
            self._install_ff()
    
    def plan_from_pddl(self, dom_file, prob_file, horizon=np.inf, timeout=10,
                       remove_files=False):
        """PDDL-specific planning method.
        """
        cmd_str = self._get_cmd_str(dom_file, prob_file, timeout)
        start_time = time.time()
        output = subprocess.getoutput(cmd_str)
        if remove_files:
            os.remove(dom_file)
            os.remove(prob_file)
        self._cleanup()
        if time.time()-start_time > timeout:
            raise PlanningTimeout("Planning timed out!")
        pddl_plan = self._output_to_plan(output)
        if len(pddl_plan) > horizon:
            raise PlanningFailure("PDDL planning failed due to horizon")
        return pddl_plan

    def _get_cmd_str(self, dom_file, prob_file, timeout):
        timeout_cmd = "gtimeout" if sys.platform == "darwin" else "timeout"
        cmd_str = "{} {} {} -o {} -f {}".format(
            timeout_cmd, timeout, self._exec, dom_file, prob_file)
        return cmd_str

    def _get_cmd_str_searchonly(self, sas_file, timeout):
        raise NotImplementedError("Cannot run translate_separately=True for FF")

    def _output_to_plan(self, output):
        num_node_expansions = re.findall(r"evaluating (.+) states", output.lower())
        total_time = re.findall(r"(\d+\.\d+) seconds total time", output.lower())
        search_time = re.findall(r"(\d+\.\d+) seconds total time", output.lower())
        if "num_node_expansions" not in self._statistics:
            self._statistics["num_node_expansions"] = 0
        if len(num_node_expansions) == 1:
            assert int(num_node_expansions[0]) == float(num_node_expansions[0])
            self._statistics["num_node_expansions"] += int(
                num_node_expansions[0])
        if "found legal plan" in output:
            plan_length = re.findall(r"(\d+):", output.lower())
            self._statistics["plan_length"] = len(plan_length)
        if len(total_time) == 1:
            try: 
                total_time_float = float(total_time[0])
                self._statistics["total_time"] = total_time_float
            except:
                raise PlanningFailure("Error on output's total time format: {}".format(total_time[0]))
        if len(search_time) == 1:
            try: 
                search_time_float = float(search_time[0])
                self._statistics["search_time"] = search_time_float
            except:
                raise PlanningFailure("Error on output's search time format: {}".format(search_time[0]))
        if "goal can be simplified to FALSE" in output:
            raise PlanningFailure("Plan not found with FF! Error: {}".format(
                output))
        if "unsolvable" in output:
            raise PlanningFailure("Plan not found with FF! Error: {}".format(
                output))
        ff_plan = re.findall(r"\d+?: (.+)", output.lower())
        if not ff_plan:
            raise PlanningFailure("Plan not found with FF! Error: {}".format(
                output))
        if ff_plan[-1] == "reach-goal":
            ff_plan = ff_plan[:-1]
        return ff_plan

    def _install_ff(self):
        loc = os.path.dirname(self._exec)
        if sys.platform == "darwin":
            # Install FF patched for Mac.
            os.system("git clone {} {}".format(FF_MAC_URL, loc))
        else:
            # Install FF directly from official website.
            os.system("curl {} --output temp_ff_install.tgz".format(FF_URL))
            os.system("mkdir {}".format(loc))
            os.system("tar -xzvf temp_ff_install.tgz -C {} --strip-components 1".format(loc))
            os.system("rm temp_ff_install.tgz")
        # Compile FF.
        os.system("cd {} && make && cd -".format(loc))
        assert os.path.exists(self._exec)
