import json
import sys
sys.path.append('../simulation')
from enum import Enum
import re
import json
import copy

import evolving_graph.utils as utils
from evolving_graph.execution import Relation, State
from evolving_graph.scripts import read_script, Action, ScriptObject, ScriptLine, ScriptParseException, Script
from evolving_graph.execution import ScriptExecutor
from evolving_graph.environment import EnvironmentGraph, EnvironmentState
from evolving_graph.preparation import AddMissingScriptObjects, AddRandomObjects, ChangeObjectStates, \
    StatePrepare, AddObject, ChangeState, Destination



class MotionPlanner(object):
    def __init__(self, init_scene_graph, final_state_dict, name_equivalence, properties_data, object_placing, acting_char_id=162, instance_selection=False):
        self.env_graph = init_scene_graph
        self.name_equivalence = name_equivalence
        self.properties_data = properties_data
        self.object_placing = object_placing
        self.acting_char_id = acting_char_id
        self.instance_selection = instance_selection
        
        self.init_state = EnvironmentState(self.env_graph, self.name_equivalence, instance_selection=instance_selection)
        self.final_state_dict = final_state_dict

        self.env_state = EnvironmentState(self.env_graph, self.name_equivalence, instance_selection=instance_selection)
        
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
        '''
        given task, find state transition, how object changes

        groundtruth: diff between init scene graph, final scene graph. Only return changed objects and relations
        '''
        change_in_init, change_in_target = MotionPlanner.filter_unique_subdicts(self.init_state.to_dict(), self.final_state_dict)
        return change_in_init, change_in_target

    def execute_primitive_action(self, action):
        """Proxy for self.env. Maybe need to do some translation here. Scene graph changes"""
        if '[' not in action:
            print('Wrong format! Fail to execute')
            return 
        action = action.strip()
        script_lines = []
        if len(action) > 0 and not action.startswith('#'):
            script_lines.append(MotionPlanner.parse_script_line(action, 0))
        else:
            return
        action_script = Script(script_lines)

        prev_state = copy.deepcopy(self.env_state)
        self.env_state = next(self.executor.call_action_method(action_script, self.env_state, self.executor.info, self.executor.char_index), None)
        if self.env_state is None:
            print(f'Fail to execute {action}. Return to previous state.\n')
            self.env_state = prev_state
            return
    
    def execute_primitive_action_script(self, action_script):
        """Proxy for self.env. Maybe need to do some translation here. Scene graph changes"""
        state_enum = self.executor.find_solutions(action_script)
        state = next(state_enum, None)
        self.env_state = state

    def execute_sequence_primitive_action(self, actions) -> bool:
        """Whether goal string satisfied after actions"""
        for action in actions:
            self.execute_primitive_action(action)
        cur_state, target_state = MotionPlanner.filter_unique_subdicts(self.env_state.to_dict(), self.final_state_dict)
        print(f'{cur_state=}')
        print(f'{target_state=}')
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

        possible_primitive_actions = ['Open', 'Walk']
        
        acting_char_node = self.env_state.get_char_node(self.acting_char_id)
        relevant_obj_list = []

        prev_state = copy.deepcopy(self.env_state)
        rel_subgoals = []
        state_subgoals = []

        for subgoal in subgoals:
            subgoal_type, subgoal_args = MotionPlanner.parse_subgoal(subgoal)
            if subgoal_type == 'relation_goal':
                relation, obj1, id1, obj2, id2 = subgoal_args
                id1 = int(id1)
                id2 = int(id2)
                if id1 != self.acting_char_id:
                    relevant_obj_list.append((id1, obj1))
                if id2 != self.acting_char_id:
                    relevant_obj_list.append((id2, obj2))
                rel_subgoals.append({'from_id': id1, 'relation_type': relation, 'to_id': id2})
            elif subgoal_type == 'state_goal':
                obj, id, state = subgoal_args
                id = int(id)
                state = state.upper()
                if id != self.acting_char_id:
                    relevant_obj_list.append((id, obj))
                original_state = self.env_state.get_node(id).to_dict()
                assert original_state['id'] == id
                target_node_state_dict = copy.deepcopy(original_state)
                target_node_state_dict['states'] = [state]
                state_subgoals.append(target_node_state_dict)
            else:
                raise ValueError('Invalid subgoal type')
        
        relevant_obj_list = list(set(relevant_obj_list))

        # Starting BFS
        queue = list()
        queue.append((self.env_state, 0))
        print(f'[0] Start searching for subgoal plan\n')
        search_steps = 0
        search_id_to_action = {}
        search_id_to_child_id = {}

        idx = 1
        while search_steps < search_budget:
            print('---------\n')
            print(f'Search step {search_steps} starts!\n')
            step_state_candidates = []
            while queue:
                self.env_state, state_idx = queue.pop(0)
                prev_state = copy.deepcopy(self.env_state)
                # enumerate all possible actions on all relevant objects
                for possible_obj in relevant_obj_list:
                    for action in possible_primitive_actions:
                        # check whether the action is applicable
                        attempt_action = f'[{action}] <{possible_obj[1]}> ({possible_obj[0]})'
                        search_id_to_action[idx] = attempt_action
                        if state_idx not in search_id_to_child_id:
                            search_id_to_child_id[state_idx] = [idx]
                        else:
                            search_id_to_child_id[state_idx].append(idx)
                        try:
                            self.execute_primitive_action(attempt_action)
                            # check whether subgoal is achieved
                            if MotionPlanner.check_relation_satisfied(self.env_state, rel_subgoals) and MotionPlanner.check_state_satisfied(self.env_state, state_subgoals):
                                print(f'[{idx}] attempt action: {attempt_action} SUCCEED!\n')
                                success_action = MotionPlanner.trace_success_path(search_id_to_child_id,idx,search_id_to_action)
                                print('subgoal achieved by action: ', success_action)
                                print('---------\n')
                                return True
                            else:
                                print(f'[{idx}] attempt action: {attempt_action} NOT YET ACHIEVED, based on {state_idx} state. Continue searching.')
                                step_state_candidates.append((copy.deepcopy(self.env_state), idx))
                                idx += 1
                                self.env_state = prev_state
                        except:
                            print(f'attempt action: [{attempt_action}] <{possible_obj}> FAILED')
            queue = step_state_candidates
            search_steps += 1
        
        print(f'Tried all actions on all relevent objectes for {search_budget} steps, but FAILED!')
        print('---------\n')
        return False

    def execute_subgoal_sequence(self, subgoals: list, search_budget_per_subgoal) -> bool:
        """ 
        check whether all subgoals can be satisfied. 
        subgoals: list[list[str]], search_budget_per_subgoal: int
        """
        for subgoal in subgoals:
            rv = self.incremental_subgoal_plan(subgoal,search_budget_per_subgoal)
            if not rv:
                return False
        return True
    
    @staticmethod
    def check_relation_satisfied(state, rel_subgoals):
        cur_state_dict = state.to_dict()
        for d in rel_subgoals:
            if d not in cur_state_dict['edges']:
                return False
        return True
    
    @staticmethod 
    def check_state_satisfied(state, state_subgoals):
        cur_state_dict = state.to_dict()
        for d in state_subgoals:
            if d not in cur_state_dict['nodes']:
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

    def check_final_state(self, state):
        cur_state, target_state = MotionPlanner.filter_unique_subdicts(state.to_dict(), self.final_state_dict)
        return MotionPlanner.check_state_dict_same(cur_state, target_state)

    @staticmethod   
    def filter_unique_subdicts(dict_a, dict_b, key1='nodes', key2='edges'):
        d_a = {}
        d_b = {}

        for key in [key1, key2]:
            set_a = set()
            set_b = set()
            for d in dict_a[key]:
                if key == 'nodes':
                    d['properties'] = sorted(d['properties'])
                    d['states'] = sorted(d['states'])
                set_a.add(str(d))
            for d in dict_b[key]:
                if key == 'nodes':
                    d['properties'] = sorted(d['properties'])
                    d['states'] = sorted(d['states'])
                set_b.add(str(d)) 
            unique_in_a = set_a - set_b
            unique_in_b = set_b - set_a
            d_a[key] = [eval(d) for d in unique_in_a]
            d_b[key] = [eval(d) for d in unique_in_b]
        return d_a, d_b

    @staticmethod   
    def check_state_dict_same(dict_a, dict_b):
        return len(dict_a['nodes']) == 0 and len(dict_a['edges']) == 0 and len(dict_b['nodes']) == 0 and len(dict_b['edges']) == 0

    @staticmethod
    def show_status_change_direct(start_state, end_state, init_scene_graph, out_file):
        diff_a, diff_b = MotionPlanner.filter_unique_subdicts(start_state.to_dict(), end_state.to_dict())

        existing_nodes = set()
        add_nodes = set()
        for dic in [diff_a, diff_b]:
            for d in dic['nodes']:
                existing_nodes.add(d['id'])
        for dic in [diff_a, diff_b]:
            for d in dic['edges']:
                add_nodes.add(d['from_id'])
                add_nodes.add(d['to_id'])
        add_nodes = add_nodes - existing_nodes
        for node_id in add_nodes:
            diff_a['nodes'].append((init_scene_graph.get_node(node_id).to_dict()))
            diff_b['nodes'].append((init_scene_graph.get_node(node_id).to_dict()))

        if out_file is None:
            print('Objects in the scene:\n')
            all_nodes = existing_nodes.union(add_nodes)
            for node_id in all_nodes:
                print(init_scene_graph.get_node(node_id).__str__())
                print('\n')
            print('-----------------\n')
            print('Init scene\n')
            print('Nodes:\n')
            for n in existing_nodes:
                print(str(start_state.get_node(n).to_dict()))
            print('\n')
            print('Edges:\n')
            for d in diff_a['edges']:
                fn = init_scene_graph.get_node(int(d['from_id']))
                tn = init_scene_graph.get_node(int(d['to_id']))
                relation = d['relation_type']
                print(f'{fn} is {relation} to {tn}\n')
            print('-----------------\n')
            print('Target scene\n')
            print('Nodes:\n')
            for n in existing_nodes:
                print(str(end_state.get_node(n).to_dict()))
            print('\n')
            print('Edges:\n')
            for d in diff_b['edges']:
                fn = init_scene_graph.get_node(int(d['from_id']))
                tn = init_scene_graph.get_node(int(d['to_id']))
                print(f'{fn} is {relation} to {tn}\n')
            return

        with open(out_file, 'w') as f:
            f.write('Objects in the scene:\n')
            all_nodes = existing_nodes.union(add_nodes)
            for node_id in all_nodes:
                f.write(init_scene_graph.get_node(node_id).__str__())
                f.write('\n')
            f.write('-----------------\n')
            f.write('Init scene\n')
            f.write('Nodes:\n')
            for n in existing_nodes:
                f.write(str(start_state.get_node(n).to_dict()))
            f.write('\n')
            f.write('Edges:\n')
            for d in diff_a['edges']:
                fn = init_scene_graph.get_node(int(d['from_id']))
                tn = init_scene_graph.get_node(int(d['to_id']))
                relation = d['relation_type']
                f.write(f'{fn} is {relation} to {tn}\n')
            f.write('-----------------\n')
            f.write('Target scene\n')
            f.write('Nodes:\n')
            for n in existing_nodes:
                f.write(str(end_state.get_node(n).to_dict()))
            f.write('\n')
            f.write('Edges:\n')
            for d in diff_b['edges']:
                fn = init_scene_graph.get_node(int(d['from_id']))
                tn = init_scene_graph.get_node(int(d['to_id']))
                f.write(f'{fn} is {relation} to {tn}\n')
    
    @staticmethod
    def parse_script_line(string, index):
        """
        :param string: script line in format [action] <object> (object_instance) <subject> (object_instance)
        :return: ScriptLine objects; raises ScriptParseException
        """
        params = []

        patt_action = r'^\[(\w+)\]'
        patt_params = r'\<(.+?)\>\s*\((.+?)\)'

        action_match = re.search(patt_action, string.strip())
        if not action_match:
            raise ScriptParseException('Cannot parse action')
        action_string = action_match.group(1).upper()
        if action_string not in Action.__members__:
            raise ScriptParseException('Unknown action "{}"', action_string)
        action = Action[action_string]

        param_match = re.search(patt_params, action_match.string[action_match.end(1):])
        while param_match:
            params.append(ScriptObject(param_match.group(1), int(param_match.group(2))))
            param_match = re.search(patt_params, param_match.string[param_match.end(2):])

        if len(params) != action.value[1]:
            raise ScriptParseException('Wrong number of parameters for "{}". Got {}, expected {}',
                                    action.name, len(params), action.value[1])

        return ScriptLine(action, params, index)

    @staticmethod
    def parse_subgoal(input_string):
        relation_pattern = r'#([A-Za-z_]+)#\s+<([^>]+)>\s+\((\w+)\)\s+<([^>]+)>\s+\((\w+)\)'
        state_pattern = r'<([^>]+)>\s+\((\w+)\):\s+\{(.+)\}'
        if re.match(relation_pattern, input_string):
            match = re.match(relation_pattern, input_string)
            if match:
                return 'relation_goal', (match.group(1), match.group(2), match.group(3), match.group(4), match.group(5))
            else:
                return "Invalid relation format"
        elif re.match(state_pattern, input_string):
            match = re.match(state_pattern, input_string)
            if match:
                return 'state_goal', (match.group(1), match.group(2), match.group(3))
            else:
                return "Invalid state format"
        else:
            return "Invalid input format"


