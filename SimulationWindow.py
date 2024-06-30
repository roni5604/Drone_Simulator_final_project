import sys

import pygame
import threading

from AutoAlgo1 import AutoAlgo1
from CPU import CPU
from Map import Map
from Point import Point

map_num = 4
start_points = [
    Point(100, 50),
    Point(50, 60),
    Point(73, 68),
    Point(84, 73),
    Point(92, 100)
]
map_path = f"Maps/p1{map_num}.png"

real_map = Map(map_path, start_points[map_num - 1])


class Button:
    def __init__(self, text, x, y, width, height, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (200, 200, 200)
        self.text = text
        self.action = action

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.Font(None, 36)
        text_surf = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect.topleft)

    def collidepoint(self, pos):
        return self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.collidepoint(event.pos) and self.action:
                self.action()


class SimulationWindow:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1800, 700))
        pygame.display.set_caption("Drone Simulator")
        self.clock = pygame.time.Clock()
        self.running = True
        self.toogleStop = True
        self.info_label = None
        self.toogleRealMap = True
        self.algo1 = None
        self.initialize()

    def initialize(self):

        self.buttons = [
            Button("Start/Pause", 1400, 600, 150, 50, self.toggle_cpu),
            Button("SwitchDrone", 1650, 600, 150, 50, self.switch_drone),
            Button("speedUp", 1450, 100, 100, 50, self.speed_up),
            Button("speedDown", 1600, 100, 150, 50, self.speed_down),
            Button("spin180", 1420, 200, 100, 50, lambda: self.spin_by(180)),
            Button("spin90", 1550, 200, 100, 50, lambda: self.spin_by(90)),
            Button("spin60", 1700, 200, 100, 50, lambda: self.spin_by(60)),
            Button("spin30", 1400, 300, 100, 50, lambda: self.spin_by(30)),
            Button("spin-30", 1500, 300, 100, 50, lambda: self.spin_by(-30)),
            Button("spin-45", 1600, 300, 100, 50, lambda: self.spin_by(-45)),
            Button("spin-60", 1700, 300, 100, 50, lambda: self.spin_by(-60)),
            Button("Snack Driver", 1450, 400, 150, 50, self.toggle_snackDriver),
            Button("toggle AI", 1650, 400, 150, 50, self.toggle_ai),
            Button("Return Home", 1450, 500, 150, 50, self.return_home_func),
            Button("Keep Left", 1650, 500, 150, 50, self.toggle_stay_in_middle)
        ]

        self.info_label2_rect = pygame.Rect(1450, 0, 300, 80)


        self.main()

    def toggle_cpu(self):
        if self.toogleStop:
            CPU.stop_all_cpus()
        else:
            CPU.resume_all_cpus()
        self.toogleStop = not self.toogleStop

    def speed_up(self):
        self.algo1.speed_up()

    def speed_down(self):
        self.algo1.speed_down()

    def spin_by(self, degrees):
        self.algo1.spin_by(degrees)

    def toggle_real_map(self):
        self.algo1.toogle_real_map = not self.algo1.toogle_real_map

    def toggle_ai(self):
        self.algo1.toogle_ai = not self.algo1.toogle_ai

    def return_home_func(self):
        self.algo1.return_home = not self.algo1.return_home
        self.algo1.speed_down()
        self.algo1.spin_by2(180, True, lambda: self.algo1.speed_up())

    def open_graph(self):
        self.algo1.m_graph.draw_graph(self.screen)


    def toggle_keep_right_driver(self):
        self.algo1.toggle_keep_right_driver = not self.algo1.toggle_keep_right_driver

    def toggle_snackDriver(self):

        self.algo1.toggle_snackDriver = not self.algo1.toggle_snackDriver

    def toggle_stay_in_middle(self):
        self.algo1.toggle_keep_middle_driver = not self.algo1.toggle_keep_middle_driver

    def update_info(self, delta_time):
        font = pygame.font.Font(None, 24)
        info_text2 = f"return home: {self.algo1.return_home} isRisky: {self.algo1.is_risky} "
        text_surf2 = font.render(info_text2, True, (0, 0, 0))
        pygame.draw.rect(self.screen, (255, 255, 255), self.info_label2_rect)
        self.screen.blit(text_surf2, self.info_label2_rect.topleft)

        for button in self.buttons:
            button.draw(self.screen)


    def reset_map(self):


        # Draw the map image
        map_image = pygame.image.load(map_path)
        self.screen.blit(map_image, (0, 0))

        # Clear the screen by filling it with the background color (optional)
        background_color = (0, 0, 0)  # Black, or any background color of your choice
        self.screen.fill(background_color)

        # Update the display
        pygame.display.flip()

    def switch_drone(self):
        # clean the screen and the drawing
        self.reset_map()
        self.algo1.switch_drone(real_map)

    def main(self):

        self.algo1 = AutoAlgo1(real_map)

        painter_cpu = CPU(200, "painter")  # 60 FPS painter
        # painter_cpu.add_function(lambda delta_time: self.screen.fill((255, 255, 255)))
        painter_cpu.add_function(lambda delta_time: self.algo1.paint(self.screen))
        painter_cpu.add_function(lambda delta_time: pygame.display.flip())
        painter_cpu.play()

        self.algo1.play()

        updates_cpu = CPU(60, "updates")
        updates_cpu.add_function(lambda delta_time: self.algo1.drone.update(delta_time))
        updates_cpu.play()

        info_cpu = CPU(6, "update_info")
        info_cpu.add_function(self.update_info)
        info_cpu.play()

        while self.running:
            for event in pygame.event.get():
                for button in self.buttons:
                    button.handle_event(event)
                if event.type == pygame.QUIT:
                    self.running = False

            self.clock.tick(60)


if __name__ == "__main__":
    window = SimulationWindow()
    pygame.quit()
