import arcade

from constants import (
    PLAYER_COUNT,
    PLAYER_COLORS,
    SIDEBAR_WIDTH,
    DEFAULT_COLOR,
    SIDEBAR_MARGIN,
    HEIGHT,
    WIDTH,
    ROW_COUNT,
    COLUMN_COUNT,
    MARGIN,
    HIGHLIGHT_COLOR,
)
from objects.board import Board
from objects.power import Power


def pop_if(items, index, default=None):
    try:
        return items.pop(index)
    except IndexError:
        return default


class GameView(arcade.View):
    """ Manage the 'game' view. """

    square_sprites = arcade.SpriteList()
    piece_sprites = [arcade.SpriteList() for _ in range(PLAYER_COUNT)]
    all_sprites = [square_sprites] + piece_sprites

    # def __init__(self, width, height, title):
    def __init__(self):
        """
        Set up the application.
        """
        # Create Window
        super().__init__()
        self.background_color = arcade.color.BLACK

    def setup_game(self):
        self.board = Board(self)
        self.board.add_squares()
        self.board.add_players()

    def setup_sidebar(self):
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
        [sprite_list.draw() for sprite_list in GameView.all_sprites]
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
            try:
                power = list(self.board.selected.piece.powers.values())[num-1]
            except IndexError:
                power = None

            if self.board.selected and power:
                self.board.power = power.name
                self.debug_window.text = f"Activating {power.name}…\n"

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

        if self.board.power:
            power = self.board.selected.piece.powers.get(self.board.power)
            if power.is_valid(square, self):
                if power.execute(square):
                    self.debug_window.text = "Boom."
                    square.piece.remove_power(power.name)
                else:
                    self.debug_window.text = "Not useful now. Deactivating."

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
            if square.piece and not square.piece in GameView.piece_sprites[self.board.current.idx]:
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
        for sprite in GameView.square_sprites:
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

