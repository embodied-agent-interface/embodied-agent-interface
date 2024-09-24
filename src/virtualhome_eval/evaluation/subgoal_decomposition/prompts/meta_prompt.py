system_prompt = \
'''# Background Introduction
You are determining complete state transitions of a household task solving by a robot. The goal is to list all intermediate states and necessary actions in temporal order to achieve the target goals. The output consists of Boolean expressions, which are comprised of state and action primitives. Here, a state or action primitive is a first-order predicate as combinition of a predicate name and its parameters. Please note that do not use actions in your output unless necessary.In short, your task is to output the subgoal plan in the required format.

# Data Vocabulary Introduction
## Available States
State primitive is a tuple of a predicate name and its arguments. Its formal definition looks like this "<PredicateName>(Params)", where <PredicateName> is the state name and each param should be ended with an id. For example, when a television is plugged in, it is represented as "PLUGGED_IN(television.1). Another example is, if character is facing a television, it is represented as "FACING(character.1, television.1)". Below is a complete vocabulary of state primitives that you can and only can choose from. Note that 'obj' can represent both items and agents, while 'character' can only represent agents.
| Predicate Name | Arguments | Description |
| --- | --- | --- |
| CLOSED | (obj1.id) | obj1 is closed |
| OPEN | (obj1.id) | obj1 is open |
| ON | (obj1.id) | obj1 is turned on, or it is activated |
| OFF | (obj1.id) | obj1 is turned off, or it is deactivated |
| PLUGGED_IN | (obj1.id) | obj1 is plugged in |
| PLUGGED_OUT | (obj1.id) | obj1 is unplugged |
| SITTING | (character1.id) | character1 is sitting, and this represents a state of a character |
| LYING | (character1.id) | character1 is lying |
| CLEAN | (obj1.id) | obj1 is clean |
| DIRTY | (obj1.id) | obj1 is dirty |
| ONTOP | (obj1.id, obj2.id) | obj1 is on top of obj2 |
| INSIDE | (obj1.id, obj2.id) | obj1 is inside obj2 |
| BETWEEN | (obj1.id, obj2.id, obj3.id) | obj1 is between obj2 and obj3 |
| NEXT_TO | (obj1.id, obj2.id) | obj1 is close to or next to obj2 |
| FACING | (character1.id, obj1.id) | character1 is facing obj1 |
| HOLDS_RH | (character1.id, obj1.id) | character1 is holding obj1 with right hand |
| HOLDS_LH | (character1.id, obj1.id) | character1 is holding obj1 with left hand |
## Available Actions
Action primitive is similar to state primitive. Its formal definition looks like this "<ActionName>(Params)", where <ActionName> is the action name and each param should be ended with an id. Note that, you do not need to list actions in most cases. When you choose to list actions, you should only choose from the following list of actions. For other cases, use state predicate as substitutes. Here, 'obj' only refers to items, not agents.
| Action Name | Arguments | Argument Restriction | Description |
| --- | --- | --- | --- |
| DRINK | (obj1.id) | obj1 is ['DRINKABLE', 'RECIPIENT'] | drinks obj1, need to hold obj1 first |
| EAT | (obj1.id) | obj1 is ['EATABLE'] | eats obj1, need to hold obj1 first |
| CUT | (obj1.id) | obj1 is ['EATABLE', 'CUTABLE'] | cuts obj1, obj1 is food|
| TOUCH | (obj1.id) | none | touches obj1 |
| LOOKAT | (obj1.id) | none | looks at obj1, it has a precondition that agent should be facing at obj1 first |
| WATCH | (obj1.id) | none | watches obj1 |
| READ | (obj1.id) | obj1 is ['READABLE'] | reads obj1, need to hold obj1 first |
| TYPE | (obj1.id) | obj1 is ['HAS_SWITCH'] | types on obj1 |
| PUSH | (obj1.id) | obj1 is ['MOVABLE'] | pushes obj1 |
| PULL | (obj1.id) | obj1 is ['MOVABLE'] | pulls obj1 |
| MOVE | (obj1.id) | obj1 is ['MOVABLE'] | moves obj1 |
| SQUEEZE | (obj1.id) | obj1 is ['CLOTHES'] | squeezes obj1 |
| SLEEP | none | none | sleeps, need to be at LYING or SITTING first |
| WAKEUP | none | none | wakes up, need to be at LYING or SITTING first |
| RINSE | (obj1.id) | none | rinses obj1, use only for cleaning appliances or teeth |
| SCRUB | (obj1.id) | none | scrubs obj1, use only for cleaning appliances or teeth |
| WASH | (obj1.id) | none | washes obj1, use only for appliances |
| GRAB | (obj1.id) | obj1 is ['GRABBABLE'] | grabs obj1 |
| SWITCHOFF | (obj1.id) | obj1 is ['HAS_SWITCH'] | switches off obj1 |

# Rules You Must Follow
- Temporal logic formula refers to a Boolean expression that describes a subgoals plan with temporal and logical order.
- The atomic Boolean expression includes both state primitive and action primitive.
- Boolean expressions in the same line are interchangeable with no temporal order requirement.
- Boolean expresssions in different lines are in temporal order, where the first one should be satisfied before the second one.
- Boolean expression can be combined with the following logical operators: "and", "or".
- The "and" operator combines Boolean expressions that are interchangeable but needs to be satisfied simultaneously in the end.
- The "or" operator combines Boolean expressions that are interchangeable but only one of them needs to be satisfied in the end.
- When there is temporal order requirement, output the Boolean expressions in different lines.
- Add intermediate states if necessary to improve logical consistency.
- If you want to change state of A, while A is in B and B is closed, you should make sure B is open first.
- Your output format should strictly follow this json format: {"necessity_to_use_action": <necessity>, "actions_to_include": [<actions>], "output": [<your subgoal plan>]}, where in <necessity> you should put "yes" or "no" to indicate whether actions should be included in subgoal plans. If you believe it is necessary to use actions, in the field <actions>, you should list all actions you used in your output. Otherwise, you should simply output an empty list []. In the field <your subgoal plan>, you should list all Boolean expressions in the required format and the temporal order.

Below are two examples for your better understanding.
## Example 1: Task category is "Listen to music"
## Relevant Objects in the Scene
| obj | category | properties |
| --- | --- | --- |
| bathroom.1 | Rooms | [] |
| character.65 | Characters | [] |
| home_office.319 | Rooms | [] |
| couch.352 | Furniture | ['LIEABLE', 'MOVABLE', 'SITTABLE', 'SURFACES'] |     
| television.410 | Electronics | ['HAS_PLUG', 'HAS_SWITCH', 'LOOKABLE'] |      
| dvd_player.1000 | placable_objects | ['CAN_OPEN', 'GRABBABLE', 'HAS_PLUG', 'HAS_SWITCH', 'MOVABLE', 'SURFACES'] |

## Initial States
CLEAN(dvd_player.1000)
CLOSED(dvd_player.1000)
OFF(dvd_player.1000)
PLUGGED_IN(dvd_player.1000)
INSIDE(character.65, bathroom.1)

## Goal States
[States]
CLOSED(dvd_player.1000)
ON(dvd_player.1000)
PLUGGED_IN(dvd_player.1000)
[Actions Must Include]: Actions are listed in the execution order, each line is one action to satisfy. If "A or B or ..." is presented in one line, then only one of them needs to be satisfied.
None

## Necessity to Use Actions
No

## Output: Based on initial states in this task, achieve final goal states logically and reasonably. It does not matter which state should be satisfied first, as long as all goal states can be satisfied at the end. Make sure your output follows the json format, and do not include irrelevant information, do not include any explanation.
{"necessity_to_use_action": "no", "actions_to_include": [], "output": ["NEXT_TO(character.65, dvd_player.1000)", "FACING(character.65, dvd_player.1000)", "PLUGGED_IN(dvd_player.1000) and CLOSED(dvd_player.1000)", "ON(dvd_player.1000)"]}

# Example 2: Task category is "Browse internet"
## Relevant Objects in the Scene
| bathroom.1 | Rooms | [] |
| character.65 | Characters | [] |
| floor.208 | Floor | ['SURFACES'] |
| wall.213 | Walls | [] |
| home_office.319 | Rooms | [] |
| floor.325 | Floors | ['SURFACES'] |
| floor.326 | Floors | ['SURFACES'] |
| wall.330 | Walls | [] |
| wall.331 | Walls | [] |
| doorjamb.346 | Doors | [] |
| walllamp.351 | Lamps | [] |
| chair.356 | Furniture | ['GRABBABLE', 'MOVABLE', 'SITTABLE', 'SURFACES'] |   
| desk.357 | Furniture | ['MOVABLE', 'SURFACES'] |
| powersocket.412 | Electronics | [] |
| mouse.413 | Electronics | ['GRABBABLE', 'HAS_PLUG', 'MOVABLE'] |
| mousepad.414 | Electronics | ['MOVABLE', 'SURFACES'] |
| keyboard.415 | Electronics | ['GRABBABLE', 'HAS_PLUG', 'MOVABLE'] |
| cpuscreen.416 | Electronics | [] |
| computer.417 | Electronics | ['HAS_SWITCH', 'LOOKABLE'] |

## Initial States
CLEAN(computer.417)
OFF(computer.417)
ONTOP(mouse.413, mousepad.414)
ONTOP(mouse.413, desk.357)
ONTOP(keyboard.415, desk.357)
INSIDE(character.65, bathroom.1)

## Goal States
[States]
ON(computer.417)
INSIDE(character.65, home_office.319)
HOLDS_LH(character.65, keyboard.415)
FACING(character.65, computer.417)
HOLDS_RH(character.65, mouse.413)
[Actions Must Include]: Actions are listed in the execution order, each line is one action to satisfy. If "A or B or ..." is presented in one line, then only one of them needs to be satisfied.
LOOKAT or WATCH

## Necessity to Use Actions
Yes

## Output: Based on initial states in this task, achieve final goal states logically and reasonably. It does not matter which state should be satisfied first, as long as all goal states can be satisfied at the end. Make sure your output follows the json format. Do not include irrelevant information, only output json object.
{"necessity_to_use_action": "yes", "actions_to_include": ["LOOKAT"], "output": ["NEXT_TO(character.65, computer.417)", "ONTOP(character.65, chair.356)", "HOLDS_RH(character.65, mouse.413) and HOLDS_LH(character.65, keyboard.415)", "FACING(character.65, computer.417)", "LOOKAT(computer.417)"]}
'''

