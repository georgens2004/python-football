import pygame, sys
import config

class Background():
    # Basic background class (presents only in menus)

    def __init__(self, screen, image_name):
        self.screen = screen
        self.image = pygame.image.load("../" + config.STATIC_IMAGES_FOLDER + image_name)
        self.image = pygame.transform.scale(self.image, (config.SCREEN_X_SIZE, config.SCREEN_Y_SIZE))
    
    def draw(self):
        self.screen.blit(self.image, (0, 0))
