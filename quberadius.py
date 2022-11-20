"""
Quberadius

"""
import random

import arcade
import arcade.gui


# Colors
DEFAULT_COLOR = arcade.color.WHITE
HIGHLIGHT_COLOR = arcade.color.YELLOW
SELECTED_COLOR = arcade.color.YELLOW_ROSE
PLAYER_COLORS = [
    arcade.color.RED,
    arcade.color.GREEN,
    arcade.color.BLUE,
    arcade.color.YELLOW,
    arcade.color.PINK,
]

# Square dimensions
PLAYER_COUNT = 3
ROW_COUNT = COLUMN_COUNT = 7
WIDTH = HEIGHT = 60
MARGIN = 5

# Window dimensions
SIDEBAR_WIDTH = 390
SIDEBAR_MARGIN = 10
BOARD_WIDTH = (WIDTH + MARGIN) * COLUMN_COUNT + MARGIN
BOARD_HEIGHT = (HEIGHT + MARGIN) * ROW_COUNT + MARGIN
SCREEN_WIDTH = BOARD_WIDTH + SIDEBAR_WIDTH
SCREEN_HEIGHT = BOARD_HEIGHT

SCREEN_TITLE = "Quberadius"


"""
TODO:
 - ESC deactivates power first
 - Limit diagonal movement
 - Limit elevation movement
 - Add Radial
 - Randomize powers
 - End game
 - Persistent powers
   - Change texture

 - Add Powers
   - Wall, Trench, Raise, Invert + CRR
   - Kamikazi + CRR
   - Roulette + CRR
   - Randomize + CRR
   - Stupify + CRR
   - ... other ideas?

 - Later
   - Animations
   - Online, multi-device
   - Custom arenas
"""


def pop_if(items, index, default=None):
    try:
        return items.pop(index)
    except IndexError:
        return default


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

    def destroy_column(self, square):
        board = square.board
        player_idx = board.current.idx
        squares = [board.grid[square.column][j] for j in range(ROW_COUNT)]
        return any([s.piece.remove(keep_idx=player_idx) for s in squares if s.piece])

    def destroy_row(self, square):
        board = square.board
        player_idx = board.current.idx
        squares = [board.grid[i][square.row] for i in range(COLUMN_COUNT)]
        return any([s.piece.remove(keep_idx=player_idx) for s in squares if s.piece])

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


class Board:
    """
    Board class that contains all Squares.

    :param array[][] grid: 2d-array of all Squares on the Board
    :param Square selected: The currently selected Square
    """
    def __init__(self, column_count=COLUMN_COUNT, row_count=ROW_COUNT, player_count=PLAYER_COUNT, **kwargs):
        self._selected = None
        self.power = False
        self.turns = 0

        # build grid
        self.grid = []
        for column in range(column_count):
            self.grid.append([])

            # add squares
            for row in range(row_count):
                square = Square(self, row, column)
                self.grid[column].append(square)

        # add players
        self.players = []
        for idx in range(player_count):
            self.players.append(Player(idx))

            # add pieces
            for x in range(int((COLUMN_COUNT * ROW_COUNT) / 3 / player_count)):
                i = random.randint(0, COLUMN_COUNT-1)
                j = random.randint(0, ROW_COUNT-1)
                while self.grid[i][j].piece:
                    i = random.randint(0, COLUMN_COUNT-1)
                    j = random.randint(0, ROW_COUNT-1)
                self.grid[i][j].piece = Piece(self.players[-1])

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
        self.alpha = 160

        self.board = board
        self._piece = None

        Qube.square_sprites.append(self)

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

        idx = self.board.current.idx
        squares = [self.board.grid[self.row][j] for j in range(ROW_COUNT)]
        return any([s.piece.remove(keep_idx=idx) for s in squares if s.piece])


class Player:
    def __init__(self, idx):
        self.idx = idx
        self.color = PLAYER_COLORS[idx]
        self.turns = 0


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

        Qube.piece_sprites[player.idx].append(self)

    def __repr__(self):
        idx = Qube.piece_sprites[self.player.idx].index(self)
        return f"Piece {idx} (Player {self.player.idx})"

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, value):
        self._player = value
        self.color = PLAYER_COLORS[value.idx]

    def remove(self, keep_idx=None):
        for list in Qube.piece_sprites:
            try:
                if self.player.idx != keep_idx:
                    list.remove(self)
                    if len(list) == 0:
                        self.square.board.players.remove(self.player)
                    return True
            except Exception:
                pass

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


