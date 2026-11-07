"""
The Module contains the Player class which contains player functionalities.
"""
# pylint: disable=E0611
import random
import pygame
from pygame import K_w, K_a, K_s, K_d, K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT
from pygame.key import get_pressed
from pygame.mixer import Sound
from ship import Ship
from paths import asset_path
from sprites import get_sheet

_DAMAGE_OVERLAYS = None


def get_damage_overlays():
    """
    Loads and extracts the transparent damage overlays for playerShip2.
    Cached so extraction is only performed once.
    """
    global _DAMAGE_OVERLAYS
    if _DAMAGE_OVERLAYS is None:
        sheet = get_sheet()
        overlays = {}
        for lvl, name in [(1, "playerShip2_damage1"), (2, "playerShip2_damage2"), (3, "playerShip2_damage3")]:
            raw = sheet.get_image_name(name)
            overlay = pygame.Surface(raw.get_size(), pygame.SRCALPHA)
            for x in range(raw.get_width()):
                for y in range(raw.get_height()):
                    c = raw.get_at((x, y))
                    if c.a > 0 and not (c.r > 200 and c.g > 200 and c.b > 200):
                        overlay.set_at((x, y), c)
            overlays[lvl] = overlay
        _DAMAGE_OVERLAYS = overlays
    return _DAMAGE_OVERLAYS


class Player(Ship):
    """
    Player class provides functions for player movement, shooting, collision detection,
    and visual damage overlays corresponding to remaining lives.
    """
    # pylint: disable=R0913
    def __init__(self, x_position, y_position, img, laser_img='laserRed01', live=4, speed=6):
        super().__init__(x_position, y_position, img, laser_img, live, speed)
        self.score = 0
        self.max_live = live
        self.shoot_sound = Sound(asset_path("sounds", "sfx_laser2.ogg"))
        self.damage_overlays = get_damage_overlays()
        self.smoke_particles = []

    def draw(self, screen):
        """
        Draws the ship, laser shots, visual hull damage overlays, and smoke when critical.
        """
        super().draw(screen)

        # Calculate visual damage level (1 = light, 2 = medium, 3 = critical)
        # 4 lives = pristine, 3 lives = damage1, 2 lives = damage2, 1 life = damage3
        damage_level = max(0, min(3, 4 - int(self.live)))
        if damage_level > 0 and damage_level in self.damage_overlays:
            screen.blit(self.damage_overlays[damage_level], (self.x_position, self.y_position))

        # Critical health smoke and sparks effect (1 life left)
        if self.live == 1:
            if random.random() < 0.45:
                wing_x = self.x_position + (26 if random.random() < 0.5 else 84)
                wing_y = self.y_position + 42
                self.smoke_particles.append({
                    "x": wing_x + random.uniform(-4, 4),
                    "y": wing_y + random.uniform(-3, 3),
                    "vx": random.uniform(-0.6, 0.6),
                    "vy": random.uniform(1.8, 3.8),
                    "radius": random.uniform(2.5, 4.5),
                    "color": random.choice([(70, 70, 80), (110, 110, 120), (255, 140, 40)]),
                    "alpha": 180,
                })

            for p in self.smoke_particles[:]:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["radius"] += 0.15
                p["alpha"] = max(0, p["alpha"] - 9)
                if p["alpha"] <= 0:
                    self.smoke_particles.remove(p)
                else:
                    pr = max(1, int(p["radius"]))
                    surf = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
                    c = p["color"]
                    pygame.draw.circle(
                        surf, (c[0], c[1], c[2], int(p["alpha"])), (pr + 1, pr + 1), pr
                    )
                    screen.blit(surf, (int(p["x"] - pr), int(p["y"] - pr)))

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
