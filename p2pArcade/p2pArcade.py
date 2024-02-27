import argparse
import random
import signal
import subprocess
import sys
import threading
import time

import arcade
import psutil
from python_banyan.banyan_base import BanyanBase

# Preset parameters for the program.
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_BALL = 0.2
BALL_COUNT = 1
PLAYER_COUNT = 2
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "P2P Pong "
MOVEMENT_SPEED = 50


# Class to create and define the ball to be used by the game.
class Ball(arcade.Sprite):
    def __init__(self, filename, sprite_scaling):
        super().__init__(filename, sprite_scaling)

        # Sets the change value for x/y to 0 so the ball stays still.
        self.change_x = 0
        self.change_y = 0

        self._my_index = None

    @property
    def my_index(self):
        return self._my_index

    @my_index.setter
    def my_index(self, index):
        self._my_index = index

    def update(self):
        return


# Creates the game instance and uses the BanyanBase to make the instances concurrent
class Game(arcade.Window, threading.Thread, BanyanBase):
    def __init__(self, back_plane_ip_address=None, process_name=None, player=0):

        # Defines parameters for the Game to use.
        title = SCREEN_TITLE + str(player)
        arcade.Window.__init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, title)

        self.all_sprites_list = None
        self.ball_list = None

        self.player_0_sprite = None

        self.player_1_sprite = None

        self.player = player

        self.score_0 = 0

        self.score_1 = 0

        self.set_mouse_visible(False)

        self.go = False

        self.run_collision_detection = False

        threading.Thread.__init__(self)

        self.the_lock = threading.Lock()

        self.daemon = True

        self.run_the_thread = threading.Event()

        self.run_the_thread = True

        if not back_plane_ip_address:
            self.start_backplane()

        # Uses the info passed in to initialize or join the BanyanBase
        BanyanBase.__init__(self, back_plane_ip_address=back_plane_ip_address, process_name=process_name,
                            loop_time=.0001)

        # Sets the "topics" that can be passed through BanyanBase to update the game.
        self.set_subscriber_topic('enable_balls')
        self.set_subscriber_topic('enable_collisions')
        self.set_subscriber_topic('p0_move')
        self.set_subscriber_topic('p1_move')
        self.set_subscriber_topic('update_ball')
        self.set_subscriber_topic('remove_ball_0')
        self.set_subscriber_topic('remove_ball_1')

        # Sets the background color.
        arcade.set_background_color(arcade.color.ASH_GREY)

        # Runs the setup function to prepare the game
        self.setup()

        # Starts the game.
        self.start()

        try:
            arcade.run()
        except KeyboardInterrupt:
            self.stop_event = False
            sys.exit(0)

    # Adds the ball to the game.
    def add_ball(self):
        for i in range(BALL_COUNT):
            ball = Ball(":resources:images/items/coinGold.png",
                        SPRITE_SCALING_BALL)

            ball.center_x = SCREEN_WIDTH / 2
            ball.center_y = SCREEN_HEIGHT / 2
            ball.change_x = random.randrange(-3, 4)
            ball.change_y = random.randrange(-3, 4)

            ball.my_index = i

            self.all_sprites_list.append(ball)
            self.ball_list.append(ball)

    def setup(self):

        # The list of all sprites used by the game.
        self.all_sprites_list = arcade.SpriteList()
        self.ball_list = arcade.SpriteList()

        # Assigns the texture and information for player 0, then adds player 0 to the list of sprites.
        self.player_0_sprite = arcade.Sprite(":resources:images/tiles/bridgeB.png", SPRITE_SCALING_PLAYER)
        self.player_0_sprite.center_x = SCREEN_WIDTH / 2
        self.player_0_sprite.center_y = 50
        self.all_sprites_list.append(self.player_0_sprite)

        # Assigns, and flips, the texture and information for player 1, then adds player 1 to the list of sprites.
        self.player_1_sprite = arcade.Sprite(":resources:images/tiles/bridgeB.png", SPRITE_SCALING_PLAYER, angle=180)
        self.player_1_sprite.center_x = SCREEN_WIDTH / 2
        self.player_1_sprite.center_y = 575
        self.all_sprites_list.append(self.player_1_sprite)

        # Adds the ball to the list of sprites.
        self.add_ball()

    def on_draw(self):
        arcade.start_render()
        # Draws all sprites onto the screen.
        self.all_sprites_list.draw()

        # Draws the scores for both players onto the screen.
        output = f"Score {self.score_0}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

        output = f"Score {self.score_1}"
        arcade.draw_text(output, 590, 20, arcade.color.WHITE, 14)

    # Defines the movement parameters for both players.
    def on_key_press(self, button, modifiers):
        if self.player == 0:
            if button == arcade.key.RIGHT:
                payload = {'p0_x': MOVEMENT_SPEED, 'p0_y': 0}
                topic = 'p0_move'
                self.publish_payload(payload, topic)
            if button == arcade.key.LEFT:
                payload = {'p0_x': -(MOVEMENT_SPEED), 'p0_y': 0}
                topic = 'p0_move'
                self.publish_payload(payload, topic)
        elif self.player == 1:
            if button == arcade.key.RIGHT:
                payload = {'p1_x': MOVEMENT_SPEED, 'p1_y': 0}
                topic = 'p1_move'
                self.publish_payload(payload, topic)
            if button == arcade.key.LEFT:
                payload = {'p1_x': -(MOVEMENT_SPEED), 'p1_y': 0}
                topic = 'p1_move'
                self.publish_payload(payload, topic)

    # Starts the game once a player clicks the screen.
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            payload = {'go': True}
            self.publish_payload(payload, 'enable_balls')

            payload = {'collision': True}
            self.publish_payload(payload, 'enable_collisions')

    # Executes the updates for ball movement.
    def on_update(self, delta_time):

        self.all_sprites_list.update()

        if self.go:
            if self.player == 0:
                with self.the_lock:
                    ball_updates = [[self.ball_list.sprite_list[i].center_x, self.ball_list.sprite_list[i].center_y] for i in range(len(self.ball_list))]
                    payload = {'updates': ball_updates}
                    self.publish_payload(payload, 'update_balls')

    # Starts the "Backplane" which is what allows the instances to connect using a TCP/IP connection.
    def start_backplane(self):
        try:
            for proc in psutil.process_iter(attrs=['pid', 'name']):
                if 'backplane' in proc.info['name']:
                    return
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

        if sys.platform.startswith('win32'):
            return subprocess.Popen(['backplane'],
                                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW)

        else:
            return subprocess.Popen(['backplane'], stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                    stdout=subprocess.PIPE)

    def run(self):

        self.receive_loop()

    # Processes the "incoming messages" which are the updates to the arcade library being sent through the Banyan Backplane.
    def incoming_message_processing(self, topic, payload):

        if self.external_message_processor:
            self.external_message_processor(topic, payload)

        else:
            # Processes the updates for the balls.
            if topic == 'update_balls':
                the_coordinates = payload['updates']
                with self.the_lock:
                    for i in range(len(the_coordinates)):
                        try:
                            self.ball_list.sprite_list[i].center_x = the_coordinates[i][0] + self.ball_list.sprite_list[
                                i].change_x
                            self.ball_list.sprite_list[i].center_y = the_coordinates[i][1] + self.ball_list.sprite_list[
                                i].change_y

                            if self.ball_list.sprite_list[i].left <= 0:
                                self.ball_list.sprite_list[i].change_x *= -1

                            if self.ball_list.sprite_list[i].right >= SCREEN_WIDTH:
                                self.ball_list.sprite_list[i].change_x *= -1

                            if self.ball_list.sprite_list[i].bottom <= 0:
                                ball_index = self.ball_list.sprite_list[i].my_index
                                payload = {'ball': ball_index}
                                self.publish_payload(payload, 'remove_ball_1')

                            if self.ball_list.sprite_list[i].top >= SCREEN_HEIGHT:
                                ball_index = self.ball_list.sprite_list[i].my_index
                                payload = {'ball': ball_index}
                                self.publish_payload(payload, 'remove_ball_0')

                        except (TypeError, IndexError):
                            continue

                # Checks for collision detection to bounce the ball off the players.
                with self.the_lock:
                    if self.run_collision_detection:
                        hit_list = arcade.check_for_collision_with_list(self.player_0_sprite, self.ball_list)

                        if hit_list:
                            for ball in hit_list:
                                ball.change_y *= -1

                                time.sleep(0.0001)

                with self.the_lock:
                    if self.run_collision_detection:
                        hit_list = arcade.check_for_collision_with_list(self.player_1_sprite, self.ball_list)

                        if hit_list:
                            for ball in hit_list:
                                ball.change_y *= -1

                                time.sleep(0.0001)

            # Processes the movement for both players/
            elif topic == 'p0_move':
                self.player_0_sprite.center_x += payload['p0_x']

                if self.player_0_sprite.left <= 0:
                    self.player_0_sprite.left = 0
                elif self.player_0_sprite.right >= SCREEN_WIDTH:
                    self.player_0_sprite.right = SCREEN_WIDTH

            elif topic == 'p1_move':
                self.player_1_sprite.center_x += payload['p1_x']

                if self.player_1_sprite.left <= 0:
                    self.player_1_sprite.left = 0
                elif self.player_1_sprite.right >= SCREEN_WIDTH:
                    self.player_1_sprite.right = SCREEN_WIDTH

            # Removes the ball if it hits the top or bottom of the screen, and gives the points to the appropriate
            # player.
            elif topic == 'remove_ball_0':
                with self.the_lock:
                    ball_index = payload['ball']
                    for ball in self.ball_list.sprite_list:
                        if ball_index == ball.my_index:
                            ball.remove_from_sprite_lists()
                            self.score_0 += 1
                self.add_ball()

            elif topic == 'remove_ball_1':
                with self.the_lock:
                    ball_index = payload['ball']
                    for ball in self.ball_list.sprite_list:
                        if ball_index == ball.my_index:
                            ball.remove_from_sprite_lists()
                            self.score_1 += 1
                self.add_ball()

            # Enables the movement for the ball.
            elif topic == 'enable_balls':
                self.go = True
            # Enables collisions with the ball, players, and edges.
            elif topic == 'enable_collisions':
                self.run_collision_detection = True

# Defines the game instance and required options.
def p2pArcade():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or Common Backplane IP address")
    parser.add_argument("-n", dest="process_name", default="p2p Pong",
                        help="Banyan Process Name Header Entry")
    parser.add_argument("-p", dest="player", default="0",
                        help="Select player 0 or 1")

    args = parser.parse_args()

    if args.back_plane_ip_address == 'None':
        args.back_plane_ip_address = None
    game_options = {'back_plane_ip_address': args.back_plane_ip_address, 'process_name': args.process_name + ' player' + str(args.player), 'player': int(args.player)}
    # Create an instance of MyGame and pass in the options.
    Game(**game_options)


# signal handler function called when Control-C occurs
def signal_handler(sig, frame):
    print('Exiting Through Signal Handler')
    raise KeyboardInterrupt


# listen for SIGINT
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    p2pArcade()
