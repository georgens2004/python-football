import pygame, sys
import config

import math

class PlayerCreator():
    # An abstract class for players creation

    def create_player(screen, is_controlled, team, num, initial_pos, current_pos=-1):
        if current_pos == -1:
            current_pos = initial_pos
        player =  Player(screen, team, num, initial_pos, current_pos)
        if is_controlled:
            player.set_controlled_settings()
        else:
            player.set_default_settings()
        return player


class Player():

    # team: 0 or 1
    # speed: player's speed in game
    # power: ball initial speed after player's kick
    # catch_radius: where player can catch the ball (dist from border to border)
    
    def __init__(self, screen, team, number, initial_pos, current_pos):
        self.screen = screen
        self.team = team
        self.number = number + 1

        self.initial_pos = initial_pos
        self.pos = current_pos
        self.dir = [1, 0]

        self.ball = None

        self.image = pygame.image.load("../" + config.STATIC_IMAGES_FOLDER + config.PLAYER_IMAGES[self.team])
        self.image = pygame.transform.scale(self.image, (config.PLAYER_RADIUS * 2, config.PLAYER_RADIUS * 2))
    
    def draw(self):
        # Basic drawing function
        self.screen.blit(self.image, (self.pos[0] - config.PLAYER_RADIUS, self.pos[1] - config.PLAYER_RADIUS))
        font = pygame.font.SysFont(config.PLAYER_NUMBER_FONT, config.PLAYER_NUMBER_FONT_SIZE)
        text = font.render(str(self.number), False, (0, 0, 0))
        text_rect = text.get_rect(center=(self.pos[0], self.pos[1]))
        self.screen.blit(text, text_rect)

    def set_default_settings(self):
        # Setting default settings for non-controlled player
        self.speed = config.DEFAULT_SPEED
        self.power = config.DEFAULT_POWER
        self.catch_radius = config.DEFAULT_CATCH_RADIUS
    
    def set_controlled_settings(self):
        # Setting other settings for controlled player
        self.speed = config.CONTROLLED_SPEED
        self.power = config.CONTROLLED_POWER
        self.catch_radius = config.CONTROLLED_CATCH_RADIUS
    
    def restart(self):
        # When game restarts
        self.pos = self.initial_pos
        self.ball = None
    
    def scale_dir(self):
        denom = math.sqrt(self.dir[0] ** 2 + self.dir[1] ** 2)
        self.dir = [self.dir[0] / denom, self.dir[1] / denom]
    
    def step(self):
        # One player step (each game tick)
        self.pos = [self.pos[0] + self.dir[0] * self.speed, self.pos[1] + self.dir[1] * self.speed]
        if self.ball is not None:
            self.ball.stick_to_owner()

    def get_dist(self, pos):
        return math.sqrt((self.pos[0] - pos[0]) ** 2 + (self.pos[1] - pos[1]) ** 2)
    
    def own_ball(self, ball):
        # Get ball
        ball.become_owned(self)
        self.ball = ball
    
    def lose_ball(self):
        # Lose ball
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
        # Controlled player makes this move every game tick (moving towards mouse direction)
        if self.get_dist(pygame.mouse.get_pos()) > config.PLAYER_RADIUS:
            self.dir = [pos[0] - self.pos[0], pos[1] - self.pos[1]]
            self.scale_dir()
            self.step()

    def shoot(self):
        # Shoot if controlled player has ball
        if self.ball is None:
            return
        self.ball.dir = self.dir
        self.ball.speed = self.power
        self.ball.pos = [self.ball.pos[0] + self.dir[0] * (self.speed + 1), self.ball.pos[1] + self.dir[1] * (self.speed + 1)]
        self.lose_ball()
        
