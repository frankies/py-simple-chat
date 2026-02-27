import pygame
from pygame.sprite import Sprite

class Alien(Sprite):
    def __init__(self, ai_game, typ):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.type = typ  # 'normal'/'red'/'blue'

        # 加载images文件夹中的外星人图片（核心路径修正）
        self.image = pygame.image.load('images/alien.jpg').convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 40))

        # 类型属性：普通/红色/蓝色
        if self.type == 'red':
            self.image.fill((255, 50, 50), special_flags=pygame.BLEND_MULT)
            self.hp = 1
            self.points = 50
        elif self.type == 'blue':
            self.image.fill((50, 50, 255), special_flags=pygame.BLEND_MULT)
            self.hp = 2
            self.points = 100
        else:
            self.hp = 1
            self.points = 30

        self.rect = self.image.get_rect()
        self.x = float(self.rect.x)

    def update(self):
        self.x += self.settings.alien_speed * self.settings.fleet_direction
        self.rect.x = self.x

    def check_edges(self):
        sr = self.screen.get_rect()
        return self.rect.right >= sr.right or self.rect.left <= 0
