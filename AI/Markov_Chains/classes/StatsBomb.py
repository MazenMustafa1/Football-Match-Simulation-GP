import sys
import os

import pandas as pd
from tabulate import tabulate

# Move up two levels to 'AI'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

# Import module (rename if the space causes issues)
from XGmodel import DB_access as DBAccess  # Renaming to avoid issues


print("DB access imported successfully!")

class StatsBomb:
    def __init__(self, team_name):
        self.team_name = team_name

    def get_open_play_avg_xg_all_positions(self):
        df_shot = DBAccess.get_team_open_play_shots(self.team_name)
        # print('hiii')
        # print(tabulate(df_shot.head(50), headers='keys', tablefmt='psql'))
        # print(len(df_shot))
        # print(df_shot.iloc[0]['distance'])

        box_shots_df = pd.DataFrame(columns=df_shot.columns)
        wing_shots_df = pd.DataFrame(columns=df_shot.columns)
        center_shots_df = pd.DataFrame(columns=df_shot.columns)

        # Loop through the DataFrame
        for i in range(len(df_shot)):
            row = df_shot.iloc[i]  # Get the row

            if row['distance'] <= 12:
                box_shots_df = pd.concat([box_shots_df, row.to_frame().T], ignore_index=True)

            if row['angle'] <= 12:
                wing_shots_df = pd.concat([wing_shots_df, row.to_frame().T], ignore_index=True)

            if row['angle'] > 12:
                center_shots_df = pd.concat([center_shots_df, row.to_frame().T], ignore_index=True)

        # print(tabulate(box_shots_df.head(50), headers='keys', tablefmt='psql'))
        # print(tabulate(wing_shots_df.head(50), headers='keys', tablefmt='psql'))
        # print(tabulate(center_shots_df.head(50), headers='keys', tablefmt='psql'))

        box_avg = self.calc_avg(box_shots_df)
        wing_avg = self.calc_avg(wing_shots_df)
        center_avg = self.calc_avg(center_shots_df)

        return [center_avg, box_avg, wing_avg]

    def calc_avg(self, df):
        avg=0
        for i in range(len(df)):
            row = df.iloc[i]
            avg += DBAccess.calculate_xg(row)

        avg = avg/ len(df)
        return avg


sb = StatsBomb('Barcelona')
# sb.get_open_play_avg_xg_all_positions()

