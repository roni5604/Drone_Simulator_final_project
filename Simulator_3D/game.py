import pygame
import math
import random
from drone import Drone
from sensor import Sensor
from map import Map
from button import Button
from world_params import *

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("3D Drone Simulation")
        self.clock = pygame.time.Clock()
        self.running = True
        self.drone = Drone()
        self.sensor = Sensor(self.drone)
        self.map = Map()
        self.button_ai = Button('Self-Driver', SCREEN_WIDTH - 200, SCREEN_HEIGHT - 120, 190, 50)
        self.button_return = Button('Return Home', SCREEN_WIDTH - 200, SCREEN_HEIGHT - 190, 190, 50)
        self.button_sensors = Button('Switch Sensors', SCREEN_WIDTH - 200, SCREEN_HEIGHT - 50, 190, 50)
        self.do_ai = False
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
                    current_map = APARTMENT1_WALLS
                elif self.drone.current_layer == 2:
                    current_map = APARTMENT2_WALLS

                if current_map[map_y][map_x] == 1:
                    color = (0, 0, 255) if self.drone.current_layer == 1 else (0, 255, 0)
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
                    current_map = APARTMENT1_WALLS
                elif self.drone.current_layer == 2:
                    current_map = APARTMENT2_WALLS
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
            if self.drone.current_layer == 1 and APARTMENT2_FLOOR[map_y][map_x] == 1:
                if depth < 1:
                    self.screen.blit(self.drone.warning_light_img, (10, 80))
                    break
            if self.drone.current_layer == 2 and CEILING2_MAP[map_y][map_x] == 1:
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
            if self.drone.current_layer == 1 and APARTMENT1_FLOOR[map_y][map_x] == 1:
                if depth < 1:
                    self.screen.blit(self.drone.warning_light_img, (10, 80))
                    break
            if self.drone.current_layer == 2 and APARTMENT2_FLOOR[map_y][map_x] == 1:
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
                    self.drone.current_map = APARTMENT1_WALLS
                elif self.drone.current_layer == 2:
                    self.drone.current_map = APARTMENT2_WALLS

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
                if APARTMENT2_FLOOR[int(self.drone.y / self.map.scale)][int(self.drone.x / self.map.scale)] == 2 and random.random() < 0.5:
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
                if APARTMENT2_FLOOR[int(self.drone.y / self.map.scale)][int(self.drone.x / self.map.scale)] == 2 and random.random() < 0.5:
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
        elif pop_speed == -2:
            self.drone.z = 1.5
            self.drone.current_layer = 1
            self.drone.current_map = APARTMENT1_WALLS

        elif pop_speed == -3:
            self.drone.speed = 0
            if self.drone.z >= -10:
                self.drone.z -= 0.5
        elif pop_speed == -4:
            self.drone.z = 1.5
            self.drone.current_map = APARTMENT2_WALLS
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

            self.screen.fill((0, 0, 0))
            self.cast_rays()
            self.sensor.draw(self.screen)
            self.calculate_risky_up_down()
            self.calculate_risky()
            self.drone.draw(self.screen)

            self.button_sensors.draw(self.screen)
            self.button_ai.draw(self.screen)
            self.button_return.draw(self.screen)

            pygame.draw.rect(self.screen, (255, 255, 255), (
                MINIMAP_OFFSET_X - 5, MINIMAP_OFFSET_Y - 5, self.map.width * MINIMAP_SCALE + 10,
                self.map.height * MINIMAP_SCALE + 10), 2)
            for y in range(20):
                for x in range(20):
                    color = (0, 0, 0)
                    if APARTMENT1_WALLS[y][x] == 1 or APARTMENT2_WALLS[y][x] == 1:
                        color = (0, 0, 255) if self.drone.current_layer == 1 else (0, 255, 0)
                    if self.drone.current_layer == 1:
                        if (y, x) in self.drone.visited_positions_1:
                            color = (255, 0, 0)
                    if self.drone.current_layer == 2:
                        if (y, x) in self.drone.visited_positions_2:
                            color = (255, 0, 0)
                    if self.do_return:
                        if (y, x) == self.drone.current_point:
                            color = (128, 128, 128)

                    pygame.draw.rect(self.screen, color, (
                        MINIMAP_OFFSET_X + x * MINIMAP_SCALE, MINIMAP_OFFSET_Y + y * MINIMAP_SCALE, MINIMAP_SCALE,
                        MINIMAP_SCALE))

            pygame.draw.rect(self.screen, (255, 255, 255), (
                MINIMAP_OFFSET_X - 105, MINIMAP_OFFSET_Y - 5, self.map.width * MINIMAP_SCALE + 10,
                self.map.height * MINIMAP_SCALE + 10), 2)
            for y in range(20):
                for x in range(20):
                    color = (0, 0, 255) if self.drone.current_layer == 1 else (0, 255, 0)
                    if APARTMENT2_FLOOR[y][x] == 2:
                        color = (0, 0, 0)
                    if (y, x) == self.drone.current_point:
                        color = (255, 0, 0)
                    pygame.draw.rect(self.screen, color, (
                        MINIMAP_OFFSET_X - 100 + x * MINIMAP_SCALE, MINIMAP_OFFSET_Y + y * MINIMAP_SCALE, MINIMAP_SCALE,
                        MINIMAP_SCALE))

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()
