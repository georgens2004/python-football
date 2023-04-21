from painter import Painter
import config
import pygame
import match.game as game

popup = None

class Popup():

    def __init__(self, screen, text, ticks, buttons=[]):
        self.screen = screen

        font = pygame.font.SysFont(config.POPUP_FONT, config.POPUP_FONT_SIZE)
        self.text = font.render(text, False, (63, 0, 140))
        self.text_rect = self.text.get_rect(center=(config.SCREEN_X_SIZE // 2, config.SCREEN_Y_SIZE // 2))

        self.buttons = buttons
        for idx in range(len(self.buttons)):
            self.buttons[idx].set_center(config.SCREEN_X_SIZE // 2, config.SCREEN_Y_SIZE // 2 + config.POPUP_BTN_CENTER_INDENT + idx * (config.MENU_BTN_SIZE_Y + config.POPUP_BTN_Y_PADDING))

        self.ticks = ticks
        self.hidden = False
    
    def show(self):
        game.game.pause()
        Painter().add(self.draw)

    def draw(self):
        if Painter().top() != self.draw:
            self.hidden = True
            return
        self.hidden = False
        self.screen.blit(self.text, self.text_rect)
        for btn in self.buttons:
            btn.draw()
        self.ticks -= 1
        if (self.ticks == 0):
            self.disappear()
    
    def disappear(self):
        Painter().pop()
        game.game.unpause()
        game.game.restart()
        global popup
        popup = None
    
    def pick_setting(self, event):
        for btn in self.buttons:
            if btn.click(event):
                break

