import pygame, sys
import config

class Painter():
    # Class for drawing every object on the screen each tick 
    # Very useful in cases when we have like game, players, ball and popup
    # Singleton class

    draw_funcs = []

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Painter, cls).__new__(cls)
        return cls.instance
    
    def add(self, draw_func):
        self.draw_funcs.append(draw_func)

    def pop(self):
        self.draw_funcs.pop()
    
    def top(self):
        if len(self.draw_funcs) > 0:
            return self.draw_funcs[-1]
        return None
    
    def paint(self):
        # Drawing everything on the screen each tick
        for draw_func in self.draw_funcs:
            draw_func()

    def reset(self, draw_func):
        self.draw_funcs = [draw_func]

