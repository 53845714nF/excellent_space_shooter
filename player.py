"""
The Module contains the Player class which contains player functionalities.
"""
# pylint: disable=E0611
from pygame import K_w, K_a, K_s, K_d, K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT
from pygame.key import get_pressed
from pygame.mixer import Sound
from ship import Ship


class Player(Ship):
    """
    Player clas provides functions for player movement, shooting and collision detection.
    """
    # pylint: disable=R0913
    def __init__(self, x_position, y_position, img, laser_img='laserRed01', live=4, speed=6):
        super().__init__(x_position, y_position, img, laser_img, live, speed)
        self.score = 0
        self.shoot_sound = Sound('assets/sounds/sfx_laser2.ogg')

    def movement(self, screen):
        """
        This Function handel the Movement of the Player.
        It allows to fly around with wasd or the arrow keys.
        And space for shoot.

        :param display screen: The Display of the game
        """
        # WASD Control
        keys = get_pressed()
        if keys[K_UP] or keys[K_w]:
            if self.y_position - self.speed > 0:
                self.y_position -= self.speed
        if keys[K_LEFT] or keys[K_a]:
            if self.x_position - self.speed > 0:
                self.x_position -= self.speed
        if keys[K_DOWN] or keys[K_s]:
            if self.y_position + self.speed + self.get_height() + 15 < screen.get_height():
                self.y_position += self.speed
        if keys[K_RIGHT] or keys[K_d]:
            if self.x_position + self.speed + self.get_width() < screen.get_width():
                self.x_position += self.speed

        # Space Key for Shoot
        if keys[K_SPACE]:
            self.shoot_sound.play()
            self.shoot()

    # pylint: disable=W0237
    def move_shots(self, screen, direction, enemies):
        self.waite_shoot()
        for shoot in self.shots:
            shoot.move(direction)
            if shoot.off_screen(screen):
                self.shots.remove(shoot)
            else:
                for enemy in enemies[:]:
                    if shoot.collision(enemy):
                        enemy.live -= 1
                        self.score += 10
                        try:
                            self.shots.remove(shoot)
                        except:
                            pass

    def collision(self, enemies):
        """
         Check the collision of the player with enemies.

         :param enemies: list of enemies that can possible can crash with the player
         """
        for enemy in enemies:
            offset_x = enemy.x_position - self.x_position
            offset_y = enemy.y_position - self.y_position
            if self.mask.overlap(enemy.mask, (offset_x, offset_y)) is not None:
                self.lost_live_sound.play()
                self.live -= 1
                enemy.live -= 1
