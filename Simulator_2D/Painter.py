import pygame

class Painter:
    def __init__(self, algo):
        self.algo = algo

    def paint_component(self, screen):
        self.algo.paint(screen)