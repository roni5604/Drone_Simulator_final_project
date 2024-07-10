import pygame
import math
import random
from drone import Drone
from sensor import Sensor
from map import Map
from button import Button
from world_params import *
from battery import Battery

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BROWN = (101, 67, 33)
D_YELLOW = (204, 204, 0)

class Game:
    def __init__(self):  # Initialize the game
        pygame.init()  # Initialize pygame
        pygame.font.init()  # Initialize pygame font
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Set the screen size
        pygame.display.set_caption("3D Drone Simulation")  # Set the title of the window
        self.battery = Battery()
        self.clock = pygame.time.Clock()  # Initialize the clock
        self.running = True  # Set the game to running
        self.drone = Drone()  # Create the drone
        self.map = Map()  # Create the map
        self.button_ai = Button('Self-Driver', SCREEN_WIDTH - 950, SCREEN_HEIGHT - 55, 200,
                                50)  # Create the self-driving button
        self.button_return = Button('Return Home', SCREEN_WIDTH - 700, SCREEN_HEIGHT - 55, 200,
                                    50)  # Create the return home button
        self.button_sensors = Button('Switch Sensors', SCREEN_WIDTH - 200, SCREEN_HEIGHT - 55, 200,
                                     50)  # Create the switch sensors button
        self.button_charge = Button('Charge', SCREEN_WIDTH - 450, SCREEN_HEIGHT - 55, 200,
                                    50)  # Create the charge button
        self.do_ai = False  # Set the self-driving mode to False
        self.do_return = False  # Set the return home mode to False

    def cast_rays(self):
        """
        Simulates ray casting from the drone's perspective to create a 3D-like view.
        """
        current_map = []
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
                    color = BROWN if self.drone.current_layer == 1 else GRAY
                    wall_height = SCREEN_HEIGHT / (depth * 0.05)
                    ceiling_height = -SCREEN_HEIGHT / (depth * 0.05)  # Ceiling height
                    pygame.draw.rect(self.screen, color, (
                        ray * (SCREEN_WIDTH // 120), (SCREEN_HEIGHT / 2) - wall_height / 2, SCREEN_WIDTH // 120,
                        wall_height))
                    pygame.draw.rect(self.screen, color, (
                        ray * (SCREEN_WIDTH // 120), (SCREEN_HEIGHT / 2) - wall_height / 2 - ceiling_height,
                        SCREEN_WIDTH // 120, ceiling_height))
                    break

    def calculate_risky(self):
        """
        Determines risky directions based on the drone's sensor data.
        """
        sensor_angles = self.drone.sensors[self.drone.current_sensor]
        sensor_risky = {}
        for sensor_angle in sensor_angles:
            if sensor_angle.is_up_down == 1:
                self.calculate_risky_up_down(True)
            elif sensor_angle.is_up_down == 2:
                self.calculate_risky_up_down(False)
            else:
                angle = math.radians(self.drone.gyro_angle + sensor_angle.config)
                for depth in range(1, 50):
                    target_x = self.drone.x + math.cos(angle) * depth
                    target_y = self.drone.y + math.sin(angle) * depth
                    map_x = int(target_x / self.map.scale)
                    map_y = int(target_y / self.map.scale)
                    if self.drone.current_layer == 1:
                        current_map = APARTMENT1_WALLS
                    elif self.drone.current_layer == 2:
                        current_map = APARTMENT2_WALLS

                    if map_x < 0 or map_x > 20 or map_y > 20 or map_y < 0:
                        break
                    if current_map[map_y][map_x] == 1:
                        print(f'{sensor_angle}:  {depth}')
                        if depth < self.drone.dangerous_distance:
                            sensor_angle.distance = depth
                            sensor_risky[sensor_angle] = depth
                            self.screen.blit(self.drone.warning_light_img, (10, 80))
                        break

        return sensor_risky

    def calculate_risky_up_down(self, is_up):
        """
        Determines risky directions based on the drone's sensor data.
        """
        if is_up:
            angle_up = math.radians(self.drone.angle + 90)
            for depth in range(1, 100):
                target_x = self.drone.x + math.cos(angle_up) * depth
                target_y = self.drone.y + math.sin(angle_up) * depth
                map_x = int(target_x / self.map.scale)
                map_y = int(target_y / self.map.scale)
                if map_x < 0 or map_x > 20 or map_y > 20 or map_y < 0:
                    break
                if self.drone.current_layer == 1 and APARTMENT2_FLOOR[map_y][map_x] == 1:
                    print(f'up:  {depth}')
                    if depth < 1:
                        self.screen.blit(self.drone.warning_light_img, (10, 80))
                        break
                if self.drone.current_layer == 2 and CEILING2_MAP[map_y][map_x] == 1:
                    if depth < 1:
                        self.screen.blit(self.drone.warning_light_img, (10, 80))
                        break
        else:
            angle_down = math.radians(self.drone.angle - 90)
            for depth in range(1, 50):
                target_x = self.drone.x + math.cos(angle_down) * depth
                target_y = self.drone.y + math.sin(angle_down) * depth
                map_x = int(target_x / self.map.scale)
                map_y = int(target_y / self.map.scale)
                if map_x < 0 or map_x > 20 or map_y > 20 or map_y < 0:
                    break

                if self.drone.current_layer == 1 and APARTMENT1_FLOOR[map_y][map_x] == 1:
                    print(f'down:  {depth}')
                    if depth < 1:
                        self.screen.blit(self.drone.warning_light_img, (10, 80))
                        break
                if self.drone.current_layer == 2 and APARTMENT2_FLOOR[map_y][map_x] == 1:
                    if depth < 1:
                        self.screen.blit(self.drone.warning_light_img, (10, 80))
                        break

    def autonomous_movement(self):
        """
        Controls the autonomous movement of the drone.
        """
        if not self.do_ai:
            return
        if not self.drone.move_floor:
            sensor_readings = self.calculate_risky()
            if sensor_readings:
                self.drone.moving = False
                self.drone.speed_down()
                self.drone.return_home_speed.append(self.drone.speed)
                min_sensor_dist = min(sensor_readings.values())
                degree = 0
                for sensor_angle in sensor_readings:
                    if sensor_readings[sensor_angle] == min_sensor_dist:
                        degree = sensor_angle.config
                if degree < 0:  # Closer to left wall

                    self.drone.gyro_angle = self.drone.format_rotation(self.drone.gyro_angle + 1)  # Rotate right
                else:  # Closer to right wall
                    self.drone.gyro_angle = self.drone.format_rotation(self.drone.gyro_angle - 1)  # Rotate left

            else:
                self.drone.moving = True

            if self.drone.moving:
                self.drone.speed_up()
                if self.drone.timing_change == 50:
                    self.drone.right_left *= 1
                    self.drone.timing_change = 0
                self.drone.gyro_angle = self.drone.format_rotation(self.drone.gyro_angle +0.5 * self.drone.right_left)
                self.drone.return_home_speed.append(self.drone.speed)
                self.drone.timing_change += 1
                self.drone.angle = math.radians(self.drone.gyro_angle)
                new_x = self.drone.x + math.cos(self.drone.angle) * self.drone.speed
                new_y = self.drone.y + math.sin(self.drone.angle) * self.drone.speed
                if self.drone.current_layer == 1:
                    self.drone.current_map = APARTMENT1_WALLS
                elif self.drone.current_layer == 2:
                    self.drone.current_map = APARTMENT2_WALLS

                if self.drone.current_map[int(new_y / self.map.scale)][int(new_x / self.map.scale)] in [
                    0]:  # Allow passage through holes
                    self.drone.x, self.drone.y = new_x, new_y
                    self.drone.current_point = (int(self.drone.y / self.map.scale), int(self.drone.x / self.map.scale))
                    if self.drone.current_layer == 1:
                        self.drone.update_points(1)
                        self.drone.visited_positions_1.add(
                            (int(self.drone.y / self.map.scale), int(self.drone.x / self.map.scale)))
                    elif self.drone.current_layer == 2:
                        self.drone.update_points(2)
                        self.drone.visited_positions_2.add(
                            (int(self.drone.y / self.map.scale), int(self.drone.x / self.map.scale)))
        if self.drone.move_floor or random.random() < 0.006:
            if self.drone.current_layer == 1:
                if APARTMENT2_FLOOR[int(self.drone.y / self.map.scale)][
                    int(self.drone.x / self.map.scale)] == 2 and random.random() < 0.5:
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
                        self.drone.update_points(2)
                        self.drone.move_floor = False
                        self.drone.moving = True

            elif self.drone.current_layer == 2:
                if APARTMENT2_FLOOR[int(self.drone.y / self.map.scale)][
                    int(self.drone.x / self.map.scale)] == 2 and random.random() < 0.5:
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
                        self.drone.update_points(1)
                        self.drone.move_floor = False
                        self.drone.moving = True
        if self.drone.gyro_angle >= 180:
            self.drone.return_home_angle.append(self.drone.gyro_angle - 180)
        else:
            self.drone.return_home_angle.append(self.drone.gyro_angle + 180)

    def return_home_movement(self):
        """
        Controls the drone's movement to return to its starting point.
        """
        if not self.do_return:
            return
        if not self.drone.return_home_angle or not self.drone.return_home_speed:
            if self.drone.spin_back > 0:
                self.drone.speed = 0
                self.drone.gyro_angle = self.drone.format_rotation(self.drone.gyro_angle + 2)
                self.drone.spin_back -= 2
            else:
                self.drone.spin_back = 0
                self.drone.moving = False
                self.drone.return_home_speed = []
                self.drone.return_home_angle = []
                self.button_return.color = WHITE
                self.do_return = False
            return

        while self.drone.spin_back < 180:
            self.drone.speed = 0
            self.drone.gyro_angle = self.drone.format_rotation(self.drone.gyro_angle + 2)
            self.drone.spin_back += 2
            return
        self.drone.gyro_angle = self.drone.return_home_angle.pop()
        pop_speed = self.drone.return_home_speed.pop()
        if pop_speed == 0:
            self.drone.speed = 0
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
        else:
            self.drone.speed = pop_speed
            new_x = self.drone.x + math.cos(self.drone.angle) * self.drone.speed
            new_y = self.drone.y + math.sin(self.drone.angle) * self.drone.speed
            self.drone.x, self.drone.y = new_x, new_y
            self.drone.current_point = (int(self.drone.y / self.map.scale), int(self.drone.x / self.map.scale))

    def draw_map(self):
        """
        Draw the map from a top-down view.
        """
        for y in range(len(APARTMENT1_WALLS)):
            for x in range(len(APARTMENT1_WALLS[y])):
                if self.drone.current_layer == 1 and APARTMENT1_WALLS[y][x] == 1:
                    pygame.draw.rect(self.screen, BROWN,
                                     (x * self.map.scale, y * self.map.scale, self.map.scale, self.map.scale))
                elif self.drone.current_layer == 2 and APARTMENT2_WALLS[y][x] == 1:
                    pygame.draw.rect(self.screen, GRAY,
                                     (x * self.map.scale, y * self.map.scale, self.map.scale, self.map.scale))

    def run(self):
        """
        Main game loop for the drone simulation.

        This function handles the main operations of the drone simulation, including event handling, updating the drone's
        state, rendering the display, and managing the minimap. The loop continues running until the user closes the
        window.

        The function performs the following steps:
        1. Set up minimap scaling and positioning.
        2. Enter the main loop that runs while the simulation is active.
        3. Handle user events such as quitting, mouse button clicks, and key presses.
        4. Update the drone's movement and angle based on user input and autonomous functions.
        5. Render the screen, including the drone's view, sensors, and minimap.
        6. Update the display and control the frame rate.

        Variables:
        - MINIMAP_SCALE: Scaling factor for the minimap.
        - MINIMAP_OFFSET_X: Horizontal offset for the minimap on the screen.
        - MINIMAP_OFFSET_Y: Vertical offset for the minimap on the screen.

        Returns:
        None
        """

        MINIMAP_SCALE = 10  # Increase the scaling factor to make the minimap larger
        MINIMAP_OFFSET_X = SCREEN_WIDTH - 220  # Adjust the offset to accommodate the new scale
        MINIMAP_OFFSET_Y = 20

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if self.button_sensors.rect.collidepoint(mouse_x, mouse_y):
                        self.drone.current_sensor= (self.drone.current_sensor + 1) % len(self.drone.sensors)
                        self.button_sensors.color = GRAY
                    if self.button_ai.rect.collidepoint(mouse_x, mouse_y):
                        self.do_ai = True
                        self.do_return = False
                        self.button_ai.color = GRAY
                        self.button_return.color = WHITE
                        self.button_sensors.color = WHITE

                    if self.button_return.rect.collidepoint(mouse_x, mouse_y):
                        self.do_return = True
                        self.do_ai = False
                        self.button_ai.color = WHITE
                        self.button_return.color = GRAY
                        self.button_sensors.color = WHITE
                    if self.button_charge.rect.collidepoint(mouse_x, mouse_y):
                        self.battery.is_half = False
                        self.battery.charge = self.battery.max_charge

            self.drone.angle = math.radians(self.drone.gyro_angle)
            if self.battery.drain():
                self.do_return = True
                self.do_ai = False
                self.button_ai.color = WHITE
                self.button_return.color = GRAY

            self.autonomous_movement()
            self.return_home_movement()

            self.screen.fill((0, 0, 0))
            self.cast_rays()

            self.calculate_risky()
            self.drone.draw_sensors(self.screen)
            self.drone.draw(self.screen)

            self.button_sensors.draw(self.screen)
            self.button_ai.draw(self.screen)
            self.button_return.draw(self.screen)
            self.button_charge.draw(self.screen)
            # Draw the battery
            self.battery.draw(self.screen)

            # Draw the main minimap
            pygame.draw.rect(self.screen, (255, 255, 255), (
                MINIMAP_OFFSET_X - 5, MINIMAP_OFFSET_Y - 5, 20 * MINIMAP_SCALE + 10, 20 * MINIMAP_SCALE + 10), 2)
            for y in range(20):
                for x in range(20):
                    color = (0, 0, 0)
                    if self.drone.current_layer == 1:
                        if APARTMENT1_WALLS[y][x] == 1:
                            color = BROWN
                        if (y, x) in self.drone.visited_positions_1:
                            color = RED
                        if (y, x) in self.drone.scaled_points_1:
                            color = GREEN
                    else:
                        if APARTMENT2_WALLS[y][x] == 1:
                            color = GRAY
                        if (y, x) in self.drone.visited_positions_2:
                            color = RED
                        if (y, x) in self.drone.scaled_points_2:
                            color = GREEN
                    if self.do_return:
                        if (y, x) == self.drone.current_point:
                            color = BLUE

                    pygame.draw.rect(self.screen, color, (
                        MINIMAP_OFFSET_X + x * MINIMAP_SCALE, MINIMAP_OFFSET_Y + y * MINIMAP_SCALE, MINIMAP_SCALE,
                        MINIMAP_SCALE))
                    # Draw a small white point for the drone's current position
                    if (y, x) == self.drone.current_point:
                        center_x = MINIMAP_OFFSET_X + x * MINIMAP_SCALE + MINIMAP_SCALE // 2
                        center_y = MINIMAP_OFFSET_Y + y * MINIMAP_SCALE + MINIMAP_SCALE // 2
                        pygame.draw.circle(self.screen, BLACK, (center_x, center_y), MINIMAP_SCALE // 4)

            # Keep the secondary minimap unchanged
            MINIMAP_SCALE_SECONDARY = 8
            MINIMAP_OFFSET_X_SECONDARY = SCREEN_WIDTH - 400  # Adjust the offset as needed
            MINIMAP_OFFSET_Y_SECONDARY = 20

            # Draw the secondary minimap
            pygame.draw.rect(self.screen, (255, 255, 255), (
                MINIMAP_OFFSET_X_SECONDARY - 5, MINIMAP_OFFSET_Y_SECONDARY - 5, 20 * MINIMAP_SCALE_SECONDARY + 10,
                20 * MINIMAP_SCALE_SECONDARY + 10), 2)
            for y in range(20):
                for x in range(20):
                    color = BROWN if self.drone.current_layer == 1 else GRAY
                    if APARTMENT2_FLOOR[y][x] == 2:
                        color = BLACK
                    pygame.draw.rect(self.screen, color, (
                        MINIMAP_OFFSET_X_SECONDARY + x * MINIMAP_SCALE_SECONDARY,
                        MINIMAP_OFFSET_Y_SECONDARY + y * MINIMAP_SCALE_SECONDARY, MINIMAP_SCALE_SECONDARY,
                        MINIMAP_SCALE_SECONDARY))
                    # Draw a small white point for the drone's current position
                    if (y, x) == self.drone.current_point:
                        center_x = MINIMAP_OFFSET_X_SECONDARY + x * MINIMAP_SCALE_SECONDARY + MINIMAP_SCALE_SECONDARY // 2
                        center_y = MINIMAP_OFFSET_Y_SECONDARY + y * MINIMAP_SCALE_SECONDARY + MINIMAP_SCALE_SECONDARY // 2
                        pygame.draw.circle(self.screen, D_YELLOW, (center_x, center_y), MINIMAP_SCALE_SECONDARY // 6)

            # Draw sensor lines on the secondary minimap
            self.drone.draw_sensor_lines(self.screen, MINIMAP_OFFSET_X_SECONDARY , MINIMAP_OFFSET_Y_SECONDARY,
                                         MINIMAP_SCALE_SECONDARY)
            self.drone.draw_sensor_lines(self.screen, MINIMAP_OFFSET_X, MINIMAP_OFFSET_Y,
                                         MINIMAP_SCALE)

            pygame.display.flip()
            self.clock.tick(30)
            self.button_sensors.color = WHITE

        pygame.quit()
