import sys
from enum import Enum

import pygame

from CPU import CPU
from Drone import Drone
from Graph import Graph
from Point import Point
from Tools import Tools
from WorldParams import WorldParams


class PixelState(Enum):
    BLOCKED = 0
    EXPLORED = 1
    UNEXPLORED = 2
    VISITED = 3


def create_custom_drone(real_map, list_of_lidars_degrees):
    drone = Drone(real_map)
    for degree in list_of_lidars_degrees:
        drone.add_lidar(degree)
    return drone


class AutoAlgo1:
    def __init__(self, real_map):
        self.map_size = 3000
        self.map = [[PixelState.UNEXPLORED for _ in range(self.map_size)] for _ in range(self.map_size)]
        self.drone = create_custom_drone(real_map, list_of_lidars_degrees=[0, 90, -90])
        self.drone_number = 1
        self.points = []
        self.is_rotating = 0
        self.degrees_left = []
        self.degrees_left_func = []
        self.degrees_right = []
        self.degrees_right_func = []
        self.is_speed_up = False
        self.m_graph = Graph()
        self.ai_cpu = CPU(200, "Auto_AI")  # 10Hz CPU
        self.ai_cpu.add_function(self.update)
        self.drone_starting_point = Point(self.map_size // 2, self.map_size // 2)
        self.is_init = True
        self.last_front_lidar_dis = 0
        self.is_rotate_right = False
        self.changed_right = 0
        self.changed_left = 0
        self.try_to_escape = False
        self.left_or_right = 1
        self.max_rotation_to_direction = 20
        self.is_finish = True
        self.is_left_right_rotation_enable = True
        self.is_risky = False
        self.max_risky_distance = 150
        self.try_to_escape = False
        self.risky_dis = 0
        self.max_angle_risky = 10
        self.is_lidars_max = False
        self.save_point_after_seconds = 3
        self.max_distance_between_points = 100
        self.start_return_home = False
        self.init_point = Point()
        self.counter = 0
        self.toogle_real_map = True
        self.toogle_ai = False
        self.return_home = False
        self.last_gyro_rotation = 0
        self.toggle_snackDriver = False
        self.toggle_keep_right_driver = False
        self.toggle_keep_middle_driver = False

    def play(self):
        """Start the AI CPU and the drone."""
        self.drone.play()
        self.ai_cpu.play()

    def update(self, delta_time):
        """Update the state of the drone and AI."""
        self.update_visited()
        self.update_map_by_lidars()
        self.ai(delta_time)
        self.snake_driver(delta_time)
        self.keep_right_driver(delta_time)  # Add this line
        self.stay_in_middle_driver(delta_time)  # Add this line

        if self.is_rotating != 0:
            self.update_rotating(delta_time)
        if self.is_speed_up:
            self.drone.speed_up(delta_time)
        else:
            self.drone.slow_down(delta_time)

    def speed_up(self):
        self.is_speed_up = True

    def speed_down(self):
        self.is_speed_up = False

    def update_map_by_lidars(self):
        drone_point = self.drone.get_optical_sensor_location()
        from_point = Point(drone_point.x + self.drone_starting_point.x, drone_point.y + self.drone_starting_point.y)

        for lidar in self.drone.lidars:
            rotation = self.drone.get_gyro_rotation() + lidar.degrees
            for distance_in_cm in range(int(lidar.current_distance)):
                p = Tools.get_point_by_distance(from_point, rotation, distance_in_cm)
                self.set_pixel(p.x, p.y, PixelState.EXPLORED)

            if 0 < lidar.current_distance < WorldParams.lidar_limit - WorldParams.lidar_noise:
                p = Tools.get_point_by_distance(from_point, rotation, lidar.current_distance)
                self.set_pixel(p.x, p.y, PixelState.BLOCKED)

    def update_visited(self):
        """Mark the current drone position as visited on the map."""
        drone_point = self.drone.get_optical_sensor_location()
        from_point = Point(drone_point.x + self.drone_starting_point.x, drone_point.y + self.drone_starting_point.y)
        self.set_pixel(from_point.x, from_point.y, PixelState.VISITED)

    def set_pixel(self, x, y, state):
        """Set the state of a specific pixel on the map."""
        xi = int(x)
        yi = int(y)
        if state == PixelState.VISITED:
            self.map[xi][yi] = state
            return
        if self.map[xi][yi] == PixelState.UNEXPLORED:
            self.map[xi][yi] = state

    def paint_blind_map(self, screen):
        """Draw the blind map on the screen."""
        for i in range(self.map_size):
            for j in range(self.map_size):
                if self.map[i][j] != PixelState.UNEXPLORED:
                    color = (0, 0, 0)
                    if self.map[i][j] == PixelState.BLOCKED:
                        color = (255, 0, 0)
                    elif self.map[i][j] == PixelState.EXPLORED:
                        color = (255, 255, 0)
                    elif self.map[i][j] == PixelState.VISITED:
                        color = (0, 0, 255)
                    screen.set_at((i, j), color)

    def paint_points(self, screen):
        for p in self.points:
            pygame.draw.circle(screen, (0, 255, 0),
                               (int(p.x + self.drone.start_point.x), int(p.y + self.drone.start_point.y)), 10, 1)

    def paint(self, screen):
        if self.toogle_real_map:
            self.drone.real_map.paint(screen)

        self.paint_blind_map(screen)
        self.paint_points(screen)
        self.drone.paint(screen)

    def ai(self, delta_time):
        """Artificial Intelligence algorithm for navigating the drone."""
        if not self.toogle_ai:
            return

        if self.is_init:
            self.speed_up()
            drone_point = self.drone.get_optical_sensor_location()
            self.init_point = Point(drone_point.x, drone_point.y)
            self.points.append(drone_point)
            self.m_graph.add_vertex(drone_point)
            self.is_init = False

        if self.is_left_right_rotation_enable:
            self.do_left_right()

        drone_point = self.drone.get_optical_sensor_location()

        if self.return_home:
            if Tools.get_distance_between_points(self.get_last_point(), drone_point) < self.max_distance_between_points:
                if len(self.points) <= 1 and Tools.get_distance_between_points(self.get_last_point(),
                                                                               drone_point) < self.max_distance_between_points / 5:
                    self.speed_down()
                else:
                    self.remove_last_point()
        else:
            if Tools.get_distance_between_points(self.get_last_point(),
                                                 drone_point) >= self.max_distance_between_points:
                self.points.append(drone_point)
                self.m_graph.add_vertex(drone_point)

        if not self.is_risky:

            lidar = self.drone.lidars[0]
            if lidar.current_distance <= self.max_risky_distance:
                self.is_risky = True
                self.risky_dis = lidar.current_distance

            lidar1 = self.drone.lidars[1]
            if lidar1.current_distance <= self.max_risky_distance / 3:
                self.is_risky = True

            lidar2 = self.drone.lidars[2]
            if lidar2.current_distance <= self.max_risky_distance / 3:
                self.is_risky = True

        else:

            if not self.try_to_escape:
                self.try_to_escape = True
                lidar1 = self.drone.lidars[1]
                a = lidar1.current_distance

                lidar2 = self.drone.lidars[2]
                b = lidar2.current_distance

                spin_by = self.max_angle_risky

                if a > 270 and b > 270:
                    self.is_lidars_max = True
                    l1 = Tools.get_point_by_distance(drone_point, lidar1.degrees + self.drone.get_gyro_rotation(),
                                                     lidar1.current_distance)
                    l2 = Tools.get_point_by_distance(drone_point, lidar2.degrees + self.drone.get_gyro_rotation(),
                                                     lidar2.current_distance)
                    last_point = self.get_avg_last_point()
                    dis_to_lidar1 = Tools.get_distance_between_points(last_point, l1)
                    dis_to_lidar2 = Tools.get_distance_between_points(last_point, l2)

                    if self.return_home:
                        if Tools.get_distance_between_points(self.get_last_point(),
                                                             drone_point) < self.max_distance_between_points:
                            self.remove_last_point()
                    else:
                        if Tools.get_distance_between_points(self.get_last_point(),
                                                             drone_point) >= self.max_distance_between_points:
                            self.points.append(drone_point)
                            self.m_graph.add_vertex(drone_point)

                    spin_by = 90
                    if self.return_home:
                        spin_by *= -1

                    if dis_to_lidar1 < dis_to_lidar2:
                        spin_by *= -1

                else:
                    if a < b:
                        spin_by *= -1

                self.spin_by2(spin_by, True, lambda: self.reset_risk())

    def reset_risk(self):
        self.try_to_escape = False
        self.is_risky = False

    def get_last_point(self):
        if not self.points:
            return self.init_point
        return self.points[-1]

    def remove_last_point(self):
        if not self.points:
            return self.init_point
        return self.points.pop()

    def get_avg_last_point(self):
        if len(self.points) < 2:
            return self.init_point
        p1 = self.points[-1]
        p2 = self.points[-2]
        return Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)

    def do_left_right(self):
        if self.is_finish:
            self.left_or_right *= -1
            self.counter += 1
            self.is_finish = False

            self.spin_by2(self.max_rotation_to_direction * self.left_or_right, False, lambda: self.set_finish())

    def set_finish(self):
        self.is_finish = True

    def spin_by2(self, degrees, is_first, func):
        self.last_gyro_rotation = self.drone.get_gyro_rotation()
        if is_first:
            self.degrees_left.insert(0, degrees)
            self.degrees_left_func.insert(0, func)
        else:
            self.degrees_left.append(degrees)
            self.degrees_left_func.append(func)
        self.is_rotating = 1

    def spin_by(self, degrees):
        self.last_gyro_rotation = self.drone.get_gyro_rotation()
        self.degrees_left.append(degrees)
        self.degrees_left_func.append(None)
        self.is_rotating = 1

    def update_rotating(self, delta_time):
        """Update the rotation of the drone."""
        if not self.degrees_left:
            return

        degrees_left_to_rotate = self.degrees_left[0]
        is_left = degrees_left_to_rotate < 0

        curr = self.drone.get_gyro_rotation()
        just_rotated = curr - self.last_gyro_rotation

        if is_left:
            if just_rotated > 0:
                just_rotated = -(360 - just_rotated)
        else:
            if just_rotated < 0:
                just_rotated = 360 + just_rotated

        self.last_gyro_rotation = curr
        degrees_left_to_rotate -= just_rotated
        self.degrees_left[0] = degrees_left_to_rotate

        if (is_left and degrees_left_to_rotate >= 0) or (not is_left and degrees_left_to_rotate <= 0):
            self.degrees_left.pop(0)
            func = self.degrees_left_func.pop(0)
            if func:
                func()
            if not self.degrees_left:
                self.is_rotating = 0
            return

        direction = 1 if degrees_left_to_rotate > 0 else -1
        self.drone.rotate_left(delta_time * direction)

    ############################################################################################
    def spin_by_to_back_home(self, degrees, is_first, func):
        self.last_gyro_rotation = self.drone.get_gyro_rotation()
        if is_first:
            self.degrees_right.insert(0, degrees)
            self.degrees_right_func.insert(0, func)
        else:
            self.degrees_right.append(degrees)
            self.degrees_right_func.append(func)
        self.is_rotating = 1


    def update_rotating_to_back_home(self, delta_time):
        if not self.degrees_right:
            return

        degrees_right_to_rotate = self.degrees_right[0]
        is_left = degrees_right_to_rotate < 0

        curr = self.drone.get_gyro_rotation()
        just_rotated = curr - self.last_gyro_rotation

        if is_left:
            if just_rotated > 0:
                just_rotated = -(360 - just_rotated)
        else:
            if just_rotated < 0:
                just_rotated = 360 + just_rotated

        self.last_gyro_rotation = curr
        degrees_right_to_rotate -= just_rotated
        self.degrees_right[0] = degrees_right_to_rotate

        if (is_left and degrees_right_to_rotate >= 0) or (not is_left and degrees_right_to_rotate <= 0):
            self.degrees_right.pop(0)
            func = self.degrees_right_func.pop(0)
            if func:
                func()
            if not self.degrees_right:
                self.is_rotating = 0
            return

        direction = 1 if degrees_right_to_rotate > 0 else -1
        self.drone.rotate_right(delta_time * direction)








    ############################################################################################
    def snake_driver(self, delta_time):
        if not self.toggle_snackDriver:
            return

        if self.is_init:
            self.speed_up()
            drone_point = self.drone.get_optical_sensor_location()
            self.init_point = Point(drone_point.x, drone_point.y)
            self.points.append(drone_point)
            self.m_graph.add_vertex(drone_point)
            self.is_init = False

        drone_point = self.drone.get_optical_sensor_location()

        if self.return_home:
            self.perform_return_home(delta_time)
        else:
            if Tools.get_distance_between_points(self.get_last_point(),
                                                 drone_point) >= self.max_distance_between_points:
                self.points.append(drone_point)
                self.m_graph.add_vertex(drone_point)

            if not self.is_risky:
                lidar = self.drone.lidars[0]
                if lidar.current_distance <= self.max_risky_distance:
                    self.is_risky = True
                    self.risky_dis = lidar.current_distance

                lidar1 = self.drone.lidars[1]
                if lidar1.current_distance <= self.max_risky_distance / 3:
                    self.is_risky = True

                lidar2 = self.drone.lidars[2]
                if lidar2.current_distance <= self.max_risky_distance / 3:
                    self.is_risky = True

                if not self.is_risky:
                    self.perform_snake_movement(delta_time)

            else:
                if not self.try_to_escape:
                    self.try_to_escape = True
                    lidar1 = self.drone.lidars[1]
                    a = lidar1.current_distance

                    lidar2 = self.drone.lidars[2]
                    b = lidar2.current_distance

                    spin_by = self.max_angle_risky

                    if a > 270 and b > 270:
                        self.is_lidars_max = True
                        l1 = Tools.get_point_by_distance(drone_point, lidar1.degrees + self.drone.get_gyro_rotation(),
                                                         lidar1.current_distance)
                        l2 = Tools.get_point_by_distance(drone_point, lidar2.degrees + self.drone.get_gyro_rotation(),
                                                         lidar2.current_distance)
                        last_point = self.get_avg_last_point()
                        dis_to_lidar1 = Tools.get_distance_between_points(last_point, l1)
                        dis_to_lidar2 = Tools.get_distance_between_points(last_point, l2)

                        if self.return_home:
                            if Tools.get_distance_between_points(self.get_last_point(),
                                                                 drone_point) < self.max_distance_between_points:
                                self.remove_last_point()
                        else:
                            if Tools.get_distance_between_points(self.get_last_point(),
                                                                 drone_point) >= self.max_distance_between_points:
                                self.points.append(drone_point)
                                self.m_graph.add_vertex(drone_point)

                        spin_by = 90
                        if self.return_home:
                            spin_by *= -1

                        if dis_to_lidar1 < dis_to_lidar2:
                            spin_by *= -1

                    else:
                        if a < b:
                            spin_by *= -1

                    self.spin_by2(spin_by, True, lambda: self.reset_risk())

    def perform_return_home(self, delta_time):
        # here need to be changed!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        """Handles the drone's return to home functionality."""
        if not self.points:
            self.drone.stop()
            return

        drone_point = self.drone.get_optical_sensor_location()
        last_point = self.get_last_point()

        if Tools.get_distance_between_points(last_point, drone_point) < 0.5:
            self.remove_last_point()
            if not self.points:
                self.drone.stop()
        else:
            if not self.is_risky:
                lidar = self.drone.lidars[0]
                if lidar.current_distance <= self.max_risky_distance:
                    self.is_risky = True
                    self.risky_dis = lidar.current_distance

                lidar1 = self.drone.lidars[1]
                if lidar1.current_distance <= self.max_risky_distance / 3:
                    self.is_risky = True

                lidar2 = self.drone.lidars[2]
                if lidar2.current_distance <= self.max_risky_distance / 3:
                    self.is_risky = True

                if not self.is_risky:
                    self.move_towards_last_point(delta_time, last_point)
                else:
                    return
            else:
                if not self.try_to_escape:
                    self.try_to_escape = True
                    lidar1 = self.drone.lidars[1]
                    a = lidar1.current_distance

                    lidar2 = self.drone.lidars[2]
                    b = lidar2.current_distance

                    spin_by = self.max_angle_risky

                    if a > 270 and b > 270:
                        self.is_lidars_max = True
                        l1 = Tools.get_point_by_distance(drone_point, lidar1.degrees + self.drone.get_gyro_rotation(),
                                                         lidar1.current_distance)
                        l2 = Tools.get_point_by_distance(drone_point, lidar2.degrees + self.drone.get_gyro_rotation(),
                                                         lidar2.current_distance)
                        last_point = self.get_avg_last_point()
                        dis_to_lidar1 = Tools.get_distance_between_points(last_point, l1)
                        dis_to_lidar2 = Tools.get_distance_between_points(last_point, l2)
                        spin_by = 90
                        if dis_to_lidar1 < dis_to_lidar2:
                            spin_by *= -1

                    else:
                        if a < b:
                            spin_by *= -1

                    self.spin_by2(spin_by, True, lambda: self.reset_risk())
                else:
                    self.move_towards_last_point(delta_time, last_point)

    def move_towards_last_point(self, delta_time, last_point):
        """Move the drone towards the last point."""
        drone_point = self.drone.get_optical_sensor_location()
        angle_to_point = Tools.get_rotation_between_points(drone_point, last_point)

        # Calculate the difference between the current rotation and the target angle
        rotation_difference = angle_to_point - (self.drone.get_gyro_rotation() + 90)

        # here need to be changed!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Rotate towards the last point using spin_by2
        self.spin_by2(-angle_to_point, False, lambda: self.reset_risk())
        self.move_forward(delta_time, 10)

    def move_forward(self, delta_time, distance):
        """Move the drone forward by a specified distance."""
        self.drone.speed_up(delta_time)

    def perform_snake_movement(self, delta_time):
        zigzag_angle = 10
        zigzag_distance = 10
        left_or_right = 1

        if self.return_home:
            zigzag_angle *= -1

        self.spin_by(zigzag_angle * left_or_right)
        left_or_right *= -1

        self.move_forward(delta_time, zigzag_distance)

        self.spin_by(zigzag_angle * left_or_right)
        left_or_right *= -1

        self.move_forward(delta_time, zigzag_distance)

    ############################################################################################

    #################### keep right driver function ##############################################

    def keep_right_driver(self, delta_time):
        if not self.toggle_keep_right_driver:
            return

        if self.is_init:
            self.speed_up()
            drone_point = self.drone.get_optical_sensor_location()
            self.init_point = Point(drone_point.x, drone_point.y)
            self.points.append(drone_point)
            self.m_graph.add_vertex(drone_point)
            self.is_init = False

        drone_point = self.drone.get_optical_sensor_location()

        if self.return_home:
            if Tools.get_distance_between_points(self.get_last_point(), drone_point) < self.max_distance_between_points:
                if len(self.points) <= 1 and Tools.get_distance_between_points(self.get_last_point(),
                                                                               drone_point) < self.max_distance_between_points / 5:
                    self.speed_down()
                else:
                    self.remove_last_point()
            else:
                if Tools.get_distance_between_points(self.get_last_point(),
                                                     drone_point) >= self.max_distance_between_points:
                    self.points.append(drone_point)
                    self.m_graph.add_vertex(drone_point)

        if not self.is_risky:
            lidar = self.drone.lidars[0]
            if lidar.current_distance <= self.max_risky_distance:
                self.is_risky = True
                self.risky_dis = lidar.current_distance

            lidar1 = self.drone.lidars[1]
            if lidar1.current_distance <= self.max_risky_distance / 3:
                self.is_risky = True

            lidar2 = self.drone.lidars[2]
            if lidar2.current_distance <= self.max_risky_distance / 3:
                self.is_risky = True

            if not self.is_risky:
                self.perform_keep_right_movement(delta_time)

        else:
            if not self.try_to_escape:
                self.try_to_escape = True
                lidar1 = self.drone.lidars[1]
                a = lidar1.current_distance

                lidar2 = self.drone.lidars[2]
                b = lidar2.current_distance

                spin_by = self.max_angle_risky

                if a > 270 and b > 270:
                    self.is_lidars_max = True
                    l1 = Tools.get_point_by_distance(drone_point, lidar1.degrees + self.drone.get_gyro_rotation(),
                                                     lidar1.current_distance)
                    l2 = Tools.get_point_by_distance(drone_point, lidar2.degrees + self.drone.get_gyro_rotation(),
                                                     lidar2.current_distance)
                    last_point = self.get_avg_last_point()
                    dis_to_lidar1 = Tools.get_distance_between_points(last_point, l1)
                    dis_to_lidar2 = Tools.get_distance_between_points(last_point, l2)

                    if self.return_home:
                        if Tools.get_distance_between_points(self.get_last_point(),
                                                             drone_point) < self.max_distance_between_points:
                            self.remove_last_point()
                    else:
                        if Tools.get_distance_between_points(self.get_last_point(),
                                                             drone_point) >= self.max_distance_between_points:
                            self.points.append(drone_point)
                            self.m_graph.add_vertex(drone_point)

                    spin_by = 90
                    if self.return_home:
                        spin_by *= -1

                    if dis_to_lidar1 < dis_to_lidar2:
                        spin_by *= -1

                else:
                    if a < b:
                        spin_by *= -1

                self.spin_by2(spin_by, True, lambda: self.reset_risk())

    def perform_keep_right_movement(self, delta_time):
        keep_right_angle = -10
        keep_right_distance = 10

        if self.return_home:
            keep_right_angle *= -1

        self.spin_by(keep_right_angle)
        self.move_forward(delta_time, keep_right_distance)

    ############################################################################################

    def stay_in_middle_driver(self, delta_time):
        if not self.toggle_keep_middle_driver:
            return

        if self.is_init:
            self.speed_up()
            drone_point = self.drone.get_optical_sensor_location()
            self.init_point = Point(drone_point.x, drone_point.y)
            self.points.append(drone_point)
            self.m_graph.add_vertex(drone_point)
            self.is_init = False

        drone_point = self.drone.get_optical_sensor_location()

        if self.return_home:
            if Tools.get_distance_between_points(self.get_last_point(), drone_point) < self.max_distance_between_points:
                if len(self.points) <= 1 and Tools.get_distance_between_points(self.get_last_point(),
                                                                               drone_point) < self.max_distance_between_points / 5:
                    self.speed_down()
                else:
                    self.remove_last_point()
            else:
                if Tools.get_distance_between_points(self.get_last_point(),
                                                     drone_point) >= self.max_distance_between_points:
                    self.points.append(drone_point)
                    self.m_graph.add_vertex(drone_point)

        if not self.is_risky:
            lidar_left = self.drone.lidars[2]
            lidar_right = self.drone.lidars[1]
            mid_point = (lidar_left.current_distance + lidar_right.current_distance) / 2

            if lidar_left.current_distance <= self.max_risky_distance or lidar_right.current_distance <= self.max_risky_distance:
                self.is_risky = True

            else:
                self.keep_middle_movement(delta_time, mid_point)

        else:
            if not self.try_to_escape:
                self.try_to_escape = True
                lidar1 = self.drone.lidars[1]
                a = lidar1.current_distance

                lidar2 = self.drone.lidars[2]
                b = lidar2.current_distance

                spin_by = self.max_angle_risky

                if a > 270 and b > 270:
                    self.is_lidars_max = True
                    l1 = Tools.get_point_by_distance(drone_point, lidar1.degrees + self.drone.get_gyro_rotation(),
                                                     lidar1.current_distance)
                    l2 = Tools.get_point_by_distance(drone_point, lidar2.degrees + self.drone.get_gyro_rotation(),
                                                     lidar2.current_distance)
                    last_point = self.get_avg_last_point()
                    dis_to_lidar1 = Tools.get_distance_between_points(last_point, l1)
                    dis_to_lidar2 = Tools.get_distance_between_points(last_point, l2)

                    if self.return_home:
                        if Tools.get_distance_between_points(self.get_last_point(),
                                                             drone_point) < self.max_distance_between_points:
                            self.remove_last_point()
                    else:
                        if Tools.get_distance_between_points(self.get_last_point(),
                                                             drone_point) >= self.max_distance_between_points:
                            self.points.append(drone_point)
                            self.m_graph.add_vertex(drone_point)

                    spin_by = 90
                    if self.return_home:
                        spin_by *= -1

                    if dis_to_lidar1 < dis_to_lidar2:
                        spin_by *= -1

                else:
                    if a < b:
                        spin_by *= -1

                self.spin_by2(spin_by, True, lambda: self.reset_risk())

    def keep_middle_movement(self, delta_time, mid_point):
        if mid_point < 0:
            self.spin_by(self.max_rotation_to_direction)
        elif mid_point > 0:
            self.spin_by(-self.max_rotation_to_direction)
        self.move_forward(delta_time, 10)

    def switch_drone(self, real_map):
        if self.drone_number == 3:
            self.drone_number = 1
        else:
            self.drone_number += 1

        self.drone.stop()

        if self.drone_number == 1:
            self.drone = create_custom_drone(real_map, list_of_lidars_degrees=[0, 90, -90])
        elif self.drone_number == 2:
            self.drone = create_custom_drone(real_map, list_of_lidars_degrees=[0, 45, -45, 70, -70])
        elif self.drone_number == 3:
            self.drone = create_custom_drone(real_map, list_of_lidars_degrees=[45, -45, 90, -90, 135, -135])


        # reset all the variables to the initial state
        self.points = []
        self.is_rotating = 0
        self.degrees_left = []
        self.degrees_left_func = []
        self.degrees_right = []
        self.degrees_right_func = []
        self.is_speed_up = False
        self.is_init = True
        self.last_front_lidar_dis = 0
        self.is_rotate_right = False
        self.changed_right = 0
        self.changed_left = 0
        self.try_to_escape = False
        self.left_or_right = 1
        self.is_finish = True
        self.is_left_right_rotation_enable = True
        self.is_risky = False
        self.max_risky_distance = 150
        self.try_to_escape = False
        self.risky_dis = 0
        self.max_angle_risky = 10
        self.is_lidars_max = False
        self.save_point_after_seconds = 3
        self.max_distance_between_points = 100
        self.start_return_home = False
        self.init_point = Point()
        self.counter = 0
        self.toogle_real_map = True
        self.toogle_ai = False
        self.return_home = False
        self.last_gyro_rotation = 0
        self.toggle_snackDriver = False
        self.toggle_keep_right_driver = False

        # reset the position of the drone and clear the map
        self.drone_starting_point = Point(self.map_size // 2, self.map_size // 2)
        self.map = [[PixelState.UNEXPLORED for _ in range(self.map_size)] for _ in range(self.map_size)]

        # start the drone
        self.drone.play()



    # we need to compare 2 types of drones, with different lidars (number of lidars and the degrees of the lidars)
    # we need to compare the movement of the drones, the speed of the drones,
    # the rotation of the drones, the distance of the drones