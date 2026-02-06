from typing import Optional, Tuple

import pygame
from pygame.locals import *

from constans import WHITE
from utils import dice_confirmation, TopmostManager
from ui.ui_elements import Label, Button, Image, InputBox, ImageCache, CustomDialog
from manager.dice_service import DiceService

# ステータス作るよ
class Status:
    MAX_STATUS_VALUE = 99

    def __init__(self, screen, parent, root, font_data: Tuple[str, int], name: str, status_name: str, label_name: str, status: str|int, 
                 x: int, y: int, w: int, h: int, hover_text: str="",
                 button_flag: bool=True, input_flag: bool=True, box_flag: bool=True, dice_text: str=""):
        self.screen = screen
        self.parent = parent
        self.root = root

        self.font_data = font_data

        self.name = name                # ステータスの名前
        self.status_name = status_name  # CharaStatusでの名前
        self.label_name = label_name if label_name != "" else self.name     # 実際に表示する名前（スペースなどで位置調整する場合があるため）
        self.hover_text = hover_text    # マウスオーバー時に表示される説明文
        self.dice_text = dice_text      # ダイスボタンに表示するテキスト

        self.create_label(x, y)

        # ステータスの値
        self.status = status

        # 入力可能かのフラグ
        self.input_flag = input_flag
        self.input = None   # 初期化
        if box_flag:    # インプットボックスを作るかのフラグ
            self.create_input(x, y, w, h)

        self.button = None  # 初期化
        if button_flag: # ダイスボタンを作るかのフラグ
            self.create_dice_button()

        self.dice_service = DiceService()

    # ラベル作成
    def create_label(self, x: int, y: int):
        self.status_label = Label(self.screen, self.font_data, self.label_name, x, y, parent=self.parent)    # ラベル作成

    # インプットボックスを作成
    def create_input(self, x: int, y: int, w: int, h: int):
        # ステータスラベルの隣
        input_x = x + self.status_label.rect.w + 5
        input_y = y - 4     # ラベルより大きいので少し上に
        self.input = InputBox(self.screen, self.font_data, Rect(input_x, input_y, w, h), str(self.status), self.input_flag, parent=self.parent)

    # ダイスボタンを作成
    def create_dice_button(self):
        # インプットボックスがあればその位置、なければラベルの位置
        rect = self.input.rect.copy() if self.input else self.status_label.rect.copy()
        # その幅分隣
        rect.x = rect.x + rect.w + 5
        self.button = Button(self.screen, self.font_data, self.dice_text, rect, self.dice_process, parent=self.parent)

    def relayout(self, screen, parent):
        self.screen = screen
        self.parent = parent
        if self.status_label:
            self.status_label.relayout(screen, parent)
        if self.input:
            self.input.relayout(screen, parent)
        if self.button:
            self.button.relayout(screen, parent)

    def draw(self):
        self.status_label.draw()
        if self.input:
            self.input.draw()
        if self.button:
            self.button.draw()

    # 入力ボックスの最大値最小値を決めるよ
    def determine_input_range(self, edu: int) -> Tuple[int, int]:
        min, max = 0, self.MAX_STATUS_VALUE

        # 最大値最小値を決めるよ
        if self.status_name == "age":
            min = edu + 6

        elif self.dice_text:
            pieces, dice, plus_item = dice_confirmation(self.dice_text)
            min, max = pieces, dice * pieces
            if plus_item:
                num = int(self.dice_text[-1])
                if plus_item.group() == "+":
                    min += num
                    max += num
                else:
                    min -= num
                    max -= num
        return min, max
    
    # 入力ボックスの処理まとめるよ
    def input_process(self, edu: int):
        min, max = self.determine_input_range(edu)
        value_type = type(self.status)
        num = 2 if value_type == int else None

        # カスタムダイアログに入力された値を取得してラベルを更新する
        with TopmostManager(self.root):
            dialog = CustomDialog(self.root, self.name, f"あなたの{self.name}を入力してください", self.input.label_text, value_type, min, max, num)
            value = dialog.result

        if value is not None:
            if self.input:
                self.input.update_label(f"{value}")

    # ダイス処理まとめるよ
    def dice_process(self):
        result = self.dice_service.roll(self.dice_text)
        self.input.update_label(f"{result}")

    def handle_mouse_hover(self, pos):
        if self.status_label.collidepoint(pos):
            return self.hover_text
        elif self.input and self.input.collidepoint(pos):
            return self.hover_text
        elif self.button and self.button.collidepoint(pos):
            return "ダイスでランダムに値を決めることができます"
        return None

