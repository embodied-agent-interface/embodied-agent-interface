import copy
import sys

from virtualhome_eval.simulation.evolving_graph.execution import ExecutionInfo
from typing import List, Dict, Any, Tuple, Union


class TemporalOrderChecker:
    def __init__(self, error_info: ExecutionInfo, prev_states: List[Dict]) -> None:
        self.error_info = error_info
        self.prev_states = prev_states
        self.msg_list = []

    def check_edge_goal(self, edge_goal: Dict, edges: List[Dict]) -> bool:
        tar_from_id = edge_goal["from_id"]
        tar_to_id = edge_goal["to_id"]
        tar_relation = edge_goal["relation"]
        is_from_id_matched = False
        is_to_id_matched = False
        is_relation_matched = False
        is_found = False
        for edge in edges:
            from_id = edge["from_id"]
            to_id = edge["to_id"]
            relation = edge["relation_type"]

            is_from_id_matched = from_id == tar_from_id or tar_from_id == -1
            is_to_id_matched = to_id == tar_to_id or tar_to_id == -1
            is_relation_matched = tar_relation in relation

            is_found = is_from_id_matched and is_to_id_matched and is_relation_matched
            if is_found:
                return True
        return False

    def check_node_goal(self, node_goal: Dict, nodes: List[Dict]) -> bool:
        tar_id = node_goal["id"]
        tar_state = node_goal["state"]

        is_id_matched = False
        is_state_matched = False
        is_found = False
        for node in nodes:
            id = node["id"]
            states = node["states"]
            is_id_matched = id == tar_id
            is_state_matched = tar_state in states
            is_found = is_id_matched and is_state_matched
            if is_found:
                return True
        return False

    def get_precond_str(self, negate, precond) -> str:
        precondition_str = ""
        if "relation" in precond:
            from_id = precond["from_id"]
            to_id = precond["to_id"]
            relation = precond["relation"]
            precondition_str = f"{relation}({from_id}, {to_id})"
        else:
            id = precond["id"]
            state = precond["state"]
            precondition_str = f"{state}({id})"
        return f"not {precondition_str}" if negate else precondition_str

    def search_in_prev_states(self, precond_pair: Tuple[bool, Dict]) -> bool:
        negate, precond = precond_pair
        is_edge_goal = "relation" in precond
        found_satisified = False
        for prev_state in self.prev_states:
            if is_edge_goal:
                edges = prev_state["edges"]
                edge_found = self.check_edge_goal(precond, edges)
                found_satisified = edge_found if not negate else not edge_found
            else:
                nodes = prev_state["nodes"]
                node_found = self.check_node_goal(precond, nodes)
                found_satisified = node_found if not negate else not node_found
            if found_satisified:
                error_msg = f"Precondition {self.get_precond_str(negate, precond)} is satisfied in previous states. "
                self.msg_list.append(error_msg)
                break
        return found_satisified

    def check_missing_preconds(self):
        self.missing_preconds = self.error_info.missing_preconds
        self.missing_connective = self.error_info.missing_connective
        preconds_found_list = []
        for precond_pair in self.missing_preconds:
            assert isinstance(precond_pair, tuple)
            precond_found = self.search_in_prev_states(precond_pair)
            preconds_found_list.append(precond_found)

        if self.missing_connective == "and":
            return all(preconds_found_list)
        elif self.missing_connective == "or":
            return any(preconds_found_list)
        else:
            return preconds_found_list[0]

    def run_checker(self) -> ExecutionInfo:
        if self.error_info.error_type != 1:
            return self.error_info
        rst = self.check_missing_preconds()
        if not rst:
            return self.error_info
        else:
            new_error_info = ExecutionInfo(True)
            error_msg = " ".join(self.msg_list)
            new_error_info.messages = copy.deepcopy(self.error_info.messages)
            new_error_info.assign_error_type("time")
            new_error_info.error(error_msg)
            return new_error_info
