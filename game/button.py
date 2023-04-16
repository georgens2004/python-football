import pygame
import config
import sys

import match.game as game
from painter import Painter
from handlers import AppState

'''   Button on-click functions   '''

# Start game
def start_game_call(screen):
    game.game = game.Game(screen, game.game_modes[0])
    Painter().reset(game.game.draw)
    AppState().set_state("Game")

# Quit 
def quit_call(screen):
    sys.exit()

# Show replay
def show_replay_call(screen):
    game.game.show_replay()

'''   End   '''

class Button():
    # Basic button class

    def __init__(self, screen, text, size_x, size_y, on_click):
        self.screen = screen

        self.text = text
        self.btn_image = pygame.image.load("../" + config.STATIC_IMAGES_FOLDER + config.BTN_IMAGE)
        self.btn_image = pygame.transform.scale(self.btn_image, (size_x, size_y))
        
        self.size_x = size_x
        self.size_y = size_y

        self.on_click = on_click
    
    def set_center(self, center_x, center_y):
        self.center_x = center_x
        self.center_y = center_y

        font = pygame.font.SysFont(config.BTN_FONT, config.BTN_FONT_SIZE)
        self.text_rendered = font.render(self.text, False, (0, 0, 0))
        self.text_rect = self.text_rendered.get_rect(center=(center_x, center_y))

    def draw(self):
        self.screen.blit(self.btn_image, (self.center_x - self.size_x // 2, self.center_y - self.size_y // 2))
        self.screen.blit(self.text_rendered, self.text_rect)
    
    def click(self, event):
        # Check if button was clicked
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        pos = pygame.mouse.get_pos()
        if self.center_x - self.size_x // 2 < pos[0] and pos[0] < self.center_x + self.size_x // 2:
            if self.center_y - self.size_y // 2 < pos[1] and pos[1] < self.center_y + self.size_y // 2:
                self.on_click(self.screen)
                return True

        return False


''' Buttons '''

start_game_btn = None
quit_btn = None
show_replay_btn = None

def init_buttons(screen):
    # Initializing some global buttons in the beginning of the program
    global start_game_btn
    start_game_btn = Button(screen, "Start game", config.MENU_BTN_SIZE_X, config.MENU_BTN_SIZE_Y, start_game_call)
    global quit_btn
    quit_btn = Button(screen, "Quit", config.MENU_BTN_SIZE_X, config.MENU_BTN_SIZE_Y, quit_call)
    global show_replay_btn
    show_replay_btn = Button(screen, "Replay", config.REPLAY_BTN_SIZE_X, config.REPLAY_BTN_SIZE_Y, show_replay_call)
