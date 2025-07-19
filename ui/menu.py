from constans import *
from utils import *
from ui.ui_elements import Button

class MenuController:
    def __init__(self, screen, root, callback, save_enabled=True, load_enabled=True) -> None:
        self.screen = screen
        self.window_size = self.screen.get_size()
        self.root = root
        self.callback = callback
        self.save_enabled = save_enabled
        self.load_enabled = load_enabled

        self.menu = None
        self.create_menu()

    def create_menu(self):
        self.menu = Menu(self.screen, self.root, self.callback, self.save_enabled, self.load_enabled)

    def update_item_position(self, screen):
        self.screen = screen
        self.create_menu()

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
        self.window_size = self.screen.get_size()
        self.root = root

        self.set_font()
        
        # 基準となるテキストフレームの位置を割り出す
        self.frame_rect = get_frame_rect(self.screen)

        # メニュー全体のサイズを割り出す
        self.size_calculation()

        self.callback = callback

        self.save_enabled = save_enabled
        self.load_enabled = load_enabled

        self.buttons = []
        self.create_button()

    def set_font(self):
        self.font = setting_font(FONT_PATH, FONT_SIZ, self.window_size)

    def size_calculation(self):
        # 一つのボタン当たりのサイズを割り出す
        surface = self.font.render("セーブ", True, WHITE)
        rect = surface.get_rect()
        self.button_w = 100 if rect.w + 5 <= 100 else rect.w + 5
        self.button_h = 30 if rect.h + 2 <= 30 else rect.h + 2
        
        # メニュー全体のサイズ
        w, h = self.button_w * 4, self.button_h
        self.rect = Rect((self.frame_rect.right-w), (self.frame_rect.y-h), w, h)

    # ボタン作成
    def create_button(self):
        save_button = Button(self.screen, self.font, "セーブ", Rect(self.rect.x, self.rect.y, self.button_w, self.button_h), self.save_event, WHITE, BLACK, WHITE, GRAY)
        load_button = Button(self.screen, self.font, "ロード", Rect(self.rect.x+self.button_w, self.rect.y, self.button_w, self.button_h), self.load_event, WHITE, BLACK, WHITE, GRAY)
        setting_button = Button(self.screen, self.font, "設定", Rect(self.rect.x+(self.button_w*2), self.rect.y, self.button_w, self.button_h), self.setting_event, WHITE, BLACK, WHITE, GRAY)
        end_button = Button(self.screen, self.font, "終了", Rect(self.rect.x+(self.button_w*3), self.rect.y, self.button_w, self.button_h), self.end_event, WHITE, BLACK, WHITE, GRAY)
        self.buttons = [save_button, load_button, setting_button, end_button]

    def save_event(self):
        if self.callback:
            self.callback(State.SAVE)
    
    def load_event(self):
        if self.callback:
            self.callback(State.LOAD)

    def setting_event(self):
        if self.callback:
            self.callback(State.SETTING)

    def end_event(self):
        Close(self.root)

    def draw(self):
        for button in self.buttons:
            if (not self.save_enabled and button.text == "セーブ") or (not self.load_enabled and button.text == "ロード"):
                button.set_enabled(False)
            button.draw()

# 画面サイズが変更された時メニューの表示を更新
def update_menu(screen, menu_controller):
    if get_frame_rect(screen) != menu_controller.menu.frame_rect:
        menu_controller.screen = screen
        menu_controller.create_menu()
    return menu_controller
