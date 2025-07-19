
from constans import PROF_DATA_PATH
from ui.ui_elements import *
from characters import *

from character_sheet.base_page import BacePage

class ConfirmPage(BacePage):
    def __init__(self, screen, root, player, save_data, callback, ofset=...):
        super().__init__(screen, root, player, ofset)
        self.save_data = save_data
        self.callback = callback

    def create_items(self):
        self.elements.clear()

        sex_name = "男" if self.player.sex == "man" else ("女" if self.player.sex == "woman" else "その他")
        status_list = [f"名前：{getattr(self.player, "name")}",
                       f"年齢：{getattr(self.player, "age")}",
                       f"性別：{sex_name}",
                       f"職業：{self.player.Profession}",
                       f"趣味：{self.player.Hobby}",
                       " ",
                       f"STR：{self.player.STR}",
                       f"CON：{self.player.CON}",
                       f"SIZ：{self.player.SIZ}",
                       f"DEX：{self.player.DEX}",
                       f"APP：{self.player.APP}",
                       f"EDU：{self.player.EDU}",
                       f"INT：{self.player.INT}",
                       f"POW：{self.player.POW}",
                       " "
                       ]

        box_x, box_y = self.rect.width // 2, 10
        box_w, box_h = 0, 0
        margin_x, margin_y = 10, 5
        start_x = box_x + 10
        x, y = start_x, box_y + 10
        total_width = 0

        for i, status in enumerate(status_list, 1):
            item = self.create_label(status, x, y)
            width = item.rect.width + margin_x
            height = item.rect.height + margin_y
            
            # ボックスを作るために最大幅を記録する
            total_width += width

            # 3の倍数だった場合は次の行に移動する
            if i % 3 == 0:
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
    
    def create_image(self):
        # 画面サイズから画像サイズを計算する
        h_percent = RATIO[self.window_size][1] 
        sex_img_scale = 0.5 * h_percent
        prof_img_scale = 0.2 * h_percent

        # 性別画像
        sex_img_path = f"silhouette_{self.player.sex}.png"
        self.sex_img = Image(self.surface, sex_img_path, sex_img_scale, 100, 10, line_flag=True, bg_flag=True)
        self.sex_img.set_rect(self.rect.width // 2 - self.sex_img.rect.width - 10, self.sex_img.rect.y, None, None)

        # 職業画像
        profession_data = load_json(JSON_FOLDER, PROF_DATA_PATH)
        profession_name = profession_data.get(self.player.Profession, {}).get("name", "")
        if profession_name:
            prof_img_path = f"prof_{profession_name}.png"
            self.prof_img = Image(self.surface, prof_img_path, prof_img_scale, self.box.rect.x, self.box.rect.y+self.box.rect.h+10, line_flag=True, bg_flag=True)
        else:
            self.prof_img = None

    # ラベルを作成する        
    def create_label(self, text, x, y):
        font = self.fonts[0]
        label = Label(self.surface, font, text, x, y)
        self.add_elements(label)
        return label

    def draw(self):
        self.create_items()
        self.create_image()
        self.bg_img.draw()
        self.box.draw()
        self.sex_img.draw()
        if self.prof_img:
            self.prof_img.draw()

        for element in self.elements:
            element.draw()
        return self.surface, self.rect
        
