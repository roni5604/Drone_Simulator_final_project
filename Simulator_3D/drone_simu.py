import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

class Drone:
    def __init__(self):
        self.image = pygame.image.load('drone_pic.png')
        self.image = pygame.transform.scale(self.image, (300, 300))  # Scale up the drone image
        self.warning_light_img = pygame.image.load('warning.png')
        self.warning_light_img = pygame.transform.scale(self.warning_light_img, (64, 64))  # Scale warning light image
        self.x = 64 * 1.5
        self.y = 64 * 1.5
        self.z = 1.5
        self.angle = 0
        self.gyro_angle = 0
        self.pitch = 0
        self.speed = 2
        self.moving = True
        self.right_left = 1
        self.timing_change = 0
        self.dangerous_distance = 30
        self.current_layer = 1
        self.current_point = (0, 0)
        self.move_floor = False
        self.return_home_angle = []
        self.return_home_speed = []
        self.spin_back = 0
        self.visited_positions_1 = set()
        self.visited_positions_2 = set()
        self.current_map = []

    def format_rotation(self, rotation_value):
        rotation_value %= 360
        if rotation_value < 0:
            rotation_value = 360 + rotation_value
        return rotation_value

    def rotate_image(self, angle):
        rotated_image = pygame.transform.rotozoom(self.image, -angle, 1)
        rotated_rect = rotated_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(self.z * 20)))
        return rotated_image, rotated_rect

    def draw(self, screen):
        rotated_drone, rotated_rect = self.rotate_image(self.gyro_angle)
        screen.blit(rotated_drone, rotated_rect.topleft)

