from typing import Dict, Tuple, Any, Optional, Callable

from pygame import Rect

from constans import JSON_FOLDER, PROF_DATA_PATH
from ui.ui_elements import Box, Label, Image
from utils import load_json
from models.characters import Player

from character_sheet.base_page import BasePage

class ConfirmPage(BasePage):
    def __init__(self, screen, root, player: Player, save_data: Dict[str, Any], callback: Callable, ofset: Optional[Tuple[int, int]]=None):
        super().__init__(screen, root, player, ofset)
        self.save_data = save_data
        self.callback = callback
        
        self.status_dict = {}
        self.set_player_data()

        self.label_dict = {}
        self.box = None
        self.sex_img_dict = {}
        self.prof_img_dict = {}
        self.create_items()

    # プレイヤーデータをリストに入れる
    def set_player_data(self):
        player_sex = getattr(self.player, "sex", "man")
        sex_name = "男" if player_sex == "man" else ("女" if player_sex == "woman" else "その他")
        self.status_dict = {"名前":f"名前：{getattr(self.player, "name", "")}",
                            "年齢":f"年齢：{getattr(self.player, "age", 0)}",
                            "性別":f"性別：{sex_name}",
                            "職業":f"職業：{getattr(self.player, "Profession", "")}",
                            "趣味":f"趣味：{getattr(self.player, "Hobby", "")}",
                            "STR":f"STR：{getattr(self.player, "STR", 0)}",
                            "CON":f"CON：{getattr(self.player, "CON", 0)}",
                            "SIZ":f"SIZ：{getattr(self.player, "SIZ", 0)}",
                            "DEX":f"DEX：{getattr(self.player, "DEX", 0)}",
                            "APP":f"APP：{getattr(self.player, "APP", 0)}",
                            "EDU":f"EDU：{getattr(self.player, "EDU", 0)}",
                            "INT":f"INT：{getattr(self.player, "INT", 0)}",
                            "POW":f"POW：{getattr(self.player, "POW", 0)}"}

    # アイテムを作成する
    def create_items(self):
        self.create_labels()
        self.set_label_rect_and_create_box()
        self.create_images()

    # ボックスを作成する
    def set_label_rect_and_create_box(self):
        box_x, box_y = self.rect.width // 2, 10
        box_w, box_h = 0, 0
        margin_x, margin_y = 10, 5
        start_x = box_x + 10
        x, y = start_x, box_y + 10
        total_width = 0

        for name, label in self.label_dict.items():
            label.x, label.y = x, y
            label.rect.x, label.rect.y = x, y
            width = label.rect.width + margin_x
            height = label.rect.height + margin_y
            
            # ボックスを作るために最大幅を記録する
            total_width += width

            # 特定の項目の場合は次の行に移動する
            if name in ("名前", "性別", "職業", "趣味", "SIZ", "EDU", "POW"):
                x = start_x
                y += height

                # ボックス高さを記録する
                box_h += height

                # ボックス幅より合計幅が大きい場合は合計幅をボックス幅にする
                if box_w < total_width:
                    box_w = total_width

                # 合計幅をリセット
                total_width = 0

            else:
                x += width

        self.box = Box(self.surface, Rect(box_x, box_y, box_w+10, box_h+10))

    # 画像を作成する
    def create_images(self):
        # 性別画像
        sex_img_scale = 0.5
        for sex in ("man", "woman", "neuter"):
            sex_img_path = f"silhouette_{sex}.png"
            img = Image(self.screen, sex_img_path, scale=sex_img_scale, x=100, y=10, line_flag=True, bg_flag=True, parent=self)
            img.rect.topleft = (self.rect.width // 2 - img.rect.width - 10, img.rect.y)
            self.sex_img_dict[sex] = img

        # 職業画像
        prof_img_scale = 0.2
        profession_data = load_json(PROF_DATA_PATH, JSON_FOLDER)
        for prof_data in profession_data:
            prof_img_path = f"prof_{profession_data[prof_data]["name"]}.png"
            self.prof_img_dict[prof_data] = Image(self.screen, prof_img_path, scale=prof_img_scale, x=self.box.rect.x, y=self.box.rect.y+self.box.rect.h+10, line_flag=True, bg_flag=True, parent=self)

    # ラベルを作成する
    def create_labels(self):
        font_data = self.font_datas[0]
        for name, text in self.status_dict.items():
            label = Label(self.screen, font_data, text, parent=self)
            self.label_dict[name] = label

    # ステータスラベルをアップデートする
    def update_labels(self):
        self.set_player_data()
        for name, text in self.status_dict.items():
            self.label_dict[name].set_text(text)
        self.set_label_rect_and_create_box()

    def relayout(self, screen):
        super().relayout(screen)
        for label in self.label_dict.values():
            label.relayout(screen, self)
        self.set_label_rect_and_create_box()
        for sex_img in self.sex_img_dict.values():
            sex_img.relayout(screen, self)
        for prof_img in self.prof_img_dict.values():
            prof_img.relayout(screen, self)

    def draw(self):
        self.update_labels()
        self.bg_img.draw()
        self.box.draw()
        self.sex_img_dict[self.player.sex].draw()
        if self.player.Profession:
            self.prof_img_dict[self.player.Profession].draw()
        for label in self.label_dict.values():
            label.draw()
        return self.surface, self.rect
        