class Qube(arcade.Window):
    """
    Main application class.
    """
    square_sprites = arcade.SpriteList()
    piece_sprites = [arcade.SpriteList() for _ in range(PLAYER_COUNT)]
    all_sprites = [square_sprites] + piece_sprites

    def __init__(self, width, height, title):
        """
        Set up the application.
        """
        # Create Window
        super().__init__(width, height, title)
        self.background_color = arcade.color.BLACK

        # Globals
        self.board = Board()
        self.board.current = self.board.players[0]
        self.build_sidebar()

    def build_sidebar(self):
        # Create sidebar
        self.sidebar = arcade.gui.UIBoxLayout()
        self.title = arcade.gui.UITextArea(
            text="Quberadius",
            text_color=PLAYER_COLORS[0],
            width=SIDEBAR_WIDTH,
            height=50,
            font_size=36,
            font_name="Kenney Future",
        )
        self.sidebar.add(self.title.with_space_around(bottom=0))
        self.debug_window = arcade.gui.UITextArea(
            text="",
            text_color=DEFAULT_COLOR,
            width=SIDEBAR_WIDTH,
            height=250,
            font_size=12,
            font_name="Kenney Future",
        )
        self.sidebar.add(self.debug_window)

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="right",
            anchor_y="top",
            align_x=SIDEBAR_MARGIN,
            child=self.sidebar,
        ))

    def on_draw(self):
        """
        Render the screen.
        """
        # We should always start by clearing the window pixels
        self.clear()

        # Redraw all the things
        [sprite_list.draw() for sprite_list in Qube.all_sprites]
        self.manager.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        """Handle user keyboard input
        Q: Quit the game

        Arguments:
            symbol {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were pressed
        """
        if symbol == arcade.key.Q:
            arcade.close_window()

        if symbol == arcade.key.ESCAPE:
            self.debug_window.text = "Deselecting piece."

            if self.board.power:
                self.board.selected.piece.powers += [self.board.power]
                self.board.power = None

            if self.board.selected:
                self.board.selected = None

        if symbol == arcade.key.D:
            import pdb; pdb.set_trace()

        numbers = {
            arcade.key.KEY_1: 1,
            arcade.key.KEY_2: 2,
            arcade.key.KEY_3: 3,
            arcade.key.KEY_4: 4,
            arcade.key.KEY_5: 5,
            arcade.key.KEY_6: 6,
            arcade.key.KEY_7: 7,
            arcade.key.KEY_8: 8,
            arcade.key.KEY_9: 9,
        }
        if (num := numbers.get(symbol)):
            if self.board.selected and (power := pop_if(self.board.selected.piece.powers, num-1)):
                self.board.power = power
                self.debug_window.text = f"Activating {power.name}…\n"

        if symbol == arcade.key.SPACE:
            if not self.board.power and self.board.selected \
                    and self.board.selected.piece.powers:
                self.board.power = self.board.selected.piece.powers.pop()
                self.debug_window.text = f"Activating {self.board.power.name}…\n"

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called when the user presses a mouse button.
        """
        # Convert the clicked mouse position into grid coordinates
        column = int(x // (WIDTH + MARGIN))
        row = int(y // (HEIGHT + MARGIN))
        output = [f"Click ({x}, {y})"]

        # Off grid? Exit
        if row >= ROW_COUNT or column >= COLUMN_COUNT:
            output.append("Sidebar")
            self.debug_window.text = "\n".join(output)
            return

        square = self.board.grid[column][row]
        output.append(str(square))

        if isinstance(self.board.power, Power):
            power = self.board.power
            if power.is_valid(square, self):
                if power.execute(square):
                    self.debug_window.text = "Boom."
                else:
                    self.debug_window.text = "Not useful now. Deactivating."
                    self.board.selected.piece.powers += [self.board.power]
            else:
                self.board.selected.piece.powers += [self.board.power]

            self.board.selected = None
            self.board.power = None
            return # turn continues

        # Deselect a piece
        elif square == self.board.selected:
            output.append(f"Deselected: {self.board.selected.piece}")
            self.board.selected = False

        # ... select a piece
        elif square.piece and square.piece.player == self.board.current:
            if self.board.selected:
                output.append(f"Deselected: {self.board.selected.piece}")

            output.append(f"Selected: {square.piece}")
            self.board.selected = square

        # .. move a piece
        elif self.board.selected and self.board.selected.piece.can_move_to(square):
            # not mine? kill it
            if square.piece and not square.piece in Qube.piece_sprites[self.board.current.idx]:
                square.piece.remove()

            square.piece = self.board.selected.piece  # add piece to new square

            # incr turn
            self.board.current.turns += 1
            if self.board.current.turns % 3 == 0:
                self.board.selected.piece.powers.append(1)

            self.board.selected.piece = None  # remove piece from old square
            self.board.selected = None  # deselect square

            # end turn
            if self.board.power == 1:
                self.board.power = None
            else:
                # next player's turn
                player_idx = self.board.players.index(self.board.current)
                self.board.current = self.board.players[(player_idx + 1) % len(self.board.players)]

                # next player's color
                self.sidebar.children[0].children[0] = arcade.gui.UITextArea(
                    text="Quberadius",
                    text_color=self.board.current.color,
                    width=SIDEBAR_WIDTH,
                    height=50,
                    font_size=36,
                    font_name="Kenney Future",
                )

        # count rounds
        if self.board.players[0] == self.board.current:
            self.board.turns += 1

        # append incoming players powers
        if self.board.selected:
            powers = self.board.selected.piece.powers
            output.append("\n".join([str(i+1) + ": " + str(p) for i, p in enumerate(powers)]))
        self.debug_window.text = "\n".join(output)

    def on_mouse_motion(self, x, y, dx, dy):
        # Reset previously highlighted squares
        for sprite in Qube.square_sprites:
            if sprite.color == HIGHLIGHT_COLOR:
                sprite.color = DEFAULT_COLOR

        # Convert the clicked mouse position into grid coordinates
        column = int(x // (WIDTH + MARGIN))
        row = int(y // (HEIGHT + MARGIN))
        if row >= ROW_COUNT or column >= COLUMN_COUNT:
            return

        square = self.board.grid[column][row]

        if square.color == DEFAULT_COLOR:
            square.color = HIGHLIGHT_COLOR


def main():
    Qube(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
