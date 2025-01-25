from transitions import Machine
from transitions.extensions import GraphMachine
from collections import defaultdict
import copy

class MarkovChain:
    # to do, convert sequence input to list of ints
    def __init__(self, sequence: list[str]):
        self.sequence = sequence
        self.states = [state for state in set(sequence)]
        self.sequence_length = len(sequence)
        self.transition_counts = self.generate_counts()
        self.transition_probabilities = self.generate_probabilities()
        
    def generate_counts(self):
        states = set(self.sequence)
        state_dict = defaultdict(lambda: defaultdict(int))
        for state1 in states:
            for state2 in states:
                state_dict[state1][state2] = 0
        old_pitch = self.sequence[0]
        
        for i in range(1,len(self.sequence)):
            new_pitch = self.sequence[i]
            state_dict[old_pitch][new_pitch] += 1
            old_pitch = new_pitch
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