def evaluate_pure_motion_plan_succ(dataset, motion_planner: MotionPlanner):
    succ = 0
    for task in dataset:
        motion_planner.reset(task)
        state, goal = motion_planner.get_current_state_string(), motion_planner.get_current_goal_string()
        symbolic_goal = prompt_for_symbolic_goal_from_natural_language_goal(state, goal)
        # additionally, you can evaluate on the sybmolic goal accuracy by matching two "programs"
        succ += int(motion_planner.execute_subgoal_sequence([symbolic_goal]))
    return succ / len(dataset)


def evaluate_action_plan_succ(dataset, motion_planner: MotionPlanner):
    succ = 0
    for task in dataset:
        motion_planner.reset(task)
        state, goal = motion_planner.get_current_state_string(), motion_planner.get_current_goal_string()
        actions = prompt_for_action_sequence_plan(state, goal)
        succ += int(motion_planner.execute_sequence_primitive_action(actions))
    return succ / len(dataset)


def evaluate_subgoal_plan_succ(dataset, motion_planner: MotionPlanner):
    succ = 0
    for task in dataset:
        motion_planner.reset(task)
        state, goal = motion_planner.get_current_state_string(), motion_planner.get_current_goal_string()
        subgoals = prompt_for_subgoal_sequence_plan(state, goal)
        succ += int(motion_planner.execute_subgoal_sequence(actions))
    return succ / len(dataset)


