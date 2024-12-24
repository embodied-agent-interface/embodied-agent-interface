prompt = """
The task is to guide the robot to take actions from the current state to fulfill some node goals, edge goals, and action goals. The input will be the related objects in the scene, nodes and edges in the current environment, and the desired node goals, edge goals, and action goals. The output should be action commands in JSON format so that after the robot executes the action commands sequentially, the ending environment would satisfy the goals.

Data format:
Objects in the scene indicates those objects involved in the action execution. It follows the format: <object_name> (object_id)

Nodes and edges in the current environment shows the nodes' names, states and properties, and edges in the environment. 
Nodes follow the format: object_name, states:... , properties:...
Edges follow the format: object_name A is ... to object_name B
 
Node goals show the target object states in the ending environment. They follow the format: object_name is ... (some state)

Edge goals show the target relationships of objects in the ending environment. They follow the format: object_name A is ... (some relationship) to object_name B.

Action goals specify the necessary actions you need to include in your predicted action commands sequence, and the order they appear in action goals should also be the RELATIVE order they appear in your predicted action commands sequence if there are more than one line. Each line in action goals include one action or more than one actions concatenated by OR. You only need to include ONE of the actions concatenated by OR in the same line. For example, if the action goal is:
The following action(s) should be included:
GRAB
TYPE or TOUCH
OPEN
------------------------
Then your predicted action commands sequence should include GRAB, either TYPE or TOUCH, and OPEN. Besides, GRAB should be executed earlier than TYPE or TOUCH, and TYPE or TOUCH should be executed earlier than OPEN.
If the action goal is:
The following action(s) should be included:
There is no action requirement.
It means there is no action you have to include in output, and you can use any action to achieve the node and edge goals. Warning: No action requirement does not mean empty output. You should always output some actions and their arguments.

Action commands include action names and objects. Each action's number of objects is fixed (0, 1, or 2), and the output should include object names followed by their IDs:
[]: Represents 0 objects.
[object, object_id]: Represents 1 object.
[object 1, object_1_id, object 2, object_2_id]: Represents 2 objects.
The output must be in JSON format, where:
Dictionary keys are action names.
Dictionary values are lists containing the objects (with their IDs) for the corresponding action.
The order of execution is determined by the order in which the key-value pairs appear in the JSON dictionary.

For example, If you want to first FIND the sink and then PUTBACK a cup into the sink, you should express it as:
{
  "FIND": ["sink", "sink_id"],
  "PUTBACK": ["cup", "cup_id", "sink", "sink_id"]
}

The object of action also needs to satisfied some properties preconditions. For example, SWITCHON's object number is 1. To switch on something, the object should 'HAS_SWITCH'. The rule is represented as SWITCHON = ("Switch on", 1, [['HAS_SWITCH']]). Another example is POUR. POUR's object number is 2. To pour sth A into sth B, A should be pourable and drinkable, and B should be RECIPIENT. The rule is represented as POUR = ("Pour", 2, [['POURABLE', 'DRINKABLE'], ['RECIPIENT']]).

Action Definitions Format:
Each action is defined as a combination of:
Action Name (String): A descriptive name for the action.
Required Number of Parameters (Integer): The count of parameters needed to perform the action.
Preconditions for Each Object (List of Lists of Strings): Conditions that must be met for each object involved in the action.

Supported Actions List:
CLOSE: (1, [['CAN_OPEN']]) # Change state from OPEN to CLOSED
DRINK: (1, [['DRINKABLE', 'RECIPIENT']]) # Consume a drinkable item
FIND: (1, [[]]) # Locate and approach an item
WALK: (1, [[]]) # Move towards something
GRAB: (1, [['GRABBABLE']]) # Take hold of an item that can be grabbed
LOOKAT: (1, [[]]) # Direct your gaze towards something
OPEN: (1, [['CAN_OPEN']]) # Open an item that can be opened
POINTAT: (1, [[]]) # Point towards something
PUTBACK: (2, [['GRABBABLE'], []]) # Place one object back onto or into another
PUTIN: (2, [['GRABBABLE'], ['CAN_OPEN']]) # Insert one object into another
RUN: (1, [[]]) # Run towards something
SIT: (1, [['SITTABLE']]) # Sit on a suitable object
STANDUP: (0, []) # Stand up from a sitting or lying position
SWITCHOFF: (1, [['HAS_SWITCH']]) # Turn off an item with a switch
SWITCHON: (1, [['HAS_SWITCH']]) # Turn on an item with a switch
TOUCH: (1, [[]]) # Physically touch something
TURNTO: (1, [[]]) # Turn your body to face something
WATCH: (1, [[]]) # Observe something attentively
WIPE: (1, [[]]) # Clean or dry something by rubbing
PUTON: (1, [['CLOTHES']]) # Dress oneself with an item of clothing
PUTOFF: (1, [['CLOTHES']]) # Remove an item of clothing
GREET: (1, [['PERSON']]) # Offer a greeting to a person
DROP: (1, [[]]) # Let go of something so it falls
READ: (1, [['READABLE']]) # Read text from an object
LIE: (1, [['LIEABLE']]) # Lay oneself down on an object
POUR: (2, [['POURABLE', 'DRINKABLE'], ['RECIPIENT']]) # Transfer a liquid from one container to another
PUSH: (1, [['MOVABLE']]) # Exert force on something to move it away from you
PULL: (1, [['MOVABLE']]) # Exert force on something to bring it towards you
MOVE: (1, [['MOVABLE']]) # Change the location of an object
WASH: (1, [[]]) # Clean something by immersing and agitating it in water
RINSE: (1, [[]]) # Remove soap from something by applying water
SCRUB: (1, [[]]) # Clean something by rubbing it hard with a brush
SQUEEZE: (1, [['CLOTHES']]) # Compress clothes to extract liquid
PLUGIN: (1, [['HAS_PLUG']]) # Connect an electrical device to a power source
PLUGOUT: (1, [['HAS_PLUG']]) # Disconnect an electrical device from a power source
CUT: (1, [['EATABLE', 'CUTABLE']]) # Cut some food
EAT: (1, [['EATABLE']]) # Eat some food
RELEASE: (1, [[]]) # Let go of something inside the current room
TYPE: (1, [['HAS_SWITCH']]) # Type on a keyboard

Notice:
1. CLOSE action is opposed to OPEN action, CLOSE sth means changing the object's state from OPEN to CLOSE. 

2. You cannot [PUTIN] <character> <room name>. If you want robot INSIDE some room, please [WALK] <room name>.

3. The subject of all these actions is <character>, that is, robot itself. Do not include <character> as object_name. NEVER EVER use character as any of the object_name, that is, the argument of actions.

4. The action name should be upper case without white space. 

5. Importantly, if you want to apply ANY action on <object_name>, you should NEAR it. Therefore, you should apply WALK action as [WALK] <object_name> to first get near to the object before you apply any following actions, if you have no clue you are already NEAR <object_name>

6. Output only object names and their IDs, not just the names.

7. Output should not be empty! Always output some actions and their arguments.

8. If you want to apply an action on an object, you should WALK to the object first.

Input:
The relevant objects in the scene are:
<object_in_scene>

The current environment state is
<cur_change>

Node goals are:
<node_goals>

Edge goals are:
<edge_goals>

Action goals are:
<action_goals>

Please output the list of action commands in json format so that after the robot executes the action commands sequentially, the ending environment would satisfy all the node goals, edge goals and action goals. The dictionary keys should be action names. The dictionary values should be a list containing the objects of the corresponding action. Only output the json of action commands in a dictionary with nothing else.

Output:
"""

if __name__ == "__main__":
    pass