from typing import Optional, Tuple, List, Dict

import pygame
from pygame.locals import *

from constans import JSON_FOLDER, PROF_DATA_PATH, HOBBY_DATA_PATH, BLACK
from utils import load_json
from ui.ui_elements import Image, Label
from ui.ui_container import UIContainer
from ui.ui_container_element import ContainerImage, ContainerPullDown

# 職業クラス
class Profession(UIContainer):
    def __init__(self, screen, parent, parent_container, font_datas: List[Tuple[str, int]], 
                 name: str, eng_name: str, skills: Dict[str, int], rect: pygame.Rect, view_rect: pygame.Rect,
                 row: int=0, col: int=0):
        super().__init__(screen, parent)
        self.parent_container = parent_container
        self.font_datas = font_datas

        self.name = name
        self.eng_name = eng_name
        self.skills = skills
        self.path = f"prof_{eng_name}.png"
        self.rect = rect
        self.view_rect = view_rect
        self.row = row
        self.col = col

        self.create_images()
        self.labels = []
        self.create_labels()
    
    # 画像たちを作成する
    def create_images(self):
        small_img_size = 0.1
        big_img_size = 0.35
        self.small_img = ContainerImage(self.screen, parent_container=self, path=self.path, scale=small_img_size, x=self.rect.x, y=self.rect.y, 
                                        line_flag=True, bg_flag=True, 
                                        parent=self.parent, focusable=True, hover_text=f"あなたの職業を選択してください\n【{self.name}】",
                                        row=self.row, col=self.col)
        self.add(self.small_img)
        self.big_img = Image(self.screen, path=self.path, scale=big_img_size, x=self.view_rect.x, y=self.view_rect.y, 
                             line_flag=True, bg_flag=True, parent=self.parent)
        self.add(self.big_img)

    # ラベルたちを作成する
    def create_labels(self):
        font_data = self.font_datas[0]
        small_font_data = self.font_datas[1]

        # 名前ラベル
        self.lbl_name = self.create_label(font_data=font_data, text=f"【{self.name}】")

        # 所持技能ラベル
        self.lbl_skill_title = self.create_label(font_data=small_font_data, text="所持技能： ")

        # 各スキル
        self.lbl_skills = []
        for skill in self.skills:
            skill_label = self.create_label(font_data=small_font_data, text=skill)
            self.lbl_skills.append(skill_label)

        self.labels = [self.lbl_name, self.lbl_skill_title] + self.lbl_skills

    # ラベルを作成する
    def create_label(self, font_data: Tuple[str, int], text: str) -> Label:
        label = Label(self.screen, font_data=font_data, text=text, parent=self.parent)
        self.add(label)
        return label

    # 画像の位置をセットする
    def set_img_position(self, size: str="small", x: Optional[int]=None, y: Optional[int]=None):
        if size == "big":
            if x:
                self.big_img.rect.x = x
            if y:
                self.big_img.rect.y = y
        else:
            if x:
                self.small_img.rect.x = x
            if y:
                self.small_img.rect.y = y

    # ラベルの位置をセットする
    def set_label_position(self):
        self.lbl_name.x = self.big_img.rect.x+self.big_img.rect.w+5
        self.lbl_name.y = self.big_img.rect.y

        # 所持技能ラベルの表示位置
        self.lbl_skill_title.x = self.big_img.rect.x + self.big_img.rect.w + 15
        self.lbl_skill_title.y = self.big_img.rect.y + 30

        sk_x, sk_y = self.lbl_skill_title.x + 10, self.lbl_skill_title.y + self.lbl_skill_title.rect.h + 10
        sx, sy = sk_x, sk_y

        for label in self.lbl_skills:
            label.rect.x = label.x = sx
            label.rect.y = label.y = sy
            
            sx += label.rect.w + 10
            if sx > 530:
                sx = sk_x
                sy += label.rect.h + 10

    def relayout(self, screen, parent):
        self.screen = screen
        self.parent = parent
        self.small_img.relayout(screen, parent)
        self.big_img.relayout(screen, parent)
        for label in self.labels:
            label.relayout(screen, parent)

    # 表示
    def draw(self, is_selected: bool=False):
        if self.small_img:
            self.small_img.draw()
        if is_selected and self.big_img:
            self.big_img.draw()
            self.text_draw()

    # 職業ステータスを表示する
    def text_draw(self):
        self.lbl_name.draw()
        self.lbl_skill_title.draw()
        for label in self.lbl_skills:
            label.draw()

