import pygame
from Simulator_2D.AutoAlgo1 import AutoAlgo1
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
map_path = f"Simulator_2D/Maps/p1{map_num}.png"

real_map = Map(map_path, start_points[map_num - 1])


class Button:
    def __init__(self, text, x, y, width, height, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (200, 200, 200)  # Default color
        self.active_color = (100, 100, 100)  # Color when active
        self.text = text
        self.action = action
        self.is_active = False  # State tracking

    def draw(self, screen):
        current_color = self.active_color if self.is_active else self.color
        pygame.draw.rect(screen, current_color, self.rect)
        font = pygame.font.Font(None, 36)
        text_surf = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect.topleft)

    def collidepoint(self, pos):
        return self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.collidepoint(event.pos):
                self.is_active = not self.is_active  # Toggle the state
                if self.action:
                    self.action()


class SimulationWindow:
    def __init__(self):
        self.info_lidars_rect = None
        self.info_drone_rect = None
        self.info_algo_rect = None
        self.buttons = None
        self.info_label2_rect = None
        pygame.init()
        self.screen = pygame.display.set_mode((1800, 700))
        pygame.display.set_caption("Drone Simulator")
        self.clock = pygame.time.Clock()
        self.running = True
        self.toogleStop = True
        self.info_label = None
        self.toogleRealMap = True
        self.algo1 = None
        self.algo = "None"

        self.initialize()

    def initialize(self):

        self.buttons = [
            Button("AI Algorithm", 1500, 100, 200, 50, self.toggle_ai),
            Button("Snack Driver", 1500, 160, 200, 50, self.toggle_snackDriver),
            Button("Keep Left ", 1500, 220, 200, 50, self.toggle_keep_right_driver),
            Button("Keep Right ", 1500, 280, 200, 50, self.toggle_keep_right_driver),
            Button("SwitchMap", 1500, 400, 200, 50, self.switch_map),
            Button("SwitchDrone", 1500, 460, 200, 50, self.switch_drone),
            Button("Return Home", 1500, 520, 200, 50, self.return_home_func)
        ]
        self.info_label2_rect = pygame.Rect(1450, 0, 300, 20)
        self.info_algo_rect = pygame.Rect(1450, 20, 300, 20)
        self.info_drone_rect = pygame.Rect(1450, 40, 300, 20)
        self.info_lidars_rect = pygame.Rect(1450, 60, 300, 20)

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

    def set_false_toggles(self):
        self.algo1.set_false_toggles()

    def spin_by(self, degrees):
        self.algo1.spin_by(degrees)

    def toggle_real_map(self):
        self.algo1.toogle_real_map = not self.algo1.toogle_real_map

    def toggle_ai(self):

        self.algo = "AI"
        self.algo1.set_false_toggles()
        self.algo1.toogle_ai = not self.algo1.toogle_ai

    def return_home_func(self):
        self.algo = "Return Home"
        self.algo1.set_false_toggles()
        self.algo1.return_home = not self.algo1.return_home
        self.algo1.drone.speed = 0


    def open_graph(self):
        self.algo1.m_graph.draw_graph(self.screen)

    def toggle_keep_right_driver(self):
        self.algo = "keep right driver"

        self.algo1.set_false_toggles()
        self.algo1.toggle_keep_right_driver = not self.algo1.toggle_keep_right_driver

    def toggle_snackDriver(self):
        self.algo = "Snake driver"
        self.algo1.set_false_toggles()
        self.algo1.toggle_snackDriver = not self.algo1.toggle_snackDriver

    def toggle_stay_in_middle(self):
        self.algo = "Stay in middle"
        self.algo1.set_false_toggles()
        self.algo1.toggle_keep_middle_driver = not self.algo1.toggle_keep_middle_driver
    def get_drone_properties(self):
        return self.algo1.get_drone_properties()

    def update_info(self, delta_time):
        font = pygame.font.Font(None, 24)
        info_text2 = f"isRisky: {self.algo1.is_risky} "
        info_algo = f'Algorithm: {self.algo}'
        drone_number, drone_lidar = self.get_drone_properties()

        text_surf2 = font.render(info_text2, True, (0, 0, 0))
        info_drone_properites = f"{drone_number}, Rotation: {self.algo1.drone.rotation}"

        info_algo_text = font.render(info_algo, True, (0, 0, 0))
        drone_text = font.render(info_drone_properites, True, (0, 0, 0))
        lidars_text = font.render(drone_lidar, True, (0, 0, 0))

        pygame.draw.rect(self.screen, (255, 255, 255), self.info_label2_rect)
        self.screen.blit(text_surf2, self.info_label2_rect.topleft)
        pygame.draw.rect(self.screen, (255, 255, 255), self.info_algo_rect)
        self.screen.blit(info_algo_text, self.info_algo_rect.topleft)
        pygame.draw.rect(self.screen, (255, 255, 255), self.info_drone_rect)
        self.screen.blit(drone_text, self.info_drone_rect.topleft)
        pygame.draw.rect(self.screen, (255, 255, 255), self.info_lidars_rect)
        self.screen.blit(lidars_text, self.info_lidars_rect.topleft)


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

    def switch_map(self):
        global map_num, real_map, map_path
        map_num = (map_num % 4) + 1
        map_path = f"Maps/p1{map_num}.png"
        real_map = Map(map_path, start_points[map_num - 1])
        self.reset_map()
        self.algo1.switch_map(real_map)

    def main(self):

        self.algo1 = AutoAlgo1(real_map)

        painter_cpu = CPU(200, "painter")  # 60 FPS painter
        # painter_cpu.add_function(lambda delta_time: self.screen.fill((255, 255, 255)))
        painter_cpu.add_function(lambda delta_time: self.algo1.paint(self.screen))
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

            self.algo1.paint(self.screen)  # Ensure painting is done
            self.update_info(0)  # Update info display
            pygame.display.flip()  # Flip the display buffer
            self.clock.tick(60)


if __name__ == "__main__":
    window = SimulationWindow()
    pygame.quit()
