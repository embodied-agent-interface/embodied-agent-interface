"""General interface for a planner.
"""

import abc
import numpy as np


class Planner:
    """An abstract planner for PDDLGym.
    """
    def __init__(self):
        self._statistics = {}

    @abc.abstractmethod
    def __call__(self, domain, state, horizon=np.inf, timeout=10,
                 return_files=False, translate_separately=False):
        """Takes in a PDDLGym domain and PDDLGym state. Returns a plan.
        Note that the state already contains the goal, accessible via
        `state.goal`. The domain for an env is given by `env.domain`.
        """
        raise NotImplementedError("Override me!")

    def reset_statistics(self):
        """Reset the internal statistics dictionary.
        """
        self._statistics = {}

    def get_statistics(self):
        """Get the internal statistics dictionary.
        """
        return self._statistics


class PlanningFailure(Exception):
    """Exception raised when planning fails.
    """
    pass


class PlanningTimeout(Exception):
    """Exception raised when planning times out.
    """
    pass
