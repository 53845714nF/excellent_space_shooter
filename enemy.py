"""
Modul for enemy class
"""
from random import randrange
from ship import Ship


class Enemy(Ship):
    """
    Enemy provide specific Functions for Spaceship Enemy.
    """

    def __init__(self, x_position, y_position, color, speed):
        self.color = color
        self.img = self.map_color_ship() + str(randrange(1, 5))
        self.laser_img = self.map_color_laser()
        super().__init__(x_position, y_position, self.img, laser_img=self.laser_img, speed=speed)

    def move(self):
        """
        Enemy moves from top to bottom.
        """
        self.y_position += self.speed

    def map_color_ship(self):
        """
        Map color to the right enemy image.
        """
        return {
            'black': 'enemyBlack',
            'blue': 'enemyBlue',
            'green': 'enemyGreen',
            'red': 'enemyRed'
        }[self.color]

    def map_color_laser(self):
        """
        Map color to the right laser image.
        """
        return {
            'black': 'laserRed01',
            'blue': 'laserBlue01',
            'green': 'laserGreen07',
            'red': 'laserRed01'
        }[self.color]
