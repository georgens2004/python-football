import pygame, sys
import config

from painter import Painter
import menu
from match import game

import match.popup as popup


def game_event_handler(event):
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        game.game = None
        Painter().reset(menu.main_menu.draw)
        AppState().set_state("Main menu")
        return
    
    game.game.handle_event(event)


def menu_event_handler(event):
    if menu.current_menu == "Main":
        menu.main_menu.pick_setting(event)

def popup_event_handler(event):
    popup.popup.pick_setting(event)

class AppState():

    states_and_handlers = {
        "Game": game_event_handler,
        "Main menu": menu_event_handler
    }

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(AppState, cls).__new__(cls)
        return cls.instance
    
    def set_state(self, state):
        self.state = state
    
    def handle_event(self, event):
        if popup.popup is not None and not popup.popup.hidden:
            popup_event_handler(event)
            return
        self.states_and_handlers[self.state](event)

