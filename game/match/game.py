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

    def __init__(self, name, team_size, goalkeepers_count, defenders_count, wingers_count, strikers_count):
        self.name = name
        self.team_size = team_size
        self.goalkeepers_count = goalkeepers_count
        self.defenders_count = defenders_count
        self.wingers_count = wingers_count
        self.strikers_count = strikers_count


def init_game_modes():
    global game_modes
    game_modes = [
        GameMode(
            "Unlimited 5v5", 
            config.GAMEMODE_UNLIMITED_5v5_TEAM_SIZE, 
            config.GAMEMODE_UNLIMITED_5v5_GOALKEEPERS_COUNT,
            config.GAMEMODE_UNLIMITED_5v5_DEFENDERS_COUNT,
            config.GAMEMODE_UNLIMITED_5v5_WINGERS_COUNT,
            config.GAMEMODE_UNLIMITED_5v5_STRIKERS_COUNT
        ),
        GameMode(
            "Unlimited 3v3", 
            config.GAMEMODE_UNLIMITED_3v3_TEAM_SIZE, 
            config.GAMEMODE_UNLIMITED_3v3_GOALKEEPERS_COUNT,
            config.GAMEMODE_UNLIMITED_3v3_DEFENDERS_COUNT,
            config.GAMEMODE_UNLIMITED_3v3_WINGERS_COUNT,
            config.GAMEMODE_UNLIMITED_3v3_STRIKERS_COUNT
        )
    ]


