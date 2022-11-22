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
 - ENTER to use selected CRR power
 - Keep piece selected after power use?
 - Limit diagonal movement
 - Limit elevation movement
 - Add new Areas of Effect
   - Radial
   - Diagonal?
 - Randomize powers
 - New Views
   - Start Game/Set Options
   - End Game/Restart


 - Add Powers
   EASY
   - Wall, Trench, Raise, Invert + CRR
   - Kamikazi + CRR
   - Roulette + CRR
   - Randomize + CRR
   - Stupify + CRR
   - Earthquake - randomize all elevations
   - Push CRR - push pieces away from player
   - Pull CRR - pull pieces toward player
   - Teleport - move to any square

   MEDIUM
   - Anchor CRR - selected piece(s?) can't move
   - Attract CRR - pull pieces into aoe
   - Dominoes - destroy all pieces touching this one
   - Power Up - increase aoe
   - Reflect - turns powers back on opponent
   - Shield - unaffected by powers
   - Wrap - wraps grid

   HARD
   - Armor - unjumpable
   - Blind - other players can see until squares are revisited
   - Flood - fill trenches with water, destroying pieces
   - Fly - unaffected by elevation but can't destroy pieces w/o landing, raise sprite
   - Grow - increase Piece size/movement, flatten elevations
   - Invisibility - piece can only be seen by player
   - Puppeteer - control another piece
   - Rewind - undo last turn(s)


 - Later
   - Persistent powers
   - Resizable window
   - Highlight clickable squares
     - Piece selection
     - Power selection
   - Animations
   - Online, multi-device
   - Custom arenas
   - Game types
     - Race
     - Capture the flag
     - Real-time
       - keyboard interface
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