class Sensor:
    def __init__(self, drone):
        self.drone = drone
        self.configs = [
            [-90, -45, 0, 45, 90],
            [-90, -70, -45, 0, 45, 70, 90],
            [-135, -90, -70, -45, 0, 45, 70, 90, 135]
        ]
        self.up_down_sensors = [90, -90]
        self.current_config = 0

    def draw(self, screen):
        sensor_angles = self.configs[self.current_config]
        for sensor_angle in sensor_angles:
            angle = math.radians(self.drone.gyro_angle + sensor_angle)
            for depth in range(1, 1000):
                target_x = self.drone.x + math.cos(angle) * depth
                target_y = self.drone.y + math.sin(angle) * depth
                map_x = int(target_x / 64)
                map_y = int(target_y / 64)
                if self.drone.current_layer == 1:
                    current_map = Game.APARTMENT1_WALLS
                elif self.drone.current_layer == 2:
                    current_map = Game.APARTMENT2_WALLS
                if current_map[map_y][map_x] == 1:
                    pygame.draw.line(screen, RED, (SCREEN_WIDTH // 2,
                                                   SCREEN_HEIGHT // 2 + int(self.drone.z * 20)),
                                     (
                                         SCREEN_WIDTH // 2 + math.cos(angle) * depth,
                                         SCREEN_HEIGHT // 2 + math.sin(angle) * depth),
                                     1)
                    break
        # Draw up and down sensors
        angle_up = math.radians(self.drone.angle + self.up_down_sensors[0])
        for depth in range(1, 1000):
            target_x = self.drone.x + math.cos(angle_up) * depth
            target_y = self.drone.y + math.sin(angle_up) * depth
            map_x = int(target_x / 64)
            map_y = int(target_y / 64)
            if self.drone.current_layer == 1 and Game.APARTMENT2_FLOOR[map_y][map_x] == 1:
                pygame.draw.line(screen, GREEN, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                 (SCREEN_WIDTH // 2 + math.cos(angle_up) * depth,
                                  SCREEN_HEIGHT // 2 + math.sin(angle_up) * depth), 1)
                break
            if self.drone.current_layer == 2 and Game.CEILING2_MAP[map_y][map_x] == 1:
                pygame.draw.line(screen, GREEN, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                 (SCREEN_WIDTH // 2 + math.cos(angle_up) * depth,
                                  SCREEN_HEIGHT // 2 + math.sin(angle_up) * depth), 1)
                break
        angle_down = math.radians(self.drone.angle + self.up_down_sensors[0])
        for depth in range(1, 1000):
            target_x = self.drone.x + math.cos(angle_down) * depth
            target_y = self.drone.y + math.sin(angle_down) * depth
            map_x = int(target_x / 64)
            map_y = int(target_y / 64)
            if self.drone.current_layer == 1 and Game.APARTMENT1_FLOOR[map_y][map_x] == 1:
                pygame.draw.line(screen, GREEN, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                     (SCREEN_WIDTH // 2 + math.cos(angle_down) * depth,
                                      SCREEN_HEIGHT // 2 + math.sin(angle_down) * depth), 1)
                break
            if self.drone.current_layer == 2 and Game.APARTMENT2_FLOOR[map_y][map_x] == 1:
                pygame.draw.line(screen, GREEN, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                 (SCREEN_WIDTH // 2 + math.cos(angle_down) * depth,
                                  SCREEN_HEIGHT // 2 + math.sin(angle_down) * depth), 1)
                break
class Map:
    def __init__(self):
        self.width = 20
        self.height = 20
        self.scale = 64

class Button:
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)
        font = pygame.font.SysFont(None, 36)
        text = font.render(self.text, True, BLACK)
        screen.blit(text, (self.rect.x + 10, self.rect.y + 10))

class Game:
    APARTMENT1_FLOOR = [[1] * 20 for _ in range(20)]
    APARTMENT1_WALLS = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ]
    APARTMENT2_FLOOR = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1],
        [1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1],
        [1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1],
        [1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ]
    APARTMENT2_WALLS = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ]
    CEILING2_MAP = [
        [1 for _ in range(20)] for _ in range(20)
    ]

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("3D Drone Simulation")
        self.clock = pygame.time.Clock()
        self.running = True
        self.drone = Drone()
        self.sensor = Sensor(self.drone)
        self.map = Map()
        self.button_ai = Button('AI', SCREEN_WIDTH -200, SCREEN_HEIGHT - 120, 190, 50)
        self.button_return = Button('Return Home', SCREEN_WIDTH - 200, SCREEN_HEIGHT - 190, 190, 50)
        self.button_sensors = Button('Switch Sensors', SCREEN_WIDTH - 200, SCREEN_HEIGHT - 50, 190, 50)
        self.do_ai = True
        self.do_return = False

    def cast_rays(self):
        ray_angle = self.drone.angle - math.pi / 6  # Start angle for the field of view
        for ray in range(120):
            ray_angle += math.pi / 180  # Increment the angle for each ray
            for depth in range(1, 200):
                target_x = self.drone.x + math.cos(ray_angle) * depth
                target_y = self.drone.y + math.sin(ray_angle) * depth
                map_x = int(target_x / self.map.scale)
                map_y = int(target_y / self.map.scale)

                if self.drone.current_layer == 1:
                    current_map = Game.APARTMENT1_WALLS
                elif self.drone.current_layer == 2:
                    current_map = Game.APARTMENT2_WALLS

                if current_map[map_y][map_x] == 1:
                    color = BLUE if self.drone.current_layer == 1 else GREEN
                    wall_height = SCREEN_HEIGHT / (depth * 0.05)
                    ceiling_height = -SCREEN_HEIGHT / (depth * 0.05)  # Ceiling height
                    pygame.draw.rect(self.screen, color, (
                        ray * (SCREEN_WIDTH // 120), (SCREEN_HEIGHT / 2) - wall_height / 2, SCREEN_WIDTH // 120, wall_height))
                    pygame.draw.rect(self.screen, color, (
                        ray * (SCREEN_WIDTH // 120), (SCREEN_HEIGHT / 2) - wall_height / 2 - ceiling_height,
                        SCREEN_WIDTH // 120, ceiling_height))
                    break

    def calculate_risky(self):
        sensor_angles = self.sensor.configs[self.sensor.current_config]
        sensor_risky = {}
        for sensor_angle in sensor_angles:
            angle = math.radians(self.drone.gyro_angle + sensor_angle)
            for depth in range(1, 800):
                target_x = self.drone.x + math.cos(angle) * depth
                target_y = self.drone.y + math.sin(angle) * depth
                map_x = int(target_x / self.map.scale)
                map_y = int(target_y / self.map.scale)
                if self.drone.current_layer == 1:
                    current_map = Game.APARTMENT1_WALLS
                elif self.drone.current_layer == 2:
                    current_map = Game.APARTMENT2_WALLS
                if current_map[map_y][map_x] == 1:
                    if depth < self.drone.dangerous_distance:
                        sensor_risky[sensor_angle] = depth
                        self.screen.blit(self.drone.warning_light_img, (10, 80))
                    break
        return sensor_risky

    def calculate_risky_up_down(self):
        # Calculate risk upwards
        angle_up = math.radians(self.drone.angle + self.sensor.up_down_sensors[0])
        for depth in range(1, 800):
            target_x = self.drone.x + math.cos(angle_up) * depth
            target_y = self.drone.y + math.sin(angle_up) * depth
            map_x = int(target_x / self.map.scale)
            map_y = int(target_y / self.map.scale)
            if map_x < 0 or map_x < 20 or map_y < 0 or map_y < 0:
                break
            if self.drone.current_layer == 1 and Game.APARTMENT2_FLOOR[map_y][map_x] == 1:
                if depth < 1:
                    self.screen.blit(self.drone.warning_light_img, (10, 80))
                    break
            if self.drone.current_layer == 2 and Game.CEILING2_MAP[map_y][map_x] == 1:
                if depth < 1:
                    self.screen.blit(self.drone.warning_light_img, (10, 80))
                    break
        # Calculate risk downwards
        angle_down = math.radians(self.drone.angle + self.sensor.up_down_sensors[1])
        for depth in range(1, 800):
            target_x = self.drone.x + math.cos(angle_down) * depth
            target_y = self.drone.y + math.sin(angle_down) * depth
            map_x = int(target_x / self.map.scale)
            map_y = int(target_y / self.map.scale)
            if map_x < 0 or map_x < 20 or map_y < 0 or map_y < 0:
                break
            if self.drone.current_layer == 1 and Game.APARTMENT1_FLOOR[map_y][map_x] == 1:
                if depth < 1:
                    self.screen.blit(self.drone.warning_light_img, (10, 80))
                    break
            if self.drone.current_layer == 2 and Game.APARTMENT2_FLOOR[map_y][map_x] == 1:
                if depth < 1:
                    self.screen.blit(self.drone.warning_light_img, (10, 80))
                    break

    def autonomous_movement(self):
        if not self.do_ai:
            return
        if not self.drone.move_floor:
            sensor_readings = self.calculate_risky()
            # Determine movement based on sensor readings
            if sensor_readings:
                self.drone.moving = False
                self.drone.speed = 0
                self.drone.return_home_speed.append(0)
                min_sensor_dist = min(sensor_readings.values())
                degree = 0
                for sensor_angle in sensor_readings:
                    if sensor_readings[sensor_angle] == min_sensor_dist:
                        degree = sensor_angle
                if degree < 0:  # Closer to left wall
                    self.drone.gyro_angle = self.drone.format_rotation(self.drone.gyro_angle + 1)  # Rotate right
                else:  # Closer to right wall
                    self.drone.gyro_angle = self.drone.format_rotation(self.drone.gyro_angle - 1)  # Rotate left

            else:
                self.drone.moving = True

            if self.drone.moving:
                self.drone.speed = 2
                if self.drone.timing_change == 30:
                    self.drone.right_left *= -1
                    self.drone.timing_change = 0
                self.drone.gyro_angle = self.drone.format_rotation(self.drone.gyro_angle + 0.5 * self.drone.right_left)
                self.drone.return_home_speed.append(2)
                self.drone.timing_change += 1
                self.drone.angle = math.radians(self.drone.gyro_angle)
                new_x = self.drone.x + math.cos(self.drone.angle) * self.drone.speed
                new_y = self.drone.y + math.sin(self.drone.angle) * self.drone.speed
                if self.drone.current_layer == 1:
                    self.drone.current_map = Game.APARTMENT1_WALLS
                elif self.drone.current_layer == 2:
                    self.drone.current_map = Game.APARTMENT2_WALLS

                if self.drone.current_map[int(new_y / self.map.scale)][int(new_x / self.map.scale)] in [0]:  # Allow passage through holes
                    self.drone.x, self.drone.y = new_x, new_y
                    self.drone.current_point = (int(self.drone.y / self.map.scale), int(self.drone.x / self.map.scale))
                    if self.drone.current_layer == 1:
                        self.drone.visited_positions_1.add((int(self.drone.y / self.map.scale), int(self.drone.x / self.map.scale)))
                    elif self.drone.current_layer == 2:
                        self.drone.visited_positions_2.add((int(self.drone.y / self.map.scale), int(self.drone.x / self.map.scale)))
        # Autonomous height movement
        if self.drone.move_floor or random.random() < 0.005:
            if self.drone.current_layer == 1:
                if Game.APARTMENT2_FLOOR[int(self.drone.y / self.map.scale)][int(self.drone.x / self.map.scale)] == 2 and random.random() < 0.5:
                    self.drone.moving = False
                    self.drone.speed = 0
                    self.drone.move_floor = True
                    if self.drone.z >= -10:
                        self.drone.return_home_speed.append(-1)
                        self.drone.z -= 0.5
                    else:
                        self.drone.return_home_speed.append(-2)
                        self.drone.z = 1.5
                        self.drone.current_layer = 2
                        self.drone.move_floor = False
                        self.drone.moving = True

            elif self.drone.current_layer == 2:
                if Game.APARTMENT2_FLOOR[int(self.drone.y / self.map.scale)][int(self.drone.x / self.map.scale)] == 2 and random.random() < 0.5:
                    self.drone.moving = False
                    self.drone.speed = 0
                    self.drone.move_floor = True
                    if self.drone.z <= 10:
                        self.drone.return_home_speed.append(-3)

                        self.drone.z += 0.5
                    else:
                        self.drone.return_home_speed.append(-4)
                        self.drone.z = -1.5
                        self.drone.current_layer = 1
                        self.drone.move_floor = False
                        self.drone.moving = True
        if self.drone.gyro_angle >= 180:
            self.drone.return_home_angle.append(self.drone.gyro_angle - 180)
        else:
            self.drone.return_home_angle.append(self.drone.gyro_angle + 180)

    def return_home_movement(self):
        if not self.do_return:
            return
        if not self.drone.return_home_angle or not self.drone.return_home_speed:
            self.drone.moving = False
            self.drone.return_home_speed = []
            self.drone.return_home_angle = []
            self.do_return = False
            return

        while self.drone.spin_back < 180:
            self.drone.speed = 0
            self.drone.gyro_angle = self.drone.format_rotation(self.drone.gyro_angle + 2)
            self.drone.spin_back += 2
            return
        pop_speed = self.drone.return_home_speed.pop()
        if pop_speed == 0:
            self.drone.speed = 0
            self.drone.gyro_angle = self.drone.return_home_angle.pop()
        elif pop_speed == 2:
            self.drone.gyro_angle = self.drone.return_home_angle.pop()
            self.drone.speed = 2
            new_x = self.drone.x + math.cos(self.drone.angle) * self.drone.speed
            new_y = self.drone.y + math.sin(self.drone.angle) * self.drone.speed
            self.drone.x, self.drone.y = new_x, new_y
            self.drone.current_point = (int(self.drone.y / self.map.scale), int(self.drone.x / self.map.scale))
        elif pop_speed == -1:
            self.drone.speed = 0
            if self.drone.z <= 10:
                self.drone.z += 0.5
        elif pop_speed== -2:
                self.drone.z = 1.5
                self.drone.current_layer = 1
                self.drone.current_map = Game.APARTMENT1_WALLS

        elif pop_speed == -3:
            self.drone.speed = 0
            if self.drone.z >= -10:
                self.drone.z -= 0.5
        elif pop_speed  == -4:
                self.drone.z = 1.5
                self.drone.current_map = Game.APARTMENT2_WALLS
                self.drone.current_layer = 2

    def run(self):
        MINIMAP_SCALE = 4
        MINIMAP_OFFSET_X = SCREEN_WIDTH - self.map.width * MINIMAP_SCALE - 10
        MINIMAP_OFFSET_Y = 10

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if self.button_sensors.rect.collidepoint(mouse_x, mouse_y):
                        self.sensor.current_config = (self.sensor.current_config + 1) % len(self.sensor.configs)
                    if self.button_ai.rect.collidepoint(mouse_x, mouse_y):
                        self.do_ai = True
                        self.do_return = False
                    if self.button_return.rect.collidepoint(mouse_x, mouse_y):
                        self.do_return = True
                        self.do_ai = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.drone.gyro_angle = self.drone.format_rotation(self.drone.gyro_angle - 1)
            if keys[pygame.K_RIGHT]:
                self.drone.gyro_angle = self.drone.format_rotation(self.drone.gyro_angle + 1)
            self.drone.angle = math.radians(self.drone.gyro_angle)

            if keys[pygame.K_SPACE]:
                self.drone.moving = not self.drone.moving

            self.autonomous_movement()
            self.return_home_movement()

            self.screen.fill(BLACK)
            self.cast_rays()
            self.sensor.draw(self.screen)
            self.calculate_risky_up_down()
            self.calculate_risky()
            self.drone.draw(self.screen)

            self.button_sensors.draw(self.screen)
            self.button_ai.draw(self.screen)
            self.button_return.draw(self.screen)

            pygame.draw.rect(self.screen, WHITE, (
                MINIMAP_OFFSET_X - 5, MINIMAP_OFFSET_Y - 5, self.map.width * MINIMAP_SCALE + 10,
                self.map.height * MINIMAP_SCALE + 10), 2)
            for y in range(20):
                for x in range(20):
                    color = BLACK
                    if Game.APARTMENT1_WALLS[y][x] == 1 or Game.APARTMENT2_WALLS[y][x] == 1:
                        color = BLUE if self.drone.current_layer == 1 else GREEN
                    if self.drone.current_layer == 1:
                        if (y, x) in self.drone.visited_positions_1:
                            color = RED
                    if self.drone.current_layer == 2:
                        if (y, x) in self.drone.visited_positions_2:
                            color = RED
                    if self.do_return:
                        if (y, x) == self.drone.current_point:
                            color = GRAY

                    pygame.draw.rect(self.screen, color, (
                        MINIMAP_OFFSET_X + x * MINIMAP_SCALE, MINIMAP_OFFSET_Y + y * MINIMAP_SCALE, MINIMAP_SCALE,
                        MINIMAP_SCALE))

            pygame.draw.rect(self.screen, WHITE, (
                MINIMAP_OFFSET_X - 105, MINIMAP_OFFSET_Y - 5, self.map.width * MINIMAP_SCALE + 10,
                self.map.height * MINIMAP_SCALE + 10), 2)
            for y in range(20):
                for x in range(20):
                    color = BLUE if self.drone.current_layer == 1 else GREEN
                    if Game.APARTMENT2_FLOOR[y][x] == 2:
                        color = BLACK
                    if (y, x) == self.drone.current_point:
                        color = RED
                    pygame.draw.rect(self.screen, color, (
                        MINIMAP_OFFSET_X - 100 + x * MINIMAP_SCALE, MINIMAP_OFFSET_Y + y * MINIMAP_SCALE, MINIMAP_SCALE,
                        MINIMAP_SCALE))

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()