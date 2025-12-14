import pygame

from utils import *
from ui.ui_elements import *

# メニュー用のボタン
class MenuButton(Button):
    def __init__(self, screen, font_data, text, rect, on_click=None, enabled=True,
                 parent=None, row=0, col=0, focusable=True, **kwargs):
        super().__init__(screen=screen, font_data=font_data, text=text, rect=rect,
                         on_click=on_click, text_color=WHITE, in_color=BLACK, out_color=WHITE, on_color=GRAY,
                         parent=parent, sound_type="click", row=row, col=col, focusable=focusable, **kwargs)

        self.enabled = enabled
        # focusable は enabled に従う。
        self.focusable = bool(self.enabled)

        if not self.enabled:
            self._set_color()

    # ボタンの有効無効によって各カラーを設定する
    def _set_color(self):
        if self.enabled:
            self.text_color = WHITE
            self.in_color = BLACK
            self.out_color = WHITE
        else:
            self.text_color = (180, 180, 180)
            self.in_color = (40, 40, 40)
            self.out_color = (180, 180, 180)
        
        # textカラーが変わったらtext_surfaceも更新する
        self.update_text_surface()
            
    # ボタンの有効・無効を切り替える    
    def set_enabled(self, state: bool):
        self.enabled = state
        self.focusable = state
        self._set_color()

    def is_clicked(self, pos):
        # enabled=Falseの時はクリック判定しない
        if not self.enabled:
            return False
        return self.collidepoint(pos)

    def handle_mouse_hover(self, pos):
        # enabled=Falseの時はhover無効
        if self.enabled:
            hover = self.collidepoint(pos)
            if hover and not self.hovered:  # 初めてホバーした時
                sound_manager.play("カーソル移動")
            self.hovered = hover

    def draw_button(self):
        # マウスオーバー時ボタンの色を変える
        color = self.on_color if (self.hovered and self.enabled) else self.in_color

        # ボタンの内側
        pygame.draw.rect(self.parent_surface, color, self.rect)
        # ボタンの外枠
        pygame.draw.rect(self.parent_surface, self.out_color, self.rect, 2)

# メニューボタンを並べたバー
class MenuBar(UIElement):
    """
    MenuBarはテキストフレームの上部に並ぶ複数のMenuButtonを管理する。
    sceneからはcreateボタン、set_enabled(index, bool)、register_all(focus_manager)などで操作する。
    """
    PADDING = 0
    def __init__(self, screen, font_data, callback, enabled_flag={"セーブ":True, "ロード":True, "ログ":True}, parent=None, sound_type="click", row=0, col=0, focusable=False, **kwargs):
        """
        labels_with_callbacks: [(label_text, callback, enabled_bool, col_opt), ...]
        parent: 通常 TextFramePanel か screen。 親のsurface座標を基準に配置する。
        """
        super().__init__(screen=screen, parent=parent, sound_type=sound_type, row=row, col=col, focusable=focusable, **kwargs)

        self.font_data = font_data
        self.callback = callback

        self.enabled_flag = enabled_flag
        self.menu_items = [
            ("セーブ", self.on_save, enabled_flag["セーブ"], 0),
            ("ロード", self.on_load, enabled_flag["ロード"], 1),
            ("設定", self.on_setting, True, 2),
            ("ログ", self.on_log, enabled_flag["ログ"], 3),
            ("終了", self.on_exit, True, 4)
        ]

        self.buttons = []
        self._build(self.menu_items)

    # メニューボタンを作成する
    def _build(self, labels_with_callbacks):
        x0, y0, widths, h = self.calculation_rect(labels_with_callbacks)

        cur_x = x0
        btns = []
        for i, (label, cd, enabled, col) in enumerate(labels_with_callbacks):
            w = widths[i]
            rect = Rect(cur_x, y0, w, h)
            btn = MenuButton(self.screen, self.font_data, label, rect, on_click=cd, enabled=enabled, parent=self.parent, row=90, col=(col if col is not None else i))
            btns.append(btn)
            cur_x += w + self.PADDING

        self.buttons = btns

        """
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
        """

    # メニューバー全体のrectを計算する
    def calculation_rect(self, labels_with_callbacks):
        font = setting_font(self.font_data[0], self.font_data[1], self.screen_size)
        widths = []
        heights = []
        for label, cb, enabled, col in labels_with_callbacks:
            surf = font.render(label, True, WHITE)
            w, h = surf.get_size()
            widths.append(w + 10)
            heights.append(h + 8)
        total_w = sum(widths) + (len(widths)-1) * self.PADDING if widths else 0
        h = max(heights) if heights else 0

        # parent のフレームを基準に右寄せで配置
        frame_rect = self.parent.get_rect()
        x0 = frame_rect.right - total_w - self.PADDING
        y0 = frame_rect.y - h

        self.rect = Rect(x0, y0, total_w, h)

        return x0, y0, widths, h

    def on_save(self):
        if self.callback:
            self.callback(State.SAVE)
    
    def on_load(self):
        if self.callback:
            self.callback(State.LOAD)

    def on_setting(self):
        if self.callback:
            self.callback(State.SETTING)

    def on_log(self):
        if self.callback:
            self.callback(State.LOG)

    def on_exit(self):
        Close(self.root)

    def draw(self):
        for btn in self.buttons:
            btn.draw()

    def update_item_position(self, screen, parent=None):
        super().update_item_position(screen, parent)
        for btn in self.buttons:
            btn.update_item_position(screen, parent)

    # enabled/disable 個別操作
    def set_enabled(self, idx, enabled: bool):
        if 0 < idx < len(self.buttons):
            self.buttons[idx].set_enabled(enabled)

    # FocusManagerとの一括登録
    def register_all(self, focus_manager):
        for btn in self.buttons:
            if btn.is_focusable():
                focus_manager.register(btn)

    # FocusManagerとの一括解除
    def unregister_all(self, focus_manager):
        for btn in self.buttons:
            if btn in focus_manager.elements:
                focus_manager.elements.remove(btn)

    def handle_mouse_hover(self, pos):
        for btn in self.buttons:
            btn.handle_mouse_hover(pos)

    def handle_click(self, pos):
        for btn in self.buttons:
            if btn.handle_click(pos):
                return True
        return False


