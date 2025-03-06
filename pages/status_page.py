from utils import sound_check
from status import Status, SexChange
from manager.sound_manager import SoundManager

class StatusPage:
    def __init__(self, screen, root, player):
        self.screen = screen
        self.root = root
        self.player = player

        self.sex_button = None  # 性別ボタン
        self.status_items = []  # ステータスのアイテム一覧
        self.sound_manager = SoundManager()
        sound_check(self.sound_manager)

    def load_status_items(self, status_json):
        if not self.status_items:   # すでにアイテムがあるか確認
            for status, items in status_json.items():
                item = Status(self.screen, self.root, items["name"], status, items["view_name"], getattr(self.player, status),
                            items["x"], items["y"], items["w"], items["h"], items["text"],
                            items["button_flag"], items["input_flag"], items["box_flag"], items["dice_text"])
                self.status_items.append(item)
                if status == "sex":
                    self.sex_button = SexChange(self.screen, 310, 80, self.player.sex)

    def draw(self):
        for item in self.status_items:
            item.draw()
        if self.sex_button:
            self.sex_button.draw(self.player.sex)
    
    def handle_mouse_hover(self, pos):
        for item in self.status_items:
            if item.button:
                item.button.update(pos)
            text = item.handle_mouse_hover(pos)
            if text is not None:
                return text
        return None

    def handle_click(self, pos):
        if self.handle_sex_button(pos):
            return None
        else:
            # 他のステータスの処理
            for item in self.status_items:
                # インプットボックス
                if item.input and item.input.rect.collidepoint(pos) and item.input_flag:   # かつ入力フラグがonの場合
                    item.input_process(self.player.EDU)
                    return item
                # ダイスボタン
                if item.button and item.button.update(pos, True):
                    return item

    # 性別ボタンを押したとき
    def handle_sex_button(self, pos):
        on_button = False

        # 男ボタン
        if self.sex_button and self.sex_button.man.rect.collidepoint(pos):
            self.player.sex = "man"
            on_button = True
            
        # 女ボタン
        elif self.sex_button and self.sex_button.woman.rect.collidepoint(pos):
            self.player.sex = "woman"
            on_button = True

        # その他ボタン
        elif self.sex_button and self.sex_button.neuter.rect.collidepoint(pos):
            self.player.sex = "neuter"
            on_button = True

        if on_button:
            self.sound_manager.play("クリック")
            self.sex_button.update_sex(self.player.sex)
        
        return on_button

