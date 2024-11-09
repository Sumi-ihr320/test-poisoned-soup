from status import Status, SexChange

class StatusPage:
    def __init__(self, screen, root, hero_data):
        self.screen = screen
        self.root = root
        self.hero_data = hero_data

        self.sex_button = None  # 男女ボタン
        self.status_items = []  # ステータスのアイテム一覧

    def load_status_items(self, status_json):
        if not self.status_items:   # すでにアイテムがあるか確認
            for status, items in status_json.items():
                item = Status(self.screen, self.root, items["name"], status, items["view_name"], self.hero_data[status],
                            items["x"], items["y"], items["w"], items["h"], items["text"],
                            items["button_flag"], items["input_flag"], items["box_flag"], items["dice_text"])
                self.status_items.append(item)
                if status == "sex":
                    self.sex_button = SexChange(self.screen, 310, 80, self.hero_data["sex"])

    def draw(self):
        for item in self.status_items:
            item.draw()
        if self.sex_button:
            self.sex_button.draw(self.hero_data["sex"])
    
    def handle_mouse_hover(self, pos):
        for item in self.status_items:
            if item.button:
                item.button.update(pos)
            text = item.handle_mouse_hover(pos)
            if text is not None:
                return text
        return None

    def handle_click(self, pos):
        # 男ボタン
        if self.sex_button and self.sex_button.man.rect.collidepoint(pos):
                self.hero_data["sex"] = True
                self.sex_button.update_sex(True)
                return None
        # 女ボタン
        elif self.sex_button and self.sex_button.woman.rect.collidepoint(pos):
                self.hero_data["sex"] = False
                self.sex_button.update_sex(False)
                return None
        else:
            # 他のステータスの処理
            for item in self.status_items:
                # インプットボックス
                if item.input and item.input.rect.collidepoint(pos) and item.input_flag:   # かつ入力フラグがonの場合
                    item.input_process(self.hero_data["EDU"])
                    return item
                # ダイスボタン
                if item.button:
                    if item.button.update(pos, True):
                        return item