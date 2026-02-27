import pygame

class Ship:
    def __init__(self, ai_game):
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = self.screen.get_rect()

        self.image = pygame.image.load('images/ship.bmp').convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 60))
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.screen_rect.midbottom

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

        self.invincible = False
        self.invincible_timer = 0

    def update(self):
        if self.moving_right and self.rect.right < 1200:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        if self.moving_up and self.rect.top > 0:
            self.y -= self.settings.ship_speed
        if self.moving_down and self.rect.bottom < 800:
            self.y += self.settings.ship_speed

        self.rect.x = self.x
        self.rect.y = self.y

        if self.invincible:
            self.invincible_timer += 1
            if self.invincible_timer > 120:
                self.invincible = False
                self.invincible_timer = 0

    def blitme(self):
        if self.invincible and self.invincible_timer % 4 < 2:
            return
        self.screen.blit(self.image, self.rect)