class TextFramePanel(UIElement):
    PADDING = 10
    def __init__(self, screen, parent=None, font_data=(FONT_PATH, FONT_SIZ), frame_size=FRAME_SIZE, next_callback=None, enabled_flag={"セーブ":True, "ロード":True, "ログ":True}, sound_type="click", row=0, col=0, focusable=False, **kwargs):
        super().__init__(screen=screen, parent=parent, sound_type=sound_type, row=row, col=col, focusable=focusable, **kwargs)
        self.frame_size = frame_size
        self.margin_bottom = 30

        # テキストフレームのrect計算
        self.rect = self.calc_frame_rect()

        self.font_data = font_data

        # メニューバー
        self.menu_bar = MenuBar(screen=self.screen, font_data=self.font_data, callback=next_callback, enabled_flag=enabled_flag, parent=self)

        # 内部ラベル
        self.text_label = TextFrameLabel(screen=self.screen, frame_rect=self.rect, parent=self.parent, font_data=self.font_data)

        # Nextボタン
        #btn_w, btn_h = (40, 28)
        #next_x = self.rect.right - btn_w - self.PADDING
        #next_y = self.rect.bottom - btn_h - self.PADDING
        next_x = self.rect.right - self.PADDING
        next_y = self.rect.bottom - self.PADDING
        # next_rect = Rect(self.rect.right - btn_w - self.PADDING, self.rect.bottom - btn_h - self.PADDING, btn_w, btn_h)
        self.next_label = Label(screen=self.screen, font_data=self.font_data, text="▶", x=next_x, y=next_y, anchor=("right", "bottom"), text_color=WHITE, parent=self, row=100, focusable=True)

        #self.children = []
        #self.focusables = []    # focur_managerに渡す用

    # テキストフレームのrectを割り出す
    def calc_frame_rect(self):
        screen_w, screen_h = self.screen_size
        frame_w, frame_h = get_new_size(self.screen_size, (FRAME_SIZE))
        frame_x = (screen_w // 2) - (frame_w // 2)
        frame_y = screen_h - (frame_h + self.margin_bottom)

        return Rect(frame_x, frame_y, frame_w, frame_h)

    def regster_all(self, focus_manager):
        self.menu_bar.register_all(focus_manager)
        focus_manager.regster(self.next_label)

    #def add_child(self, element):
    #    self.children.append(element)
    #    if element.focusable:
    #        self.focusables.append(element)

    def set_text(self, text):
        self.text_label.set_text(text)

    def add_log_entry(self, log_view, text):
        log_view.append(text)
        pass

    def update_item_position(self, screen, parent=None):
        super().update_item_position(screen, parent)
        self.menu_bar.update_item_position(screen, self)
        self.text_label.update_item_position(screen, self.rect, self)
        self.next_label.update_item_position(screen, self)

    def draw(self):
        # テキストフレームの描画
        pygame.draw.rect(self.screen, WHITE, self.rect, 3)

        # メニューバーの描画    
        if self.menu_bar:
            self.menu_bar.draw()
        # テキストラベルの描画
        if self.text_label:
            self.text_label.draw()
        # nextボタンの描画
        if self.next_label:
            self.next_label.draw()

    def handle_mouse_hover(self, pos):
        self.menu_bar.handle_mouse_hover(pos)
        self.next_label.handle_mouse_hover(pos)

    def handle_click(self, pos):
        if self.menu_bar.handle_click(pos):
            return True
        elif self.next_label.handle_click(pos):
            return True
        else:
            return False
