import random

import arcade

from constants import HEIGHT, WIDTH, MARGIN


class Square(arcade.Sprite):
    def __init__(self, board, row, column, **kwargs):
        # calculate coordinates
        self.i = self.column = column
        self.j = self.row = row
        self.x = column * (WIDTH + MARGIN) + (WIDTH / 2 + MARGIN)
        self.y = row * (HEIGHT + MARGIN) + (HEIGHT / 2 + MARGIN)

        # initiate Sprite
        super().__init__(
            center_x=self.x,
            center_y=self.y,
            image_width=128,
            image_height=128,
            scale=WIDTH / 128,
            filename=":resources:images/tiles/stoneCenter_rounded.png",
            angle=random.choice([0, 90, 180, 270]),
        )

        self.elevation = 3
        self.alpha = 170

        self.board = board
        self._piece = None

    def __repr__(self):
        return f"Square ({self.i}, {self.j})"

    @property
    def piece(self):
        return self._piece

    @piece.setter
    def piece(self, value):
        # add Piece to Square
        self._piece = value

        # if Piece, move and add Square back reference
        if value:
            value.center_x = self.center_x
            value.center_y = self.center_y
            value.alpha = self.alpha
            value.square = self

    def remove_piece(self, keep_player=None):
        for list in self.board.game.piece_sprites:
            try:
                if self.piece.player != keep_player:
                    list.remove(self.piece)
                    if len(list) == 0:
                        self.players.remove(self.piece.player)
                    return True
            except Exception:
                pass

    def push_down_column(self):
        return any([self.board.grid[i][self.column].push_down() for i in range(COLUMN_COUNT)])

    def push_down_row(self):
        return any([self.board.grid[self.row][j].push_down() for j in range(ROW_COUNT)])

    def push_down(self):
        if self.elevation >= 5:
            return False

        self.elevation += 1
        self.center_x -= 2
        self.center_y -= 2
        self.alpha -= 40

        if self.piece:
            self.piece.center_x = self.center_x
            self.piece.center_y = self.center_y
            self.piece.alpha = self.alpha

        return True

    def pull_up_column(self):
        return any([self.board.grid[i][self.column].pull_up() for i in range(COLUMN_COUNT)])

    def pull_up_row(self):
        return any([self.board.grid[self.row][j].pull_up() for j in range(ROW_COUNT)])

    def pull_up(self):
        if self.elevation <= 1:
            return False

        self.elevation -= 1
        self.center_x += 2
        self.center_y += 2
        self.alpha += 40

        if self.piece:
            self.piece.center_x = self.center_x
            self.piece.center_y = self.center_y
            self.piece.alpha = self.alpha

        return True
