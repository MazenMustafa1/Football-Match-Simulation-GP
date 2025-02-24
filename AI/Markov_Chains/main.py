import numpy as np
from AI.Markov_Chains.classes.Match_Manager import Match_Manager
from AI.Markov_Chains.classes.Team import Team



a = Team('Real Madrid',np.matrix([[0.25, 0.20, 0.1], [0.1, 0.25, 0.2], [0.1, 0.1, 0.25]]), np.transpose(np.matrix([0.05, 0.15, 0.05])))
b = Team('Barcelona', np.matrix([[0.25, 0.20, 0.1], [0.1, 0.25, 0.2], [0.1, 0.1, 0.25]]), np.transpose(np.matrix([0.05, 0.15, 0.05])))

match = Match_Manager(a,b)

match.start_match()