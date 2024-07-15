import sys
from typing import Dict, List, Tuple

from virtualhome_eval.simulation.evolving_graph.execution import Relation, State
from virtualhome_eval.simulation.evolving_graph.scripts import (
    read_script,
    Action,
    ScriptObject,
    ScriptLine,
    ScriptParseException,
    Script,
    parse_script_line,
)
from virtualhome_eval.simulation.evolving_graph.execution import (
    ScriptExecutor,
    ExecutionInfo,
)
from virtualhome_eval.simulation.evolving_graph.environment import (
    EnvironmentGraph,
    EnvironmentState,
)
from virtualhome_eval.simulation.evolving_graph.prune_graph import *
import virtualhome_eval.simulation.evolving_graph.utils as utils


class MotionPlanner(object):
    def __init__(
        self,
        init_scene_graph,
        final_state_dict,
        name_equivalence=None,
        properties_data=None,
        object_placing=None,
        acting_char_id=None,
        instance_selection=True,
    ):
        self.env_graph = init_scene_graph
        self.name_equivalence = utils.load_name_equivalence()
        self.properties_data = utils.load_properties_data()
        self.object_placing = utils.load_object_placing()
        self.instance_selection = instance_selection

        self.init_state = EnvironmentState(
            self.env_graph, self.name_equivalence, instance_selection=instance_selection
        )
        self.final_state_dict = final_state_dict
        self.final_graph = EnvironmentGraph(final_state_dict)
        self.id_to_name = self.id_to_name()
        if acting_char_id != None:
            self.acting_char_id = acting_char_id
        else:
            for id, name in self.id_to_name.items():
                if name == "character":
                    self.acting_char_id = id
                    break

        self.env_state = EnvironmentState(
            self.env_graph, self.name_equivalence, instance_selection=instance_selection
        )
        assert self.env_state is not None

        self.executor = ScriptExecutor(self.env_graph, self.name_equivalence)

    def reset(self):
        """Reset the current state. Typically a task should be represented as a dictionary contains an initial stte, and a goal representaiton. load scene graph"""
        self.env_state = self.init_state
        # self.env.reset(task)

    def get_current_state(self):
        return self.env_state

    def get_current_state_string(self) -> str:
        """Return a string representation of the current state in self.env. For example

        return scene graph

        dictionary: dict[list]
        'nodes': list of nodes
        'edges': list of relations between nodes

        """
        return str(self.env_state.to_dict())

    def get_current_goal_string(self) -> str:
        """
        given task, find state transition, how object changes

        groundtruth: diff between init scene graph, final scene graph. Only return changed objects and relations
        """
        change_in_init, change_in_target = MotionPlanner.filter_unique_subdicts(
            self.init_state.to_dict(), self.final_state_dict
        )
        return change_in_init, change_in_target

    def get_relevant_nodes(self, script_id=None):
        diff_a, diff_b = MotionPlanner.filter_unique_subdicts(
            self.init_state.to_dict(), self.final_state_dict
        )
        existing_nodes = set()
        add_nodes = set()
        for dic in [diff_a, diff_b]:
            for d in dic["nodes"]:
                existing_nodes.add((d["class_name"], d["id"]))
        for dic in [diff_a, diff_b]:
            for d in dic["edges"]:
                add_nodes.add((self.id_to_name[d["from_id"]], d["from_id"]))
                add_nodes.add((self.id_to_name[d["to_id"]], d["to_id"]))
        all_nodes = existing_nodes.union(add_nodes)
        return all_nodes

    def get_nl_goal_string(self) -> str:
        object_in_scene = ""
        change_in_init = ""
        change_in_target = ""
        diff_a, diff_b = MotionPlanner.filter_unique_subdicts(
            self.init_state.to_dict(), self.final_state_dict
        )

        existing_nodes = set()
        add_nodes = set()
        for dic in [diff_a, diff_b]:
            for d in dic["nodes"]:
                existing_nodes.add(d["id"])
        for dic in [diff_a, diff_b]:
            for d in dic["edges"]:
                add_nodes.add(d["from_id"])
                add_nodes.add(d["to_id"])
        add_nodes = add_nodes - existing_nodes
        for node_id in add_nodes:
            diff_a["nodes"].append((self.env_graph.get_node(node_id).to_dict()))
            diff_b["nodes"].append((self.final_graph.get_node(node_id).to_dict()))

        object_in_scene += "Objects in the scene:\n"
        all_nodes = existing_nodes.union(add_nodes)
        for node_id in all_nodes:
            node_dict = self.env_graph.get_node(node_id).to_dict()
            object_in_scene += (
                str(node_dict["class_name"])
                + ", id: "
                + str(node_dict["id"])
                + ", properties: "
                + str(node_dict["properties"])
            )
            object_in_scene += "\n"
        object_in_scene += "-----------------\n"
        # print('Init scene\n')
        change_in_init += "Nodes:\n"
        for node_id in existing_nodes:
            node_dict = self.env_graph.get_node(node_id).to_dict()
            change_in_init += (
                str(node_dict["class_name"])
                + ", states: "
                + str(node_dict["states"])
                + ", properties:"
                + str(node_dict["properties"])
                + "\n"
            )
        change_in_init += "\n"
        change_in_init += "Edges:\n"
        for d in diff_a["edges"]:
            fn = self.env_graph.get_node(int(d["from_id"]))
            tn = self.env_graph.get_node(int(d["to_id"]))
            rel = d["relation_type"]
            if rel == "CLOSE":
                rel = "NEAR"
            change_in_init += f"{fn} is {rel} to {tn}\n"
        change_in_init += "-----------------\n"
        # print('Target scene\n')
        change_in_target += "Nodes:\n"
        for nid in existing_nodes:
            node_dict = self.final_graph.get_node(nid).to_dict()
            change_in_target += (
                str(node_dict["class_name"])
                + ", states: "
                + str(node_dict["states"])
                + ", properties:"
                + str(node_dict["properties"])
                + "\n"
            )
        change_in_target += "\n"
        change_in_target += "Edges:\n"
        for d in diff_b["edges"]:
            fn = self.final_graph.get_node(int(d["from_id"]))
            tn = self.final_graph.get_node(int(d["to_id"]))
            rel = d["relation_type"]
            if rel == "CLOSE":
                rel = "NEAR"
            change_in_target += f"{fn} is {rel} to {tn}\n"

        return object_in_scene, change_in_init, change_in_target

    def get_goal_describe_nl(self, task_name, task_description, object_states) -> str:
        object_in_scene = ""
        goal_str = ""
        relevant_name_to_id = {}
        cur_obj_states = {}
        diff_a, diff_b = MotionPlanner.filter_unique_subdicts(
            self.init_state.to_dict(), self.final_state_dict
        )

        existing_nodes = set()
        add_nodes = set()
        for dic in [diff_a, diff_b]:
            for d in dic["nodes"]:
                existing_nodes.add(d["id"])
        for dic in [diff_a, diff_b]:
            for d in dic["edges"]:
                add_nodes.add(d["from_id"])
                add_nodes.add(d["to_id"])
        add_nodes = add_nodes - existing_nodes

        # object_in_scene += 'Objects in the scene:\n'
        all_nodes = existing_nodes.union(add_nodes)
        character_flag = False
        for node_id in all_nodes:
            node_dict = self.env_graph.get_node(node_id).to_dict()
            if node_dict["class_name"] == "character":
                character_flag = True
            obj_state = object_states.get(node_dict["class_name"], [])
            if obj_state != []:
                obj_state = [state.upper() for state in obj_state]
            object_in_scene += (
                str(node_dict["class_name"])
                + ", initial states: "
                + str(node_dict["states"])
                + ", possible states: "
                + str(obj_state)
            )
            object_in_scene += "\n"
            relevant_name_to_id[str(node_dict["class_name"])] = node_dict["id"]
        if not character_flag:
            object_in_scene += (
                "character, initial states: "
                + str(node_dict["states"])
                + ", possible states: "
                + str(obj_state)
            )
            object_in_scene += "\n"

        goal_str += "Goal name: " + task_name + "\n"
        goal_str += "Goal description: " + task_description + "\n"

        return object_in_scene, goal_str, relevant_name_to_id

    def get_symbolic_goal_nl(self, node_goals, edge_goals, action_goals=None) -> str:
        relevant_name_to_id = {}
        object_in_scene = ""
        change_in_init = ""
        change_in_target = ""
        diff_a, diff_b = MotionPlanner.filter_unique_subdicts(
            self.init_state.to_dict(), self.final_state_dict
        )

        existing_nodes = set()
        add_nodes = set()
        for dic in [diff_a, diff_b]:
            for d in dic["nodes"]:
                existing_nodes.add(d["id"])
        for dic in [diff_a, diff_b]:
            for d in dic["edges"]:
                add_nodes.add(d["from_id"])
                add_nodes.add(d["to_id"])
        add_nodes = add_nodes - existing_nodes
        for node_id in add_nodes:
            diff_a["nodes"].append((self.env_graph.get_node(node_id).to_dict()))
            diff_b["nodes"].append((self.final_graph.get_node(node_id).to_dict()))

        object_in_scene += "Objects in the scene:\n"
        all_nodes = existing_nodes.union(add_nodes)
        for node_id in all_nodes:
            node_dict = self.env_graph.get_node(node_id).to_dict()
            object_in_scene += (
                str(node_dict["class_name"])
                + ", id: "
                + str(node_dict["id"])
                + ", properties: "
                + str(node_dict["properties"])
            )
            object_in_scene += "\n"
            relevant_name_to_id[str(node_dict["class_name"])] = node_dict["id"]
        object_in_scene += "-----------------\n"
        change_in_init += "Nodes:\n"
        for node_id in existing_nodes:
            node_dict = self.env_graph.get_node(node_id).to_dict()
            change_in_init += (
                str(node_dict["class_name"])
                + ", states: "
                + str(node_dict["states"])
                + ", properties:"
                + str(node_dict["properties"])
                + "\n"
            )
        change_in_init += "\n"
        change_in_init += "Edges:\n"
        for d in diff_a["edges"]:
            fn = self.env_graph.get_node(int(d["from_id"]))
            tn = self.env_graph.get_node(int(d["to_id"]))
            rel = d["relation_type"]
            if rel == "CLOSE":
                rel = "NEAR"
            change_in_init += f"{fn} is {rel} to {tn}\n"
        change_in_init += "-----------------\n"

        node_goal_str = ""
        for node_goal in node_goals:
            node_goal_str += (
                node_goal["class_name"] + " is " + node_goal["state"] + "\n"
            )
        node_goal_str += "-----------------\n"
        # print(f'{node_goal_str=}')

        edge_goal_str = ""
        for edge_goal in edge_goals:
            edge_goal_str += (
                self.id_to_name[edge_goal["from_id"]]
                + " is "
                + edge_goal["relation_type"]
                + " to "
                + self.id_to_name[edge_goal["to_id"]]
                + "\n"
            )
        edge_goal_str += "-----------------\n"
        # print(f'{edge_goal_str=}')
        if action_goals is not None and len(action_goals) > 0:
            action_goal_str = "The following action(s) should be included:\n"
            for action_goal in action_goals:
                if "|" in action_goal:
                    action_candidates = action_goal.split("|")
                    action_goal_str += ""
                    for action in action_candidates:
                        if action != action_candidates[-1]:
                            action_goal_str += action + " or "
                        else:
                            action_goal_str += action + "\n"
                else:
                    action_goal_str += action_goal + "\n"
                action_goal_str += action_goal + "\n"
            action_goal_str += "-----------------\n"
        else:
            action_goal_str = "There is no action requirement.\n"
        return (
            object_in_scene,
            change_in_init,
            node_goal_str,
            edge_goal_str,
            action_goal_str,
            relevant_name_to_id,
        )

    def get_id_to_name(self) -> Dict[int, str]:
        id_to_name = {}
        for d in self.init_state.to_dict()["nodes"]:
            id_to_name[d["id"]] = d["class_name"]
        for d in self.final_state_dict["nodes"]:
            if d["id"] not in id_to_name:
                id_to_name[d["id"]] = d["class_name"]
        return id_to_name

    def execute_primitive_action(self, action):
        """Proxy for self.env. Maybe need to do some translation here. Scene graph changes"""
        if "[" not in action:
            print("Wrong format! Fail to execute")
            return False
        action = action.strip()
        script_lines = []
        if len(action) > 0 and not action.startswith("#"):
            script_lines.append(MotionPlanner.parse_script_line(action, 0))
        else:
            return False
        action_script = Script(script_lines)

        prev_state = copy.deepcopy(self.env_state)
        self.env_state = next(
            self.executor.call_action_method(
                action_script,
                self.env_state,
                self.executor.info,
                self.executor.char_index,
            ),
            None,
        )
        if self.env_state is None:
            print("Fail to execute. Return to previous state.\n")
            self.env_state = prev_state
            return False
        return True

    def execute_primitive_action_script(self, action_script):
        """Proxy for self.env. Maybe need to do some translation here. Scene graph changes"""
        state_enum = self.executor.find_solutions(action_script)
        state = next(state_enum, None)
        self.env_state = state

    def my_execute_primitive_action(self, action, index=1):
        """Proxy for self.env. Maybe need to do some translation here."""

        if "[" not in action or action.startswith("#"):
            raise ValueError("Invalid action format")
        action_line = [parse_script_line(action, index)]
        action_script = Script(action_line)

        # ii. we can also self-define how this should be executed
        isSuccess, next_state = self.executor.execute_one_step(
            action_script, self.env_state
        )
        if isSuccess:
            self.env_state = next_state
        return isSuccess

    def my_execute_primitive_action_eval(self, action, index=1):
        """This function activates the evaluation mode."""
        if "[" not in action or action.startswith("#"):
            raise ValueError("Invalid action format")
        action_line = [parse_script_line(action, index)]
        action_script = Script(action_line)

        my_info = ExecutionInfo(eval_mode=True)
        success = True
        next_state = next(
            self.executor.call_action_method(
                action_script, self.env_state, my_info, self.executor.char_index
            ),
            None,
        )
        if next_state is None:
            success = False
        else:
            self.env_state = next_state
        return success, my_info

    def execute_sequence_primitive_action(self, actions) -> bool:
        """Whether goal string satisfied after actions"""
        for action in actions:
            try:
                self.execute_primitive_action(action)
            except:
                print(f"{action} fails")
                self.execute_primitive_action(action)
        cur_state, target_state = MotionPlanner.filter_unique_subdicts(
            self.env_state.to_dict(), self.final_state_dict
        )
        return MotionPlanner.check_state_dict_same(cur_state, target_state)

    def incremental_subgoal_plan(self, subgoals, search_budget) -> bool:
        """Based on the current state, search for an (optimal) plan that achieves all subgoals in the list.
        This can be implemented by a BFS search.

        subgoal: list[str], search_budget: int
        subgoal format:
        1. Relation: '#RELATION# <Object1> (id1) <Object2> (id2)'
        2. State: '<Object> (id): {STATE}'

        eg.
        1. '#CLOSE# <fridge> (234) <char162> (162)'
        2. '<fridge> (234): {OPEN}'

        Args:
            subgoal: a sequence of strings representing a conjunction of primitive propositions (i.e. grounded predicates).
                For example, ['inventory-holding A', 'object-of-type B SugarCane']
            search_budget: a search budget specification, either in time (s) or the maximum number of expanded nodes.

        Returns:
            True if the subgoal has been achieved within a search budget.
        """

        possible_primitive_actions = ["Open", "Walk"]

        acting_char_node = self.env_state.get_char_node(self.acting_char_id)
        relevant_obj_list = []

        prev_state = copy.deepcopy(self.env_state)
        rel_subgoals = []
        state_subgoals = []

        for subgoal in subgoals:
            subgoal_type, subgoal_args = MotionPlanner.parse_subgoal(subgoal)
            if subgoal_type == "relation_goal":
                relation, obj1, id1, obj2, id2 = subgoal_args
                id1 = int(id1)
                id2 = int(id2)
                if id1 != self.acting_char_id:
                    relevant_obj_list.append((id1, obj1))
                if id2 != self.acting_char_id:
                    relevant_obj_list.append((id2, obj2))
                rel_subgoals.append(
                    {"from_id": id1, "relation_type": relation, "to_id": id2}
                )
            elif subgoal_type == "state_goal":
                obj, id, state = subgoal_args
                id = int(id)
                state = state.upper()
                if id != self.acting_char_id:
                    relevant_obj_list.append((id, obj))
                original_state = self.env_state.get_node(id).to_dict()
                assert original_state["id"] == id
                target_node_state_dict = copy.deepcopy(original_state)
                target_node_state_dict["states"] = [state]
                state_subgoals.append(target_node_state_dict)
            else:
                raise ValueError("Invalid subgoal type")

        relevant_obj_list = list(set(relevant_obj_list))

        # Starting BFS
        queue = list()
        queue.append((self.env_state, 0))
        print(f"[0] Start searching for subgoal plan\n")
        search_steps = 0
        search_id_to_action = {}
        search_id_to_child_id = {}

        idx = 1
        while search_steps < search_budget:
            print("---------\n")
            print(f"Search step {search_steps} starts!\n")
            step_state_candidates = []
            while queue:
                self.env_state, state_idx = queue.pop(0)
                prev_state = copy.deepcopy(self.env_state)
                # enumerate all possible actions on all relevant objects
                for possible_obj in relevant_obj_list:
                    for action in possible_primitive_actions:
                        # check whether the action is applicable
                        attempt_action = (
                            f"[{action}] <{possible_obj[1]}> ({possible_obj[0]})"
                        )
                        search_id_to_action[idx] = attempt_action
                        if state_idx not in search_id_to_child_id:
                            search_id_to_child_id[state_idx] = [idx]
                        else:
                            search_id_to_child_id[state_idx].append(idx)
                        try:
                            self.execute_primitive_action(attempt_action)
                            # check whether subgoal is achieved
                            if MotionPlanner.check_relation_satisfied(
                                self.env_state, rel_subgoals
                            ) and MotionPlanner.check_state_satisfied(
                                self.env_state, state_subgoals
                            ):
                                print(
                                    f"[{idx}] attempt action: {attempt_action} SUCCEED!\n"
                                )
                                success_action = MotionPlanner.trace_success_path(
                                    search_id_to_child_id, idx, search_id_to_action
                                )
                                print("subgoal achieved by action: ", success_action)
                                print("---------\n")
                                return True
                            else:
                                print(
                                    f"[{idx}] attempt action: {attempt_action} NOT YET ACHIEVED, based on {state_idx} state. Continue searching."
                                )
                                step_state_candidates.append(
                                    (copy.deepcopy(self.env_state), idx)
                                )
                                idx += 1
                                self.env_state = prev_state
                        except:
                            print(
                                f"attempt action: [{attempt_action}] <{possible_obj}> FAILED"
                            )
            queue = step_state_candidates
            search_steps += 1

        print(
            f"Tried all actions on all relevent objectes for {search_budget} steps, but FAILED!"
        )
        print("---------\n")
        return False

    def execute_subgoal_sequence(
        self, subgoals: list, search_budget_per_subgoal
    ) -> bool:
        """
        check whether all subgoals can be satisfied.
        subgoals: list[list[str]], search_budget_per_subgoal: int
        """
        for subgoal in subgoals:
            rv = self.incremental_subgoal_plan(subgoal, search_budget_per_subgoal)
            if not rv:
                return False
        return True

    def id_to_name(self):
        id_to_name = {}
        for d in self.init_state.to_dict()["nodes"]:
            id_to_name[d["id"]] = d["class_name"]
        for d in self.final_state_dict["nodes"]:
            if d["id"] not in id_to_name:
                id_to_name[d["id"]] = d["class_name"]
        return id_to_name

    @staticmethod
    def check_relation_satisfied(state, rel_subgoals):
        cur_state_dict = state.to_dict()
        for d in rel_subgoals:
            if d not in cur_state_dict["edges"]:
                return False
        return True

    @staticmethod
    def check_state_satisfied(state, state_subgoals):
        cur_state_dict = state.to_dict()
        for d in state_subgoals:
            if d not in cur_state_dict["nodes"]:
                return False
        return True

    @staticmethod
    def trace_success_path(search_id_to_child_id, s_id, search_id_to_action):
        # convert search_id_to_child_id to search_child_id_to_id
        search_child_id_to_id = {}
        for k, v in search_id_to_child_id.items():
            for c in v:
                if c not in search_child_id_to_id:
                    search_child_id_to_id[c] = [k]
                else:
                    search_child_id_to_id[c].append(k)
        action_path = []
        while s_id != 0:
            action_path.append(search_id_to_action[s_id])
            s_id = search_child_id_to_id[s_id][0]
        action_path = action_path[::-1]
        return action_path

    @staticmethod
    def filter_unique_subdicts(dict_a, dict_b, key1="nodes", key2="edges"):
        d_a = {}
        d_b = {}

        for key in [key1, key2]:
            set_a = set()
            set_b = set()
            for d in dict_a[key]:
                if key == "nodes":
                    d["properties"] = sorted(d["properties"])
                    d["states"] = sorted(d["states"])
                set_a.add(str(d))
            for d in dict_b[key]:
                if key == "nodes":
                    d["properties"] = sorted(d["properties"])
                    d["states"] = sorted(d["states"])
                set_b.add(str(d))
            unique_in_a = set_a - set_b
            unique_in_b = set_b - set_a
            d_a[key] = [eval(d) for d in unique_in_a]
            d_b[key] = [eval(d) for d in unique_in_b]
        return d_a, d_b

    @staticmethod
    def get_node_edge_changes(diff_in_current, diff_in_final):
        nodes_changes = {
            "add": copy.deepcopy(diff_in_final["nodes"]),  #
            "remove": copy.deepcopy(diff_in_current["nodes"]),
            "modify": [],
        }
        edge_changes = {
            "add": copy.deepcopy(diff_in_final["edges"]),
            "remove": copy.deepcopy(diff_in_current["edges"]),
            "modify": [],
        }
        for node in diff_in_current["nodes"]:
            init_object_id = node["id"]
            for final_node in diff_in_final["nodes"]:
                final_object_id = final_node["id"]
                if init_object_id == final_object_id:
                    nodes_changes["modify"].append((node, final_node))
                    nodes_changes["add"].remove(final_node)
                    nodes_changes["remove"].remove(node)
                    list.remove
                    break
        for edge in diff_in_current["edges"]:
            init_from_id, init_to_id, init_relation_type = (
                edge["from_id"],
                edge["to_id"],
                edge["relation_type"],
            )
            for final_edge in diff_in_final["edges"]:
                final_from_id, final_to_id, final_relation_type = (
                    final_edge["from_id"],
                    final_edge["to_id"],
                    final_edge["relation_type"],
                )
                try:
                    if init_from_id == final_from_id and init_to_id == final_to_id:
                        edge_changes["modify"].append((edge, final_edge))
                        edge_changes["add"].remove(
                            final_edge
                        ) if final_edge in edge_changes["add"] else None
                        edge_changes["remove"].remove(edge) if edge in edge_changes[
                            "remove"
                        ] else None
                except:
                    print(f"diff_in_current: {diff_in_current}\n\n")
                    print(f"diff_in_final: {diff_in_final}\n\n")
                    print(f"edge_changes: {edge_changes}")
                    print(f"edge: {edge}, final_edge: {final_edge}")
                    assert False

        return nodes_changes, edge_changes

    @staticmethod
    def check_state_dict_same(dict_a, dict_b):
        return (
            len(dict_a["nodes"]) == 0
            and len(dict_a["edges"]) == 0
            and len(dict_b["nodes"]) == 0
            and len(dict_b["edges"]) == 0
        )

    @staticmethod
    def show_status_change_direct(start_state, end_state, init_scene_graph, out_file):
        diff_a, diff_b = MotionPlanner.filter_unique_subdicts(
            start_state.to_dict(), end_state.to_dict()
        )

        existing_nodes = set()
        add_nodes = set()
        for dic in [diff_a, diff_b]:
            for d in dic["nodes"]:
                existing_nodes.add(d["id"])
        for dic in [diff_a, diff_b]:
            for d in dic["edges"]:
                add_nodes.add(d["from_id"])
                add_nodes.add(d["to_id"])
        add_nodes = add_nodes - existing_nodes
        for node_id in add_nodes:
            diff_a["nodes"].append((init_scene_graph.get_node(node_id).to_dict()))
            diff_b["nodes"].append((init_scene_graph.get_node(node_id).to_dict()))

        if out_file is None:
            print("Objects in the scene:\n")
            all_nodes = existing_nodes.union(add_nodes)
            for node_id in all_nodes:
                print(init_scene_graph.get_node(node_id).__str__())
                print("\n")
            print("-----------------\n")
            print("Init scene\n")
            print("Nodes:\n")
            for n in existing_nodes:
                print(str(start_state.get_node(n).to_dict()))
            print("\n")
            print("Edges:\n")
            for d in diff_a["edges"]:
                fn = init_scene_graph.get_node(int(d["from_id"]))
                tn = init_scene_graph.get_node(int(d["to_id"]))
                relation = d["relation_type"]
                print(f"{fn} is {relation} to {tn}\n")
            print("-----------------\n")
            print("Target scene\n")
            print("Nodes:\n")
            for n in existing_nodes:
                print(str(end_state.get_node(n).to_dict()))
            print("\n")
            print("Edges:\n")
            for d in diff_b["edges"]:
                fn = init_scene_graph.get_node(int(d["from_id"]))
                tn = init_scene_graph.get_node(int(d["to_id"]))
                print(f"{fn} is {relation} to {tn}\n")
            return

        with open(out_file, "w") as f:
            f.write("Objects in the scene:\n")
            all_nodes = existing_nodes.union(add_nodes)
            for node_id in all_nodes:
                f.write(init_scene_graph.get_node(node_id).__str__())
                f.write("\n")
            f.write("-----------------\n")
            f.write("Init scene\n")
            f.write("Nodes:\n")
            for n in existing_nodes:
                f.write(str(start_state.get_node(n).to_dict()))
            f.write("\n")
            f.write("Edges:\n")
            for d in diff_a["edges"]:
                fn = init_scene_graph.get_node(int(d["from_id"]))
                tn = init_scene_graph.get_node(int(d["to_id"]))
                relation = d["relation_type"]
                f.write(f"{fn} is {relation} to {tn}\n")
            f.write("-----------------\n")
            f.write("Target scene\n")
            f.write("Nodes:\n")
            for n in existing_nodes:
                f.write(str(end_state.get_node(n).to_dict()))
            f.write("\n")
            f.write("Edges:\n")
            for d in diff_b["edges"]:
                fn = init_scene_graph.get_node(int(d["from_id"]))
                tn = init_scene_graph.get_node(int(d["to_id"]))
                f.write(f"{fn} is {relation} to {tn}\n")

    @staticmethod
    def correct_data_format(data_line):
        # Pattern to match strings and capture the relevant groups
        # This pattern accounts for all three formats.
        pattern = r"""
            \[([A-Z]+)\]                            # Matches the action name
            (?:\s*([^<>\(\)]+)\s*\((\d+)\))?        # Optionally matches the first object and ID
            (?:\s*([^<>\(\)]+)\s*\((\d+)\))?        # Optionally matches the second object and ID
        """

        def add_brackets(match):
            action = match.group(1)
            parts = [f"[{action}]"]
            for i in range(2, 6, 2):  # Process matched object groups
                object_name = match.group(i)
                object_id = match.group(i + 1)
                if object_name and object_id:
                    parts.append(f"<{object_name.strip()}> ({object_id})")

            return " ".join(parts)

        corrected_line = re.sub(pattern, add_brackets, data_line, flags=re.VERBOSE)
        return corrected_line

    @staticmethod
    def parse_script_line(string, index):
        """
        :param string: script line in format [action] <object> (object_instance) <subject> (object_instance)
        :return: ScriptLine objects; raises ScriptParseException
        """
        params = []
        patt_action = r"^\[(\w+)\]"
        patt_params = r"\<(.+?)\>\s*\((.+?)\)"
        string = MotionPlanner.correct_data_format(string)

        action_match = re.search(patt_action, string.strip())
        if not action_match:
            raise ScriptParseException("Cannot parse action")
        action_string = action_match.group(1).upper()
        if action_string not in Action.__members__:
            raise ScriptParseException('Unknown action "{}"', action_string)
        action = Action[action_string]

        param_match = re.search(patt_params, action_match.string[action_match.end(1) :])

        while param_match:
            params.append(ScriptObject(param_match.group(1), int(param_match.group(2))))
            param_match = re.search(
                patt_params, param_match.string[param_match.end(2) :]
            )

        if len(params) != action.value[1]:
            raise ScriptParseException(
                'Wrong number of parameters for "{}". Got {}, expected {}',
                action.name,
                len(params),
                action.value[1],
            )

        return ScriptLine(action, params, index)

    @staticmethod
    def parse_subgoal(input_string):
        relation_pattern = (
            r"#([A-Za-z_]+)#\s+<([^>]+)>\s+\((\w+)\)\s+<([^>]+)>\s+\((\w+)\)"
        )
        state_pattern = r"<([^>]+)>\s+\((\w+)\):\s+\{(.+)\}"
        if re.match(relation_pattern, input_string):
            match = re.match(relation_pattern, input_string)
            if match:
                return "relation_goal", (
                    match.group(1),
                    match.group(2),
                    match.group(3),
                    match.group(4),
                    match.group(5),
                )
            else:
                return "Invalid relation format"
        elif re.match(state_pattern, input_string):
            match = re.match(state_pattern, input_string)
            if match:
                return "state_goal", (match.group(1), match.group(2), match.group(3))
            else:
                return "Invalid state format"
        else:
            return "Invalid input format"
