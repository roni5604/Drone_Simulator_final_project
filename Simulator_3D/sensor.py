import pygame
import math
from world_params import *

class Sensor:
    """
    Initializes the Sensor class with a reference to the drone and sensor configurations.

    This constructor sets up the sensor configurations, including angles for different sensor setups and up/down sensors.

    Parameters:
    - drone (Drone): The drone instance to which the sensors are attached.

    Attributes:
    - drone (Drone): Reference to the drone instance.
    - configs (list of list of int): A list of sensor angle configurations.
    - up_down_sensors (list of int): Angles for up and down sensors.
    - current_config (int): Index of the current sensor configuration in use.
    
    Returns:
    None
    """
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
        """
        Draws the sensor lines on the screen based on the current sensor configuration and the drone's position.

        This function visualizes the sensors by drawing lines from the drone's position in the directions specified by the
        sensor angles. It checks for obstacles and stops the line when an obstacle is detected.

        Parameters:
        - screen (pygame.Surface): The Pygame surface to draw the sensors on.

        Returns:
        None
        """
        sensor_angles = self.configs[self.current_config]
        for sensor_angle in sensor_angles:
            angle = math.radians(self.drone.gyro_angle + sensor_angle)
            for depth in range(1, 1000):
                target_x = self.drone.x + math.cos(angle) * depth
                target_y = self.drone.y + math.sin(angle) * depth
                map_x = int(target_x / 64)
                map_y = int(target_y / 64)
                if self.drone.current_layer == 1:
                    current_map = APARTMENT1_WALLS
                elif self.drone.current_layer == 2:
                    current_map = APARTMENT2_WALLS
                if current_map[map_y][map_x] == 1:
                    pygame.draw.line(screen, (255, 0, 0), (SCREEN_WIDTH // 2,
                                                   SCREEN_HEIGHT // 2 + int(self.drone.z * 20)),
                                     (SCREEN_WIDTH // 2 + math.cos(angle) * depth,
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
            if self.drone.current_layer == 1 and APARTMENT2_FLOOR[map_y][map_x] == 1:
                pygame.draw.line(screen, (0, 255, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                 (SCREEN_WIDTH // 2 + math.cos(angle_up) * depth,
                                  SCREEN_HEIGHT // 2 + math.sin(angle_up) * depth), 1)
                break
            if self.drone.current_layer == 2 and CEILING2_MAP[map_y][map_x] == 1:
                pygame.draw.line(screen, (0, 255, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                 (SCREEN_WIDTH // 2 + math.cos(angle_up) * depth,
                                  SCREEN_HEIGHT // 2 + math.sin(angle_up) * depth), 1)
                break
        angle_down = math.radians(self.drone.angle + self.up_down_sensors[0])
        for depth in range(1, 1000):
            target_x = self.drone.x + math.cos(angle_down) * depth
            target_y = self.drone.y + math.sin(angle_down) * depth
            map_x = int(target_x / 64)
            map_y = int(target_y / 64)
            if self.drone.current_layer == 1 and APARTMENT1_FLOOR[map_y][map_x] == 1:
                pygame.draw.line(screen, (0, 255, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                     (SCREEN_WIDTH // 2 + math.cos(angle_down) * depth,
                                      SCREEN_HEIGHT // 2 + math.sin(angle_down) * depth), 1)
                break
            if self.drone.current_layer == 2 and APARTMENT2_FLOOR[map_y][map_x] == 1:
                pygame.draw.line(screen, (0, 255, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                 (SCREEN_WIDTH // 2 + math.cos(angle_down) * depth,
                                  SCREEN_HEIGHT // 2 + math.sin(angle_down) * depth), 1)
                break
