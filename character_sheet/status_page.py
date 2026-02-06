from constans import STATUS_DATA_PATH, JSON_FOLDER
from utils import load_json
from character_sheet.base_page import BacePage
from character_sheet.status import Status, SexChange

class StatusPage(BacePage):
    def __init__(self, screen, root, player, ofset=None):
        super().__init__(screen, root, player, ofset)

        self.status_data = load_json(STATUS_DATA_PATH, JSON_FOLDER)

        self.sex_button = None  # 性別ボタン

    def create_status_items(self):
        font_data = self.font_datas[0]
        for status, items in self.status_data.items():
            item = Status(self.screen, self, self.root, font_data, items["name"], status, items["view_name"], getattr(self.player, status),
                        items["x"], items["y"], items["w"], items["h"], items["text"],
                        items["button_flag"], items["input_flag"], items["box_flag"], items["dice_text"])
            self.add_elements(item)
            if status == "sex":
                self.sex_button = SexChange(self.screen, self, self.rect, font_data, items["view_name"], items["x"], items["y"], self.player.sex)

    def load_status_items(self):
        if not self.elements:   # すでにアイテムがあるか確認
            self.create_status_items()

    # 画面サイズ変更時にポジション等を更新する
    def relayout(self, screen):
        super().relayout(screen)
        for item in self.elements:
            item.relayout(screen, self)
        self.sex_button.relayout(screen, self)

    def draw(self):
        surface, rect = super().draw()
        if self.sex_button:
            self.sex_button.draw()
        return surface, rect
    
    def handle_mouse_hover(self, pos):
        #pos = self.pos_calculation(pos)
        for item in self.elements:
            if item.button:
                item.button.handle_mouse_hover(pos)
            text = item.handle_mouse_hover(pos)
            if text is not None:
                return text
        return None

    def handle_click(self, pos):
        #pos = self.pos_calculation(pos)
        if self.handle_sex_button(pos):
            return None
        else:
            # 他のステータスの処理
            for item in self.elements:
                # インプットボックス
                if item.input and item.input.collidepoint(pos) and item.input_flag:   # かつ入力フラグがonの場合
                    item.input_process(self.player.EDU)
                    return item
                # ダイスボタン
                if item.button and item.button.handle_click(pos):
                    return item

    # 性別ボタンを押したとき
    def handle_sex_button(self, pos):
        on_button = False

        # 男ボタン
        if self.sex_button and self.sex_button.man.collidepoint(pos):
            self.player.sex = "man"
            on_button = True
            
        # 女ボタン
        elif self.sex_button and self.sex_button.woman.collidepoint(pos):
            self.player.sex = "woman"
            on_button = True

        # その他ボタン
        elif self.sex_button and self.sex_button.neuter.collidepoint(pos):
            self.player.sex = "neuter"
            on_button = True

        if on_button:
            self.player.image = f"silhouette_{self.player.sex}.png"
            self.sound_manager.play("クリック")
            self.sex_button.update_sex(self.player.sex)
        
        return on_button

