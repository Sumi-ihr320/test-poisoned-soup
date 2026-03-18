from typing import Dict, Tuple, Any, Optional, Callable

from pygame import Rect
from tkinter import messagebox

from constans import JSON_FOLDER, PROF_DATA_PATH, ITEM_LIST, State
from utils import load_json, TopmostManager
from models.characters import Player, Human
from ui.ui_elements import Box, Label, Image
from utils import load_json

from character_sheet.base_page import BasePage

class ConfirmPage(BasePage):
    def __init__(self, screen, root, text_frame_rect, player: Player, save_data: Dict[str, Any], callback: Callable, offset: Optional[Tuple[int, int]]=None):
        super().__init__(screen, root, text_frame_rect, player, offset)
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

    # バリデーションと完了処理
    def validate_and_finalize(self):
        manual_input_fields = { "name": "名前が入力されていません",
                                "age": "年齢が入力されていません",
                                "STR": "STRが入力されていません",
                                "CON": "CONが入力されていません",
                                "SIZ": "SIZが入力されていません",
                                "DEX": "DEXが入力されていません",
                                "APP": "APPが入力されていません",
                                "EDU": "EDUが入力されていません",
                                "INT": "INTが入力されていません",
                                "POW": "POWが入力されていません",
                                "Profession":"職業が選択されていません",
                                "Hobby":"趣味が選択されていません"
                                }
        texts = []

        # 手動入力が必要なステータスのみエラーチェックする
        for status, error_msg in manual_input_fields.items():
            if getattr(self.player, status) == "" or getattr(self.player, status) == 0:
                texts.append(error_msg)
        if texts:
            text = "\n".join(texts)
            with TopmostManager(self.root):
                messagebox.showerror("未入力", text)
            return False
        
        # セーブデータに主人公データを入れる
        self.save_data["player_status"] = self.player.to_dict()

        # セーブデータに少女のデータを入れる
        girl = Human("下僕の少女", "Girl.png", 4, 6, 10, 5, 10, 10,"-1d4", 8, 10, 10,
                        {"目星":55, "聞き耳":55, "忍び歩き":40,"隠れる":40,"応急手当":50, "中国語（母国語）":40, "追跡":50, "その他言語（主人公の母国語）":31,"クトゥルフ神話":15, "拳銃":20},
                        17, "woman", 13, 6, 50, 50, 30, 0, 0, "放浪者")
        girl.add_item(ITEM_LIST["bloody_robe"])
        girl.add_item(ITEM_LIST["gun"])

        self.save_data["girl_status"] = girl.to_dict()
        return True
            
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
            img = Image(self.screen, path=sex_img_path, scale=sex_img_scale, x=100, y=10, line_flag=True, bg_flag=True, parent=self)
            img.rect.topleft = (self.rect.width // 2 - img.rect.width - 10, img.rect.y)
            self.sex_img_dict[sex] = img

        # 職業画像
        prof_img_scale = 0.2
        profession_data = load_json(PROF_DATA_PATH, JSON_FOLDER)
        for prof_data in profession_data:
            prof_img_path = f"prof_{profession_data[prof_data]['name']}.png"
            self.prof_img_dict[prof_data] = Image(self.screen, path=prof_img_path, scale=prof_img_scale, x=self.box.rect.x, y=self.box.rect.y+self.box.rect.h+10, line_flag=True, bg_flag=True, parent=self)

    # ラベルを作成する
    def create_labels(self):
        font_data = self.font_datas[0]
        for name, text in self.status_dict.items():
            label = Label(self.screen, font_data=font_data, text=text, parent=self)
            self.label_dict[name] = label

    # ステータスラベルをアップデートする
    def update_labels(self):
        self.set_player_data()
        for name, text in self.status_dict.items():
            self.label_dict[name].set_text(text)
        self.set_label_rect_and_create_box()

    def handle_click(self, element, result: bool):
        if result:
            if self.validate_and_finalize():
                self.callback(State.SAVE, self.save_data)

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
        player_sex = getattr(self.player, "sex", "man")
        self.sex_img_dict[player_sex].draw()
        if self.player.Profession:
            player_prof = getattr(self.player, "Profession", "")
            self.prof_img_dict[player_prof].draw()
        for label in self.label_dict.values():
            label.draw()
        return self.surface, self.rect
        
