import random
import math

import WorldParams
from Point import Point


class Tools:
    @staticmethod
    def get_point_by_distance(from_point, rotation, distance):
        """
        Calculate a new point given an initial point, a rotation angle, and a distance.

        Parameters:
        from_point (Point): The starting point.
        rotation (float): The angle in degrees.
        distance (float): The distance to move from the starting point.

        Returns:
        Point: The new point after moving the given distance at the specified angle.
        """

        radians = math.pi * (rotation / 180)  # Convert degrees to radians
        i = distance / WorldParams.WorldParams.CMPerPixel # Convert distance to pixels
        xi = from_point.x + math.cos(radians) * i # Calculate new x-coordinate
        yi = from_point.y + math.sin(radians) * i # Calculate new y-coordinate
        return Point(xi, yi)

    @staticmethod
    def noise_between(min_value, max_value, is_negative):
        """
          Generate a random noise value between given minimum and maximum values.

          Parameters:
          min_value (float): The minimum value for the noise.
          max_value (float): The maximum value for the noise.
          is_negative (bool): Flag indicating whether the noise can be negative.

          Returns:
          float: The generated noise value.
          """

        rand = random.Random()
        noise_to_distance = 1 # Base noise value
        noise = (min_value + rand.uniform(0, 1) * (max_value - min_value)) / 100
        if not is_negative:
            return noise_to_distance + noise

        if rand.choice([True, False]):
            return noise_to_distance + noise
        else:
            return noise_to_distance - noise

    @staticmethod
    def get_rotation_between_points(from_point, to_point):
        """
        Calculate the rotation angle between two points.

        Parameters:
        from_point (Point): The starting point.
        to_point (Point): The ending point.

        Returns:
        float: The rotation angle in degrees.
        """
        y1 = from_point.y - to_point.y
        x1 = from_point.x - to_point.x
        radians = math.atan2(y1, x1)  # Use atan2 for correct quadrant
        rotation = radians * 180 / math.pi
        return rotation

    @staticmethod
    def get_distance_between_points(from_point, to_point):
        """
        Calculate the distance between two points.

        Parameters:
        from_point (Point): The starting point.
        to_point (Point): The ending point.

        Returns:
        float: The distance between the two points.
        """
        x1 = (from_point.x - to_point.x) ** 2
        y1 = (from_point.y - to_point.y) ** 2
        return math.sqrt(x1 + y1)

