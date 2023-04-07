# pylint: disable=E0611
from pygame import QUIT as PG_QUIT
from pygame.display import set_mode, set_caption, update
from pygame.event import get as pg_get
from pygame.time import Clock
from pygame.font import init as font_init
from pygame.mixer import init as mixer_init
from pygame.mixer import Sound
from pygame.font import Font
from enemy_manager import EnemyManager
from player import Player
from level import Level

# Pygame init stuff
size = width, height = 750, 750
screen = set_mode(size)
set_caption('Excellent Space Shooter')
font_init()
mixer_init()

# Fonts
future_thin_font = Font('assets/fonts/kenvector_future_thin.ttf', 30)
future_font = Font('assets/fonts/kenvector_future.ttf', 60)

# Music
music = Sound('assets/sounds/space_half.mp3')
music.set_volume(0.2)
music.play()

# Game objects
player = Player(300, 650, 'playerShip2_red')
enemy_manager = EnemyManager()
level = Level(0)


def main():
    keep_going = True
    clock = Clock()
    number_enemies = 0
    lost = False
    lost_time = 0

    def redraw_window():
        level.draw_background(screen)
        enemy_manager.draw(screen)

        player.draw(screen)

        lives_label = future_thin_font.render(f'Lives: {player.live}', True, (255, 255, 255))
        screen.blit(lives_label, (10, 10))

        score_label = future_thin_font.render(f'Score: {player.score}', True, (255, 255, 255))
        screen.blit(score_label, (10, 40))

        level_label = future_thin_font.render(f'Level: {level.number}', True, (255, 255, 255))
        screen.blit(level_label, (width - level_label.get_width(), 10))

        if lost:
            lost_label = future_font.render('GAME OVER', True, (255, 204, 0))
            screen.blit(lost_label, (width / 2 - lost_label.get_width() / 2, 350))
        update()

    while keep_going:
        fps = 60
        clock.tick(fps)
        redraw_window()

        if int(player.live) <= 0:
            lost = True
            lost_time += 1

        if lost:
            if lost_time > fps * 3:
                music.fadeout(3)
                keep_going = False

        for event in pg_get():
            if event.type == PG_QUIT:
                keep_going = False

        if enemy_manager.count() == 0:
            level.number += 1
            number_enemies += 3
            enemy_manager.add(screen, number_enemies, level.number)

        player.movement(screen)
        player.move_shots(screen, 'up', enemy_manager.enemy_list)
        player.collision(enemy_manager.enemy_list)
        enemy_manager.move(screen, player)


main()
