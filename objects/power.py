from constants import COLUMN_COUNT, ROW_COUNT


class Power:
    """
    Abstract class for all Powers
    :param str name: Name of Power
    :param str valid_on: Name of squares this Power can be used on.
    """
    counter = 0

    def __init__(self, name, valid_on=None):
        self.name = name
        self.count = 1
        self.execute = getattr(self, name.lower().replace(" ", "_"))

        last_word = name.lower().split()[-1]
        self.valid_on = last_word if not valid_on and last_word in ("column", "row", "radial") else "any"

        Power.counter += 1
        self.counter = Power.counter

    def __str__(self):
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

    def destroy_column(self, square):
        board = square.board
        squares = [board.grid[square.column][j] for j in range(ROW_COUNT)]
        return any([s.remove_piece(keep_player=board.current) for s in squares if s.piece])

    def destroy_row(self, square):
        board = square.board
        squares = [board.grid[i][square.row] for i in range(COLUMN_COUNT)]
        return any([s.remove_piece(keep_player=board.current) for s in squares if s.piece])

    def lower_column(self, square):
        board = square.board
        return any([self.lower(board.grid[square.column][j]) for j in range(ROW_COUNT)])

    def lower_row(self, square):
        board = square.board
        return any([self.lower(board.grid[i][square.row]) for i in range(COLUMN_COUNT)])

    def lower(self, square):
        return square.push_down()
