import pygame

from constans import FONT_SIZ, FONT_PATH, BLACK, WHITE, GRAY
from core.game_state import Flags
from ui.ui_container import UIContainer
from ui.ui_elements import Label

class PauseMenu(UIContainer):
    def __init__(self, screen, flags: Flags):
        super().__init__(screen)

        self.is_open = False

        self.menu_options = []
        self.decide_options(flags)

        self.create_surface()
        self.build_menu()

    def decide_options(self, flags: Flags):
        if flags.get_flag("girl", "fellow"):
            self.menu_options = ["ステータス", "アイテム", "少女に声をかける", "閉じる"]
        else:
            self.menu_options = ["ステータス", "アイテム", "閉じる"]

    # surfaceを作成する
    def create_surface(self):
        self.size = self.screen.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(BLACK)
        self.surface.set_alpha(200)

    # メニューを作成する
    def build_menu(self):
        margin = 20
        y = self.size[1] // 2 - (len(self.menu_options) * FONT_SIZ + margin * (len(self.menu_options) - 1)) // 2
        for i, menu in enumerate(self.menu_options):
            lbl_menu = self.create_label(menu, y=y + i * (FONT_SIZ + margin), row=i)
            self.add(lbl_menu)

    # ラベルを作成する
    def create_label(self, text: str, y: int, row: int):
        font_data = (FONT_PATH, FONT_SIZ)
        label = Label(self.screen, font_data=font_data, text=text, x="center", y=y, anchor=("center", "center"), 
                      text_color=WHITE, hover_back_color=GRAY,
                      focusable=True, row=row)
        return label

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def handle_click(self, element):
        if element.texts[0] == "閉じる":
            self.close()
        
    def draw(self):
        if not self.is_open:
            return
        
        self.screen.blit(self.surface, (0, 0))
        super().draw()
