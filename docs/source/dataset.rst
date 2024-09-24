Dataset
=======

The dataset is publicly available at `BEHAVIOR
Annotations <https://github.com/embodied-agent-eval/embodied-agent-eval/blob/main/dataset/behavior_data.json>`__
and `VirtualHome
Annotations <https://github.com/embodied-agent-eval/embodied-agent-eval/blob/main/dataset/virtualhome_data.json>`__.

The dataset is in JSON format:
``"1057_1": {   "task_name": "Watch TV",   "natural_language_description": "Go to the living room, sit on the couch, find the      remote, switch on the TV and watch",   "vh_goal": {     "actions": [       "LOOKAT|WATCH"     ],     "goal": [{         "id": 410,         "class_name": "television",         "state": "ON"       }, {         "id": 410,         "class_name": "television",         "state": "PLUGGED_IN"       }, {         "from_id": 65,         "relation_type": "FACING",         "to_id": 410     }]   },   "tl_goal": "(exists x0. ((LOOKAT(x0) or WATCH(x0))) then (ON(television.410) and      PLUGGED_IN(television.410) and FACING(character.65, television.410)))",   "action_trajectory": [     "[WALK] <home_office> (319)",     "[WALK] <couch> (352)",     "[FIND] <couch> (352)",     "[SIT] <couch> (352)",     "[FIND] <remote_control> (1000)",     "[FIND] <television> (410)",     "[SWITCHON] <television> (410)",     "[TURNTO] <television> (410)",     "[WATCH] <television> (410)"   ],   "transition_model": <pddl_definition> }``
