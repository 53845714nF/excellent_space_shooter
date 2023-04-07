"""
Module contains the Ship class
"""
from pygame.mask import from_surface
from pygame.mixer import Sound
from laser import Laser
from sprites import Sheet


class Ship:
    """
    This class describe the functionality for spaceship in the game.
    """
    SHOOT_DELAY = 30

    def __init__(self, x_position, y_position, img, laser_img='laserRed01', live=1, speed=1):
        sheet = Sheet()
        self.x_position = x_position
        self.y_position = y_position
        self.img = sheet.get_image_name(img)
        self.laser_img = sheet.get_image_name(laser_img)
        self.live = live
        self.speed = speed
        self.mask = from_surface(self.img)
        self.shots = []
        self.shoot_delay_counter = 0
        self.lost_live_sound = Sound('assets/sounds/sfx_shieldDown.ogg')

    def draw(self, screen):
        """
        This function draws the spaceship and the laser shoot.

        :param display screen: The Display of the game
        """
        for shoot in self.shots:
            shoot.draw(screen)

        screen.blit(self.img, (self.x_position, self.y_position))

    def waite_shoot(self):
        """
        This function adds a delay in shoot process, to avoid permanent shooting.
        """
        if self.shoot_delay_counter >= self.SHOOT_DELAY:
            self.shoot_delay_counter = 0
        elif self.shoot_delay_counter > 0:
            self.shoot_delay_counter += 1

    def shoot(self):
        """
        This function create a new laser shoot.
        """
        if self.shoot_delay_counter == 0:
            laser = Laser(self.x_position + self.img.get_width() / 2,
                          self.y_position + self.img.get_height() / 2,
                          self.laser_img)

            self.shots.append(laser)
            self.shoot_delay_counter = 1

    def move_shots(self, screen, direction, obj):
        """
        This function check the behavior of the laser shoot.

        :param display screen: The Display of the game
        :param str direction: The direction of the shoot as sting have two possibility:
        'up' and 'down'
        :param obj: An object that can collide with the laser shoot
        """
        self.waite_shoot()
        for shoot in self.shots:
            shoot.move(direction)
            if shoot.off_screen(screen):
                self.shots.remove(shoot)
            elif shoot.collision(obj):
                obj.live -= 1
                self.lost_live_sound.play()
                self.shots.remove(shoot)

    def get_width(self):
        """
        :return: Returns the width from the spaceship
        """
        return self.img.get_width()

    def get_height(self):
        """
        :return: Returns the height from the spaceship
        """
        return self.img.get_height()
