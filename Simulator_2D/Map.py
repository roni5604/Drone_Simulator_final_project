import pygame
from PIL import Image


class Map:
    def __init__(self, path, drone_start_point):
        """
        Initialize the Map object.

        Parameters:
        path (str): The path to the map image file.
        drone_start_point (tuple): The starting point of the drone.
        """

        self.drone_start_point = drone_start_point
        try:
            img_map = Image.open(path)
            self.map = self.render_map_from_image_to_boolean(img_map)
        except IOError as e:
            print(e)

    def render_map_from_image_to_boolean(self, map_img):
        """
        Convert a map image to a boolean array.

        Parameters:
        map_img (Image): The map image.

        Returns:
        list: A 2D boolean array representing the map.
        """

        w, h = map_img.size
        map_array = [[False for _ in range(h)] for _ in range(w)]
        for y in range(h):
            for x in range(w):
                r, g, b = map_img.getpixel((x, y))[:3]
                if r != 0 and g != 0 and b != 0:  # assuming non-black means passable
                    map_array[x][y] = True
        return map_array

    def is_collide(self, x, y):
        """
        Check if the given coordinates collide with an obstacle.

        Parameters:
        x (int): The x-coordinate.
        y (int): The y-coordinate.

        Returns:
        bool: True if there is a collision, False otherwise.
        """

        if 0 <= x < len(self.map) and 0 <= y < len(self.map[0]):
            return not self.map[x][y]
        return True  # out of bounds is treated as collision

    def paint(self, screen):
        """
        Paint the map onto the given screen.

        Parameters:
        screen (pygame.Surface): The screen to paint the map on.
        """
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                if not self.map[i][j]:  # If the cell is False (obstacle)
                    screen.set_at((i, j), (128, 128, 128)) # Paint the obstacle with a gray color