# 選んだ性別によって画像が変わるようにするよ
class SexChange:
    def __init__(self, screen, parent, sheet_rect: pygame.Rect, font_data: Tuple[str, int], title_text: str, 
                 x: int, y: int, flag: str):
        self.screen = screen
        self.parent = parent
        self.sheet_rect = sheet_rect
        self.font_data = font_data

        self.title_text = title_text
        self.title_x, self.title_y = x, y
        self.flag = flag

        # 性別ボタン作成
        self.labels_dict = {}
        self.create_labels_dict()
        # ボタンを配置
        self.button_placement()

        self.image_cache = ImageCache()

        # 画像を作成
        self.images_dict = {}
        self.create_images_dict()

    # 性別ボタンの配置
    def button_placement(self):
        font = pygame.font.Font(self.font_data[0], self.font_data[1])

        # 性別欄のテキストの位置
        text_width = font.size(self.title_text)[0]
        start_width = font.size(self.title_text[:3])[0]
        end_width = font.size(self.title_text[-1])[0]

        # 配置したいスペースの幅
        text_max_size = text_width - (start_width + end_width)

        # 各ラベルの幅
        man_width = font.size("男")[0]
        woman_width = font.size("女")[0]
        neuter_width = font.size("その他")[0]

        # ボタンの全幅
        total_button_width = man_width + woman_width + neuter_width

        # ボタン間空間の計算
        spacing = (text_max_size - total_button_width) // 4

        # 最初のボタンの表示位置
        text_x = self.title_x + start_width + spacing
        for label in self.labels_dict.values():
            label.x = text_x
            label.y = self.title_y
            label.rect.topleft = (text_x, self.title_y)
            text_x += man_width + spacing

    # ラベルdictを作成
    def create_labels_dict(self):
        self.labels_dict = {"man": self.create_button_label("男", 0),
                            "woman": self.create_button_label("女", 1),
                            "neuter": self.create_button_label("その他", 2)}

    # 画像dictを作成
    def create_images_dict(self):
        self.images_dict = {"man": self.create_image("man"),
                            "woman": self.create_image("woman"),
                            "neuter": self.create_image("neuter")}

    # ボタンラベル作成
    def create_button_label(self, text: str, col: int) -> Label:
        push_color = (106,93,33)   # ボタンを押したときの色
        label = Label(self.screen, self.font_data, text, parent=self.parent, 
                      focusable=True, col=col,
                      hover_text_color=WHITE, hover_back_color=push_color)
        return label

    # 画像作成
    def create_image(self, flag: str) -> Image:
        image_x, image_y = 10, 10
        img_size = 0.5

        img_path = f"silhouette_{flag}.png"

        image = Image(self.screen, img_path, self.image_cache, scale=img_size, x=image_x, y=image_y, 
                      line_flag=True, bg_flag=True, line_width=2, parent=self.parent)        
        return image

    # フラグを確認してlabelのフォーカスを変更する
    def check_flag_and_set_focus(self, flag: str):
        for sex, label in self.labels_dict.items():
            if sex == flag:
                label.set_focus(True)
            else:
                label.set_focus(False)
        return

    # 性別が変わった時にボタンの状態を更新する
    def update_sex(self, flag: str):
        self.flag = flag
        self.check_flag_and_set_focus(flag)

    def relayout(self, screen: pygame.Surface, parent):
        self.screen = screen
        self.parent = parent
        for label in self.labels_dict.values():
            label.relayout(screen, parent)
        for image in self.images_dict.values():
            image.relayout(screen, parent)

    # 描画するよ
    def draw(self):
        for label in self.labels_dict.values():
            label.draw()
        
        self.images_dict[self.flag].draw()