# 職業選択画面作るよ
class ProfessionSelector(UIContainer):
    def __init__(self, screen, parent, sheet_rect: pygame.Rect, font_datas: List[Tuple[str, int]]):
        super().__init__(screen, parent)
        self.sheet_rect = sheet_rect

        self.font_datas = font_datas

        self.selected_profession = None     # 現在保持している職業

        self.load_and_setup_data()

        self.rect = None
        self.prof_item_set_position()

    # データのロードとセットアップ
    def load_and_setup_data(self):
        self.prof_data = load_json(PROF_DATA_PATH, JSON_FOLDER)
        if self.prof_data:      # データがロードできていれば作成する
            self.create_profession()

    # 最適な行数列数を計算する
    def calculate_best_grid(self, total_items: int, icon_size: Tuple[int, int], margin: Tuple[int, int]) -> Tuple[int, int]:
        # 利用可能な描画エリアの幅
        available_width = self.sheet_rect.w
        available_height = self.sheet_rect.h // 2

        # 1つのアイコンに必要な幅
        unit_width = icon_size[0] + margin[0]
        unit_height = icon_size[1] + margin[1]

        max_cols = max(1, available_width // unit_width)
        max_rows = max(1, available_height // unit_height)

        best_layout = None
        for rows in range(1, max_rows + 1):
            cols = (total_items + rows - 1) // rows
            if cols > max_cols:
                continue    # 幅オーバー

            if best_layout is None or (rows * cols < best_layout[0] * best_layout[1]):
                best_layout = (rows, cols)

        if best_layout is None:
            best_layout = (max_rows, max_cols)

        return best_layout

    # 画像を表示する場所を計算してセットする
    def prof_item_set_position(self):
        icon_w, icon_h = 50, 50
        margin_x, margin_y = 5, 5

        rows, cols = self.calculate_best_grid(len(self.children), (icon_w, icon_h), (margin_x, margin_y))

        total_w = cols * icon_w + (cols - 1) * margin_x
        total_h = rows * icon_h + (rows - 1) * margin_y

        # 開始位置（中央に揃える）
        start_x = (self.sheet_rect.w - total_w) // 2
        start_y = self.sheet_rect.h  - total_h - 10

        self.rect = pygame.Rect(start_x, start_y, total_w, total_h)

        for i, prof in enumerate(self.children):
            row = i // cols
            col = i % cols
            x = start_x + col * (icon_w + margin_x)
            y = start_y + row * (icon_h + margin_y)
            prof.set_img_position("small", x, y)
            prof.set_img_position("big", start_x, start_y-(prof.big_img.rect.h+10))
            prof.set_label_position()

    # 職業一覧の作成
    def create_profession(self):
        x, y = 100, 230
        view_x, view_y = 100, 40
        for prof_key, prof_data in self.prof_data.items():
            name = prof_data["name"]
            skill = prof_data["skill"]
            item = Profession(self.screen, parent=self.parent, parent_container=self, font_datas=self.font_datas, 
                              name=prof_key, eng_name=name, skills=skill, rect=Rect(x, y, 50, 50), view_rect=Rect(view_x, view_y, 100, 100))
            self.add(item)

    def relayout(self, screen, parent, sheet_rect: pygame.Rect):
        self.sheet_rect = sheet_rect
        super().relayout(screen, parent)

    def draw(self):
        for child in self.children:
            child.draw(is_selected=(child == self.selected_profession))

# 趣味選択画面作るよ
class HobbySelector(UIContainer):
    def __init__(self, screen, parent, font_datas: List[Tuple[str, int]], profession_rect: pygame.Rect):
        super().__init__(screen, parent)

        self.selected_hobby = None      # 現在保持している趣味
        self.font_datas = font_datas
        self.profession_rect = profession_rect

        # 趣味データをロード
        self.hobby_list = load_json(HOBBY_DATA_PATH, JSON_FOLDER)

        self.label = None
        self.pull = None
        self.create_items()        

    # アイテム作成
    def create_items(self):
        # フォントの設定
        font_data = self.font_datas[0]
        small_font_data = self.font_datas[1]

        hobby_text = "趣味"
        font = pygame.font.Font(font_data[0], font_data[1])
        text_rect = font.render(hobby_text, True, BLACK).get_rect()
        self.label = Label(self.screen, font_data=font_data, text=hobby_text, x=self.profession_rect.right, y=self.profession_rect.y-text_rect.h-10, anchor=("right", "top"), parent=self.parent)
        self.add(self.label)

        list_item = self.selected_hobby if self.selected_hobby != "" else "未選択"
        self.pull = ContainerPullDown(self.screen, font_data=small_font_data, parent_container=self, rect=Rect(440,self.label.rect.y-8,150,25), 
                                      item_list=list(self.hobby_list), label_text=list_item, pd_h=180, 
                                      parent=self.parent, focusable=True, row=0, col=0, hover_text="あなたの趣味を選択してください")
        self.pull.update_position(x=self.label.rect.x-10, anchor=("right", "top"))
        self.add(self.pull)

