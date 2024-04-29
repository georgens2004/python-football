import pygame, sys
import math

import config

class Player():

    # team: 0 or 1
    # speed: player's speed in game
    # power: ball initial speed after player's kick
    # catch_radius: where player can catch the ball (dist from border to border)
    
    def __init__(self, screen, team, number, player_class, class_number):
        self.screen = screen
        self.team = team
        self.number = number + 1

        self.player_class = player_class
        self.class_number = class_number

        self.pos = [0, 0]
        self.dir = [1, 0]

        self.ball = None

    
    def set_default_settings(self):
        self.image = pygame.image.load("../" + config.STATIC_IMAGES_FOLDER + config.PLAYER_IMAGES[self.team]).convert_alpha()
        self.image = pygame.transform.scale(self.image, (config.PLAYER_RADIUS * 2, config.PLAYER_RADIUS * 2))
        self.speed = config.DEFAULT_SPEED
        self.power = config.DEFAULT_POWER
        self.catch_radius = config.DEFAULT_CATCH_RADIUS
    
    def set_controlled_settings(self):
        self.image = pygame.image.load("../" + config.STATIC_IMAGES_FOLDER + config.PLAYER_CONTROLLED_IMAGE).convert_alpha()
        self.image = pygame.transform.scale(self.image, (config.PLAYER_RADIUS * 2, config.PLAYER_RADIUS * 2))
        self.speed = config.CONTROLLED_SPEED
        self.power = config.CONTROLLED_POWER
        self.catch_radius = config.CONTROLLED_CATCH_RADIUS

    def draw(self):
        self.screen.blit(self.image, (self.pos[0] - config.PLAYER_RADIUS, self.pos[1] - config.PLAYER_RADIUS))
        font = pygame.font.SysFont(config.PLAYER_NUMBER_FONT, config.PLAYER_NUMBER_FONT_SIZE)
        text = font.render(str(self.number), False, (0, 0, 0))
        text_rect = text.get_rect(center=(self.pos[0], self.pos[1]))
        self.screen.blit(text, text_rect)
    
    def scale_dir(self):
        denom = math.sqrt(self.dir[0] ** 2 + self.dir[1] ** 2)
        if denom != 0:
            self.dir = [self.dir[0] / denom, self.dir[1] / denom]
    
    def turn_to(self, pos):
        self.dir = [pos[0] - self.pos[0], pos[1] - self.pos[1]]
        self.scale_dir()
    
    def step(self):
        self.pos = [self.pos[0] + self.dir[0] * self.speed, self.pos[1] + self.dir[1] * self.speed]
        if self.ball is not None:
            self.ball.stick_to_owner()

    def get_dist(self, pos):
        return math.sqrt((self.pos[0] - pos[0]) ** 2 + (self.pos[1] - pos[1]) ** 2)
    
    def own_ball(self, ball):
        ball.become_owned(self)
        self.ball = ball
    
    def lose_ball(self):
        if self.ball is not None:
            self.ball.owner = None
            self.ball = None
    
    def make_simple_move(self, ball, players):
        # each game tick every bot makes this move (maybe will be more complicated than this implementation)
        if self.ball is not None:
            if self.team == 0:
                self.dir = [config.SCREEN_X_SIZE - self.pos[0], config.SCREEN_Y_SIZE // 2 - self.pos[1]]
            else:
                self.dir = [-self.pos[0], config.SCREEN_Y_SIZE // 2 - self.pos[1]]
        else:
            self.dir = [ball.pos[0] - self.pos[0], ball.pos[1] - self.pos[1]]
        self.scale_dir()
        self.step()
    
    def move_in_dir(self, pos):
        # controlled player makes this move every game tick (moving towards mouse direction)
        if self.get_dist(pygame.mouse.get_pos()) > config.PLAYER_RADIUS:
            self.dir = [pos[0] - self.pos[0], pos[1] - self.pos[1]]
            self.scale_dir()
            self.step()

    def shoot(self):
        if self.ball is None:
            return
        self.ball.dir = self.dir
        self.ball.speed = self.power
        self.ball.pos = [self.ball.pos[0] + self.dir[0] * (self.speed + 1), self.ball.pos[1] + self.dir[1] * (self.speed + 1)]
        self.lose_ball()
        
from match.bot_logic import BotDefender, BotWinger, BotStriker, BotGoalkeeper

class PlayerCreator():
    # An abstract class for players creation

    def create_player(screen, is_controlled, team, number, player_class, class_number):
        player = None
        if player_class == "defender":
            player = BotDefender(screen, team, number, player_class, class_number)
            if team == 0:
                player.set_box(config.BOT_DEFENDER_TEAM_0_BOX_CORNERS[class_number])
                player.set_initial_pos(config.BOT_DEFENDER_TEAM_0_INITIAL_POS[class_number])
            else:
                player.set_box(config.BOT_DEFENDER_TEAM_1_BOX_CORNERS[class_number])
                player.set_initial_pos(config.BOT_DEFENDER_TEAM_1_INITIAL_POS[class_number])
        elif player_class == "winger":
            player = BotWinger(screen, team, number, player_class, class_number)
            if team == 0:
                player.set_box(config.BOT_WINGER_TEAM_0_BOX_CORNERS[class_number])
                player.set_initial_pos(config.BOT_WINGER_TEAM_0_INITIAL_POS[class_number])
            else:
                player.set_box(config.BOT_WINGER_TEAM_1_BOX_CORNERS[class_number])
                player.set_initial_pos(config.BOT_WINGER_TEAM_1_INITIAL_POS[class_number])
        elif player_class == "striker":
            player = BotStriker(screen, team, number, player_class, class_number)
            if team == 0:
                player.set_box(config.BOT_STRIKER_TEAM_0_BOX_CORNERS[class_number])
                player.set_initial_pos(config.BOT_STRIKER_TEAM_0_INITIAL_POS[class_number])
            else:
                player.set_box(config.BOT_STRIKER_TEAM_1_BOX_CORNERS[class_number])
                player.set_initial_pos(config.BOT_STRIKER_TEAM_1_INITIAL_POS[class_number])
        elif player_class == "goalkeeper":
            player = BotGoalkeeper(screen, team, number, player_class, class_number)
            if team == 0:
                player.set_box(config.BOT_GOALKEEPER_TEAM_0_BOX_CORNERS[class_number])
                player.set_initial_pos(config.BOT_GOALKEEPER_TEAM_0_INITIAL_POS[class_number])
            else:
                player.set_box(config.BOT_GOALKEEPER_TEAM_1_BOX_CORNERS[class_number])
                player.set_initial_pos(config.BOT_GOALKEEPER_TEAM_1_INITIAL_POS[class_number])

        if is_controlled:
            player.set_controlled_settings()
        else:
            player.set_default_settings()
        return player

