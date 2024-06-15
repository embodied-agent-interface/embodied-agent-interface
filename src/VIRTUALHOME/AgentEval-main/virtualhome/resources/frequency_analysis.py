import re
from collections import Counter
import json

def analyze_predicate_frequency(text, action_name, predicate_dict, section, top_k=None):
    """
    Analyze the frequency of predicates in the specified section (preconditions or effects) of a given action.

    Args:
    - text (str): The entire text from the file.
    - action_name (str): The specific action to analyze.
    - predicate_dict (dict): Dictionary of predicates to check.
    - section (str): Can be either "preconditions" or "effects".
    - top_k (int, optional): Number of top predicates to return. If None, return all.

    Returns:
    - dict: A dictionary with predicates as keys and a tuple (count, frequency) as values.
    """
    # Regular expression to find the specific action block
    action_pattern = re.compile(
        r"GPT predicted action:\s*:action " + re.escape(action_name) +
        r".*?:preconditions \(.*?\).*?:effects \(.*?\)",
        re.DOTALL
    )

    # Find the action block
    action_block = action_pattern.search(text)
    if not action_block:
        return {}  # No action block found for the given action_name

    # Extract the content of the specified section
    section_pattern = re.compile(r":" + re.escape(section) + r" \((.*?)\)", re.DOTALL)
    section_content = section_pattern.search(action_block.group(0))
    if not section_content:
        return {}  # No content found for the specified section

    # Extract all words from the section content that match the keys in predicate_dict
    predicates = re.findall(r"(\b" + r"\b|\b".join(map(re.escape, predicate_dict.keys())) + r"\b)", section_content.group(1))
    
    # Count predicates
    predicate_counts = Counter(predicates)
    
    # Calculate total counts
    total_counts = sum(predicate_counts.values())
    
    # Calculate frequencies
    predicate_frequencies = {pred: (count, count / total_counts if total_counts > 0 else 0) for pred, count in predicate_counts.items()}
    
    # If top_k is specified, return the top_k elements
    if top_k is not None:
        predicate_frequencies = dict(predicate_frequencies.most_common(top_k))
    
    return predicate_frequencies

# Example text input and parameters
text_example = """GPT predicted action:
:action spacial_walk
  :parameters (?char - character ?obj - object)
  :preconditions (and (sittable ?obj) (inside_room ?obj bedroom) (inside ?char dining_room) (next_to ?char ?obj))
  :effects (and (lieable ?obj))

GPT predicted action:
:action run
  :parameters (?char - character ?obj - object)
  :preconditions (and (running ?char) (next_to ?char ?obj))
  :effects (and (tired ?char))"""

predicate_path = '/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/resources/pddl_files/predicates_category.json'
predicate_dict = json.load(open(predicate_path, 'r'))
# Function call example
analyze_predicate_frequency(text_example, "spacial_walk", predicate_dict_example, "preconditions")
