import numpy as np
import pandas as pd
import psycopg2
import math
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from tabulate import tabulate

import warnings
warnings.simplefilter("ignore", UserWarning)
# Database connection parameters
conn = psycopg2.connect(
    dbname="Footex",
    user="postgres",
    password="00000",
    host="localhost",
    port=5432
)

# Fetch match data
df_matches = pd.read_sql("SELECT * FROM matches;", conn)

# Fetch shot data
query = """
SELECT 
    s.*, 
    e.under_pressure, 
    e.location,
    m.match_id,
    home_team.team_name AS home_team_name,
    away_team.team_name AS away_team_name,
    event_team.team_name AS event_team_name  -- Team that performed the event
FROM shot_events s
JOIN base_events e ON s.event_id = e.event_id
JOIN matches m ON e.match_id = m.match_id  -- Ensures match_id exists in matches
JOIN teams home_team ON m.home_team_id = home_team.team_id
JOIN teams away_team ON m.away_team_id = away_team.team_id
JOIN teams event_team ON e.team_id = event_team.team_id  -- Get the team performing the shot
WHERE e.type = 'Shot' 
AND e.period <= 4;

"""


df_shot = pd.read_sql(query, conn)

df_evaluate = pd.read_sql(query, conn)
# Close the connection
conn.close()

# Split 'location' into 'x' and 'y' columns
df_shot[['x', 'y']] = df_shot['location'].apply(lambda loc: pd.Series(ast.literal_eval(loc) if isinstance(loc, str) else loc))

# print(tabulate(df_shot.head(10), headers='keys', tablefmt='psql'))

def calculate_angle(x, y):
  # 44 and 36 is the location of each goal post
  g0 = [120, 44]
  p = [x, y]
  g1 = [120, 36]

  v0 = np.array(g0) - np.array(p)
  v1 = np.array(g1) - np.array(p)

  angle = math.atan2(np.linalg.det([v0, v1]), np.dot(v0, v1))
  return abs(np.degrees(angle))

def calculate_distance(x, y):
  x_dist = 120-x
  y_dist = 0
  if y<36:
    y_dist = 36-y
  elif y>44:
    y_dist = y-44
  return math.sqrt(x_dist**2 + y_dist**2)

def is_preferable_side(y, body_part_name):
  # what I mean by preferable side is if a right-footed player gets a chance from left side of the pitch (usually a left winger)
  # he could perform a finesse right-footed shot which I think has bigger probability of scoring instead of left-footed shot
  preferable_side = 0
  side = 'center'
  if (y<40):
    side = 'left'
  elif (y>40):
    side = 'right'

  if ((side=='left') & (body_part_name=='Right Foot')) | ((side=='right') & (body_part_name=='Left Foot')):
    preferable_side = 1
  return preferable_side


def calculate_xg(row):
    under_pressure = 0 if np.isnan(row['under_pressure']) else 1
    angle = calculate_angle(row['x'], row['y'])
    distance = calculate_distance(row['x'], row['y'])
    preferable_side = is_preferable_side(row['y'], row['shot_body_part'])
    header = 1 if row['shot_body_part'] == 'Head' else 0
    first_time = row['first_time']
    one_on_one = row['one_on_one']

    technique_name = {}
    sub_type_name = {}

    technique_name['Backheel'] = technique_name['Diving Header'] = 0
    technique_name['Half Volley'] = technique_name['Lob'] = 0
    technique_name['Normal'] = technique_name['Overhead Kick'] = 0
    technique_name['Volley'] = sub_type_name['Corner'] = 0
    sub_type_name['Free Kick'] = sub_type_name['Open Play'] = 0
    sub_type_name['Penalty'] = 0

    technique_name[row['shot_technique']] = 1
    sub_type_name[row['shot_type']] = 1

    X = [[under_pressure, angle, distance, preferable_side, header,
          technique_name['Backheel'], technique_name['Diving Header'],
          technique_name['Half Volley'], technique_name['Lob'],
          technique_name['Normal'], technique_name['Overhead Kick'],
          technique_name['Volley'], sub_type_name['Corner'],
          sub_type_name['Free Kick'], sub_type_name['Open Play'],
          sub_type_name['Penalty'], first_time, one_on_one]]

    xg = XG_model.predict_proba(X)[:, 1][0]
    return xg


