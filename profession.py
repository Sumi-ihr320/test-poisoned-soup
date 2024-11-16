import pygame
from pygame.locals import *

from constans import *
from utils import *
from ui_elements import *

# 職業クラス
class Profession:
    def __init__(self, screen, name, eng_name, skills, x, y, view_x, view_y):
        self.screen = screen

        self.name = name
        self.eng_name = eng_name
        self.skills = skills
        self.path = f"{PATH}{PICTURE}prof_{eng_name}.png"
        self.x, self.y = x, y
        self.view_x, self.view_y = view_x, view_y

        # 画像は最初に一度だけロードしキャッシュする
        self.small_img = self.load_img(self.x, self.y, 0.1)
        self.big_img = self.load_img(self.view_x, self.view_y, 0.35)
        
    # 画像インスタンスを作成
    def load_img(self, x, y, size):
        try:
            return Image(self.screen, self.path, size, x, y, line_flag=True, bg_flag=True)
        except FileNotFoundError:
            print(f"Error: 画像が見つかりません - {self.path}")
            return None

    # 画像を表示
    def image_draw(self, is_selected=False):
        if self.small_img:
            self.small_img.draw()
        if is_selected and self.big_img:
            self.big_img.draw()
            self.text_draw()

    # 職業ステータスを表示する
    def text_draw(self):
        font = pygame.font.Font(FONT_PATH, FONT_SIZ)
        small_font = pygame.font.Font(FONT_PATH, SMALL_SIZ)

        # 名前ラベル
        lbl_name = Label(self.screen, font, f"【{self.name}】", self.big_img.rect.x+self.big_img.rect.w+5, self.view_y)
        lbl_name.draw()

        # 所持技能ラベルの表示位置
        skill_x, skill_y = self.big_img.rect.x + self.big_img.rect.w + 15, self.view_y + 30

        # 所持技能ラベル
        lbl_skill = Label(self.screen, small_font, "所持技能： ", skill_x, skill_y)
        lbl_skill.draw()

        # 個々のスキルの表示位置
        sk_x, sk_y = skill_x + 10, skill_y + lbl_skill.rect.h + 10
        sx, sy = sk_x, sk_y

        # スキルを順番に表示していく
        for skill in self.skills:
            skill_label = Label(self.screen, small_font, skill, sx, sy)
            skill_label.draw()
            sx += skill_label.rect.w + 10
            if sx > 530:
                sx = sk_x
                sy += skill_label.rect.h + 10

    def handle_mouse_hover(self, pos):
        if self.small_img.rect.collidepoint(pos):
            return f"あなたの職業を選択してください\n【{self.name}】"
        return None

    def handle_click(self, pos):
        if self.small_img.rect.collidepoint(pos):
            return True
        return False

# 職業選択画面作るよ
class ProfessionSelecter:
    def __init__(self, screen):
        self.screen = screen
        self.prof_items = []
        self.selected_profession = None     # 現在保持している職業

        self.load_and_setup_data()

    # データのロードとセットアップ
    def load_and_setup_data(self):
        self.prof_data = load_json(PROF_DATA_PATH)
        if self.prof_data:      # データがロードできていれば描画する
            self.list_image_view()

    # 一覧の表示
    def list_image_view(self):
        x, y = 100, 230
        view_x, view_y = 100, 40
        for prof_key, prof_data in self.prof_data.items():
            name = prof_data["name"]
            skill = prof_data["skill"]
            item = Profession(self.screen, prof_key, name, skill, x, y, view_x, view_y)
            self.prof_items.append(item)
            x += 55
            if x >= 590:
                y += 55
                x = 100
    
    def draw(self):
        for item in self.prof_items:
            item.image_draw()

    def handle_click(self, pos):
        for item in self.prof_items:
            if item.handle_click(pos):
                return item
        return None

# 趣味選択画面作るよ
class HobbySelecter:
    def __init__(self, screen, select_item):
        self.screen = screen
        self.select_item = select_item

        # 趣味データをロード
        self.hobby_list = load_json(HOBBY_DATA_PATH)

        self.label = None
        self.pull = None
        self.create_item()        

    # アイテム作成
    def create_item(self):
        # フォントの設定
        font = pygame.font.Font(FONT_PATH, FONT_SIZ)
        small_font = pygame.font.Font(FONT_PATH, SMALL_SIZ)

        self.label = Label(self.screen, font, "趣味", 548, 175)
        listitem = self.select_item if self.select_item != "" else "未選択"
        self.pull = PullDown(self.screen, small_font, (440,200,150,25), list(self.hobby_list), listitem, 207)

    def draw_item(self, is_dropped):
        self.label.draw()
        self.pull.draw(is_dropped)

    def handle_mouse_hover(self, pos, is_dropped):
        if self.pull.box.rect.collidepoint(pos):
            return "あなたの趣味を選択してください"
        elif self.pull.list_box and self.pull.list_box.rect.collidepoint(pos):
            self.pull.handle_mouse_hover(pos, is_dropped)
        return None
