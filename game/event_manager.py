import pygame, sys
import config

from match import game
import handlers

import match.popup as popup

def manage_events(screen):
    # events management
    if game.game is not None:
        game.game.tick()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        
        handlers.AppState().handle_event(event)

