from constans import *
from utils import *
from ui.ui_elements import *

class MenuController:
    def __init__(self, screen, root, callback, enableds=(True, True, True)) -> None:
        """
        enableds = (save, load, log)
        """
        self.screen = screen
        self.screen_size = self.screen.get_size()
        self.root = root
        self.callback = callback
        self.enableds = enableds

        self.menu = None
        self.create_menu()

    def create_menu(self):
        self.menu = Menu(self.screen, self.root, self.callback, self.enableds)

    def update_item_position(self, screen):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.menu.update_item_position(screen)

    def draw(self):
        self.menu.draw()

    def handle_mouse_hover(self, pos):
        for button in self.menu.buttons:
            button.handle_mouse_hover(pos)

    def handle_click(self, pos):
        for button in self.menu.buttons:
            if button.handle_click(pos):
                return True
        return False

# メニュー作るよ
class Menu(UIElement):
    def __init__(self, screen, root, callback=None, enableds=(True, True, True), parent=None, sound_type="click", row=0, col=0, forcusable=False, **kwargs):
        super().__init__(screen=screen, parent=parent, sound_type=sound_type, row=row, col=col, focusable=forcusable, **kwargs)
        self.root = root
        
        self.font_data = (FONT_PATH, FONT_SIZ)

        # 基準となるテキストフレームの位置を割り出す
        self.frame_rect = get_frame_rect(self.screen)

        # メニュー全体のサイズを割り出す
        self.size_calculation()

        self.callback = callback

        self.save_enabled, self.load_enabled, self.log_enabled = enableds

        self.buttons = []
        self.create_button()

    # 一つのボタン当たりのサイズを割り出す
    def size_calculation(self):
        font = pygame.font.Font(self.font_data[0], self.font_data[1])
        surface = font.render("セーブ", True, WHITE)
        rect = surface.get_rect()
        self.button_w = 100 if rect.w + 5 <= 100 else rect.w + 5
        self.button_h = 30 if rect.h + 2 <= 30 else rect.h + 2
        
        log_surface = font.render("ログ", True, WHITE)
        log_rect = log_surface.get_rect()
        self.log_button_w = 80 if log_rect.w + 5 <= 80 else log_rect.w + 5

        # メニュー全体のサイズ
        w, h = (self.button_w * 4) + self.log_button_w, self.button_h
        self.rect = Rect((self.frame_rect.right-w), (self.frame_rect.y-h), w, h)

    # ボタン作成
    def create_button(self):
        save_button = Button(self.screen, self.font_data, "セーブ", Rect(self.rect.x, self.rect.y, self.button_w, self.button_h), self.save_event, WHITE, BLACK, WHITE, GRAY, focusable=True)
        if not self.save_enabled:
            save_button.set_enabled(False)
        load_button = Button(self.screen, self.font_data, "ロード", Rect(self.rect.x+self.button_w, self.rect.y, self.button_w, self.button_h), self.load_event, WHITE, BLACK, WHITE, GRAY, col=1, focusable=True)
        if not self.load_enabled:
            load_button.set_enabled(False)
        setting_button = Button(self.screen, self.font_data, "設定", Rect(self.rect.x+(self.button_w*2), self.rect.y, self.button_w, self.button_h), self.setting_event, WHITE, BLACK, WHITE, GRAY, col=2, focusable=True)
        log_button = Button(self.screen, self.font_data, "ログ", Rect(self.rect.x+(self.button_w*3), self.rect.y, self.log_button_w, self.button_h), self.log_event, WHITE, BLACK, WHITE, GRAY, col=3, focusable=True)
        if not self.log_enabled:
            log_button.set_enabled(False)
        end_button = Button(self.screen, self.font_data, "終了", Rect(self.rect.x+(self.button_w*3+self.log_button_w), self.rect.y, self.button_w, self.button_h), self.end_event, WHITE, BLACK, WHITE, GRAY, col=4, focusable=True)
        self.buttons = [save_button, load_button, setting_button, log_button, end_button]

    def save_event(self):
        if self.callback:
            self.callback(State.SAVE)
    
    def load_event(self):
        if self.callback:
            self.callback(State.LOAD)

    def setting_event(self):
        if self.callback:
            self.callback(State.SETTING)

    def log_event(self):
        if self.callback:
            self.callback(State.LOG)

    def end_event(self):
        Close(self.root)

    def update_item_position(self, screen, parent=None):
        super().update_item_position(screen, parent)
        for button in self.buttons:
            button.update_item_position(screen, parent)

    def draw(self):
        for button in self.buttons:
            button.draw()
