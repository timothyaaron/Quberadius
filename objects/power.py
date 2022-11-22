from constants import COLUMN_COUNT, ROW_COUNT


class Power:
    """
    Abstract class for all Powers
    :param str name: Name of Power
    :param str valid_on: Name of squares this Power can be used on.
    """
    def __init__(self, name, valid_on=None):
        self.name = name
        self.count = 1
        self.execute = getattr(self, name.lower().replace(" ", "_"))

        last_word = name.lower().split()[-1]
        self.valid_on = last_word if not valid_on and last_word in ("column", "row", "radial") else "any"

    def __repr__(self):
        return f"{self.name} ({self.count})"

    # TODO: support radial, self, ally, enemy, empty
    def is_valid(self, square, game):
        if self.valid_on == "row":
            if square.row != square.board.selected.row:
                game.debug_window.text = f"Only usable on your row.\nDeactivated."
                return False
            return True

        if self.valid_on == "column":
            if square.column != square.board.selected.column:
                game.debug_window.text = f"Only usable on your column.\nDeactivated."
                return False
            return True

        if self.valid_on == "any":
            return True

    def remove_piece(self, piece):
        pass

    def destroy_column(self, square):
        board = square.board
        squares = [board.grid[square.column][j] for j in range(ROW_COUNT)]
        return any([board.remove_piece(s.piece, keep_player=board.current) for s in squares if s.piece])

    def destroy_row(self, square):
        board = square.board
        squares = [board.grid[i][square.row] for i in range(COLUMN_COUNT)]
        return any([board.remove_piece(s.piece, keep_player=board.current) for s in squares if s.piece])

    def lower_column(self, square):
        board = square.board
        return any([self.lower(board.grid[square.column][j]) for j in range(ROW_COUNT)])

    def lower_row(self, square):
        board = square.board
        return any([self.lower(board.grid[i][square.row]) for i in range(COLUMN_COUNT)])

    def lower(self, square):
        if square.elevation <= 1:
            return False

        square.elevation -= 1
        square.center_x -= 2
        square.center_y -= 2
        square.alpha -= 40

        if square.piece:
            square.piece.center_x = square.center_x
            square.piece.center_y = square.center_y
            square.piece.alpha = square.alpha

        return True