class Replay():

    def __init__(self, screen, team_players_count):
        self.screen = screen
        self.field = Field(screen)
        self.saved_moments = deque()
        self.objects_count = team_players_count * 2 + 1

        font = pygame.font.SysFont(config.REPLAY_FIELD_TEXT_FONT, config.REPLAY_FIELD_TEXT_SIZE)
        self.text = font.render(config.REPLAY_FIELD_TEXT, False, (2, 163, 18))
        self.text_rect = self.text.get_rect(center=(config.SCREEN_X_SIZE // 2, config.SCREEN_Y_SIZE // 2))

        self.saved_obects_count = config.REPLAY_SAVED_SECS * config.GAME_FPS * self.objects_count
    
    def add(self, obj):
        self.saved_moments.append(obj)
        if len(self.saved_moments) > self.saved_obects_count:
            self.pop()
    
    def pop(self):
        if len(self.saved_moments) > 0:
            self.saved_moments.popleft()

    def clear(self):
        self.saved_moments.clear()
    
    def show(self):
        Painter().add(self.draw)
        self.slide_idx = 0
    
    def draw(self):
        if self.slide_idx >= len(self.saved_moments):
            self.disappear()
            return
        self.field.draw()
        self.screen.blit(self.text, self.text_rect)
        for i in range(self.objects_count):
            self.saved_moments[self.slide_idx + i].draw()
        self.slide_idx += self.objects_count
    
    def disappear(self):
        Painter().pop()
        
    def size(self):
        return len(self.saved_moments)
    

class Game():

    def __init__(self, screen, game_mode):
        self.screen = screen
        self.game_mode = game_mode 

        self.field = Field(screen)
        self.scoreboard = Scoreboard(screen)

        self.players = []
        for team in range(2):
            size_prefix = 0
            for i in range(self.game_mode.goalkeepers_count):
                self.players.append(PlayerCreator.create_player(screen, False, team, i, "goalkeeper", i))
            size_prefix += self.game_mode.goalkeepers_count
            for i in range(self.game_mode.defenders_count):
                self.players.append(PlayerCreator.create_player(screen, False, team, size_prefix + i, "defender", i))
            size_prefix += self.game_mode.defenders_count
            for i in range(self.game_mode.wingers_count):
                self.players.append(PlayerCreator.create_player(screen, False, team, size_prefix + i, "winger", i))
            size_prefix += self.game_mode.wingers_count
            for i in range(self.game_mode.strikers_count):
                self.players.append(PlayerCreator.create_player(screen, False, team, size_prefix + i, "striker", i))
        
        self.team = [self.players[:self.game_mode.team_size], self.players[self.game_mode.team_size:]]

        self.controlled_player = self.game_mode.goalkeepers_count + self.game_mode.defenders_count + self.game_mode.wingers_count
        self.players[self.controlled_player] = PlayerCreator.create_player(screen, True, 0, self.controlled_player, "striker", 0)
        self.ball = Ball(screen)

        self.paused = False
        self.replay = Replay(screen, self.game_mode.team_size)
        self.watching_replay = False
    
    def draw(self):
        if self.watching_replay:
            return
        self.field.draw()
        self.scoreboard.draw()
        self.ball.draw()
        for player in self.players:
            player.draw()
    
    def pause(self):
        self.paused = True
    
    def unpause(self):
        self.paused = False
        self.watching_replay = False
    
    def save_moment(self):
        for player in self.players:
            player_copy = copy.copy(player)
            self.replay.add(player_copy)
        ball_copy = copy.copy(self.ball)
        self.replay.add(ball_copy)
        while self.replay.size() > self.replay.saved_obects_count:
            self.replay.pop()
    
    def show_replay(self):
        self.pause()
        self.watching_replay = True
        self.replay.show()
    
    def check_ball_owner(self):
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
        self.scoreboard.update_score(team_0_change, team_1_change)
        popup.popup = popup.Popup(self.screen, config.POPUP_GOAL, config.POPUP_GOAL_TICKS, [button.show_replay_btn])
        popup.popup.show()
    
    def ball_out(self):
        popup.popup = popup.Popup(self.screen, config.POPUP_BALL_OUT, config.POPUP_BALL_OUT_TICKS)
        popup.popup.show()
    
    def check_goal(self):
        status = self.field.check_ball_in_gates(self.ball)
        if status == 0:
            self.goal_scored(0, 1)
            return True
        elif status == 1:
            self.goal_scored(1, 0)
            return True
        return False
        
    def check_out(self):
        if self.field.check_ball_out(self.ball):
            self.ball_out()

    def restart(self):
        for player in self.players:
            player.restart()
        self.ball.restart()
        self.replay.clear()

    def switch_controlled_player(self, new_controlled_player):
        if new_controlled_player >= self.game_mode.team_size or new_controlled_player == self.controlled_player:
            return
        old_player = self.players[self.controlled_player]
        new_player = self.players[new_controlled_player]

        old_player, new_player = new_player, old_player
        self.controlled_player = new_controlled_player
        old_player.set_controlled_settings()
        new_player.set_default_settings()
    
    def check_if_areas_intersect(self, moved_player):
        found_intersection = True
        iters_count = 0
        while found_intersection and iters_count < 4:
            iters_count += 1
            found_intersection = False
            for player in self.players:
                dist = moved_player.get_dist(player.pos)
                if player != moved_player and dist < config.PLAYER_AREA_RADIUS * 2 - config.PLAYER_AREA_RADIUS_MEASUREMENT_ERROR:
                    scale_coef = config.PLAYER_AREA_RADIUS * 2 / dist
                    moved_player.pos = [player.pos[0] + (moved_player.pos[0] - player.pos[0]) * scale_coef, 
                                        player.pos[1] + (moved_player.pos[1] - player.pos[1]) * scale_coef]
                    found_intersection = True
                    break        
    
    def tick(self):
        if self.paused:
            return

        for i in range(self.game_mode.team_size):
            if i != self.controlled_player:
                player = self.players[i]
                player.move(self.ball, self.team[0], self.team[1])
                self.check_if_areas_intersect(player)

        for i in range(self.game_mode.team_size, self.game_mode.team_size * 2):
            player = self.players[i]
            player.move(self.ball, self.team[1], self.team[0])
            self.check_if_areas_intersect(player)
        
        global mouse_pressed
        player = self.players[self.controlled_player]
        if mouse_pressed:
            player.move_in_dir(pygame.mouse.get_pos())
            self.check_if_areas_intersect(player)
            if player.player_class == "goalkeeper":
                player.stick_to_box_borders()
        
        self.check_ball_owner()
        self.ball.stick_to_owner()
        self.ball.fly()
        if not self.check_goal():
            self.check_out()
        self.save_moment()
    
    def handle_event(self, event):
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
            elif event.key == pygame.K_6:
                self.switch_controlled_player(5)
            elif event.key == pygame.K_SPACE:
                self.players[self.controlled_player].shoot()
