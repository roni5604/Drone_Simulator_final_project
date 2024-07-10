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

    def __init__(self, confing, is_up_down=0):
        self.font = pygame.font.SysFont(None, 24)  # Initialize font
        self.is_up_down = is_up_down
        self.config = confing
        self.distance = 0


    def draw(self, drone, screen):
        """
        Draws the sensor lines on the screen based on the current sensor configuration and the drone's position.

        This function visualizes the sensors by drawing lines from the drone's position in the directions specified by the
        sensor angles. It checks for obstacles and stops the line when an obstacle is detected.

        Parameters:
        - screen (pygame.Surface): The Pygame surface to draw the sensors on.

        Returns:
        None
        """
        if self.is_up_down == 0:
            angle = math.radians(drone.gyro_angle + self.config + 90)
            for depth in range(1, 800):
                target_x = drone.x + math.cos(angle) * depth
                target_y = drone.y + math.sin(angle) * depth
                map_x = int(target_x / 64)
                map_y = int(target_y / 64)
                if drone.current_layer == 1:
                    current_map = APARTMENT1_WALLS
                elif drone.current_layer == 2:
                    current_map = APARTMENT2_WALLS
                if current_map[map_y][map_x] == 1:
                    pygame.draw.line(screen, (255, 0, 0), (SCREEN_WIDTH // 2,
                                                           SCREEN_HEIGHT // 2 + int(drone.z * 20)),
                                     (SCREEN_WIDTH // 2 + math.cos(angle) * depth,
                                      SCREEN_HEIGHT // 2 + math.sin(angle) * depth),
                                     1)
                    if depth <= 100:
                        # Draw the circle at the intersection point
                        pygame.draw.circle(screen, (255, 255, 255), (int(SCREEN_WIDTH // 2 + math.cos(angle) * depth),
                                                           int(SCREEN_HEIGHT // 2 + math.sin(angle) * depth)), 5)
                        text = self.font.render(str(depth), True, (255, 255, 255))
                        screen.blit(text, (SCREEN_WIDTH // 2 + math.cos(angle) * depth + 10,
                                           SCREEN_HEIGHT // 2 + math.sin(angle) * depth))
                    break
            return
        if self.is_up_down == 1:
            # Draw up and down sensors
            angle_up = math.radians(drone.angle + self.config)
            for depth in range(1, 800):
                target_x = drone.x + math.cos(angle_up) * depth
                target_y = drone.y + math.sin(angle_up) * depth
                map_x = int(target_x / 64)
                map_y = int(target_y / 64)
                if drone.current_layer == 1 and APARTMENT2_FLOOR[map_y][map_x] == 1:
                    self.distance = depth
                    pygame.draw.line(screen, (0, 255, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                     (SCREEN_WIDTH // 2 + math.cos(angle_up) * depth,
                                      SCREEN_HEIGHT // 2 + math.sin(angle_up) * depth), 1)
                    break
                if drone.current_layer == 2 and CEILING2_MAP[map_y][map_x] == 1:
                    self.distance = depth
                    pygame.draw.line(screen, (0, 255, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                     (SCREEN_WIDTH // 2 + math.cos(angle_up) * depth,
                                      SCREEN_HEIGHT // 2 + math.sin(angle_up) * depth), 1)
                    if depth <= drone.dangerous_distance:

                        text = self.font.render(str(depth), True, (255, 255, 255))
                        screen.blit(text, (SCREEN_WIDTH // 2 + math.cos(angle_up) * depth,
                                           SCREEN_HEIGHT // 2 + math.sin(angle_up) * depth))
                    break
            return
        if not self.is_up_down == 2:
            angle_down = math.radians(drone.angle + self.config)
            for depth in range(1, 800):
                target_x = drone.x + math.cos(angle_down) * depth
                target_y = drone.y + math.sin(angle_down) * depth
                map_x = int(target_x / 64)
                map_y = int(target_y / 64)
                if drone.current_layer == 1 and APARTMENT1_FLOOR[map_y][map_x] == 1:
                    self.distance = depth
                    pygame.draw.line(screen, (0, 255, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                     (SCREEN_WIDTH // 2 + math.cos(angle_down) * depth,
                                      SCREEN_HEIGHT // 2 + math.sin(angle_down) * depth), 1)
                    break
                if drone.current_layer == 2 and APARTMENT2_FLOOR[map_y][map_x] == 1:
                    self.distance = depth
                    pygame.draw.line(screen, (0, 255, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                     (SCREEN_WIDTH // 2 + math.cos(angle_down) * depth,
                                      SCREEN_HEIGHT // 2 + math.sin(angle_down) * depth), 1)
                    if depth <= drone.dangerous_distance:

                        # Draw the distance text
                        text = self.font.render(str(depth), True, (255, 255, 255))
                        screen.blit(text, (SCREEN_WIDTH // 2 + math.cos(angle_down) * depth,
                                           SCREEN_HEIGHT // 2 + math.sin(angle_down) * depth))
                    break
            return
