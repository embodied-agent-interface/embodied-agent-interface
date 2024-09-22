import fire
from multiprocessing import Process
import  os
import json
import os
import json
import fire
from behavior_eval.evaluation.transition_modeling.transition_modeling_evaluator import TransitionModelingEvaluator
import behavior_eval

def get_transition_modling_prompt(demo_name):
    env=TransitionModelingEvaluator(demo_name=demo_name)
    prompt=env.get_prompt()
    rst={
        "identifier":demo_name,
        "llm_prompt":prompt,
    }
    return rst

def generate_prompts(rst_dir):
    os.makedirs(rst_dir,exist_ok=True)
    with open(behavior_eval.demo_name_path, 'r') as f:
        demo_names = json.load(f)
    if os.path.exists(os.path.join(rst_dir,"transition_modeling_prompts.json")):
        with open(os.path.join(rst_dir,"transition_modeling_prompts.json"), 'r') as f:
            statistics = json.load(f)
        name_in_save_dir=set()
        for info in statistics:
            name_in_save_dir.add(info["identifier"])
    else:
        statistics=[]
        name_in_save_dir=set()
    args_list=[]
    for demo_name in demo_names:
        if demo_name in name_in_save_dir:
            continue
        args_list.append([demo_name])

    for args in args_list:
        try:
            rst=get_transition_modling_prompt(*args)
            statistics.append(rst)
        except Exception as e:
            print("Error in ",args[0])
            print(e)

        with open(os.path.join(rst_dir,"transition_modeling_prompts.json"), 'w') as f:
            json.dump(statistics,f,indent=4)

    with open(os.path.join(rst_dir,"transition_modeling_prompts.json"), 'w') as f:
        json.dump(statistics,f,indent=4)
    
    print("All Done!")


if __name__ == "__main__": 
    fire.Fire(generate_prompts)
