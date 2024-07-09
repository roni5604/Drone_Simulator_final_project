import random
import pygame

import Tools
import WorldParams
import Drone


class Lidar:
    def __init__(self, drone: 'Drone', degrees: float):
        self.drone = drone
        self.degrees = degrees
        self.current_distance = 0.0

    def get_distance(self, delta_time: int) -> float:
        actual_point_to_shoot = self.drone.get_point_on_map()
        rotation = self.drone.get_rotation() + self.degrees

        distance_in_cm = 1.0
        while distance_in_cm <= WorldParams.WorldParams.lidar_limit:
            p = Tools.Tools.get_point_by_distance(actual_point_to_shoot, rotation, distance_in_cm)
            if self.drone.real_map.is_collide(int(p.x), int(p.y)):
                break
            distance_in_cm += 1

        return distance_in_cm

    def get_simulation_distance(self, delta_time: int) -> float:
        ran = random.Random()
        if ran.random() <= 0.05:  # 5% of the time, not getting an answer
            distance_in_cm = 0.0
        else:
            distance_in_cm = self.get_distance(delta_time)
            distance_in_cm += ran.randint(-WorldParams.WorldParams.lidar_noise,
                                          WorldParams.WorldParams.lidar_noise)  # +- 5 CM to the final calc

        self.current_distance = distance_in_cm  # store it for instance get
        return distance_in_cm

    def paint(self, screen: pygame.Surface):
        actual_point_to_shoot = self.drone.get_point_on_map()
        from_rotation = self.drone.get_rotation() + self.degrees
        to = Tools.Tools.get_point_by_distance(actual_point_to_shoot, from_rotation, self.current_distance)

        pygame.draw.line(screen, (255, 0, 0), (int(actual_point_to_shoot.x), int(actual_point_to_shoot.y)),
                         (int(to.x), int(to.y)))
