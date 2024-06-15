import json

class Vocabulary:
    def __init__(self, file_path):
        self.vocab = self.load_vocab(file_path)
        
    def load_vocab(self, file_path):
        with open(file_path, 'r') as f:
            vocab = json.load(f)
        return vocab
    
    def get_vocab(self):
        return self.vocab
    
    def get_tl_predicates(self):
        return self.vocab['tl_predicates']
    
    def get_actions_all(self):
        return self.vocab['actions']
    
    def get_actions_all_in_list(self):
        return list(self.vocab['actions'].keys())
    
    def get_subgoal_actions(self):
        return self.vocab['subgoal_actions']
    
    def get_subgoal_actions_in_list(self):
        return list(self.vocab['subgoal_actions'].keys())
    
    def get_vh_info(self):
        '''
        Returns the vocabulary for properties, states and relations in VH
        '''
        return self.vocab['properties'], self.vocab['vh_states'], self.vocab['vh_relations']
    
    def get_tl_to_vh_predicates_dict(self):
        return self.vocab['tl_predicates_to_vh']
    
    def get_vh_states_to_tl_dict(self):
        return self.vocab['vh_states_to_tl']
    
    def get_vh_relations_to_tl_dict(self):
        return self.vocab['vh_relations_to_tl']

vocab_data_path = 'F:\\Projects\\Research\\embodiedAI\\AgentEval\\virtualhome\\resources\\vocabulary.json'

vocab = Vocabulary(vocab_data_path)


