import random

import arcade

from constants import PLAYER_COLORS, WIDTH
from objects.power import Power


class Piece(arcade.Sprite):
    def __init__(self, player, **kwargs):
        super().__init__(
            center_x=0,
            center_y=0,
            image_width=128,
            image_height=128,
            scale=WIDTH / 128 / 1.4,
            filename=":resources:images/tiles/boxCrate_double.png",
            angle=random.randint(-5, 5),
        )
        self.alpha = 160
        self.player = player
        self.square = None
        self.powers = [
            Power("Destroy Row"), Power("Destroy Column"),
            Power("Lower Row"), Power("Lower Column"), Power("Lower"),
        ]
        self.turns = 0

    def __repr__(self):
        return f"Player {self.player.idx})"

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, value):
        self._player = value
        self.color = PLAYER_COLORS[value.idx]

    def can_move_to(self, square):
        column = self.square.column
        row = self.square.row
        for i in range(column-1, column+2):
            for j in range(row-1, row+2):
                try:
                    if self.square.board.grid[i][j] == square:
                        return True
                except Exception:
                    pass
        return False
