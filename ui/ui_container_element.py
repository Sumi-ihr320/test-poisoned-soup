from typing import Optional, Tuple

from constans import BLACK, GRAY, WHITE, BLUE
from utils import pos_to_local
from ui.ui_elements import Label, Button, Image
from ui.ui_input_box import InputBox
from ui.ui_pull_down import PullDown
from manager.sound_manager import sound_manager

# コンテナ用のラベル（クリックした際に親コンテナを返す）
class ContainerLabel(Label):
    def __init__(self, screen, font_data, parent_container, text, x = 0, y = 0, centerx = None, centery = None, anchor = ("left", "top"), text_color = BLACK, background_color = None, hover_type = "box", hover_line_bold = 1, hover_text_color = None, hover_back_color = WHITE, hover_text = None, sound_type = "click", row = 0, col = 0, focusable = False, parent = None, **kwargs):
        super().__init__(screen, font_data, text, x, y, centerx, centery, anchor, text_color, background_color, hover_type, hover_line_bold, hover_text_color, hover_back_color, hover_text, sound_type, row, col, focusable, parent, **kwargs)
        self.parent_container = parent_container

    def handle_click(self, pos) -> bool:
        if self.collidepoint(pos):
            self.on_decide()
            return self.parent_container
        return False

# コンテナ用のボタン（クリックした際に親コンテナを返す）
class ContainerButton(Button):
    def __init__(self, screen, font_data, parent_container, text, rect, on_click = None, text_color = BLACK, in_color = WHITE, out_color = GRAY, on_color = BLUE, parent = None, sound_type = "click", row = 0, col = 0, focusable = False, hover_text = None, **kwargs):
        super().__init__(screen, font_data, text, rect, on_click, text_color, in_color, out_color, on_color, parent, sound_type, row, col, focusable, hover_text, **kwargs)
        self.parent_container = parent_container

    def handle_click(self, pos) -> bool:
        if self.is_clicked(pos):
            if self.sound_type == "click":
                sound_manager.play("クリック")
            else:
                sound_manager.play("選択")
            self.on_click() # コールバック関数を呼び出す
            return self.parent_container
        return None

class ContainerImage(Image):
    def __init__(self, screen, parent_container, path, cache = None, scale = None, x = 0, y = 0, centerx = None, centery = None, 
                 line_flag = False, line_width = 1, bg_flag = False, size_wh = None, anchor = ..., 
                 parent = None, sound_type = "click", row = 0, col = 0, focusable = False, 
                 hover_text = None, **kwargs):
        super().__init__(screen, path, cache, scale, x, y, centerx, centery, line_flag, line_width, bg_flag, size_wh, anchor, parent, sound_type, row, col, focusable, hover_text, **kwargs)
        self.parent_container = parent_container
    
    def handle_click(self, pos) -> bool:
        if self.collidepoint(pos):
            self.on_decide()
            return self.parent_container
        return None

# コンテナ用のInputBox（クリックした際に親コンテナを返す）
class ContainerInputBox(InputBox):
    def __init__(self, screen, root, font_data, parent_container, rect, label_text = "", input_flag = True, line_bold = 2, 
                 sound_type = "click", row = 0, col = 0, focusable = False, parent = None, 
                 hover_text: Optional[str] = None, **kwargs):
        super().__init__(screen, root, font_data, rect, label_text, input_flag, line_bold, sound_type, row, col, focusable, parent, hover_text=hover_text, **kwargs)
        self.parent_container = parent_container
    
    def handle_click(self, pos) -> bool:
        if self.collidepoint(pos):
            self.on_decide()
            return self.parent_container
        return None

class ContainerPullDown(PullDown):
    def __init__(self, screen, font_data, parent_container, rect, item_list, label_text = "", pd_h = 285, 
                 parent = None, sound_type = "click", row = 0, col = 0, focusable = False, 
                 hover_text = None, **kwargs):
        super().__init__(screen, font_data, rect, item_list, label_text, pd_h, parent, sound_type, row, col, focusable, hover_text, **kwargs)
        self.parent_container = parent_container

    # クリック時の動作
    def handle_click(self, pos: Tuple[int, int], is_dropped: bool) -> Optional[str]:
        if is_dropped and self.list_box and self.list_box.collidepoint(pos):
            hit_pos = pos_to_local(pos, self.parent)
            for text, surf, text_rect, hit_rect in self.entries:
                if hit_rect.collidepoint(hit_pos):
                    sound_manager.play("クリック")
                    return {"text": text, "container": self.parent_container}
        return None