def evaluate_single_match(id):
# let's try to evaluate it on all matches and store it into dataframe
    df_evaluate_match = df_shot.loc[df_shot['match_id'] == id].copy()
    # calculate xg per shot using advanced model
    df_evaluate_match['our_xg'] = df_evaluate_match.apply(lambda row: calculate_xg(row), axis=1)
    current_teams = np.concatenate((df_evaluate_match['home_team_name'].unique(),
                                df_evaluate_match['away_team_name'].unique()))
    team_stats = []

    for team in current_teams:
        df_team = df_evaluate_match[df_evaluate_match['event_team_name'] == team]
        actual_goal = len(df_team[df_team['shot_outcome'] == 'Goal'])
        print(tabulate(df_team.head(10), headers='keys', tablefmt='psql'))
        sum_xg = df_team['our_xg'].sum()
        sum_xg_sb = df_team['statsbomb_xg'].sum()
        print(team)
        print("Actual goals: " + str(actual_goal))
        print("Expected goals: " + str(round(sum_xg, 2)))
        print("Expected goals by Statsbomb: " + str(round(sum_xg_sb, 2)))
        team_stats.append({
            "team": team,
            "actual_goals": actual_goal,
            "our_xg": round(sum_xg, 2),
            "statsbomb_xg": round(sum_xg_sb, 2)
        })
    return team_stats

def get_team_open_play_shots(team_name):
    return df_shot[(df_shot['event_team_name'] == team_name) & (df_shot['shot_type'] == 'Open Play')]

df_shot['angle'] = df_shot.apply(lambda row:calculate_angle(row['x'], row['y']), axis=1)
df_shot['distance'] = df_shot.apply(lambda row:calculate_distance(row['x'], row['y']), axis=1)

df_shot['preferable_side'] = df_shot.apply(lambda row:is_preferable_side(row['y'], row['shot_body_part']), axis=1)
df_shot['header'] = df_shot.apply(lambda row:1 if row['shot_body_part']=='Head' else 0, axis=1)
df_shot['under_pressure'] = df_shot['under_pressure'].fillna(0)
df_shot['under_pressure'] = df_shot['under_pressure'].astype(int)
df_shot['first_time'] = df_shot['first_time'].fillna(0)
df_shot['first_time'] = df_shot['first_time'].astype(int)
df_shot['one_on_one'] = df_shot['one_on_one'].fillna(0)
df_shot['one_on_one'] = df_shot['one_on_one'].astype(int)

# One-hot encode without removing the original column
shot_technique_dummies = pd.get_dummies(df_shot['shot_technique'], prefix='shot_technique')
shot_type_dummies = pd.get_dummies(df_shot['shot_type'], prefix='shot_type')

# Concatenate the one-hot encoded columns while keeping the original ones
df_shot = pd.concat([df_shot, shot_technique_dummies, shot_type_dummies], axis=1)


df_shot['goal'] = df_shot.apply(lambda row:1 if row['shot_outcome']=='Goal' else 0, axis=1)
# print(tabulate(df_shot.head(10), headers='keys', tablefmt='psql'))
# print(df_shot['shot_technique'].unique())
# print(df_shot['shot_type'].unique())


# Modelling
X_cols = ['under_pressure', 'angle', 'distance',
       'preferable_side', 'header', 'shot_technique_Backheel',
       'shot_technique_Diving Header', 'shot_technique_Half Volley',
       'shot_technique_Lob', 'shot_technique_Normal',
       'shot_technique_Overhead Kick', 'shot_technique_Volley',
       'shot_type_Corner', 'shot_type_Free Kick',
       'shot_type_Open Play', 'shot_type_Penalty', 'first_time', 'one_on_one']

X = df_shot[X_cols]
y = df_shot['goal']

XG_model = LogisticRegression()
XG_model.fit(X, y)
y_pred = XG_model.predict_proba(X)[:, 1]
metrics.r2_score(y, y_pred)
# print(metrics.r2_score(y, y_pred))
# print(metrics.r2_score(y, df_shot['statsbomb_xg']))

df_shot['xG'] = y_pred
# print(tabulate(df_shot.head(10), headers='keys', tablefmt='psql'))
# print(tabulate(df_matches.head(10), headers='keys', tablefmt='psql'))
# print(tabulate(df_evaluate.head(10), headers='keys', tablefmt='psql'))
# print(tabulate(get_team_open_play_shots('Barcelona').head(50), headers='keys', tablefmt='psql'))
# evaluate_single_match(3773386)