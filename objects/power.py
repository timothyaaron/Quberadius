import random
from constants import COLUMN_COUNT, ROW_COUNT


POWERS = [
    "Destroy Column",
    "Destroy Row",
    "Kamakazi Column",
    "Kamakazi Row",
    "Lower Tile Column",
    "Lower Tile Row",
    "Lower Tile",
    "Raise Tile Column",
    "Raise Tile Row",
    "Raise Tile",
    "Trench Column",
    "Trench Row",
    "Trench",
    "Wall Column",
    "Wall Row",
    "Wall",
    "Earthquake",
]

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

    def kamakazi_column(self, square):
        board = square.board
        squares = [board.grid[square.column][j] for j in range(ROW_COUNT)]
        return any([s.remove_piece() for s in squares if s.piece])

    def kamakazi_row(self, square):
        board = square.board
        squares = [board.grid[i][square.row] for i in range(COLUMN_COUNT)]
        return any([s.remove_piece() for s in squares if s.piece])

    def wall_column(self, square):
        board = square.board
        return any([self.wall(board.grid[square.column][j]) for j in range(ROW_COUNT)])

    def wall_row(self, square):
        board = square.board
        return any([self.wall(board.grid[i][square.row]) for i in range(COLUMN_COUNT)])

    def wall(self, square):
        return any([square.pull_up() for _ in range(5)])

    def trench_column(self, square):
        board = square.board
        return any([self.trench(board.grid[square.column][j]) for j in range(ROW_COUNT)])

    def trench_row(self, square):
        board = square.board
        return any([self.trench(board.grid[i][square.row]) for i in range(COLUMN_COUNT)])

    def trench(self, square):
        return any([square.push_down() for _ in range(5)])

    def lower_tile_column(self, square):
        board = square.board
        return any([self.lower_tile(board.grid[square.column][j]) for j in range(ROW_COUNT)])

    def lower_tile_row(self, square):
        board = square.board
        return any([self.lower_tile(board.grid[i][square.row]) for i in range(COLUMN_COUNT)])

    def lower_tile(self, square):
        return square.push_down()

    def raise_tile_column(self, square):
        board = square.board
        return any([self.raise_tile(board.grid[square.column][j]) for j in range(ROW_COUNT)])

    def raise_tile_row(self, square):
        board = square.board
        return any([self.raise_tile(board.grid[i][square.row]) for i in range(COLUMN_COUNT)])

    def raise_tile(self, square):
        return square.pull_up()

    def earthquake(self, square):
        board = square.board
        for row in range(ROW_COUNT):
            for column in range(COLUMN_COUNT):
                square = board.grid[column][row]
                elevation = random.randint(1, 60)
                if elevation < 5:
                    square.push_down()
                    square.push_down()
                elif elevation < 25:
                    square.push_down()
                elif elevation > 55:
                    square.pull_up()
                    square.pull_up()
                elif elevation > 35:
                    square.pull_up()
        return True