from utils import *
from ui.ui_elements import Button

# 右クリック時に表示するコマンドメニュー
class RightClickCommandMenu:
    def __init__(self, screen, player, girl, flags, game_state, start_position):
        self.screen = screen
        self.window_size = self.screen.get_width()
        
        self.player = player
        self.girl = girl
        self.flags = flags
        self.game_state = game_state

        self.start_x, self.start_y = start_position

        #["ステータス(自分ののみ)","仲間(少女に対して何をするか、させるか)","アイテム","技能","そこで使えるコマンド"]
        self.command_list = ["ステータス", "仲間", "アイテム", "技能"]
        self.buttons = []
        self.create_buttons()

    # コマンドボタンを作成
    def create_buttons(self):
        font = setting_font(FONT_PATH, SMALL_SIZ, self.window_size)
        x, y = self.start_x, self.start_y
        h = 30

        # コマンドの中で最も長いwidthを取得する
        max_width = 120     # 最小値
        if self.command_list:
            for command in self.command_list:
                text_surface = font.render(command, True, BLACK)
                text_width = text_surface.get_width() + 10
                max_width = max(max_width, text_width)

        if self.command_list:
            for command in self.command_list:
                button = Button(self.screen, font, command, (x,y,max_width,h), out_color=BLACK)
                self.buttons.append(button)
                y += h

    def status_event(self):
        pass

    def handle_click(self):
        pass

    def draw(self):
        for button in self.buttons:
            button.draw()
