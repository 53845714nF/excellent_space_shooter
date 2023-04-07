"""
This Modul is only for loading the Sprites correct
Code mostly from:
https://stackoverflow.com/questions/45526988/does-anyone-have-an-example-of-using-sprite-sheets-in-tandem-with-xml-files/45527493#45527493
"""

from xml.etree import ElementTree
from pygame import Rect
from pygame.image import load


class Sheet:
    """
    Sheet class allow an easy asses to the assets sheet.
    """
    def __init__(self):
        self.spritesheet = load('assets/sheet.png').convert_alpha()
        tree = ElementTree.parse('assets/sheet.xml')

        self.map = {}
        for node in tree.iter():
            if node.attrib.get('name'):
                name = node.attrib.get('name')
                self.map[name] = {}
                self.map[name]['x'] = int(node.attrib.get('x'))
                self.map[name]['y'] = int(node.attrib.get('y'))
                self.map[name]['width'] = int(node.attrib.get('width'))
                self.map[name]['height'] = int(node.attrib.get('height'))

    def get_image_rect(self, x_position, y_position, width, height):
        """
        This function returns an img from the sheet.
        Based on the position.

        :param x_position: x position on the sheet
        :param y_position: y position on the sheet
        :param width: the width of the img on the sheet
        :param height: the height of the img on the sheet
        :return: return the img of the sheet
        """
        return self.spritesheet.subsurface(Rect(x_position, y_position, width, height))

    def get_image_name(self, name):
        """
        This function returns an img from the sheet.
        Based on the name.

        :param str name: the name from the sheet xml
        """
        rect = Rect(self.map[name]['x'], self.map[name]['y'],
                    self.map[name]['width'], self.map[name]['height'])
        return self.spritesheet.subsurface(rect)
