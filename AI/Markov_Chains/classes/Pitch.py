

pitch_territories = {
    'right_wing': {'west': 0, 'east': 40, 'south': 18 , 'north': 0},
    'left_wing': {'west': 0, 'east': 40, 'south': 80 , 'north': 62},
    'penalty_box_one': {'west': 0, 'east': 18, 'south': 62 , 'north': 18},
    'outside_box_one': {'west': 18, 'east': 40, 'south': 62 , 'north': 18},
    'center_mid': {'west': 40, 'east': 80, 'south': 62 , 'north': 18},
    'right_mid': {'west': 40, 'east': 80, 'south': 18 , 'north': 0},
    'left_mid': {'west': 40, 'east': 80, 'south': 80 , 'north': 62},
    'penalty_box_two': {'west': 102, 'east': 120, 'south': 62 , 'north': 18},
    'right_flank': {'west': 80, 'east': 120, 'south': 18 , 'north': 0},
    'left_flank': {'west': 80, 'east': 120, 'south': 80 , 'north': 62},
    'outside_box_two': {'west': 80, 'east': 102, 'south': 62 , 'north': 18},
}


class Pitch:
    def __init__(self):
        pass

    def evaluate_coordinates(self,x,y):
        for place, bounds in pitch_territories.items():
            if bounds['west'] <= x <= bounds['east'] and bounds['north'] <= y <= bounds['south']:
                return place

        return "Out of bounds"  # If the coordinates do not match any defined area



p = Pitch()

print(p.evaluate_coordinates(102,62))