def evaluate_operator_proposal_succ(dataset, motion_planner: MotionPlanner):
    operator_names = set()
    for task in dataset:
        operator_names |= prompt_for_candidate_operator_name_and_argument_sequence(task.state, task.goal)
    # For example, you will get
    # { (heat A1 B3) (clean A3 B3) }

    operators = set()
    for operator_name_and_arguments in operator_names:
        operators.add(prompt_for_operator_body(operator_name_and_arguments))

    for task in dataset:
        motion_planner.reset(task)
        pddl_actions = pddl_planner(operator, motion_planner.get_current_state_string(), motion_planner.get_current_goal_string())
        pddl_action_effects = [action.grounded_effects in pddl_actions]
        succ += int(motion_planner.execute_subgoal_sequence(actions))
    
    return succ / len(dataset)


def ada(dataset, motion_planner: MotionPlanner):
    current_operators = set()
    for i in range(10):
        operator_names = set()
        for task in dataset:
            if not task.solved:
                operator_names |= prompt_for_candidate_operator_name_and_argument_sequence(task.state, task.goal)

        operators = set()
        for operator_name_and_arguments in operator_names:
            operators.add(prompt_for_operator_body(operator_name_and_arguments))

        all_current_iteration_operators = operators | current_operators

        for task in dataset:
            motion_planner.reset(task)
            pddl_actions = pddl_planner(operator, motion_planner.get_current_state_string(), motion_planner.get_current_goal_string())
            pddl_action_effects = [action.grounded_effects in pddl_actions]
            task.solution = pddl_actions
            task.solved = motion_planner.execute_subgoal_sequence(actions)

        operator_score = dict()
        # not exactly, but similar
        for task in dataaset:
            for action in task.solution:
                operator_score[action.operator_name] += int(task.solved)
        current_operators = {all_current_iteration_operators[o] for o, s in operator_score.items() if s > 0}
        
    return current_operators