target_task_prompt = \
'''Now, it is time for you to generate the subgoal plan for the following task.
# Target Task: Task category is <task_name>
## Relevant Objects in the Scene
<relevant_objects>

## Initial States
<initial_states>

## Goal States
[States]
<final_states>
[Actions Must Include]: Actions are listed in the execution order, each line is one action to satisfy. If "A or B or ..." is presented in one line, then only one of them needs to be satisfied.
<final_actions>

## Necessity to Use Actions
<necessity>

## Output: Based on initial states in this task, achieve final goal states logically and reasonably. It does not matter which state should be satisfied first, as long as all goal states can be satisfied at the end. Make sure your output follows the json format. Do not include irrelevant information, only output json object.'''


tmp = \
'''Now, it is time for you to generate the subgoal plan for the following task.
# Target Task: Task category is Wash clothes
## Relevant Objects in the Scene
| bathroom.1 | Rooms | [] |
| character.65 | Characters | [] |
| dining_room.201 | Rooms | [] |
| basket_for_clothes.1000 | placable_objects | ['CAN_OPEN', 'CONTAINERS', 'GRABBABLE', 'MOVABLE'] |
| washing_machine.1001 | placable_objects | ['CAN_OPEN', 'CONTAINERS', 'HAS_PLUG', 'HAS_SWITCH', 'RECIPIENT'] |
| soap.1002 | placable_objects | ['CREAM', 'GRABBABLE', 'MOVABLE'] |
| clothes_jacket.1003 | placable_objects | ['CLOTHES', 'GRABBABLE', 'HANGABLE', 'MOVABLE'] |

## Initial States
CLEAN(washing_machine.1001)
CLOSED(washing_machine.1001)
OFF(washing_machine.1001)
PLUGGED_IN(washing_machine.1001)
INSIDE(clothes_jacket.1003, washing_machine.1001)
INSIDE(character.65, bathroom.1)

## Goal States
[States]
CLOSED(washing_machine.1001)
ON(washing_machine.1001)
PLUGGED_IN(washing_machine.1001)
ONTOP(clothes_jacket.1003, washing_machine.1001)
ONTOP(soap.1002, washing_machine.1001)
[Actions]: The following actions must be included in the subgoals plan, each line is one action to satisfy. If "A or B or ..." is presented in one line, then only one of them needs to be satisfied.
None

## Necessity to use actions
no

## Output: Based on initial states in this task, achieve final goal states logically and reasonably. It does not matter which state should be satisfied first, as long as all goal states can be satisfied at the end. Make sure your output follows the json format. Do not include irrelevant information, only output json object.
'''

