import pygame

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class Battery:
    def __init__(self, max_charge=100, discharge_rate=10 / 800):
        self.max_charge = max_charge
        self.charge = max_charge
        self.discharge_rate = discharge_rate
        self.is_half = False

    def drain(self):
        self.charge -= self.discharge_rate
        if self.charge < 0:
            self.charge = 0
        if not self.is_half and self.charge <= self.max_charge / 2:
            self.is_half = True
            return True


    def draw(self, screen):
        battery_width = 200
        battery_height = 30
        charge_ratio = self.charge / self.max_charge
        filled_width = int(battery_width * charge_ratio)

        # Draw the battery outline
        pygame.draw.rect(screen, WHITE, (10, 10, battery_width, battery_height), 2)

        # Draw the filled part
        pygame.draw.rect(screen, GREEN if charge_ratio > 0.2 else RED, (12, 12, filled_width, battery_height - 4))
