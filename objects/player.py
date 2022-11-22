from constants import PLAYER_COLORS

class Player:
    def __init__(self, idx):
        self.idx = idx
        self.color = PLAYER_COLORS[idx]
        self.turns = 0
