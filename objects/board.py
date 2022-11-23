import random

import arcade

from constants import (
    PLAYER_COUNT,
    DEFAULT_COLOR,
    ROW_COUNT,
    COLUMN_COUNT,
    SELECTED_COLOR,
    SIDEBAR_WIDTH,
)
from objects.piece import Piece
from objects.player import Player
from objects.square import Square


class Board:
    """
    Board class that contains all Squares.

    :param array[][] grid: 2d-array of all Squares on the Board
    :param Square selected: The currently selected Square
    """
    def __init__(self, game, column_count=COLUMN_COUNT, row_count=ROW_COUNT, player_count=PLAYER_COUNT, **kwargs):
        self.game = game
        self.column_count = column_count
        self.row_count = row_count
        self.player_count = player_count
        self._selected = None
        self.power = False
        self.turns = 0
        self.grid = []
        self.players = []

    def add_squares(self):
        # build grid
        for column in range(self.column_count):
            self.grid.append([])

            # add squares
            for row in range(self.row_count):
                square = Square(self, row, column)
                self.grid[column].append(square)
                self.game.square_sprites.append(square)

    def add_players(self):
        for idx in range(self.player_count):
            self.players.append(Player(idx))

            # add pieces
            piece_count = int(len(self.game.square_sprites) / 3 / self.player_count)
            for x in range(piece_count):
                i = random.randint(0, self.column_count-1)
                j = random.randint(0, self.row_count-1)
                while self.grid[i][j].piece:
                    i = random.randint(0, self.column_count-1)
                    j = random.randint(0, self.row_count-1)
                piece = Piece(self.players[-1])
                self.grid[i][j].piece = piece
                self.game.piece_sprites[idx].append(piece)
        self.current = self.players[0]

    def next_player(self):
        player_idx = self.players.index(self.current)
        return self.players[(player_idx + 1) % len(self.players)]

    def end_turn(self):
        self.current.turns += 1
        self.current = self.next_player()

        # next player's color
        self.game.sidebar.children[0].children[0] = arcade.gui.UITextArea(
            text="Quberadius",
            text_color=self.current.color,
            width=SIDEBAR_WIDTH,
            height=50,
            font_size=36,
            font_name="Kenney Future",
        )

        # count rounds
        if self.players[0] == self.current:
            self.turns += 1

    @property
    def selected(self) -> int:
        return self._selected

    @selected.setter
    def selected(self, new_selected):
        # clear previous
        if self._selected:
            self._selected.color = DEFAULT_COLOR

        # set selected
        self._selected = new_selected
        if self._selected:
            self._selected.color = SELECTED_COLOR
