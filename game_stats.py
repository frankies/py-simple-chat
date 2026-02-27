class GameStats:
    def __init__(self, ai_game):
        self.settings = ai_game.settings
        self.reset_stats()
        self.game_active = False
        self.high_score = 0  # 最高分得持久化可自行添加

    def reset_stats(self):
        self.ships_left = 3  # 左下角3个飞船图标
        self.score = 0
        self.level = 1
        # 重置无敌状态（核心新增）
        self.ship_invincible = False
