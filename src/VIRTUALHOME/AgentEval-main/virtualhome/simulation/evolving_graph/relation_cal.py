import json
import sys
sys.path.append('../simulation')
from enum import Enum
import re
import copy

import evolving_graph.utils as utils
from evolving_graph.execution import Relation, State
from evolving_graph.scripts import read_script, Action, ScriptObject, ScriptLine, ScriptParseException, Script
from evolving_graph.execution import ScriptExecutor
from evolving_graph.environment import EnvironmentGraph, EnvironmentState
from evolving_graph.preparation import AddMissingScriptObjects, AddRandomObjects, ChangeObjectStates, \
    StatePrepare, AddObject, ChangeState, Destination
import openai
import os
import time
import ast


# all_relation = set()
all_state_dict = {}
data_dir = '/viscam/u/shiyuz/virtualhome/virtualhome/dataset/programs_processed_precond_nograb_morepreconds/init_and_final_graphs/TrimmedTestScene1_graph/results_intentions_march-13-18'

for file in os.listdir(data_dir):
    if file.endswith('.json'):
        with open(os.path.join(data_dir, file), 'r') as f:
            data = json.load(f)
            for node in data['final_graph']['nodes']:
                node_name = node['class_name']
                states = node['states']
                if node_name not in all_state_dict:
                    all_state_dict[node_name] = set()
                for state in states:
                    all_state_dict[node_name].add(state)
            for node in data['init_graph']['nodes']:
                node_name = node['class_name']
                states = node['states']
                if node_name not in all_state_dict:
                    all_state_dict[node_name] = set()
                for state in states:
                    all_state_dict[node_name].add(state)

existing_state_path = '/viscam/u/shiyuz/virtualhome/virtualhome/resources/object_states.json'
with open(existing_state_path, 'r') as f:
    existing_state_dict = json.load(f)
    for key in existing_state_dict:
        if key not in all_state_dict:
            all_state_dict[key] = existing_state_dict[key]
        else:
            all_state_dict[key] = all_state_dict[key].union(existing_state_dict[key])

for k, v in all_state_dict.items():
    all_state_dict[k] = list(v)
    all_state_dict[k].sort()

save_path = '/viscam/u/shiyuz/virtualhome/virtualhome/resources/object_states_full.json'
with open(save_path, 'w') as f:
    json.dump(all_state_dict, f, indent=4)