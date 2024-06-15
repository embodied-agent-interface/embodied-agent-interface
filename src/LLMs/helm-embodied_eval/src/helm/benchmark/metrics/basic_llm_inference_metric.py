import json
from typing import List, Optional
import re
import yaml
import os

from sklearn.metrics import f1_score
from sklearn.preprocessing import MultiLabelBinarizer

from helm.benchmark.adaptation.request_state import RequestState
from helm.benchmark.metrics.evaluate_instances_metric import EvaluateInstancesMetric
from helm.benchmark.metrics.evaluate_reference_metrics import normalize_text
from helm.benchmark.metrics.metric import MetricName
from helm.benchmark.metrics.statistic import Stat
from helm.benchmark.scenarios.scenario import Reference
from helm.common.request import GeneratedOutput
from helm.common.request import RequestResult




def parse_json(raw_llm_output):
    
    # Replace single quotes with double quotes
    raw_llm_output = raw_llm_output.replace("'", '"')
    
    # Extract the substring between the first { and the first } after it
    match = re.search(r"{[^{}]*}", raw_llm_output, re.DOTALL)

    if match:
        result = match.group(0)

        # Print the final cleaned result
        try:
            parsed_result = json.loads(result)
            with open('intermediate_outputs/success.txt', 'a') as file:
                file.write(str(result)+"\n\n")
            return parsed_result
        except:
            print("Error parsing JSON-like content.")
            with open('intermediate_outputs/fail.txt', 'a') as file:
                file.write(str(result)+"\n\n")
            return None
    else:
        print("No valid JSON-like content found.")



class Basic_LLM_Inference_Metric(EvaluateInstancesMetric):
    """
    Defines metrics for the Basic_LLM_Inference scenario.
    """

    def __init__(self, simulator: str, subtask: str, model_name: str, add_back_sequence: str):
        self.simulator = simulator
        self.subtask = subtask
        self.model_name = model_name
        self.add_back_sequence = add_back_sequence


    def evaluate_instances(self, request_states: List[RequestState], eval_cache_path: str) -> List[Stat]:
        
        llm_output_list = []
        
        for request_state in request_states:
            raw_llm_output = request_state.result.completions[0].text
            
            
            # add back the stop sequence because it was previously removed:
            raw_llm_output = raw_llm_output + self.add_back_sequence
            # if we are checking how many outputs are parsable:
            # model_pred = parse_json(raw_llm_output)
            
            llm_output_list.append(
                {   
                    "identifier": request_state.instance.id,
                    "llm_output": raw_llm_output,
                }
            )
        save_dir = os.path.join("HELM_output", self.simulator, self.subtask)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        save_path = os.path.join(save_dir , self.model_name + "_outputs.json")
        with open(save_path, "w") as json_file:
            json.dump(llm_output_list, json_file, indent=4)
        
        dummy_stat = Stat(MetricName("dummy_stat"))
        dummy_stat.add(1.00)
        
        stats = [dummy_stat]
        
        return stats