import numpy as np


class Team:
    def __init__(self, team_name, matrix,g):
        self.team_name = team_name
        self.matrix = matrix  # Transition matrix
        self.g = g   #Goal Vector
        self.description = {0: 'Central', 1: 'Wing', 2: 'Box'}
        self.goals = 0

    def goals(self):
        return self.goals

    def set_team_name(self, team_name):
        self.team_name = team_name


    def set_matrix(self, matrix):
        self.matrix = matrix

    # Play method (expects 'from' as parameter)
    def play(self, from_position):
        print(f"[{self.team_name}]")
        ballinplay = True
        # Initial state is i
        s = [key for key, value in self.description.items() if value == from_position][0]
        describe_possession = ''

        while ballinplay:
            r = np.random.rand()

            # Make commentary text
            describe_possession = describe_possession + ' - ' + self.description[s]

            # Cumulative sum of in play probabilities
            c_sum = np.cumsum(self.matrix[s, :])
            new_s = np.sum(r > c_sum)
            if new_s > 2:
                # Ball is either goal or out of play
                ballinplay = False
                if r < self.g[s] + c_sum[0, 2]:
                    # It's a goal!
                    self.goals += 1
                    describe_possession += ' - Goal!'
                    print(describe_possession)
                    return ['goal', 'Central']
                else:
                    describe_possession += ' - Lost Ball'
                    print(describe_possession)
                    return ['lost', from_position]
            s = new_s


