import pygame
from world_params import SCREEN_WIDTH, SCREEN_HEIGHT, DRONE_PICTURE, WARNING_PICTURE


class Drone:
    def __init__(self):
        self.image = pygame.image.load(DRONE_PICTURE)
        self.image = pygame.transform.scale(self.image, (300, 300))  # Scale up the drone image
        self.warning_light_img = pygame.image.load(WARNING_PICTURE)
        self.warning_light_img = pygame.transform.scale(self.warning_light_img, (64, 64))  # Scale warning light image
        self.x = 64 * 1.5
        self.y = 64 * 1.5
        self.z = 1.5
        self.angle = 0
        self.gyro_angle = 0
        self.pitch = 0
        self.speed = 2
        self.moving = False
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
        """
    Formats the rotation value to ensure it is within the range of 0 to 359 degrees.

    This function takes an angle in degrees and adjusts it to ensure it falls within the standard 360-degree circle.
    If the angle is negative, it adjusts it to the corresponding positive angle.

    Parameters:
    - rotation_value (float): The rotation angle in degrees.

    Returns:
    - float: The formatted rotation angle within the range [0, 359].
    """
        rotation_value %= 360
        if rotation_value < 0:
            rotation_value = 360 + rotation_value
        return rotation_value

    def rotate_image(self, angle):
        """
    Rotates the drone's image to the specified angle and returns the rotated image and its new rectangle.

    This function uses the Pygame library to rotate the drone's image by a specified angle. It also adjusts the
    rectangle of the rotated image to keep it centered on the screen, accounting for the drone's vertical position.

    Parameters:
    - angle (float): The angle in degrees to rotate the image.

    Returns:
    - tuple: A tuple containing the rotated image (pygame.Surface) and its new rectangle (pygame.Rect).
    """
        rotated_image = pygame.transform.rotozoom(self.image, -angle, 1)
        rotated_rect = rotated_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(self.z * 20)))
        return rotated_image, rotated_rect

    def draw(self, screen):
        """
    Draws the drone on the screen.

    This function rotates the drone's image based on its current gyro angle and blits the rotated image onto
    the provided screen at the appropriate location.

    Parameters:
    - screen (pygame.Surface): The Pygame surface to draw the drone on.

    Returns:
    None
    """
        rotated_drone, rotated_rect = self.rotate_image(self.gyro_angle)
        screen.blit(rotated_drone, rotated_rect.topleft)
