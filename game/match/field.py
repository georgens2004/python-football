import pygame, sys
import config

class Field():

    def __init__(self, screen):

        self.screen = screen
        self.screen_rect = screen.get_rect()

        self.image = pygame.image.load("../" + config.STATIC_IMAGES_FOLDER + config.FIELD_IMAGE).convert_alpha()
        self.image = pygame.transform.scale(self.image, (config.SCREEN_X_SIZE, config.SCREEN_Y_SIZE))

    def draw(self):
        # drawing football field
        self.screen.blit(self.image, (0, 0))

    def check_ball_out(self, ball):
        return not (config.CORNERS[0][0] <= ball.pos[0] and ball.pos[0] <= config.CORNERS[2][0] and config.CORNERS[0][1] <= ball.pos[1] and ball.pos[1] <= config.CORNERS[2][1])
    
    def check_ball_in_gates(self, ball):
        if ball.pos[0] < config.GATES[0][0][0] and config.GATES[0][0][1] < ball.pos[1] and ball.pos[1] < config.GATES[0][1][1]:
            return 0
        elif config.GATES[1][0][0] < ball.pos[0] and config.GATES[1][0][1] < ball.pos[1] and ball.pos[1] < config.GATES[1][1][1]:
            return 1
        return -1

