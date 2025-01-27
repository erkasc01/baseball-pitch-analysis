from transitions import Machine
from transitions.extensions import GraphMachine
from collections import defaultdict
import copy

class MarkovChain:
    # to do, convert sequence input to list of ints
    def __init__(self, sequence):
        self.sequence = sequence
        self.states = self.get_states()
        self.sequence_length = len(sequence)
        self.transition_counts = self.generate_counts()
        self.transition_probabilities = self.generate_probabilities()
    def get_states(self):
        if isinstance(self.sequence, list):
            states = [state for state in set(sequence)]
        elif isinstance(self.sequence, defaultdict):
            states = set.union(*[set(x) for x in self.sequence.values()])
            states = [x for x in states]
        return states
    def generate_counts(self):
        states = self.states
        # Logic for single input list
        if isinstance(self.sequence, list):
            
            state_dict = defaultdict(lambda: defaultdict(int))
            for state1 in states:
                for state2 in states:
                    state_dict[state1][state2] = 0
            old_state = self.sequence[0]
            
            for i in range(1,len(self.sequence)):
                new_state = self.sequence[i]
                state_dict[old_state][new_state] += 1
                old_state = new_state
        # Logic for multiple input lists (multiple games)
        if isinstance(self.sequence, defaultdict):
            state_dict = defaultdict(lambda: defaultdict(int))
            for state1 in states:
                for state2 in states:
                    state_dict[state1][state2] = 0
            for game in self.sequence:
                old_state = self.sequence[game][0]
                for i in range(1, len(self.sequence[game])):
                    new_state = self.sequence[game][i]
                    state_dict[old_state][new_state] += 1
                    old_state = new_state
            
        return state_dict
        
    def generate_probabilities(self):
        transition_probabilities = copy.deepcopy(self.transition_counts)
        
        for state1 in transition_probabilities:
            total_count = sum([x for x in transition_probabilities[state1].values()])
            for state2 in transition_probabilities:
                transition_probabilities[state1][state2] /= total_count
        return transition_probabilities

    def generate_state_machine(self):

        transitions = []
        for state1 in self.states:
            for state2 in self.states:
                if self.transition_probabilities[state1][state2] != 0:
                    transitions.append({"trigger": str(round(self.transition_probabilities[state1][state2],3)), "source": state1, "dest": state2})
        
        pitch_machine = GraphMachine(states=self.states, transitions=transitions, initial=self.sequence[0])
        return pitch_machine