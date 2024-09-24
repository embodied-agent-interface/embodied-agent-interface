from behavior_eval.evaluation.action_sequencing.resources.prompt_templates.one_shot import prompt
import numpy as np
from behavior_eval.evaluation.action_sequencing.action_sequence_evaluator import ActionSequenceEvaluator
import openai
import os
import json
import behavior_eval
from openai import OpenAI
import fire
openai.api_key = os.getenv("OPENAI_API_KEY")

# replan evaluation usiung gpt4o:
# action with fail prob to fail
# replan once if fail

def query_gpt4(prompt):
    # Set up the OpenAI API client

    # Query GPT-4
    response = openai.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )

    # Extract and return the response content
    return response.choices[0].message.content

def query_llm(prompt):
    return query_gpt4(prompt)

def convert_state_dict_to_string(statedict):
    output_lines = []

    # Convert nodes to predicates based on properties and states
    for node_name, node_info in statedict['nodes'].items():
        properties = node_info.get('properties', set())
        states = node_info.get('states', set())

        # For each property, check if it's in states or not
        for prop in properties:
            if prop in states:
                line = f"[{prop}, {node_name}]"
            else:
                line = f"[not, {prop}, {node_name}]"
            output_lines.append(line)

    # Convert edges to binary predicates
    for relation in statedict['edges']:
        line = f"['{relation['relation']}', '{relation['from_name']}', '{relation['to_name']}']"
        output_lines.append(line)

    # Join the lines with newline characters
    result = '\n'.join(output_lines)
    return result

def replanning_eval_once(ase,fail_prob=0.2):
    state_dict=ase.evolving_graph.action_env.cur_state.get_state_dict(ase.task)
    initial_state = convert_state_dict_to_string(state_dict)
    target_state = ase.get_target_state()
    obj_list=ase.get_objects_str()
    initial_prompt = prompt.format(init_state=initial_state,target_state=target_state,obj_list=obj_list)
    llm_reponse = query_llm(initial_prompt)
    actions=ase.parse_response(llm_reponse)
    if not ase.evaluate_format(actions):
        return False
    
    flag=True
    for idx,action in enumerate(actions):
        rst={}
        try:
            action_name=action["action"]
            obj=action["object"]
            rst["action"]=action_name
            rst['object']=obj
            #  perform fail_prob to flag
            if np.random.rand()<fail_prob:
                print(f'Action {action_name} failed due to fail_prob')
                return False
            flag=ase.evolving_graph.apply_action(action_name,obj)
            success=ase.evaluate_graph_success()
            if success:
                return True
            if not flag:
                return False
        except:
            return False
    return True

def replanning_eval(demo_name,fail_prob,replan_times):
    ase=ActionSequenceEvaluator(demo_name=demo_name)
    for i in range(replan_times+1):
        flag=replanning_eval_once(ase,fail_prob)
        if flag:
            break
    success=ase.evaluate_graph_success()
    ase.close()
    return {
        'execution_success':flag,
        'goal_satisfied':success
    }

def main(seed=0,fail_prob=0.1,eval_num=20,replan_times=3,save_path='./replan_eval'):
    os.makedirs(save_path,exist_ok=True)
    np.random.seed(seed)
    with open(behavior_eval.demo_name_path,'r') as f:
        demo_names=json.load(f)
    # randomly select eval_num demos
    demo_names=np.random.choice(demo_names,eval_num)
    stats=[]
    for demo_name in demo_names:
        eval_rst=replanning_eval(demo_name,fail_prob,replan_times)
        print(eval_rst)
        stats.append({
            'demo_name':demo_name,
            'eval_rst':eval_rst
        })
        exe_succ=[stat['eval_rst']['execution_success'] for stat in stats]
        goal_succ=[stat['eval_rst']['goal_satisfied'] for stat in stats]
        
        with open(os.path.join(save_path,f'{seed}-{fail_prob}-{eval_num}-{replan_times}.json'),'w') as f:
            json.dump({
                'stats':stats,
                'execution_success_rate':np.mean(exe_succ),
                'goal_satisfied_rate':np.mean(goal_succ)
            },f,indent=4)
if __name__ == '__main__':
    fire.Fire(main)
    
