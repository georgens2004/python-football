import pygame, sys
import config

class Scoreboard():
    # Basic game scoreboard

    def __init__(self, screen):
        self.screen = screen
        self.score_0 = 0
        self.score_1 = 0
        self.scoreboard_image = pygame.image.load("../" + config.STATIC_IMAGES_FOLDER + config.SCOREBOARD_IMAGE)
        self.scoreboard_image = pygame.transform.scale(self.scoreboard_image, (config.SCOREBOARD_SIZE_X, config.SCOREBOARD_SIZE_Y))

        self.pos = [(config.SCREEN_X_SIZE - config.SCOREBOARD_SIZE_X) // 2, 0]
        self.score_font = pygame.font.Font("../" + config.STATIC_FONTS_FOLDER + config.SCOREBOARD_FONT, config.SCOREBOARD_FONT_SIZE)

    def draw(self):
        self.screen.blit(self.scoreboard_image, ((config.SCREEN_X_SIZE - config.SCOREBOARD_SIZE_X) // 2, 0))
        score_0 = self.score_font.render(str(self.score_0), False, (255, 255, 255))
        score_0_rect = score_0.get_rect(center=(self.pos[0] + config.SCOREBOARD_GOALS_0_X_OFFSET, self.pos[1] + config.SCOREBOARD_GOALS_0_Y_OFFSET))
        score_1 = self.score_font.render(str(self.score_1), False, (255, 255, 255))
        score_1_rect = score_1.get_rect(center=(self.pos[0] + config.SCOREBOARD_GOALS_1_X_OFFSET, self.pos[1] + config.SCOREBOARD_GOALS_1_Y_OFFSET))
        self.screen.blit(score_0, score_0_rect)
        self.screen.blit(score_1, score_1_rect)
    
    def update_score(self, change_0, change_1):
        self.score_0 += change_0
        self.score_1 += change_1
    
    def reset(self):
        self.score_0 = 0
        self.score_1 = 0
