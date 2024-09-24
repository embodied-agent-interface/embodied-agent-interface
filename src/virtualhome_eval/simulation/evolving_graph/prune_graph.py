import json
import copy
import os


def input_selection(mode, key, value) -> str:
    prompt_str = f'\n[{key}]: {value}\n Do you want to keep this {mode} state? (y/n/m): '
    input_str = input(prompt_str)
    while input_str != '' and input_str.lower() != 'y' and input_str.lower() != 'n' and input_str.lower() != 'm':
        print(f"Your input is {input_str}. Invalid input!")
        input_str = input(prompt_str)
    if input_str == '':
        input_str = 'n'
    return input_str

def select_num(input_list) -> int:
    print("====================================")
    print(f"Select a number from the list below:")
    for id, item in enumerate(input_list):
        print(f'[{id}]: {item}')
    input_str = input("Your selection: ")
    while input_str != '' and (input_str.isdigit() == False or int(input_str) < 0 or int(input_str) >= len(input_list)):
        print(f"Your input is {input_str}. Invalid input!")
        input_str = input("Your selection: ")
    print(f"Your selection is {int(input_str) if input_str != '' else 0}.")
    print("====================================")
    return int(input_str) if input_str != '' else 0



def select_graph_states(node_stats, edge_stats, task_name, graph_state_path, task_file_list, task_state_file_path, scene_id=1):
    if not os.path.exists(task_state_file_path):
        with open(task_state_file_path, 'w') as f:
            f.write('{}')
    with open(task_state_file_path, 'r') as f:
        task_state = json.load(f)
    
    scene_str = f'scene_{scene_id}'
    if scene_str not in task_state:
        task_state[scene_str] = {}

    print(f'====Current Task is [{task_name}]====')
    if task_name in task_state[scene_str]:
        input_str = input("Do you want to use the previous selected graph states? (y/n): ")
        if input_str.lower() == 'y' or input_str == '':
            return
        elif input_str.lower() == 'n':
            pass
        else:
            raise Exception("Invalid input!")
    
    task_state[scene_str][task_name] = {
        "graph_state_path": graph_state_path,
        "task_file_list": task_file_list,
        "selected_node_state": {},
        "selected_edge_state": {}
    }

    # now we iterate node stats first
    for key, value in node_stats.items():
        result = input_selection('node', key, value)
        if result == 'y':
            task_state[scene_str][task_name]['selected_node_state'][key] = value
        elif result == 'm':
            print(f"Merging the key [{key}] ...")
            current_selected_node_state = copy.deepcopy(task_state[scene_str][task_name]['selected_node_state'])
            if len(current_selected_node_state) == 0:
                task_state[scene_str][task_name]['selected_node_state'][key] = value
            else:
                get_id_and_node_list =  [(0, 'Add new state.')]
                get_id_and_node_list += [(id+1, key) for id, key in enumerate(current_selected_node_state.keys())]
                selected_id = select_num(get_id_and_node_list)
                if selected_id == 0:
                    task_state[scene_str][task_name]['selected_node_state'][key] = value
                else:
                    selected_key_str = get_id_and_node_list[selected_id][1]
                    tmp_key = key+'|'+selected_key_str
                    tmp_value = current_selected_node_state[selected_key_str] + value

                    del task_state[scene_str][task_name]['selected_node_state'][selected_key_str]
                    task_state[scene_str][task_name]['selected_node_state'][tmp_key] = tmp_value

            ...
    
    for key, value in edge_stats.items():
        result = input_selection('edge', key, value)
        if result == 'y':
            task_state[scene_str][task_name]['selected_edge_state'][key] = value
        elif result == 'm':
            print(f"Merging the key [{key}] ...")
            current_selected_edge_state = copy.deepcopy(task_state[scene_str][task_name]['selected_edge_state'])
            if len(current_selected_edge_state) == 0:
                task_state[scene_str][task_name]['selected_edge_state'][key] = value
            else:
                get_id_and_edge_list = [(0, 'Add new state.')]
                get_id_and_edge_list += [(id+1, key) for id, key in enumerate(current_selected_edge_state.keys())]
                selected_id = select_num(get_id_and_edge_list)
                if selected_id == 0:
                    task_state[scene_str][task_name]['selected_edge_state'][key] = value
                else:
                    selected_key_str = get_id_and_edge_list[selected_id][1]
                    selected_key_dict = eval(selected_key_str)
                    current_key_dict = eval(key)

                    selected_from, selected_relation, selected_to = selected_key_dict['from_name'], selected_key_dict['relation'], selected_key_dict['to_name']
                    current_from, current_relation, current_to = current_key_dict['from_name'], current_key_dict['relation'], current_key_dict['to_name']

                    isSuccess = False

                    tmp_entry = {}
                    if selected_relation == current_relation:
                        if '?' in selected_from and '?' in current_from and selected_to == current_to:
                            tmp_entry['relation'] = selected_relation
                            tmp_entry['to_name'] = selected_to
                            tmp_entry['from_name'] = current_from + "|" + selected_from
                            isSuccess = True
                        elif '?' in selected_to and '?' in current_to and selected_from == current_from:
                            tmp_entry['relation'] = selected_relation
                            tmp_entry['from_name'] = selected_from
                            tmp_entry['to_name'] = current_to + "|" + selected_to
                            isSuccess = True
                    
                    if isSuccess:
                        tmp_value = copy.deepcopy(current_selected_edge_state[selected_key_str])
                        tmp_value[0].update(value[0])
                        tmp_value[1] += value[1]
                        del task_state[scene_str][task_name]['selected_edge_state'][selected_key_str]
                        task_state[scene_str][task_name]['selected_edge_state'][str(tmp_entry)] = tmp_value
                    else:
                        print(f"Cannot merge the key [{key}] with the selected key [{selected_key_str}].")
                        task_state[scene_str][task_name]['selected_edge_state'][key] = value
                  
    with open(task_state_file_path, 'w') as f:
        json.dump(task_state, f, indent=2)

    return




