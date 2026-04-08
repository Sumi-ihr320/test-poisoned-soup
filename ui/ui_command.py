from dataclasses import dataclass
from typing import Sequence, Tuple, Any, Optional

from constans import FONT_PATH, SMALL_SIZ, BLACK, WHITE, BLUE
from utils import setting_font
from ui.ui_elements import Button
from ui.ui_container import UIContainer
from manager.sound_manager import sound_manager

@dataclass(frozen=True)
class Command:
    text: str
    next_scenario: str

class CommandButton(Button):
    def __init__(self, screen, font_data=(FONT_PATH, SMALL_SIZ), text="", rect=None, next_scenario="", text_color = BLACK, in_color = WHITE, out_color=BLACK, on_color = BLUE,
                 parent=None, result_type="scenario", sound_type="click", row=0, col=0, 
                 focusable=True, hover_text=None, **kwargs):
        super().__init__(screen, font_data=font_data, text=text, rect=rect, on_click=None, text_color=text_color, in_color=in_color, out_color=out_color, on_color=on_color, parent=parent, result_type=result_type, sound_type=sound_type, row=row, col=col, focusable=focusable, hover_text=hover_text, **kwargs)

        self.next_scenario = next_scenario

    def handle_click(self, pos) -> bool:
        if self.is_clicked(pos):
            if self.sound_type == "click":
                sound_manager.play("クリック")
            else:
                sound_manager.play("選択")
            self.on_click() # コールバック関数を呼び出す
            return self.next_scenario
        return None

# コマンドメニュー
class CommandMenu(UIContainer):
    def __init__(self, screen, commands: Sequence[Command], start_position: Tuple[int, int], parent: Optional[Any]=None):
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
                btn = CommandButton(screen=self.screen, text=cmd.text, rect=(x,y,max_width,h), 
                                    next_scenario=cmd.next_scenario, row=i)
                self.add(btn)
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
        for btn in self.children:
            btn.draw()
