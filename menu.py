import pygame

from constans import *
from utils import Close
from ui_elements import Button

class MenuController:
    def __init__(self, screen, root, callback, save_enabled=True, load_enabled=True) -> None:
        self.screen = screen
        self.root = root
        self.callback = callback

        self.menu = Menu(self.screen, self.root, self.callback,save_enabled, load_enabled)

    def draw(self):
        self.menu.draw()

    def handle_mouse_hover(self, pos):
        for button in self.menu.buttons:
            button.update(pos)

    def handle_click(self, pos):
        for button in self.menu.buttons:
            if button.update(pos, True):
                return True
        return False

# メニュー作るよ
class Menu:
    def __init__(self, screen, root, callback=None, save_enabled=True, load_enabled=True) -> None:
        self.screen = screen
        self.root = root
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)
        self.rect = MENU_FRAME_RECT.copy()
        self.callback = callback

        self.save_enabled = save_enabled
        self.load_enabled = load_enabled

        self.buttons = []
        self.create_button()

    # ボタン作成
    def create_button(self):
        save_button = Button(self.screen, self.font,"セーブ", Rect(self.rect.x, self.rect.y, self.rect.w,50), self.save_event, WHITE, BLACK, WHITE, GRAY)
        load_button = Button(self.screen, self.font,"ロード", Rect(self.rect.x, self.rect.y+50, self.rect.w,50), self.load_event, WHITE, BLACK, WHITE, GRAY)
        end_button = Button(self.screen, self.font,"終了", Rect(self.rect.x, self.rect.y+100, self.rect.w,50), self.end_event, WHITE, BLACK, WHITE, GRAY)
        self.buttons = [save_button, load_button, end_button]

    def save_event(self):
        if self.callback:
            self.callback(State.SAVE)
    
    def load_event(self):
        if self.callback:
            self.callback(State.LOAD)

    def end_event(self):
        Close(self.root)

    def draw(self):
        for button in self.buttons:
            if (not self.save_enabled and button.text == "セーブ") or (not self.load_enabled and button.text == "ロード"):
                button.set_enabled(False)
            button.draw()
