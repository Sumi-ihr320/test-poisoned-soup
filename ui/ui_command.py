from dataclasses import dataclass
from typing import Sequence

from constans import *
from utils import setting_font
from ui.ui_elements import Button
from ui.ui_container import UIContainer

@dataclass(frozen=True)
class Command:
    text: str
    next_scenario: str

# コマンドメニュー
class CommandMenu(UIContainer):
    def __init__(self, screen, commands: Sequence[Command], start_position, parent=None):
        super().__init__(screen, parent)
        
        self.commands = commands
        self.start_x, self.start_y = start_position
        self._build()

    # コマンドリストからボタンを作成
    def _build(self):
        x, y = self.start_x, self.start_y
        h = 30

        max_width = self._calc_max_width()

        if self.commands:
            for i, cmd in enumerate(self.commands):
                btn = Button(screen=self.screen, font_data=(FONT_PATH, SMALL_SIZ), text=cmd.text, rect=(x,y,max_width,h), out_color=BLACK, row=i, focusable=True)
                self.add((btn, cmd))
                y += h

    # コマンドの中で最も長いwidthを取得する
    def _calc_max_width(self):
        font = setting_font(FONT_PATH, SMALL_SIZ, self.screen_size)
        max_width = 120     # 最小値
        if self.commands:
            for cmd in self.commands:
                width = font.render(cmd.text, True, BLACK).get_width() + 10
                max_width = max(max_width, width)

        return max_width

    def draw(self):
        for btn, _ in self.children:
            btn.draw()

    def handle_mouse_hover(self, pos):
        for btn, _ in self.children:
            btn.update(pos)

    def handle_click(self, pos):
        # クリックされたイベントを判定
        for btn, cmd in self.children:
            if btn.is_clicked(pos):
                return cmd.next_scenario
        return None
