import pygame
import config
import time

# Screen config
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((config.SCREEN_X_SIZE, config.SCREEN_Y_SIZE))
pygame.display.set_caption("Football")

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
    while True:
        Painter().paint()
        manage_events(screen)
        time.sleep(config.GAME_FREQUENCY)

        pygame.display.flip()

run()
