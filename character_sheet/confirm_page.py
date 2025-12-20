
from constans import PROF_DATA_PATH
from ui.ui_elements import *
#from models.characters import *

from character_sheet.base_page import BacePage

class ConfirmPage(BacePage):
    def __init__(self, screen, root, player, save_data, callback, ofset=...):
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
        sex_name = "男" if self.player.sex == "man" else ("女" if self.player.sex == "woman" else "その他")
        self.status_dict = {"名前":f"名前：{getattr(self.player, "name")}",
                            "年齢":f"年齢：{getattr(self.player, "age")}",
                            "性別":f"性別：{sex_name}",
                            "職業":f"職業：{self.player.Profession}",
                            "趣味":f"趣味：{self.player.Hobby}",
                            "STR":f"STR：{self.player.STR}",
                            "CON":f"CON：{self.player.CON}",
                            "SIZ":f"SIZ：{self.player.SIZ}",
                            "DEX":f"DEX：{self.player.DEX}",
                            "APP":f"APP：{self.player.APP}",
                            "EDU":f"EDU：{self.player.EDU}",
                            "INT":f"INT：{self.player.INT}",
                            "POW":f"POW：{self.player.POW}"}

    # アイテムを作成する
    def create_items(self):
        self.create_label()
        self.create_box()
        self.create_image()

    # ボックスを作成する
    def create_box(self):
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
    def create_image(self):
        # 性別画像
        sex_img_scale = 0.5
        for sex in ("man", "woman", "neuter"):
            sex_img_path = f"silhouette_{sex}.png"
            img = Image(self.screen, sex_img_path, scale=sex_img_scale, x=100, y=10, line_flag=True, bg_flag=True, parent=self)
            img.rect.topleft = (self.rect.width // 2 - img.rect.width - 10, img.rect.y)
            self.sex_img_dict[sex] = img

        # 職業画像
        prof_img_scale = 0.2
        profession_data = load_json(JSON_FOLDER, PROF_DATA_PATH)
        for prof_data in profession_data:
            prof_img_path = f"prof_{profession_data[prof_data]["name"]}.png"
            self.prof_img_dict[prof_data] = Image(self.screen, prof_img_path, scale=prof_img_scale, x=self.box.rect.x, y=self.box.rect.y+self.box.rect.h+10, line_flag=True, bg_flag=True, parent=self)

    # ラベルを作成する
    def create_label(self):
        font_data = self.font_datas[0]
        for name, text in self.status_dict.items():
            label = Label(self.screen, font_data, text, parent=self)
            self.label_dict[name] = label

    # ステータスラベルをアップデートする
    def update_label(self):
        self.set_player_data()
        for name, text in self.status_dict.items():
            self.label_dict[name].set_text(text)
        self.create_box()

    def relayout(self, screen):
        super().relayout(screen)
        for label in self.label_dict.values():
            label.relayout(screen, self)
        self.create_box()
        for sex_img in self.sex_img_dict.values():
            sex_img.relayout(screen, self)
        for prof_img in self.prof_img_dict.values():
            prof_img.relayout(screen, self)

    def draw(self):
        self.update_label()
        self.bg_img.draw()
        self.box.draw()
        self.sex_img_dict[self.player.sex].draw()
        if self.player.Profession:
            self.prof_img_dict[self.player.Profession].draw()
        for label in self.label_dict.values():
            label.draw()
        return self.surface, self.rect
        
