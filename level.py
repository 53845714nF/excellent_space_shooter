"""
This Modul contains the Level class.
"""
from math import ceil
from pygame.image import load
from pygame.transform import scale
from paths import asset_path

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
        Maps the level number to the right image.
        """
        backgrounds = {
            0: "black",
            1: "black",
            2: "blue",
            3: "purple",
            4: "darkPurple"
        }

        filename = backgrounds.get(self.number, "black")

        return asset_path("backgrounds", filename + ".png")
