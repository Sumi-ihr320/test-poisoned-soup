from typing import Optional

from constans import BLACK, GRAY, WHITE, BLUE
from ui.ui_elements import Label, Button
from ui.ui_input_box import InputBox
from manager.sound_manager import sound_manager

# コンテナ用のラベル（クリックした際に親コンテナを返す）
class ContainerLabel(Label):
    def __init__(self, screen, font_data, text, x = 0, y = 0, centerx = None, centery = None, anchor = ("left", "top"), text_color = BLACK, background_color = None, hover_type = "box", hover_line_bold = 1, hover_text_color = None, hover_back_color = WHITE, hover_text = None, sound_type = "click", row = 0, col = 0, focusable = False, parent = None, **kwargs):
        super().__init__(screen, font_data, text, x, y, centerx, centery, anchor, text_color, background_color, hover_type, hover_line_bold, hover_text_color, hover_back_color, hover_text, sound_type, row, col, focusable, parent, **kwargs)

    def handle_click(self, pos) -> bool:
        if self.collidepoint(pos):
            self.on_decide()
            return self.parent
        return False

# コンテナ用のボタン（クリックした際に親コンテナを返す）
class ContainerButton(Button):
    def __init__(self, screen, font_data, text, rect, on_click = None, text_color = BLACK, in_color = WHITE, out_color = GRAY, on_color = BLUE, parent = None, sound_type = "click", row = 0, col = 0, focusable = False, hover_text = None, **kwargs):
        super().__init__(screen, font_data, text, rect, on_click, text_color, in_color, out_color, on_color, parent, sound_type, row, col, focusable, hover_text, **kwargs)

    def handle_click(self, pos) -> bool:
        if self.is_clicked(pos):
            if self.sound_type == "click":
                sound_manager.play("クリック")
            else:
                sound_manager.play("選択")
            self.on_click() # コールバック関数を呼び出す
            return self.parent
        return None

# コンテナ用のInputBox（クリックした際に親コンテナを返す）
class ContainerInputBox(InputBox):
    def __init__(self, screen, root, font_data, rect, label_text = "", input_flag = True, line_bold = 2, 
                 sound_type = "click", row = 0, col = 0, focusable = False, parent = None, 
                 hover_text: Optional[str] = None, **kwargs):
        super().__init__(screen, root, font_data, rect, label_text, input_flag, line_bold, sound_type, row, col, focusable, parent, hover_text=hover_text, **kwargs)
    
    def handle_click(self, pos) -> bool:
        if self.collidepoint(pos):
            self.on_decide()
            return self.parent
        return None

