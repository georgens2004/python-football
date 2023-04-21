import pygame
import config
import time

# Screen config
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((config.SCREEN_X_SIZE, config.SCREEN_Y_SIZE))
pygame.display.set_caption("Football")

pygame.event.set_allowed([
    pygame.QUIT,
    pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6,
    pygame.K_SPACE
])

clock = pygame.time.Clock()

from painter import Painter
from menu import init_menus
from event_manager import manage_events
from match.game import init_game_modes
from handlers import AppState
from button import init_buttons
import match.popup as popup

init_buttons(screen)
init_menus(screen)
init_game_modes()

AppState().set_state("Main menu")

painter = Painter()

def run():
    while 1:
        Painter().paint()
        manage_events(screen)

        clock.tick(config.GAME_FPS)

        pygame.display.flip()

run()
