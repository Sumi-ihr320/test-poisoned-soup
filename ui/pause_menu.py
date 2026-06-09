import pygame

from constans import FONT_SIZ, FONT_PATH, BLACK, WHITE, GRAY
from utils import get_scales
from core.game_state import Flags
from ui.ui_container import UIContainer
from ui.ui_elements import Label

class PauseMenuLabel(Label):
    def __init__(self, screen, font_data, text, x="center", y = 0, centerx = None, centery = None, anchor=("center", "center"), 
                 text_color=WHITE, background_color = None, hover_type = "box", hover_line_bold = 1, 
                 hover_text_color = None, hover_back_color=GRAY, hover_text = None, action_text: str=None,
                 result_type = None, sound_type = "click", row = 0, col = 0, focusable=True, parent = None, **kwargs):
        super().__init__(screen, font_data, text, x, y, centerx, centery, anchor, text_color, background_color, hover_type, hover_line_bold, hover_text_color, hover_back_color, hover_text, result_type, sound_type, row, col, focusable, parent, **kwargs)

        self.action = action_text

    def handle_click(self, pos) -> bool:
        if self.collidepoint(pos):
            self.on_decide()
            return self.action
        return None
    
class PauseMenu(UIContainer):
    def __init__(self, screen, flags: Flags):
        super().__init__(screen)

        self.is_open = False

        self.decide_options(flags)

        self.create_surface()
        self.build_menu()

    # メニューの選択肢を確認する
    def decide_options(self, flags: Flags):
        self.menu_options = []
        menu_options = [
            {"label": "ステータス", "action": "status"},
            {"label": "アイテム", "action": "inventory"},
            {"label": "少女に声をかける", "action": "talk_girl"},
            {"label": "閉じる", "action": "close"}
        ]
        for menu in menu_options:
            if menu["label"] == "少女に声をかける":
                if flags.get_flag("girl", "fellow"):
                    self.menu_options.append(menu)
            else:
                self.menu_options.append(menu)

    # surfaceを作成する
    def create_surface(self):
        self.size = self.screen.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(BLACK)
        self.surface.set_alpha(200)

    # フォントサイズを計算する
    def calculate_font_size(self):
        _, _, aspect = get_scales(self.screen_size)
        self.font_size = int(FONT_SIZ * aspect)

    # メニューを作成する
    def build_menu(self):
        margin = 20
        self.calculate_font_size()
        font_data = (FONT_PATH, self.font_size)

        y = self.size[1] // 2 - (len(self.menu_options) * self.font_size + margin * (len(self.menu_options) - 1)) // 2
        for i, menu in enumerate(self.menu_options):
            lbl_menu = PauseMenuLabel(self.screen, font_data=font_data, text=menu["label"], y=y + i * (self.font_size + margin), 
                                      action_text=menu["action"], row=i)
            self.add(lbl_menu)

    def open(self, flags: Flags):
        self.is_open = True
        self.clear()
        self.decide_options(flags)
        self.build_menu()

    def close(self):
        self.is_open = False

    def handle_click(self, result: str):
        selected_action = result

        if selected_action == "close":
            self.close()
        
        elif selected_action == "status":
            pass

        elif selected_action == "inventory":
            pass

        return selected_action

    def relayout(self, screen, parent=None):
        super().relayout(screen, parent)
        self.create_surface()
        self.clear()
        self.build_menu()

    def draw(self):
        if not self.is_open:
            return
        
        self.screen.blit(self.surface, (0, 0))
        super().draw()
