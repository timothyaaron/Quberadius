"""
Quberadius
"""
import arcade
import arcade.gui

from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from views.game_view import GameView


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


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Quberadius")
    game_view = GameView()
    game_view.setup_game()
    game_view.setup_sidebar()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()
