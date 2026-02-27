import sys
import pygame
import random
from pygame.sprite import Group

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("Alien Invasion")

        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets = Group()
        self.alien_bullets = Group()
        self.aliens = Group()

        self.play_button = Button(self, "PLAY")
        self.game_active = False
        self.game_over = False
        self.game_over_time = 0

    def run_game(self):
        while True:
            self._check_events()
            if self.game_active and not self.game_over:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_alien_bullets()
            self._update_screen()

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.game_active:
                    self._check_play_button(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                self._keydown(event)
            elif event.type == pygame.KEYUP:
                self._keyup(event)

    def _keydown(self, e):
        if e.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif e.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif e.key == pygame.K_UP:
            self.ship.moving_up = True
        elif e.key == pygame.K_DOWN:
            self.ship.moving_down = True
        elif e.key == pygame.K_SPACE and self.game_active:
            self._fire_bullet()

    def _keyup(self, e):
        if e.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif e.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif e.key == pygame.K_UP:
            self.ship.moving_up = False
        elif e.key == pygame.K_DOWN:
            self.ship.moving_down = False

    def _check_play_button(self, pos):
        if self.play_button.rect.collidepoint(pos):
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            self.aliens.empty()
            self.bullets.empty()
            self.alien_bullets.empty()
            self._create_fleet()
            pygame.mouse.set_visible(False)

    def _fire_bullet(self):
        if len(self.bullets) < 3:
            self.bullets.add(Bullet(self))

    def _update_bullets(self):
        self.bullets.update()
        for b in self.bullets.copy():
            if b.rect.bottom <= 0:
                self.bullets.remove(b)
        self._check_bullet_alien()

    def _check_bullet_alien(self):
        collide = pygame.sprite.groupcollide(self.bullets, self.aliens, True, False)
        if collide:
            for aliens in collide.values():
                for a in aliens:
                    a.hp -= 1
                    if a.hp <= 0:
                        self.stats.score += a.points
                        self.aliens.remove(a)
            self.sb.prep_score()

        if not self.aliens:
            self.bullets.empty()
            self.stats.level += 1
            self.settings.increase_speed()
            self.sb.prep_level()
            self._create_fleet()

    def _create_fleet(self):
        base = 6
        add = self.stats.level - 1
        cols = min(base + add, 11)
        rows = min(3 + (add//2), 5)

        for row in range(rows):
            for col in range(cols):
                r = random.random()
                if r < 0.1:
                    t = 'red'
                elif r < 0.2:
                    t = 'blue'
                else:
                    t = 'normal'
                a = Alien(self, t)
                a.rect.x = 60 + col * 80
                a.rect.y = 60 + row * 70
                self.aliens.add(a)

    def _update_aliens(self):
        for a in self.aliens:
            a.update()
            if a.check_edges():
                self._change_fleet_dir()
                break

        if random.random() < 0.01:
            aliens = list(self.aliens)
            if aliens:
                a = random.choice(aliens)
                b = Bullet(self, True)
                b.rect.midtop = a.rect.midbottom
                self.alien_bullets.add(b)

        if not self.ship.invincible:
            if pygame.sprite.spritecollideany(self.ship, self.aliens):
                self._ship_hit()

    def _change_fleet_dir(self):
        for a in self.aliens:
            a.rect.y += 8
        self.settings.fleet_direction *= -1

    def _update_alien_bullets(self):
        self.alien_bullets.update()
        for b in self.alien_bullets.copy():
            if b.rect.top >= 800:
                self.alien_bullets.remove(b)

        if not self.ship.invincible:
            if pygame.sprite.spritecollideany(self.ship, self.alien_bullets):
                pygame.sprite.spritecollide(self.ship, self.alien_bullets, True)
                self._ship_hit()

    def _ship_hit(self):
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            self.ship.invincible = True
            self.ship.invincible_timer = 0
        else:
            self.game_active = False
            self.game_over = True
            self.game_over_time = pygame.time.get_ticks()
            pygame.mouse.set_visible(True)

    def _update_screen(self):
        self.screen.fill((0, 0, 0))

        if self.game_active:
            self.ship.blitme()
            for b in self.bullets:
                b.draw()
            for b in self.alien_bullets:
                b.draw()
            self.aliens.draw(self.screen)
            self.sb.show_score()

        if self.game_over:
            f = pygame.font.SysFont(None, 120)
            img = f.render("GAME OVER", True, (255,0,0))
            self.screen.blit(img, (350, 300))
            if pygame.time.get_ticks() - self.game_over_time > 3000:
                self.game_over = False

        if not self.game_active and not self.game_over:
            self.play_button.draw()

        pygame.display.flip()

if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
