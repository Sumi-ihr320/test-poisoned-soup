from typing import Optional, Tuple

import pygame
from pygame.locals import *

from constans import WHITE
from utils import dice_confirmation
from ui.ui_elements import Label, Image
from ui.ui_container_element import ContainerLabel, ContainerButton, ContainerInputBox
from ui.ui_cache import ImageCache
from ui.ui_container import UIContainer
from manager.dice_service import DiceService
from manager.sound_manager import sound_manager

# ステータス作るよ
class Status(UIContainer):
    MAX_STATUS_VALUE = 99

    def __init__(self, screen, parent, root, font_data: Tuple[str, int], name: str, status_name: str, label_name: str, status: str|int, 
                 x: int, y: int, w: int, h: int, hover_text: str="", row: int=0, col: int=0,
                 button_flag: bool=True, input_flag: bool=True, box_flag: bool=True, dice_text: str=""):
        super().__init__(screen, parent)
        self.root = root

        self.font_data = font_data

        self.name = name                # ステータスの名前
        self.status_name = status_name  # CharaStatusでの名前
        self.label_name = label_name if label_name != "" else self.name     # 実際に表示する名前（スペースなどで位置調整する場合があるため）
        self.hover_text = hover_text    # マウスオーバー時に表示される説明文

        self.row = row              # フォーカスマネージャー用の行番号  
        self.col = col              # フォーカスマネージャー用の列番号

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
        self.status_label = Label(self.screen, font_data=self.font_data, text=self.label_name, x=x, y=y, 
                                  parent=self.parent, hover_text=self.hover_text, hover_back_color=None)
        self.add(self.status_label)

    # インプットボックスを作成
    def create_input(self, x: int, y: int, w: int, h: int):
        # ステータスラベルの隣
        input_x = x + self.status_label.rect.w + 5
        input_y = y - 4     # ラベルより大きいので少し上に
        self.input = ContainerInputBox(self.screen, self.root, font_data=self.font_data, parent_container=self, 
                                       rect=Rect(input_x, input_y, w, h), label_text=str(self.status), input_flag=self.input_flag, 
                                       parent=self.parent, focusable=self.input_flag, row=self.row, col=self.col, hover_text=self.hover_text)
        self.add(self.input)

    # ダイスボタンを作成
    def create_dice_button(self):
        # インプットボックスがあればその位置、なければラベルの位置
        rect = self.input.rect.copy() if self.input else self.status_label.rect.copy()
        # その幅分隣
        rect.x = rect.x + rect.w + 5
        self.button = ContainerButton(self.screen, font_data=self.font_data, parent_container=self, 
                                      text=self.dice_text, rect=rect, on_click=self.dice_process, 
                                      parent=self.parent, focusable=True, row=self.row, col=self.col+1, 
                                      hover_text="ダイスでランダムに値を決めることができます")
        self.add(self.button)

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
        num = 2 if value_type == int else 20
        self.input.input_process(title=self.name, text=f"あなたの{self.name}", min=min, max=max, 
                                 value_type=value_type, num_characters=num)

    # ダイス処理まとめるよ
    def dice_process(self):
        result = self.dice_service.roll(self.dice_text)
        self.input.update_label(f"{result}")

    def handle_mouse_hover(self, pos):
        return self.status_label.handle_mouse_hover(pos)

    def handle_click(self, pos):
        if self.input_flag and self.input and self.input.collidepoint(pos):
            self.input_process(self.parent.player.EDU)
            return "input"
        elif self.button and self.button.handle_click(pos):
            return "button"
        return None

# 選んだ性別によって画像が変わるようにするよ
class SexChange(UIContainer):
    def __init__(self, screen, parent, sheet_rect: pygame.Rect, font_data: Tuple[str, int], title_text: str, 
                 x: int, y: int, flag: str, row: int=0, col: int=0):
        super().__init__(screen, parent)

        self.sheet_rect = sheet_rect
        self.font_data = font_data

        self.title_text = title_text
        self.title_x, self.title_y = x, y

        self.flag = flag

        self.row = row
        self.col = col

        # 性別ボタン作成
        self.labels_dict = {}
        self.create_labels_dict()
        # ボタンを配置
        self.placement_button()

        self.image_cache = ImageCache()

        # 画像を作成
        self.images_dict = {}
        self.create_images_dict()

    # 性別ボタンの配置
    def placement_button(self):
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
    def create_button_label(self, text: str, col: int) -> ContainerLabel:
        push_color = (106,93,33)   # ボタンを押したときの色
        label = ContainerLabel(self.screen, font_data=self.font_data, parent_container=self, text=text, 
                               parent=self.parent, focusable=True, row=self.row, col=self.col+col,
                               hover_text_color=WHITE, hover_back_color=push_color, 
                               hover_text="探索者の性別をクリックで選択してください")
        self.add(label)
        return label

    # 画像作成
    def create_image(self, flag: str) -> Image:
        image_x, image_y = 10, 10
        img_size = 0.5

        img_path = f"silhouette_{flag}.png"

        image = Image(self.screen, path=img_path, cache=self.image_cache, scale=img_size, x=image_x, y=image_y, 
                      line_flag=True, bg_flag=True, line_width=2, parent=self.parent)
        self.add(image)
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

    # 描画するよ
    def draw(self):
        for label in self.labels_dict.values():
            label.draw()
        self.images_dict[self.flag].draw()

    def handle_mouse_hover(self, pos):
        return None

    def handle_click(self, pos: Tuple[int, int]):
        for name, label in self.labels_dict.items():
            if label.collidepoint(pos):
                sound_manager.play("クリック")
                self.update_sex(name)
                return name
        return None
        