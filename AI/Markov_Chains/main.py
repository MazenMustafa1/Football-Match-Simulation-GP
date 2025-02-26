import numpy as np
from AI.Markov_Chains.classes.Match_Manager import Match_Manager
from AI.Markov_Chains.classes.Team import Team
from AI.Markov_Chains.classes.StatsBomb import StatsBomb



team_a = 'Real Madrid'
team_b = 'Barcelona'

data_a = StatsBomb(team_a)
data_b = StatsBomb(team_b)

list_a = data_a.get_open_play_avg_xg_all_positions()
list_b = data_b.get_open_play_avg_xg_all_positions()


a = Team(team_a,np.matrix([[0.25, 0.20, 0.1], [0.1, 0.25, 0.2], [0.1, 0.1, 0.25]]), np.transpose(np.matrix(list_a)))
b = Team(team_b, np.matrix([[0.25, 0.20, 0.1], [0.1, 0.25, 0.2], [0.1, 0.1, 0.25]]), np.transpose(np.matrix(list_b)))

match = Match_Manager(a,b)

match.start_match()