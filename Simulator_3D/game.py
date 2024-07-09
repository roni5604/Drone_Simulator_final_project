import pygame
import math
import random
from drone import Drone
from sensor import Sensor
from map import Map
from button import Button
from world_params import *

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BROWN = (101, 67, 33)

class Game:
    def __init__(self): # Initialize the game
        pygame.init() # Initialize pygame
        pygame.font.init() # Initialize pygame font
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Set the screen size
        pygame.display.set_caption("3D Drone Simulation") # Set the title of the window
        self.clock = pygame.time.Clock() # Initialize the clock
        self.running = True # Set the game to running
        self.drone = Drone() # Create the drone
        self.sensor = Sensor(self.drone) # Create the sensor
        self.map = Map() # Create the map
        self.button_ai = Button('Self-Driver', SCREEN_WIDTH - 200, SCREEN_HEIGHT - 120, 190, 50) # Create the
        # self-driving button
        self.button_return = Button('Return Home', SCREEN_WIDTH - 200, SCREEN_HEIGHT - 190, 190, 50) # Create the
        # return home button
        self.button_sensors = Button('Switch Sensors', SCREEN_WIDTH - 200, SCREEN_HEIGHT - 50, 190, 50) # Create the
        # switch sensors button
        self.do_ai = False # Set the self-driving mode to False
        self.do_return = False # Set the return home mode to False


    def cast_rays(self):
        """
        Simulates ray casting from the drone's perspective to create a 3D-like view.

        This function casts 120 rays in a fan shape starting from the drone's current angle minus 30 degrees to the drone's
        current angle plus 30 degrees. Each ray is incremented by 1 degree. For each ray, it calculates the intersection
        point with the walls in the current layer of the map. If a wall is hit, it calculates the height of the wall and
        the ceiling based on the distance and draws them on the screen.

        The function performs the following steps:
        1. Initialize the starting angle for the field of view.
        2. Loop through each ray and increment the angle by 1 degree.
        3. For each depth (distance from the drone), calculate the target coordinates.
        4. Convert the target coordinates to map coordinates.
        5. Check which layer the drone is currently on and set the corresponding map.
        6. Check if the ray intersects a wall at the current depth.
        7. If a wall is hit, calculate the height of the wall and ceiling based on the depth.
        8. Draw the wall and ceiling on the screen with the appropriate color.
        9. Break the depth loop when a wall is hit to move to the next ray.

        Variables:
        - ray_angle: The current angle of the ray being cast.
        - target_x: The x-coordinate of the point where the ray hits.
        - target_y: The y-coordinate of the point where the ray hits.
        - map_x: The x-coordinate in the map corresponding to the target_x.
        - map_y: The y-coordinate in the map corresponding to the target_y.
        - current_map: The map layer the drone is currently on.
        - color: The color of the wall to be drawn (brown for layer 1, gray for layer 2).
        - wall_height: The height of the wall to be drawn, inversely proportional to the depth.
        - ceiling_height: The height of the ceiling to be drawn, inversely proportional to the depth.

        Returns:
        None
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
                        ray * (SCREEN_WIDTH // 120), (SCREEN_HEIGHT / 2) - wall_height / 2, SCREEN_WIDTH // 120, wall_height))
                    pygame.draw.rect(self.screen, color, (
                        ray * (SCREEN_WIDTH // 120), (SCREEN_HEIGHT / 2) - wall_height / 2 - ceiling_height,
                        SCREEN_WIDTH // 120, ceiling_height))
                    break

    def calculate_risky(self):
        """
        Determines risky directions based on the drone's sensor data.

        This function calculates the risk of collision in different directions based on the drone's sensor configuration.
        It checks the distance from the drone to obstacles (walls) in the map. If an obstacle is detected within a
        dangerous distance, the function marks that direction as risky.

        The function performs the following steps:
        1. Retrieve the current sensor configuration angles.
        2. Loop through each sensor angle.
        3. Convert the sensor angle to radians and add it to the drone's current gyro angle.
        4. For each depth (distance from the drone), calculate the target coordinates.
        5. Convert the target coordinates to map coordinates.
        6. Check which layer the drone is currently on and set the corresponding map.
        7. Check if the sensor ray intersects a wall at the current depth.
        8. If a wall is hit within the dangerous distance, mark the direction as risky and display a warning light.
        9. Break the depth loop when a wall is hit to move to the next sensor angle.

        Variables:
        - sensor_angles: List of angles from the current sensor configuration.
        - sensor_risky: Dictionary to store risky directions and their corresponding depths.
        - angle: The current angle of the sensor ray being cast.
        - target_x: The x-coordinate of the point where the sensor ray hits.
        - target_y: The y-coordinate of the point where the sensor ray hits.
        - map_x: The x-coordinate in the map corresponding to the target_x.
        - map_y: The y-coordinate in the map corresponding to the target_y.
        - current_map: The map layer the drone is currently on.

        Returns:
        - sensor_risky: Dictionary with sensor angles as keys and depths as values for risky directions.
        """
        sensor_angles = self.sensor.configs[self.sensor.current_config]
        sensor_risky = {}
        for sensor_angle in sensor_angles:
            angle = math.radians(self.drone.gyro_angle + sensor_angle)
            for depth in range(1, 200):
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
        """
        Determines risky directions based on the drone's sensor data.

        This function calculates the risk of collision in different directions based on the drone's sensor configuration.
        It checks the distance from the drone to obstacles (walls) in the map. If an obstacle is detected within a
        dangerous distance, the function marks that direction as risky.

        The function performs the following steps:
        1. Retrieve the current sensor configuration angles.
        2. Loop through each sensor angle.
        3. Convert the sensor angle to radians and add it to the drone's current gyro angle.
        4. For each depth (distance from the drone), calculate the target coordinates.
        5. Convert the target coordinates to map coordinates.
        6. Check which layer the drone is currently on and set the corresponding map.
        7. Check if the sensor ray intersects a wall at the current depth.
        8. If a wall is hit within the dangerous distance, mark the direction as risky and display a warning light.
        9. Break the depth loop when a wall is hit to move to the next sensor angle.

        Variables:
        - sensor_angles: List of angles from the current sensor configuration.
        - sensor_risky: Dictionary to store risky directions and their corresponding depths.
        - angle: The current angle of the sensor ray being cast.
        - target_x: The x-coordinate of the point where the sensor ray hits.
        - target_y: The y-coordinate of the point where the sensor ray hits.
        - map_x: The x-coordinate in the map corresponding to the target_x.
        - map_y: The y-coordinate in the map corresponding to the target_y.
        - current_map: The map layer the drone is currently on.

        Returns:
        - sensor_risky: Dictionary with sensor angles as keys and depths as values for risky directions.
        """
        # Calculate risk upwards
        angle_up = math.radians(self.drone.angle + self.sensor.up_down_sensors[0])
        for depth in range(1, 200):
            target_x = self.drone.x + math.cos(angle_up) * depth
            target_y = self.drone.y + math.sin(angle_up) * depth
            map_x = int(target_x / self.map.scale)
            map_y = int(target_y / self.map.scale)
            if map_x < 0 or map_x < 20 or map_y > 20 or map_y < 0:
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
        for depth in range(1, 200):
            target_x = self.drone.x + math.cos(angle_down) * depth
            target_y = self.drone.y + math.sin(angle_down) * depth
            map_x = int(target_x / self.map.scale)
            map_y = int(target_y / self.map.scale)
            if map_x < 0 or map_x < 20 or map_y > 20 or map_y < 0:
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
        """
        Controls the autonomous movement of the drone.

        This function determines and executes the movement of the drone based on sensor readings and predefined behaviors.
        It adjusts the drone's direction and speed to avoid obstacles and navigates between different layers of the environment.

        The function performs the following steps:
        1. Checks if autonomous movement is enabled.
        2. If the drone is not moving between floors, calculates risky directions using sensor readings.
        3. Adjusts the drone's movement based on the sensor readings to avoid obstacles.
        4. Controls the drone's movement in the current layer, including speed and direction adjustments.
        5. Handles autonomous movement between floors, adjusting the drone's vertical position and layer.

        Variables:
        - sensor_readings: Dictionary of sensor angles and corresponding depths indicating obstacles.
        - min_sensor_dist: Minimum distance to an obstacle detected by the sensors.
        - degree: Angle of the sensor detecting the closest obstacle.
        - new_x: The new x-coordinate of the drone after moving.
        - new_y: The new y-coordinate of the drone after moving.

        Returns:
        None
        """
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
                        self.drone.update_points(1)
                        self.drone.visited_positions_1.add((int(self.drone.y / self.map.scale), int(self.drone.x / self.map.scale)))
                    elif self.drone.current_layer == 2:
                        self.drone.update_points(2)
                        self.drone.visited_positions_2.add((int(self.drone.y / self.map.scale), int(self.drone.x / self.map.scale)))
        # Autonomous height movement
        if self.drone.move_floor or random.random() < 0.003:
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
                        self.drone.update_points(2)
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

        This function handles the autonomous return of the drone to its starting point based on previously recorded
        angles and speeds. It adjusts the drone's direction, speed, and height to navigate back to its home position.

        The function performs the following steps:
        1. Checks if the return-to-home mode is enabled.
        2. If there are no recorded return angles or speeds, stops the drone and exits return-to-home mode.
        3. Rotates the drone back to its original orientation if it has spun less than 180 degrees.
        4. Adjusts the drone's movement based on the recorded return speed and angle.

        Variables:
        - pop_speed: The last recorded speed from the return home speed list.
        - new_x: The new x-coordinate of the drone after moving.
        - new_y: The new y-coordinate of the drone after moving.

        Returns:
        None
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

            self.drone.angle = math.radians(self.drone.gyro_angle)

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
                        color = BROWN if self.drone.current_layer == 1 else GRAY
                    if self.drone.current_layer == 1:
                        if (y, x) in self.drone.visited_positions_1:
                            color = RED
                        if (y, x) in self.drone.scaled_points_1:
                            color = GREEN
                    if self.drone.current_layer == 2:
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

            pygame.draw.rect(self.screen, (255, 255, 255), (
                MINIMAP_OFFSET_X - 105, MINIMAP_OFFSET_Y - 5, self.map.width * MINIMAP_SCALE + 10,
                self.map.height * MINIMAP_SCALE + 10), 2)
            for y in range(20):
                for x in range(20):
                    color = BROWN if self.drone.current_layer == 1 else GRAY
                    if APARTMENT2_FLOOR[y][x] == 2:
                        color = BLACK
                    if (y, x) == self.drone.current_point:
                        color = RED
                    pygame.draw.rect(self.screen, color, (
                        MINIMAP_OFFSET_X - 100 + x * MINIMAP_SCALE, MINIMAP_OFFSET_Y + y * MINIMAP_SCALE, MINIMAP_SCALE,
                        MINIMAP_SCALE))

            pygame.display.flip()
            self.clock.tick(30)
            self.button_sensors.color = WHITE

        pygame.quit()
