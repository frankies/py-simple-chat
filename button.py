import pygame.font

class Button:  # 类名必须是Button（首字母大写），和导入语句匹配
    def __init__(self, ai_game, msg):
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()

        # 按钮尺寸、颜色设置
        self.width, self.height = 200, 50
        self.button_color = (0, 255, 0)  # 绿色按钮
        self.text_color = (255, 255, 255)  # 白色文字
        self.font = pygame.font.SysFont(None, 48)

        # 创建按钮矩形并居中
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center

        # 渲染按钮文字
        self._prep_msg(msg)

    def _prep_msg(self, msg):
        """将msg渲染为图像，并居中显示在按钮上"""
        self.msg_image = self.font.render(msg, True, self.text_color, self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw(self):
        """绘制按钮（先画矩形，再画文字）"""
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)

    # 兼容旧调用：添加draw_button方法（避免game.py中忘记改的情况）
    def draw_button(self):
        self.draw()
        
