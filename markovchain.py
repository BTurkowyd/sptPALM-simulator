import numpy as np

class MarkovChain:
    def __init__(self, transition_matrix, emission_matrix):
        self.transition_matrix = transition_matrix
        self.emission_matrix = emission_matrix
        self.states = list(self.transition_matrix.keys())
        self.emissions = list(self.emission_matrix[self.states[0]].keys())

    def next_state(self, current_state):
        n_state = np.random.choice(self.states, p=[self.transition_matrix[current_state][next_state] for next_state in self.states])
        n_emission = np.random.choice(self.emissions, p=[self.emission_matrix[n_state][emission] for emission in self.emissions])
        return n_state, n_emission

    def generate_states(self, current_state, n = 10):
        self.future_states = []
        self.future_emissions = []
        for _ in range(n):
            next_state, next_emission = self.next_state(current_state)
            self.future_states.append(next_state)
            self.future_emissions.append(next_emission)
            current_state = next_state