tmp2 = \
'''Now, it is time for you to generate the subgoal plan for the following task.
# Target Task: Task category is Drink
## Relevant Objects in the Scene
| character.65 | Characters | [] |
| dining_room.201 | Rooms | [] |
| kitchen_counter.230 | Furniture | ['SURFACES'] |
| sink.231 | Furniture | ['CONTAINERS', 'RECIPIENT'] |
| faucet.232 | Furniture | ['HAS_SWITCH'] |
| home_office.319 | Rooms | [] |
| cup.1000 | placable_objects | ['GRABBABLE', 'MOVABLE', 'POURABLE', 'RECIPIENT'] |

## Initial States
INSIDE(character.65, home_office.319)

## Goal States
[States]
HOLDS_RH(character.65, cup.1000)
[Actions]: The following actions must be included in the subgoals plan, each line is one action to satisfy. If \"A or B or ...\" is presented in one line, then only one of them needs to be satisfied.
DRINK

## Necessity to use actions
yes

## Output: Based on initial states in this task, achieve final goal states logically and reasonably. It does not matter which state should be satisfied first, as long as all goal states can be satisfied at the end. Make sure your output follows the json format. Do not include irrelevant information, only output json object.
'''


import json
import os
def generate_meta_prompt(prompt_file_path):
    if not os.path.exists(prompt_file_path):
        with open(prompt_file_path, 'w') as f:
            json.dump({}, f)
    with open(prompt_file_path, 'r') as f:
        prompts = json.load(f)
    
    prompts['system_prompt'] = system_prompt
    prompts['target_task'] = target_task_prompt

    with open(prompt_file_path, 'w') as f:
        json.dump(prompts, f, indent=4)

def generate_system_setup(prompt_file_path):
    if not os.path.exists(prompt_file_path):
        with open(prompt_file_path, 'w') as f:
            json.dump({}, f)
    with open(prompt_file_path, 'r') as f:
        prompts = json.load(f)
    
    prompts['system_prompt'] = system_prompt
    prompts['stop_sequences'] = ['}']
    prompts["max_output_tokens"] = 2048

    with open(prompt_file_path, 'w') as f:
        json.dump(prompts, f, indent=4)

def get_meta_prompt_component():
    prompts = {}
    prompts['system_prompt'] = system_prompt
    prompts['target_task'] = target_task_prompt
    return prompts

if __name__ == '__main__':
    # logger.info(system_prompt+target_task_prompt)
    ...
