"""
EnemyManager Modul provides the EnemyManager class.
"""
from random import randrange, choice
from enemy import Enemy


class EnemyManager:
    """
    This Class provides functions for multiple Enemies.
    """
    def __init__(self):
        self.enemy_list = []

    def add(self, screen, number, level):
        """
        Add a certain number of enemies to a list of enemies.

        :param display screen: The Display of the game
        :param int number: number of enemies that are added
        :param int level: level of the game calculate the color of enemies and the speed
        """
        color = 'green'

        if level == 1:
            color = 'green'
        elif level == 2:
            color = 'blue'
        elif level == 3:
            color = 'red'
        elif level == 4:
            color = 'black'
        else:
            choice(('green', 'blue', 'red', 'black'))

        for _ in range(number):
            enemy = Enemy(x_position=randrange(50, screen.get_width() - 100),
                          y_position=randrange(-1500, -100),
                          color=color,
                          speed=level / 0.8
                          )

            self.enemy_list.append(enemy)

    def draw(self, screen):
        """
        Draw the List of Enemies on the Game Display.

        :param display screen: The Display of the game
        """
        for enemy in self.enemy_list:
            enemy.draw(screen)

    def move(self, screen, player):
        """
        Is responsibility for enemies movement also for then enemy laser movement.
        Trigger the shoot of Enemies. Removes unnecessary enemies.

        :param display screen: The Display of the game
        :param player: The player of the game, enemy laser check that player is hit
        """
        for enemy in self.enemy_list[:]:
            enemy.move()
            enemy.move_shots(screen, 'down', player)

            if randrange(0, 3 * 60) == 1:
                enemy.shoot()

            if enemy.y_position + enemy.get_height() > screen.get_height():
                self.enemy_list.remove(enemy)
            if enemy.live <= 0:
                try:
                    self.enemy_list.remove(enemy)
                except:
                    pass
    def count(self):
        """
        The number of enemies of the list.

        :return: the number of Enemies form the list
        """
        return len(self.enemy_list)
