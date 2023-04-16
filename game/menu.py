import pygame, sys
import config

from painter import Painter
from background import Background
from match import game
from handlers import AppState

import button

class Menu():
    # Basic menu class
    # Contains buttons

    def __init__(self, screen, background_image, buttons):
        self.screen = screen
        self.background = Background(screen, background_image)
        self.buttons = buttons
        for idx in range(len(self.buttons)):
            self.buttons[idx].set_center(config.SCREEN_X_SIZE // 2, config.SCREEN_Y_SIZE // 2 + config.MAIN_MENU_CENTER_INDENT + idx * (config.MENU_BTN_SIZE_Y + config.MENU_BTN_Y_PADDING))
    
    def draw(self):
        self.background.draw()
        for btn in self.buttons:
            btn.draw()

    def pick_setting(self, event):
        # If any button was pressed
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        for btn in self.buttons:
            if btn.click(event):
                break

main_menu = None

def init_menus(screen):
    # Initializing all menus in the beginning of the program
    global main_menu
    main_menu = Menu(screen, config.MAIN_MENU_BACKGROUND_IMAGE, [
        button.start_game_btn,
        button.quit_btn
    ])
    Painter().reset(main_menu.draw)


current_menu = "Main"