def main():
    print('Example 1')
    print('---------')
    
    # load object alias, states, and placing
    properties_data = utils.load_properties_data()
    object_states = utils.load_object_states()
    object_placing = utils.load_object_placing()
    name_equivalence = utils.load_name_equivalence()

    # init graph
    init_scene_graph = utils.load_graph('../example_graphs/TestScene6_graph.json')
    # Task action sequence
    script = read_script('example_scripts/example_script_1.txt')
    # final state (ground truth)
    final_state_path = '/viscam/u/shiyuz/virtualhome/virtualhome/example_graphs/processed/TestScene6_graph_script1_res.json'

    with open(final_state_path, 'r') as f:
        final_state_dict = json.load(f)
    
    planner = MotionPlanner(init_scene_graph, final_state_dict, name_equivalence, properties_data, object_placing)

    # func1 and func2 (reset, get_current_state_string)
    planner.reset()
    # print(planner.get_current_state_string())
    # func3 (get_current_goal_string)
    change_in_init, change_in_target = planner.get_current_goal_string()

    # test of (execute_primitive_action_script)
    planner.reset()
    before_state = planner.get_current_state()
    planner.execute_primitive_action_script(script)
    after_state = planner.get_current_state()
    

    out_file = '../example_graphs/processed/TestScene6_graph_script1_planner.txt'
    planner.show_status_change_direct(before_state, after_state, init_scene_graph, out_file)
    suc = planner.check_final_state(after_state)

    print(f'test 4: {suc}')
    print('finish test 4 on func execute_primitive_action_script()')


    # test of func4 and 5 (execute_primitive_action, execute_sequence_primitive_action)
    # test of execution commands sequence
    planner.reset()
    actions = ['[Find] <plate> (1)', '[Grab] <plate> (1)','[Find] <microwave> (1)', '[Open] <microwave> (1)', '[PutIn] <plate> (1) <microwave> (1)', '[SwitchOn] <microwave> (1)', '[Find] <milk> (1)', '[Grab] <milk> (1)', '[Drink] <milk> (1)', '[Find] <chair> (1)', '[Sit] <chair> (1)']
    before_state = planner.get_current_state()
    suc = planner.execute_sequence_primitive_action(actions)
    after_state = planner.get_current_state()

    print(f'execute success: {suc}')

    out_file = '../example_graphs/processed/TestScene6_graph_script1_planner_seq.txt'
    planner.show_status_change_direct(before_state, after_state, init_scene_graph, out_file)
    print('finish test 5 on func execute_primitive_action() and execute_sequence_primitive_action()')

    # test of func6 (incremental_subgoal_plan)
    planner.reset()
    subgoals = ['#CLOSE# <fridge> (1) <char162> (162)', '<fridge> (234): {OPEN}']
    suc = planner.incremental_subgoal_plan(subgoals, 2)
    print(f'incremental subgoal plan success: {suc}')
    print('finish test 6 on func incremental_subgoal_plan()')

    # # test of func7 (execute_subgoal_sequence)
    # planner.reset()
    # subgoals = [['#CLOSE# <fridge> (234) <char162> (162)'], ['<fridge> (234): {OPEN}']]
    # suc = planner.execute_subgoal_sequence(subgoals, 1)
    # print(f'execute subgoal sequence success: {suc}')
    # print('finish test 7 on func execute_subgoal_sequence()')

    
if __name__ == "__main__":
    main()