def select_graph_states_V2(node_stats, edge_stats, edge_wildcard_stats, task_name, graph_state_path, task_file_list, task_state_file_path, scene_id=1):
    if not os.path.exists(task_state_file_path):
        with open(task_state_file_path, 'w') as f:
            f.write('{}')
    
    with open(task_state_file_path, 'r') as f:
        task_state = json.load(f)

    scene_str = f'scene_{scene_id}'
    if scene_str not in task_state:
        task_state[scene_str] = {}

    print(f'====Current Task is [{task_name}]====')
    if task_name in task_state[scene_str]:
        input_str = input("Do you want to use the previous selected graph states? (y/n): ")
        if input_str.lower() == 'y' or input_str == '':
            return
        elif input_str.lower() == 'n':
            pass
        else:
            raise Exception("Invalid input!")
    
    task_state[scene_str][task_name] = {
        "graph_state_path": graph_state_path,
        "task_file_list": task_file_list,
        "goal_candidates": []
    }

    # The main loop is querying the user about the specific states in the current goal candidate, while asking the user whether to get a new goal candidate at the end of the loop.
    goal_candidate_id = 0
    while True:
        # first, check whether this is the second or later goal candidate
        if goal_candidate_id > 0:
            input_str = input("Do you want to get a new goal candidate? (y/n): ")
            while input_str != '' and input_str != 'n' and input_str != 'y':
                print(f"Invalid input: {input_str}")
                input_str = input("Do you want to get a new goal candidate? (y/n): ")
            if input_str.lower() == 'n' or input_str == '':
                break
            elif input_str.lower() == 'y':
                pass
        print(f"=============Current Goal Candidate [{goal_candidate_id+1}]=============")
        new_goal_candidate = {
            "selected_node_state": {},
            "selected_edge_state": {},
            "accurate_edge_state": {}
        }

        # ========Here, we ask the user to select the states========
        # we first go through the node states selection
        for key, value in node_stats.items():
            result = input_selection('node', key, value)
            if result == 'y':
                new_goal_candidate['selected_node_state'][key] = value
            elif result == 'm':
                print(f"Merging the key [{key}] ...")
                current_selected_nodes_state = copy.deepcopy(new_goal_candidate['selected_node_state'])
                if len(current_selected_nodes_state) == 0:
                    new_goal_candidate['selected_node_state'][key] = value
                else:
                    get_id_and_node_list = [(0, 'Add new state.')]
                    get_id_and_node_list += [(id+1, key) for id, key in enumerate(current_selected_nodes_state.keys())]
                    selected_id = select_num(get_id_and_node_list)
                    if selected_id == 0:
                        new_goal_candidate['selected_node_state'][key] = value
                    else:
                        selected_key_str = get_id_and_node_list[selected_id][1]
                        tmp_key = key + '|' + selected_key_str
                        tmp_value = current_selected_nodes_state[selected_key_str] + value
                        del new_goal_candidate['selected_node_state'][selected_key_str]
                        new_goal_candidate['selected_node_state'][tmp_key] = tmp_value

        # we then go through the edge wildcard states selection
        for key, value in edge_wildcard_stats.items():
            result = input_selection('edge', key, value)
            if result == 'y':
                new_goal_candidate['selected_edge_state'][key] = value
            elif result == 'm':
                print(f"Merging the key [{key}] ...")
                current_selected_edge_state = copy.deepcopy(new_goal_candidate['selected_edge_state'])
                if len(current_selected_edge_state) == 0:
                    new_goal_candidate['selected_edge_state'][key] = value
                else:
                    get_id_and_edge_list = [(0, 'Add new state.')]
                    get_id_and_edge_list += [(id+1, key) for id, key in enumerate(current_selected_edge_state.keys())]
                    selected_id = select_num(get_id_and_edge_list)
                    if selected_id == 0:
                        new_goal_candidate['selected_edge_state'][key] = value
                    else:
                        selected_key_str = get_id_and_edge_list[selected_id][1]
                        selected_key_dict = eval(selected_key_str)
                        current_key_dict = eval(key)

                        selected_from, selected_relation, selected_to = selected_key_dict['from_name'], selected_key_dict['relation'], selected_key_dict['to_name']
                        current_from, current_relation, current_to = current_key_dict['from_name'], current_key_dict['relation'], current_key_dict['to_name']

                        success = False
                        
                        selected_relation_candidates = selected_relation.split('|')
                        merge_relation_mode = current_relation not in selected_relation_candidates # if two relations are different, we need to start relation merging operation

                        # we have guaranteed that the property order is correct by using the sort before we call this prunning function
                        tmp_entry = {}
                        merged_name = None
                        if '?' in selected_from and '?' in current_from and selected_to == current_to:

                            merged_name = selected_from
                            selected_from_names = selected_from.split('|')
                            if current_from not in selected_from_names:
                                merged_name += '|' + current_from
                            # if merge_relation_mode:
                            # else:
                            #     merged_name += '|' + current_from

                            tmp_entry['from_name'] = merged_name
                            tmp_entry['relation'] = selected_relation if not merge_relation_mode else selected_relation + "|" + current_relation
                            tmp_entry['to_name'] = selected_to
                            success = True

                        elif '?' in selected_to and '?' in current_to and selected_from == current_from:

                            merged_name = selected_to
                            selected_to_names = selected_to.split('|')
                            if current_to not in selected_to_names:
                                merged_name += '|' + current_to
                            # if merge_relation_mode:
                            # else:
                            #     merged_name += '|' + current_to

                            tmp_entry['from_name'] = selected_from
                            tmp_entry['relation'] = selected_relation if not merge_relation_mode else selected_relation + "|" + current_relation
                            tmp_entry['to_name'] = merged_name
                            success = True
                        
                        if success:
                            tmp_value = copy.deepcopy(current_selected_edge_state[selected_key_str])
                            for k, v in value[0].items():
                                if k not in tmp_value[0]:
                                    tmp_value[0][k] = v
                                else:
                                    tmp_value[0][k] += v
                            tmp_value[1] += value[1]
                            del new_goal_candidate['selected_edge_state'][selected_key_str]
                            new_goal_candidate['selected_edge_state'][str(tmp_entry)] = tmp_value
                        else:
                            print(f"Cannot merge the key [{key}] with the selected key [{selected_key_str}].")
                            new_goal_candidate['selected_edge_state'][key] = value


                ...
            ...

        # at last, we ask the user to insert the precise states manually
        print("Now, please decide whether to insert the precise states manually.")
        print("Here is the original edge list, you may choose 0 to quit the selection or choose the edge you want to insert with the corresponding id.")
        tmp_edge_stats = copy.deepcopy(edge_stats)
        get_id_and_edge_list = [(0, 'quit')]
        get_id_and_edge_list += [(id+1, key) for id, key in enumerate(tmp_edge_stats.keys())]
        selected_id = select_num(get_id_and_edge_list)
        while selected_id != 0:
            selected_key_str = get_id_and_edge_list[selected_id][1]
            new_goal_candidate['accurate_edge_state'][selected_key_str] = tmp_edge_stats[selected_key_str]
            del tmp_edge_stats[selected_key_str]
            print("Here is the remaining original edge list, you may choose 0 to quit the selection or choose the edge you want to insert with the corresponding id.")
            get_id_and_edge_list = [(0, 'quit')]
            get_id_and_edge_list += [(id+1, key) for id, key in enumerate(tmp_edge_stats.keys())]
            selected_id = select_num(get_id_and_edge_list)

        # ========End of states selection========


        goal_candidate_id += 1
        task_state[scene_str][task_name]['goal_candidates'].append(new_goal_candidate)
        ...

    with open(task_state_file_path, 'w') as f:
        json.dump(task_state, f, indent=2)
    
    return


