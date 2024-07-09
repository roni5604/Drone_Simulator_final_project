import pygame

class Button:
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        font = pygame.font.SysFont(None, 36)
        text = font.render(self.text, True, (0, 0, 0))
        screen.blit(text, (self.rect.x + 10, self.rect.y + 10))
