import pygame, sys
import config

class Field():
    # Basic football field with it's borders and gates

    def __init__(self, screen):

        self.screen = screen
        self.screen_rect = screen.get_rect()

        self.image = pygame.image.load("../" + config.STATIC_IMAGES_FOLDER + config.FIELD_IMAGE)
        self.image = pygame.transform.scale(self.image, (config.SCREEN_X_SIZE, config.SCREEN_Y_SIZE))

    def draw(self):
        # Drawing football field
        self.screen.blit(self.image, (0, 0))

    def check_ball_out(self, ball):
        # Checking if ball is out of the field
        return not (config.CORNERS[0][0] < ball.pos[0] and ball.pos[0] < config.CORNERS[2][0] and config.CORNERS[0][1] < ball.pos[1] and ball.pos[1] < config.CORNERS[2][1])
    
    def check_ball_in_gates(self, ball):
        # Checking if ball appers to be in any team's gates
        # 0 if it is in left team's gates
        # 1 if in other team's
        # -1 otherwise
        if ball.pos[0] < config.GATES_0[0][0] and config.GATES_0[0][1] < ball.pos[1] and ball.pos[1] < config.GATES_0[1][1]:
            return 0
        elif config.GATES_1[0][0] < ball.pos[0] and config.GATES_1[0][1] < ball.pos[1] and ball.pos[1] < config.GATES_1[1][1]:
            return 1
        return -1

