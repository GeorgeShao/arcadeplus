"""
Load a Tiled map file

Artwork from: http://kenney.nl
Tiled available from: http://www.mapeditor.org/

If Python and arcadeplus are installed, this example can be run from the command line with:
python -m arcadeplus.examples.sprite_tiled_map
"""

import arcadeplus
import os
import time

TILE_SCALING = 0.5
PLAYER_SCALING = 1

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprite Tiled Map Example"
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN_TOP = 60
VIEWPORT_MARGIN_BOTTOM = 60
VIEWPORT_RIGHT_MARGIN = 270
VIEWPORT_LEFT_MARGIN = 270

# Physics
MOVEMENT_SPEED = 5
JUMP_SPEED = 23
GRAVITY = 1.1


class MyGame(arcadeplus.Window):
    """ Main application class. """

    def __init__(self):
        """
        Initializer
        """
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Sprite lists
        self.wall_list = None
        self.player_list = None
        self.coin_list = None

        # Set up the player
        self.score = 0
        self.player_sprite = None

        self.physics_engine = None
        self.view_left = 0
        self.view_bottom = 0
        self.end_of_map = 0
        self.game_over = False
        self.last_time = None
        self.frame_count = 0
        self.fps_message = None

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcadeplus.SpriteList()
        self.coin_list = arcadeplus.SpriteList()

        # Set up the player
        self.player_sprite = arcadeplus.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png",
                                           PLAYER_SCALING)

        # Starting position of the player
        self.player_sprite.center_x = 196
        self.player_sprite.center_y = 270
        self.player_list.append(self.player_sprite)

        map_name = ":resources:/tmx_maps/map.tmx"

        # Read in the tiled map
        my_map = arcadeplus.tilemap.read_tmx(map_name)
        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE

        # --- Platforms ---
        self.wall_list = arcadeplus.tilemap.process_layer(my_map, 'Platforms', TILE_SCALING)

        # --- Coins ---
        self.coin_list = arcadeplus.tilemap.process_layer(my_map, 'Coins', TILE_SCALING)

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcadeplus.set_background_color(my_map.background_color)

        # Keep player from running through the wall_list layer
        self.physics_engine = arcadeplus.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             gravity_constant=GRAVITY)

        # Set the view port boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left = 0
        self.view_bottom = 0

        self.game_over = False

    def on_draw(self):
        """
        Render the screen.
        """

        self.frame_count += 1

        # This command has to happen before we start drawing
        arcadeplus.start_render()

        # Draw all the sprites.
        self.player_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()

        if self.last_time and self.frame_count % 60 == 0:
            fps = 1.0 / (time.time() - self.last_time) * 60
            self.fps_message = f"FPS: {fps:5.0f}"

        if self.fps_message:
            arcadeplus.draw_text(self.fps_message, self.view_left + 10, self.view_bottom + 40, arcadeplus.color.BLACK, 14)

        if self.frame_count % 60 == 0:
            self.last_time = time.time()

        # Put the text on the screen.
        # Adjust the text position based on the view port so that we don't
        # scroll the text too.
        distance = self.player_sprite.right
        output = f"Distance: {distance}"
        arcadeplus.draw_text(output, self.view_left + 10, self.view_bottom + 20, arcadeplus.color.BLACK, 14)

        if self.game_over:
            arcadeplus.draw_text("Game Over", self.view_left + 200, self.view_bottom + 200, arcadeplus.color.BLACK, 30)

    def on_key_press(self, key, modifiers):
        """
        Called whenever the mouse moves.
        """
        if key == arcadeplus.key.UP:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = JUMP_SPEED
        elif key == arcadeplus.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcadeplus.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """
        Called when the user presses a mouse button.
        """
        if key == arcadeplus.key.LEFT or key == arcadeplus.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """ Movement and game logic """

        if self.player_sprite.right >= self.end_of_map:
            self.game_over = True

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        if not self.game_over:
            self.physics_engine.update()

        coins_hit = arcadeplus.check_for_collision_with_list(self.player_sprite, self.coin_list)
        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            self.score += 1

        # --- Manage Scrolling ---

        # Track if we need to change the view port

        changed = False

        # Scroll left
        left_bndry = self.view_left + VIEWPORT_LEFT_MARGIN
        if self.player_sprite.left < left_bndry:
            self.view_left -= left_bndry - self.player_sprite.left
            changed = True

        # Scroll right
        right_bndry = self.view_left + SCREEN_WIDTH - VIEWPORT_RIGHT_MARGIN
        if self.player_sprite.right > right_bndry:
            self.view_left += self.player_sprite.right - right_bndry
            changed = True

        # Scroll up
        top_bndry = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN_TOP
        if self.player_sprite.top > top_bndry:
            self.view_bottom += self.player_sprite.top - top_bndry
            changed = True

        # Scroll down
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN_BOTTOM
        if self.player_sprite.bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - self.player_sprite.bottom
            changed = True

        # If we need to scroll, go ahead and do it.
        if changed:
            self.view_left = int(self.view_left)
            self.view_bottom = int(self.view_bottom)
            arcadeplus.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


def main():
    window = MyGame()
    window.setup()
    arcadeplus.run()


if __name__ == "__main__":
    main()
