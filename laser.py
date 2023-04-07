"""
This Module contains the Laser class.
"""
from pygame.mask import from_surface


class Laser:
    """
    The Laser class have functionality for the laser shoot in the game.
    Main porpoise is the movement an collision detection.
    """
    def __init__(self, x_position, y_position, img):
        self.x_position = x_position
        self.y_position = y_position
        self.img = img
        self.mask = from_surface(self.img)

    def draw(self, screen):
        """
        Draw the laser on the game display.

        :param display screen: The Display of the game
        """
        screen.blit(self.img, (self.x_position, self.y_position))

    def move(self, direction):
        """
        Provides the movement of the laser.

        :param str direction: There are two direction that a laser can follow: 'up' and 'down'
        """
        if direction == 'up':
            self.y_position -= 10
        elif direction == 'down':
            self.y_position += 10

    def off_screen(self, screen):
        """
        This function returns a bool if the laser still visible on the screen.

        :param display screen: The Display of the game
        :return: bool laser still visible on screen
        """
        return not screen.get_height() >= self.y_position >= 0

    def collision(self, obj):
        """
        Check the collision of a laser with an object.

        :param obj: object that can possible can crash with a laser
        """
        offset_x = obj.x_position - self.x_position
        offset_y = obj.y_position - self.y_position
        return self.mask.overlap(obj.mask, (offset_x, offset_y)) is not None
