from collections import defaultdict
from copy import deepcopy
from os.path import exists
from transitions.extensions import GraphMachine


class MarkovChain:
    # To do, convert sequence input to list of ints
    def __init__(self, sequence):
        if not sequence:
            raise ValueError("ERROR: Input cannot be empty.")
        self.sequence = sequence
        self.states = self.get_states()
        self.sequence_length = self.get_input_length()
        self.transition_counts = self.generate_counts()
        self.transition_probabilities = self.generate_probabilities()
        self.state_machine = self.generate_state_machine()

    def get_states(self):
        if isinstance(self.sequence, list):
            states = [
                    state
                    for state in set(self.sequence)
                    if state not in ["CS", "PO"]
                ]
        elif isinstance(self.sequence, defaultdict):
            states = set.union(*[set(x) for x in self.sequence.values()])
            states = [x for x in states if x not in ["CS", "PO"]]
        return states

    def get_input_length(self):
        if isinstance(self.sequence, list):
            length = len(self.sequence)
        elif isinstance(self.sequence, defaultdict):
            length = [len(self.sequence[entry]) for entry in self.sequence]
        return length

    def generate_counts(self):
        states = self.states
        # Logic for single input list
        if isinstance(self.sequence, list):

            state_dict = defaultdict(lambda: defaultdict(int))
            for state1 in states:
                for state2 in states:
                    state_dict[state1][state2] = 0
            old_state = self.sequence[0]

            for i in range(1, len(self.sequence)):
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
                game_length = len(self.sequence[game])
                old_state = self.sequence[game][0]
                for i in range(1, game_length):
                    new_state = self.sequence[game][i]
                    # Misclassified balls are sometimes labeled "CS" or "PO"
                    # We will ignore these. First check if it is the
                    # last element in the game array
                    if new_state in ["CS", "PO"] and i == game_length-1:
                        continue
                    elif new_state in ["CS", "PO"] and i != game_length-1:
                        old_state = self.sequence[game][i+1]
                        i += 1
                        continue
                    state_dict[old_state][new_state] += 1
                    old_state = new_state

        return state_dict

    def generate_probabilities(self):
        transition_probabilities = deepcopy(self.transition_counts)
        for state1 in transition_probabilities:
            total_count = sum([
                            x
                            for x in transition_probabilities[state1].values()
                        ])
            for state2 in transition_probabilities:
                try:
                    transition_probabilities[state1][state2] /= total_count
                # If we end on a pitch that is the only instance of its
                # kind in the game, then there is a division error, so
                # we set the transition probability to 0
                except ZeroDivisionError:
                    transition_probabilities[state1][state2] = 0
        return transition_probabilities

    def most_common_pitch(self):
        if isinstance(self.sequence, list):
            pitches = self.sequence

        if isinstance(self.sequence, defaultdict):
            pitches = []
            for game in self.sequence:
                pitches += self.sequence[game]

        return max(pitches, key=pitches.count)

    def generate_state_machine(self):

        transitions = []
        for state1 in self.states:
            for state2 in self.states:
                if self.transition_probabilities[state1][state2] != 0:
                    probability = round(
                                self.transition_probabilities[state1][state2],
                                3
                            )
                    text = str(probability)
                    transitions.append({
                                    "trigger": text,
                                    "source": state1,
                                    "dest": state2
                                })

        pitch_machine = GraphMachine(
                            states=self.states,
                            transitions=transitions,
                            initial=self.most_common_pitch()
                        )

        return pitch_machine

    def save_state_diagram(self, pitcher_name):
        if self.state_machine:
            fpath = (
                f"static/diagrams/{pitcher_name.replace(" ", "_")}"
                "_state_machine.jpg"
            )
            if not exists(fpath):
                print((
                    f"INFO: State machine diagram for {pitcher_name} does not"
                    f" exist. Creating {fpath}."
                ))
                self.state_machine.get_graph().draw(fpath, prog="dot")
            elif exists(fpath):
                print((
                    f"INFO: State machine diagram for {pitcher_name} exists."
                    f" returning {fpath}."
                ))
            return fpath
