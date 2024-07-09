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
