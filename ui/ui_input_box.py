from typing import Tuple, Any, Optional, Union

import pygame

from constans import WHITE, BLACK
from utils import setting_font, TopmostManager
from ui.ui_base import UIElement, ResizableMixin
from ui.ui_dialogs import CustomDialog
from ui.ui_elements import Label

# インプットボックス
class InputBox(UIElement, ResizableMixin):
    def __init__(self, screen, root, font_data: Tuple[str, int], rect: pygame.Rect, label_text: str="", 
                 input_flag: bool=True, line_bold: int=2,
                 sound_type: str="click", row: int=0, col: int=0, focusable: bool=False, 
                 parent: Optional[Any]=None, hover_text: Optional[str]=None, **kwargs):
        super().__init__(screen=screen, parent=parent, sound_type=sound_type, row=row, col=col, focusable=focusable, hover_text=hover_text, **kwargs)
        self.root = root

        self.font_data = font_data
        self.font = pygame.font.Font(self.font_data[0], self.font_data[1])

        self.rect = rect
        self.set_base_rect(self.rect)

        self.input_flag = input_flag

        # ラベルの設定
        self.label_text = label_text
        self.label_padding = 10
        self.label_anchor = "center"    # "center", "midleft", "midright"などrectのアンカー
        self.label = None

        # 1度だけラベルを作成
        self.create_label()

        # ボックスのスタイル
        self.fill_color = WHITE if input_flag else None
        self.border_color = BLACK
        self.border_width = line_bold
        self.under_line = True

    # ラベルを作成
    def create_label(self):
        self.ensure_label(self.screen, self.font_data, self.parent)
        self.place_label_to_rect(self.rect)

    # Labelを作成
    def ensure_label(self, screen, font_data: Tuple[str, int], parent: Optional[Any]=None):
        if self.label is None and self.label_text is not None:
            # 初回のみ作成
            self.label = Label(screen, font_data=font_data, text=self.label_text, x=0, y=0, parent=parent, 
                               hover_back_color=None)
        elif self.label:
            self.label.set_text(self.label_text)
    
    # 親側のrectに対してラベルを配置
    def place_label_to_rect(self, host_rect: pygame.Rect) -> None:
        if not self.label:
            return
        
        # ラベルのサーフェイス更新(幅・高さが必要)
        self.label.update_text_surface()

        # ラベルの描画矩形
        text_w, text_h = self.label.max_width, self.label.max_height
        r = pygame.Rect(0, 0, text_w, text_h)

        # アンカーに合わせて座標を決める
        if self.label_anchor == "center":
            r.center = host_rect.center
        elif self.label_anchor == "midright":
            r.midright = (host_rect.right - self.label_padding, host_rect.centery)
        else:
            r.midleft = (host_rect.left + self.label_padding, host_rect.centery)

        # Label自身がrectを持つので更新
        self.label.x = r.x
        self.label.y = r.y
        self.label.rect = r

    # フラグを設定して背景色を変える
    def set_input_flag(self, flag: bool):
        self.input_flag = flag
        self.fill_color = WHITE if flag else None

    # ラベルの更新
    def update_label(self, new_text: str):
        self.label_text = new_text
        self.create_label()

    # ラベルに表示されている値を取得する
    def get_value(self) -> Union[int, str]:
        # ラベルに表示されている文字を、数字ならintにしてそうでないなら文字列として返す
        try:
            return int(self.label_text)
        except ValueError:
            return self.label_text

    # 入力処理
    def input_process(self, title, text, min, max, value_type, num_characters):
        # カスタムダイアログに入力された値を取得してラベルを更新する
        with TopmostManager(self.root):
            dialog = CustomDialog(self.root, title, f"{text}を入力してください", self.label_text, value_type, min, max, num_characters)
            value = dialog.result

        if value is not None:
            self.update_label(f"{value}")

    # ボックスを描画する
    def draw_box_rect(self, parent, rect: pygame.Rect):
        if self.fill_color is not None:
            pygame.draw.rect(parent, self.fill_color, rect)

        if self.under_line:
            pygame.draw.line(parent, self.border_color, (rect.x, rect.bottom-1), (rect.right-1, rect.bottom-1), self.border_width)

        else:
            pygame.draw.rect(parent, self.border_color, rect, self.border_width)

    # 描画
    def draw(self):
        # 入力ボックス
        self.draw_box_rect(self.parent_surface, self.rect)
        
        # ラベルがあれば描写
        if self.label:
            self.place_label_to_rect(self.rect)
            self.label.draw()

    # フォントサイズ変更
    def resize_font(self, screen_size: Tuple[int, int]):
        self.font = setting_font(self.font_data[0], self.font_data[1], screen_size)
        self.create_label()

    # スクリーンサイズ変更によるアップデート
    def relayout(self, screen, parent=None):
        super().relayout(screen, parent)
        self.rect = self.resize(self.screen_size)
        self.resize_font(self.screen_size)

    