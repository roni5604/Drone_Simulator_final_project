import pygame

from CPU import CPU
from Lidar import Lidar
from Point import Point
from Tools import Tools
from WorldParams import WorldParams


class Drone:
    def __init__(self, real_map):
        self.real_map = real_map
        self.start_point = real_map.drone_start_point
        self.point_from_start = Point()
        self.sensor_optical_flow = Point()
        self.lidars = []

        self.speed = 0.2
        self.rotation = 0
        self.gyro_rotation = self.rotation

        self.cpu = CPU(100, "Drone")  # 10Hz CPU
        self.drone_img_path = "Maps/drone_3_pixels.png"
        self.mImage = None

    def play(self):
        """Start the drone's CPU."""
        self.cpu.play()

    def stop(self):
        """Stop the drone's CPU."""
        self.cpu.stop()

    def add_lidar(self, degrees):
        """Add a lidar sensor to the drone at a specified degree."""
        lidar = Lidar(self, degrees)
        self.lidars.append(lidar)
        self.cpu.add_function(lambda x: lidar.get_simulation_distance(x))

    def get_point_on_map(self):
        x = self.start_point.x + self.point_from_start.x
        y = self.start_point.y + self.point_from_start.y
        return Point(x, y)

    def update(self, delta_time):
        distanced_moved = (self.speed * 100) * (delta_time / 1000.0)
        self.point_from_start = Tools.get_point_by_distance(self.point_from_start, self.rotation, distanced_moved)

        noise_to_distance = Tools.noise_between(WorldParams.min_motion_accuracy, WorldParams.max_motion_accuracy, False)
        self.sensor_optical_flow = Tools.get_point_by_distance(self.sensor_optical_flow, self.rotation,
                                                               distanced_moved * noise_to_distance)

        noise_to_rotation = Tools.noise_between(WorldParams.min_rotation_accuracy, WorldParams.max_rotation_accuracy,
                                                False)
        milli_per_minute = 60000
        self.gyro_rotation += (1 - noise_to_rotation) * delta_time / milli_per_minute
        self.gyro_rotation = self.format_rotation(self.gyro_rotation)

    @staticmethod
    def format_rotation(rotation_value):
        rotation_value %= 360
        if rotation_value < 0:
            rotation_value = 360 + rotation_value
        return rotation_value

    def get_rotation(self):
        return self.rotation

    def get_gyro_rotation(self):
        return self.gyro_rotation

    def get_optical_sensor_location(self):
        return Point(self.sensor_optical_flow.x, self.sensor_optical_flow.y)

    def rotate_left(self, delta_time):
        rotation_changed = WorldParams.rotation_per_second * delta_time / 1000.0
        self.rotation += rotation_changed
        self.rotation = self.format_rotation(self.rotation)

        self.gyro_rotation += rotation_changed
        self.gyro_rotation = self.format_rotation(self.gyro_rotation)

    def rotate_right(self, delta_time):
        rotation_changed = -WorldParams.rotation_per_second * delta_time / 1000.0
        self.rotation += rotation_changed
        self.rotation = self.format_rotation(self.rotation)

        self.gyro_rotation += rotation_changed
        self.gyro_rotation = self.format_rotation(self.gyro_rotation)

    def speed_up(self, delta_time):
        """Increase the drone's speed based on elapsed time."""
        self.speed += (WorldParams.accelerate_per_second * delta_time / 1000.0)
        if self.speed > WorldParams.max_speed:
            self.speed = WorldParams.max_speed

    def slow_down(self, delta_time):
        """Decrease the drone's speed based on elapsed time."""
        self.speed -= (WorldParams.accelerate_per_second * delta_time / 1000.0)
        if self.speed < 0:
            self.speed = 0

    def stop_flight(self):
        self.speed = 0


    def paint(self, screen):
        """Draw the drone on the given screen."""
        if not self.mImage:
            self.mImage = pygame.image.load(self.drone_img_path)

        # Placeholder to draw the drone image on the screen
        point = self.get_point_on_map()
        screen.blit(self.mImage, (int(point.x), int(point.y)))

        for lidar in self.lidars:
            lidar.paint(screen)
