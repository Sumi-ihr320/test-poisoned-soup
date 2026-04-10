from typing import List, Dict, Tuple, Any, Optional, Callable
import pygame
from pygame import Rect

from constans import FONT_PATH, FONT_SIZ, FRAME_SIZE, WHITE, BLACK, GRAY, State
from utils import get_new_size, setting_font, Close
from manager.sound_manager import sound_manager
from ui.ui_elements import Button, TextFrameLabel, Label
from ui.ui_container import UIContainer
from ui.log_view import LogView
from input.focus_manager import FocusManager

# メニュー用のボタン
class MenuButton(Button):
    def __init__(self, screen, font_data, text: str, rect: Rect, on_click: Callable=None, enabled: bool=True,
                 parent: Optional[Any]=None, result_type: Optional[str]="menu", row: int=0, col: int=0, focusable: bool=True, **kwargs):
        super().__init__(screen=screen, font_data=font_data, text=text, rect=rect,
                         on_click=on_click, text_color=WHITE, in_color=BLACK, out_color=WHITE, on_color=GRAY,
                         parent=parent, result_type=result_type, sound_type="click", row=row, col=col, focusable=focusable, **kwargs)

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

    def is_clicked(self, pos) -> bool:
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
class MenuBar(UIContainer):
    """
    MenuBarはテキストフレームの上部に並ぶ複数のMenuButtonを管理する。
    sceneからはcreateボタン、set_enabled(index, bool)、register_all(focus_manager)などで操作する。
    """
    PADDING = 0
    def __init__(self, screen, root, frame_rect: Rect, font_data: Tuple[str, int], callback: Callable, enabled_flags: Dict[str, bool]={"セーブ":True, "ロード":True, "ログ":True}, 
                 parent: Optional[Any]=None):
        super().__init__(screen, parent)
        self.root = root

        self.frame_rect = frame_rect

        self.font_data = font_data
        self.callback = callback

        self.enabled_flags = enabled_flags
        self.menu_items = [
            ("セーブ", self.on_save, enabled_flags["セーブ"], 0),
            ("ロード", self.on_load, enabled_flags["ロード"], 1),
            ("設定", self.on_setting, True, 2),
            ("ログ", self.on_log, enabled_flags["ログ"], 3),
            ("終了", self.on_exit, True, 4)
        ]

        self._build(self.menu_items)

    # メニューボタンを作成する
    def _build(self, labels_with_callbacks: List[Tuple[str, Callable, bool, Optional[int]]]):
        x0, y0, widths, h = self.calculation_rect(labels_with_callbacks)

        cur_x = x0
        btns = []
        for i, (label, cd, enabled, col) in enumerate(labels_with_callbacks):
            w = widths[i]
            rect = Rect(cur_x, y0, w, h)
            btn = MenuButton(self.screen, font_data=self.font_data, text=label, rect=rect, on_click=cd, enabled=enabled, 
                             parent=self.parent, row=90, col=(col if col is not None else i))
            btns.append(btn)
            cur_x += w + self.PADDING

        self.children = btns

    # メニューバー全体のrectを計算する
    def calculation_rect(self, labels_with_callbacks: List[Tuple[str, Callable, bool, Optional[int]]]) -> Tuple[int, int, List[int], int]:
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

        # テキストフレームを基準に右寄せで配置
        x0 = self.frame_rect.right - total_w - self.PADDING
        y0 = self.frame_rect.y - h

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

    # enabled/disable 個別操作
    def set_enabled(self, idx: int, enabled: bool):
        if 0 < idx < len(self.children):
            self.children[idx].set_enabled(enabled)

# テキストフレーム本体
class TextFramePanel(UIContainer):
    PADDING = 10
    def __init__(self, screen, root, parent: Optional[Any]=None, font_data: Tuple[str, int]=(FONT_PATH, FONT_SIZ), frame_size: Tuple[int, int]=FRAME_SIZE, 
                 next_callback: Optional[Callable]=None, enabled_flags: Dict[str, bool]={"セーブ":True, "ロード":True, "ログ":True}):
        super().__init__(screen, parent)
        self.root = root

        self.frame_size = frame_size
        self.margin_bottom = 20

        # テキストフレームのrect計算
        self.rect = self.calc_frame_rect()

        self.font_data = font_data

        # メニューバー
        self.menu_bar = MenuBar(screen=self.screen, root=self.root, frame_rect=self.rect, font_data=self.font_data, callback=next_callback, enabled_flags=enabled_flags)

        # 内部ラベル
        self.text_label = TextFrameLabel(screen=self.screen, frame_rect=self.rect, font_data=self.font_data)

        # Nextボタン
        next_x = self.rect.right - self.PADDING
        next_y = self.rect.bottom - self.PADDING
        self.next_label = Label(screen=self.screen, font_data=self.font_data, text="▶", x=next_x, y=next_y, anchor=("right", "bottom"), 
                                text_color=WHITE, result_type="next", row=100, focusable=True)

    # テキストフレームのrectを割り出す
    def calc_frame_rect(self) -> Rect:
        screen_w, screen_h = self.screen_size
        frame_w, frame_h = get_new_size(self.screen_size, (FRAME_SIZE))
        frame_x = (screen_w // 2) - (frame_w // 2)
        frame_y = screen_h - (frame_h + self.margin_bottom)

        return Rect(frame_x, frame_y, frame_w, frame_h)

    def set_text(self, text: str):
        self.text_label.set_text(text)

    def add_log_entry(self, log_view: LogView, text: str):
        log_view.append(text)
        pass

    def register_all(self, focus_manager: FocusManager):
        self.menu_bar.register_all(focus_manager)
        focus_manager.register(self.next_label)

    def unregister_all(self, focus_manager: FocusManager):
        self.menu_bar.unregister_all(focus_manager)
        focus_manager.elements.remove(self.next_label)

    def relayout(self, screen, parent=None):
        super().relayout(screen, parent)
        self.menu_bar.relayout(screen, self)
        self.text_label.relayout(screen, self.rect, self)
        self.next_label.relayout(screen, self)

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
        return False