def prune_graph_states(selected_node_state, selected_edge_state, node_stats, edge_stats, task_name):
    if task_name == 'Wash clothes':
        tmp = copy.deepcopy(selected_edge_state)
        for key, value in selected_edge_state.items():
            if 'basket' in key or 'pants' in key or 'HOLDS' in key or 'soap' in key:
                del tmp[key]
            if 'basket_for_clothes' in value[0]:
                del tmp[key]
        detergent_dict = {'from_name': '?[<Property.GRABBABLE: 2>, <Property.POURABLE: 10>, <Property.MOVABLE: 22>]?', 'relation': 'ON', 'to_name': 'washing_machine'}
        detergent_value = edge_stats[str(detergent_dict)]

        soap_entry = str({'from_name': '?[<Property.GRABBABLE: 2>, <Property.MOVABLE: 22>, <Property.CREAM: 23>]?', 'relation': 'ON', 'to_name': 'washing_machine'})

        soap_dict = eval(soap_entry)
        soap_value = copy.deepcopy(tmp[soap_entry])

        cleaner_dict = {'from_name': detergent_dict['from_name'] + '|' + soap_dict['from_name'], 'relation': 'ON', 'to_name': 'washing_machine'}
        cleaner_value_0 = copy.deepcopy(detergent_value[0])
        cleaner_value_0['soap'] = soap_value[0]['soap']
        cleaner_value = [cleaner_value_0, detergent_value[1] + soap_value[1]]
        
        del tmp[soap_entry]
        # tmp[str(cleaner_dict)] = cleaner_value

        return tmp
    elif task_name == 'Watch TV':
        tmp = copy.deepcopy(selected_edge_state)
        for key, value in selected_edge_state.items():
            key_dict = eval(key)
            if 'HOLDS_RH' in key_dict['relation']:
                del tmp[key]
            if 'couch' in key_dict['to_name']:
                del tmp[key]

            
        # merge chair and couch into sitter
        chair_dict = {'from_name': 'character', 'relation': 'ON', 'to_name': '?[<Property.SURFACES: 1>, <Property.GRABBABLE: 2>, <Property.SITTABLE: 3>, <Property.MOVABLE: 22>]?'}
        chair_value = edge_stats[str(chair_dict)]

        couch_dict = {'from_name': 'character', 'relation': 'ON', 'to_name': '?[<Property.SURFACES: 1>, <Property.SITTABLE: 3>, <Property.LIEABLE: 4>, <Property.MOVABLE: 22>]?'}
        couch_value = edge_stats[str(couch_dict)]
        
        sitter_dict = {'from_name': 'character', 'relation': 'ON', 'to_name': chair_dict['to_name'] + '|' + couch_dict['to_name']}
        sitter_value_0 = copy.deepcopy(chair_value[0])
        sitter_value_0['couch'] = couch_value[0]['couch']
        sitter_value = [sitter_value_0, chair_value[1] + couch_value[1]]
        del tmp[str(couch_dict)]

        tmp[str(sitter_dict)] = sitter_value
        return tmp
    else:
        print(f"=========Unpruned selected edge stats=========")
        for k, v in selected_edge_state.items():
            print(f'[{k}]: {v}')
        raise NotImplementedError(f'Task {task_name} is not implemented yet.')



