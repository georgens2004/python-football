import copy
from collections import deque

import pygame, sys
import config

from painter import Painter
from match.player import Player, PlayerCreator
from match.field import Field
from match.ball import Ball
from match.scoreboard import Scoreboard

import match.popup as popup

import button


mouse_pressed = False

game = None
game_modes = []

class GameMode():
    # Basic gamemodes (actually only 5v5 gamemode presented in the game right now)

    def __init__(self, name, team_size_0, team_size_1):
        self.name = name
        self.team_size_0 = team_size_0
        self.team_size_1 = team_size_1
    
    def get_team_size_0(self):
        return self.team_size_0

    def get_team_size_1(self):
        return self.team_size_1


def init_game_modes():
    global game_modes
    game_modes = [
        GameMode(
            "Unlimited 5v5", config.GAMEMODE_UNLIMITED_5v5_TEAM_SIZE_0, config.GAMEMODE_UNLIMITED_5v5_TEAM_SIZE_1
        ),
    ]


class Replay():
    # Replay object contains last config.REPLAY_SAVED_TICKS game ticks
    # It's rather big ogject cause every player every tick is straightforwardly copied here
    # Every tick = adding 10 players and 1 ball (with their current position)

    def __init__(self, screen):
        self.screen = screen
        self.field = Field(screen)
        self.saved_moments = deque()

        font = pygame.font.SysFont(config.REPLAY_FIELD_TEXT_FONT, config.REPLAY_FIELD_TEXT_SIZE)
        self.text = font.render(config.REPLAY_FIELD_TEXT, False, (2, 163, 18))
        self.text_rect = self.text.get_rect(center=(config.SCREEN_X_SIZE // 2, config.SCREEN_Y_SIZE // 2))
    
    def add(self, obj):
        # Adding object to the end
        self.saved_moments.append(obj)
        if len(self.saved_moments) > config.REPLAY_SAVED_TICKS * 11:
            self.pop()
    
    def pop(self):
        # Removing object from the begin
        if len(self.saved_moments) > 0:
            self.saved_moments.popleft()

    def clear(self):
        # Removes all objects
        self.saved_moments.clear()
    
    def show(self):
        # Called when player pressed 'Replay' button
        # Singleton class Painter() gets new layer while game gets paused and 'Goal' popup gets hidden
        Painter().add(self.draw)
        self.slide_idx = 0
    
    def draw(self):
        # Function for showing replay. Casually draws everything from saved_moments
        # Lasts approximetely 3.5-4.5s 
        if self.slide_idx >= len(self.saved_moments):
            self.disappear()
            return
        self.field.draw()
        self.screen.blit(self.text, self.text_rect)
        for i in range(11):
            self.saved_moments[self.slide_idx + i].draw()
        self.slide_idx += 11
    
    def disappear(self):
        # End of replay
        Painter().pop()
        
    def size(self):
        # Size getter
        return len(self.saved_moments)
    


class Game():


    def __init__(self, screen, game_mode):
        self.screen = screen
        self.game_mode = game_mode 

        self.field = Field(screen)
        self.scoreboard = Scoreboard(screen)

        self.players = []
        for i in range(self.game_mode.get_team_size_0()):
            self.players.append(PlayerCreator.create_player(screen, False, 0, i, config.INIT_TEAM_CRD_0[i]))
        for i in range(self.game_mode.get_team_size_1()):
            self.players.append(PlayerCreator.create_player(screen, False, 1, i, config.INIT_TEAM_CRD_1[i]))
        
        self.controlled_player = 2
        self.players[self.controlled_player] = PlayerCreator.create_player(screen, True, 0, self.controlled_player, config.INIT_TEAM_CRD_0[self.controlled_player])
        self.ball = Ball(screen)

        self.paused = False
        self.replay = Replay(screen)
        self.watching_replay = False
    
    def draw(self):
        # Drawing everything on the field
        if self.watching_replay:
            return
        self.field.draw()
        self.scoreboard.draw()
        self.ball.draw()
        for player in self.players:
            player.draw()
    
    def pause(self):
        # Pausing game (nobody is moving, no events handled)
        self.paused = True
    
    def unpause(self):
        # Unpausing
        self.paused = False
        self.watching_replay = False
    
    def save_moment(self):
        # Save every object to replay
        for player in self.players:
            player_copy = copy.copy(player)
            self.replay.add(player_copy)
        ball_copy = copy.copy(self.ball)
        self.replay.add(ball_copy)
        while self.replay.size() > config.REPLAY_SAVED_TICKS * 11:
            self.replay.pop()
    
    def show_replay(self):
        # Pausing game and disables drawing function during replay
        self.pause()
        self.watching_replay = True
        self.replay.show()
    
    def check_ball_owner(self):
        # Checks ball owner
        min_dist = config.BIG_RADIUS
        nearest_player = None
        for player in self.players:
            player.lose_ball()
            dist = player.get_dist(self.ball.pos)
            if dist < min_dist and dist <= config.PLAYER_RADIUS + config.BALL_RADIUS + player.catch_radius + 0.01:
                min_dist = player.get_dist(self.ball.pos)
                nearest_player = player
        
        if nearest_player is not None:
            nearest_player.own_ball(self.ball)
        else:
            self.ball.is_free = True
    
    def goal_scored(self, team_0_change, team_1_change):
        # What to do when 'Goal'
        self.scoreboard.update_score(team_0_change, team_1_change)
        popup.popup = popup.Popup(self.screen, config.POPUP_GOAL, config.POPUP_GOAL_TICKS, [button.show_replay_btn])
        popup.popup.show()
    
    def ball_out(self):
        # What to do when ball is out ('Out' popup)
        popup.popup = popup.Popup(self.screen, config.POPUP_BALL_OUT, config.POPUP_BALL_OUT_TICKS)
        popup.popup.show()
    
    def check_goal(self):
        # Checking goal
        status = self.field.check_ball_in_gates(self.ball)
        if status == 0:
            self.goal_scored(0, 1)
            return True
        elif status == 1:
            self.goal_scored(1, 0)
            return True
        return False
        
    def check_out(self):
        # Checking out
        # (only after checking goal)
        if self.field.check_ball_out(self.ball):
            self.ball_out()

    def restart(self):
        # Move players and ball to initial positions
        for player in self.players:
            player.restart()
        self.ball.restart()
        self.replay.clear()

    def switch_controlled_player(self, new_controlled_player):
        # Changing controlled player
        if (new_controlled_player >= self.game_mode.team_size_0):
            return
        self.players[self.controlled_player].set_default_settings()
        self.controlled_player = new_controlled_player
        self.players[self.controlled_player].set_controlled_settings()
    
    def tick(self):
        # Every object on the screen moves every tick
        # if game is not paused
        if self.paused:
            return
        for i in range(len(self.players)):
            if i != self.controlled_player:
                self.players[i].make_simple_move(self.ball, self.players)
        player = self.players[self.controlled_player]
        global mouse_pressed
        if mouse_pressed:
            player.move_in_dir(pygame.mouse.get_pos())
        self.check_ball_owner()
        self.ball.fly()
        if not self.check_goal():
            self.check_out()
        self.save_moment()
    
    def handle_event(self, event):
        # Basic event handler (for game controlls)
        if self.paused:
            return
        global mouse_pressed
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[2]:
                mouse_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_pressed = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.switch_controlled_player(0)
            elif event.key == pygame.K_2:
                self.switch_controlled_player(1)
            elif event.key == pygame.K_3:
                self.switch_controlled_player(2)
            elif event.key == pygame.K_4:
                self.switch_controlled_player(3)
            elif event.key == pygame.K_5:
                self.switch_controlled_player(4)
            elif event.key == pygame.K_SPACE:
                self.players[self.controlled_player].shoot()
