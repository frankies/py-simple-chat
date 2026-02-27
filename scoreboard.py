import pygame.font

class Scoreboard:
    def __init__(self, ai_game):
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats

        self.font = pygame.font.SysFont(None, 48)
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships()

    def prep_score(self):
        self.score_img = self.font.render(str(self.stats.score), True, (255,255,255), self.settings.bg_color)
        self.score_rect = self.score_img.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 20

    def prep_high_score(self):
        self.high_img = self.font.render(str(self.stats.high_score), True, (255,255,255), self.settings.bg_color)
        self.high_rect = self.high_img.get_rect()
        self.high_rect.centerx = self.screen_rect.centerx
        self.high_rect.top = 20

    def prep_level(self):
        self.level_img = self.font.render(f"Lv{self.stats.level}", True, (255,255,255), self.settings.bg_color)
        self.level_rect = self.level_img.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top = self.score_rect.bottom + 10

    def prep_ships(self):
        # 不用Group，直接存飞船图片和位置，彻底避免报错
        self.ship_images = []
        ship_img = pygame.image.load('images/ship.bmp')
        ship_img = pygame.transform.scale(ship_img, (30, 45))
        for i in range(self.stats.ships_left):
            rect = ship_img.get_rect()
            rect.x = 10 + i * (rect.width + 10)  # 横向排列
            rect.y = self.screen_rect.bottom - rect.height - 10  # 左下角显示
            self.ship_images.append((ship_img, rect))

    def show_score(self):
        # 绘制分数、等级、最高分
        self.screen.blit(self.score_img, self.score_rect)
        self.screen.blit(self.high_img, self.high_rect)
        self.screen.blit(self.level_img, self.level_rect)
        # 绘制左下角的飞船命数（实时显示剩余数量）
        for img, rect in self.ship_images:
            self.screen.blit(img, rect)

    def check_high_score(self):
        """检查是否诞生了新的最高分"""
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()  # 更新最高分的显示
