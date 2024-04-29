import pygame, sys
import config


class Ball():

    def __init__(self, screen):
        self.screen = screen
        self.initial_pos = [config.SCREEN_X_SIZE // 2, config.SCREEN_Y_SIZE // 2]
        self.pos = self.initial_pos
        self.dir = [0, 0]
        self.speed = 0
        self.owner = None

        self.image = pygame.image.load("../" + config.STATIC_IMAGES_FOLDER + config.BALL_IMAGE).convert_alpha()
        self.image = pygame.transform.scale(self.image, (config.BALL_RADIUS * 2, config.BALL_RADIUS * 2))
    
    def draw(self):
        self.screen.blit(self.image, [self.pos[0] - config.BALL_RADIUS, self.pos[1] - config.BALL_RADIUS])
    
    def restart(self):
        self.pos = self.initial_pos
        self.dir = [0, 0]
        self.speed = 0
        self.owner = None

    def fly(self):
        if self.owner is None:
            self.pos = [self.pos[0] + self.dir[0] * self.speed, self.pos[1] + self.dir[1] * self.speed]
            self.speed = max(self.speed - config.BALL_SPEED_REGRESSION, 0)
    
    def become_owned(self, player):
        self.dir = [0, 0]
        self.speed = 0
        self.owner = player
    
    def stick_to_owner(self):
        if self.owner is not None:
            self.pos = [self.owner.pos[0] + self.owner.dir[0] * (config.PLAYER_RADIUS + config.BALL_RADIUS + config.BALL_DIST_TO_OWNER), self.owner.pos[1] + self.owner.dir[1] * (config.PLAYER_RADIUS + config.BALL_RADIUS + config.BALL_DIST_TO_OWNER)]
    
