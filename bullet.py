import pygame
from pygame.sprite import Sprite

class Bullet(Sprite):
    def __init__(self, ai_game, alien_bullet=False):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.alien_bullet = alien_bullet

        # 子弹样式：玩家白色，外星人红色
        color = (255, 0, 0) if alien_bullet else (255, 255, 255)
        self.image = pygame.Surface((5, 15))
        self.image.fill(color)
        self.rect = self.image.get_rect()

        # 初始位置
        if not alien_bullet:
            self.rect.midtop = ai_game.ship.rect.midtop
        else:
            self.rect.midbottom = ai_game.ship.rect.midbottom  # 外星人子弹向下

        self.y = float(self.rect.y)

    def update(self):
        # 玩家子弹向上，外星人子弹向下
        speed = self.settings.bullet_speed
        self.y -= speed if not self.alien_bullet else -speed
        self.rect.y = self.y

    def draw(self):
        self.screen.blit(self.image, self.rect)
