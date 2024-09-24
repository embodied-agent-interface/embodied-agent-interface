from igibson.utils.ig_logging import IGLogReader
from igibson.utils.utils import parse_config
import os
import igibson
import behavior_eval
import json

class BaseEnv:
    def defalt_init(self,demo_name):
        with open(behavior_eval.demo_stats_path, "r") as f:
            demo_stats = json.load(f)
        task=demo_stats[demo_name]["task"]
        task_id=demo_stats[demo_name]["task_id"]
        scene_id=demo_stats[demo_name]["scene_id"]

        config_filename = os.path.join(igibson.configs_path, "behavior_robot_mp_behavior_task.yaml")
        config = parse_config(config_filename)

        config["task"] = task
        config["task_id"] = task_id
        config["scene_id"] = scene_id
        config["robot"]["show_visual_head"] = True
        config["image_width"]=1024
        config["image_height"]=1024
        self.config = config
    
            
    def __init__(self,config=None,demo_name=None,**kwargs) -> None:
        assert config is not None or demo_name is not None
        self.config=config
        if demo_name is not None:
            self.defalt_init(demo_name)