# below are threshold strategies
def stardard_deviation_method(node_stats, edge_stats):
    import numpy as np
    node_freq = list(node_stats.values())
    edge_freq = [freq[1] for freq in edge_stats.values()]

    # print(f'node_freq: {node_freq}')
    # print(f'edge_freq: {edge_freq}')

    def f(freq_list, N=1.0):
        mean_freq = np.mean(freq_list)
        std_dev_freq = np.std(freq_list)
        threshold = mean_freq + (N * std_dev_freq)
        return threshold

    node_threshold = f(node_freq, 0)
    edge_threshold = f(edge_freq, 0)
    selected_node_state_list = {feature: freq for feature, freq in node_stats.items() if freq > node_threshold}
    selected_edge_state_list = {feature: freq for feature, freq in edge_stats.items() if freq[1] > edge_threshold}
    
    return selected_node_state_list, selected_edge_state_list

def information_gain(node_stats, edge_stats):
    import math
    total_node_freq = sum(node_stats.values())
    total_edge_freq = sum(freq[1] for freq in edge_stats.values())

    node_entropy = -sum((freq / total_node_freq) * math.log2(freq / total_node_freq) for freq in node_stats.values())
    edge_entropy = -sum((freq[1] / total_edge_freq) * math.log2(freq[1] / total_edge_freq) for freq in edge_stats.values())

    information_gain_node = {}
    information_gain_edge = {}
    for feature, freq in node_stats.items():
        prop = freq / total_node_freq
        feature_entropy = -prop * math.log2(prop)
        gain = node_entropy - feature_entropy
        information_gain_node[feature] = gain
    for feature, freq in edge_stats.items():
        prop = freq[1] / total_edge_freq
        feature_entropy = -prop * math.log2(prop)
        gain = edge_entropy - feature_entropy
        information_gain_edge[feature] = gain
    
    sorted_information_gain_node = sorted(information_gain_node.items(), key=lambda kv: kv[1], reverse=True)
    sorted_information_gain_edge = sorted(information_gain_edge.items(), key=lambda kv: kv[1], reverse=True)

    print(f"====Selected Node Stats====")
    for feature, gain in sorted_information_gain_node:
        print(f'[{feature}]: {gain}')
    print(f"====Selcted Edge Stats=====")
    for feature, gain in sorted_information_gain_edge:
        print(f'[{feature}]: {gain}')
    
    return sorted_information_gain_node, sorted_information_gain_edge