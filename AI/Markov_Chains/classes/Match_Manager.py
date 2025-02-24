import time
from enum import Enum


class TeamEnum(Enum):
    A = "Team A"
    B = "Team B"


class Match_Manager:
    def __init__(self, team_a, team_b):
        self.team_a = team_a
        self.team_b = team_b
        self.current_team = TeamEnum.A

    def start_match(self):
        start_time = time.time()
        ball_position = "Central"
        half_time_called = False  # Prevents multiple half-time prints

        while time.time() - start_time < 60:
            elapsed_time = time.time() - start_time

            if elapsed_time >= 30 and not half_time_called:
                print("\n--- Half Time! ---\n")
                half_time_called = True  # Ensure it's printed only once

            if self.current_team == TeamEnum.A:
                result, new_position = self.team_a.play(ball_position)
                if result == 'goal':
                    print(f"{self.team_a.team_name} scores a goal!")

                self.current_team = TeamEnum.B  # Switch possession
            else:
                result, new_position = self.team_b.play(ball_position)
                if result == 'goal':
                    print(f"{self.team_b.team_name} scores a goal!")

                self.current_team = TeamEnum.A  # Switch possession

            ball_position = new_position
            time.sleep(1.5)  # Add a delay to make it run for 60 seconds

        print("\n--- Full Time! Match Over. ---\n")
        print(f"Final Result: [{self.team_a.team_name}  {self.team_a.goals} - {self.team_b.goals}  {self.team_b.team_name}]")
