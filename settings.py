class Settings:
    """存储游戏所有设置的类"""
    def __init__(self):
        """初始化游戏的静态设置"""
        # 屏幕设置
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (0, 0, 255)  # 背景色（蓝色）

        # 飞船设置
        self.ship_speed = 1.5
        self.ship_limit = 3  # 飞船总命数

        # 子弹设置
        self.bullet_speed = 2.5
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (255, 255, 255)  # 玩家子弹白色
        self.bullets_allowed = 5  # 最大子弹数

        # 外星人设置
        self.alien_speed = 0.5
        self.fleet_drop_speed = 10
        # fleet_direction为1表示向右，-1表示向左
        self.fleet_direction = 1

        # 外星人子弹设置
        self.alien_bullet_speed = 1.2
        self.alien_bullet_color = (255, 165, 0)  # 外星人子弹橙色

        # 游戏节奏加快的设置
        self.speedup_scale = 1.1
        self.score_scale = 1.5

        # 补全缺失的初始化动态设置方法！
        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """初始化随游戏进行而变化的设置"""
        self.ship_speed = 1.5
        self.bullet_speed = 2.5
        self.alien_speed = 0.5
        self.fleet_direction = 1  # 1表示向右

    def increase_speed(self):
        """提高速度设置和分数值"""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
