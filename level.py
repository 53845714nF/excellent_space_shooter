"""
This Modul contains the Level class.
"""
from math import ceil
from pygame.image import load
from pygame.transform import scale


class Level:
    """
    The Level class is responsible for numbering the levels and also for the background.
    """
    def __init__(self, number):
        self.number = number
        self.background = load(self.map_background()).convert()
        self.scroll = 0

    def draw_background(self, screen):
        """
        This function draws with a scrolling background.

        :param display screen: The Display of the game
        """
        self.background = load(self.map_background()).convert()
        self.background = scale(self.background, (screen.get_width(), screen.get_height()))

        tiles = ceil(screen.get_height() / self.background.get_height()) + 1
        i = 0

        while i < tiles:
            screen.blit(self.background, (0, self.background.get_height() * i + self.scroll))
            i += 1
        self.scroll -= 1

        if abs(self.scroll) > self.background.get_width():
            self.scroll = 0

    def map_background(self):
        """
        Maps the level number to right image.
        """
        img = 'assets/backgrounds/'
        if self.number == 0:
            img += 'black'
        elif self.number == 1:
            img += 'black'
        elif self.number == 2:
            img += 'blue'
        elif self.number == 3:
            img += 'purple'
        elif self.number == 4:
            img += 'darkPurple'
        else:
            img += 'black'

        return img + '.png'
