import pygame
from pygame.locals import *

from constans import *
from utils import *
from ui.ui_elements import *
from manager.sound_manager import SoundManager

# 職業クラス
class Profession:
    def __init__(self, screen, sheet_rect, fonts, percentage, name, eng_name, skills, rect, view_rect):
        self.screen = screen
        self.sheet_rect = sheet_rect

        self.fonts = fonts
        self.percentage = percentage

        self.name = name
        self.eng_name = eng_name
        self.skills = skills
        self.path = f"prof_{eng_name}.png"
        self.rect = rect
        self.view_rect = view_rect

        self.create_image()
    
        # サウンドの設定
        self.sound_manager = SoundManager()
        sound_check(self.sound_manager)

    # 画像を作成する
    def create_image(self):
        h_percent = self.percentage[1]
        small_img_size = 0.1 * h_percent
        big_img_size = 0.35 * h_percent

        # 画像は最初に一度だけロードしキャッシュする
        self.small_img = self.load_img(self.rect.x, self.rect.y, small_img_size)
        self.big_img = self.load_img(self.view_rect.x, self.view_rect.y, big_img_size)

    def set_position(self, size="small", x=None, y=None):
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
        font = self.fonts[0]
        small_font = self.fonts[1]

        # 名前ラベル
        lbl_name = Label(self.screen, font, f"【{self.name}】", self.big_img.rect.x+self.big_img.rect.w+5, self.big_img.rect.y)
        lbl_name.draw()

        # 所持技能ラベルの表示位置
        skill_x, skill_y = self.big_img.rect.x + self.big_img.rect.w + 15, self.big_img.rect.y + 30

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
        if self.small_img and self.small_img.rect.collidepoint(pos):
            return f"あなたの職業を選択してください\n【{self.name}】"
        return None

    def handle_click(self, pos):
        if self.small_img and self.small_img.rect.collidepoint(pos):
            self.sound_manager.play("クリック")
            return True
        return False

# 職業選択画面作るよ
class ProfessionSelecter:
    def __init__(self, screen, sheet_rect, window_size, fonts):
        self.screen = screen
        self.sheet_rect = sheet_rect
        self.window_size = window_size
        self.fonts = fonts

        self.prof_items = []
        self.selected_profession = None     # 現在保持している職業

        self.load_and_setup_data()

        self.rect = None
        self.prof_item_set_position()

    # データのロードとセットアップ
    def load_and_setup_data(self):
        self.prof_data = load_json(JSON_FOLDER, PROF_DATA_PATH)
        if self.prof_data:      # データがロードできていれば描画する
            self.list_image_view()

    # 最適な行数列数を計算する
    def calculate_best_grid(self, total_items, icon_size, margin):
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

        # ウィンドウサイズによる変更
        icon_w, icon_h = get_new_size(self.window_size, (icon_w, icon_h))
        margin_x, margin_y = get_new_size(self.window_size, (margin_x, margin_y))

        rows, cols = self.calculate_best_grid(len(self.prof_items), (icon_w, icon_h), (margin_x, margin_y))

        total_w = cols * icon_w + (cols - 1) * margin_x
        total_h = rows * icon_h + (rows - 1) * margin_y

        # 開始位置（中央に揃える）
        start_x = (self.sheet_rect.w - total_w) // 2
        start_y = self.sheet_rect.h  - total_h - 10

        self.rect = pygame.Rect(start_x, start_y, total_w, total_h)

        for i, prof in enumerate(self.prof_items):
            row = i // cols
            col = i % cols
            x = start_x + col * (icon_w + margin_x)
            y = start_y + row * (icon_h + margin_y)
            prof.set_position("small", x, y)
            prof.set_position("big", start_x, start_y-(prof.big_img.rect.h+10))
        

    # 一覧の表示
    def list_image_view(self):
        x, y = 100, 230
        view_x, view_y = 100, 40
        percentage = RATIO[self.window_size]

        for prof_key, prof_data in self.prof_data.items():
            name = prof_data["name"]
            skill = prof_data["skill"]
            item = Profession(self.screen, self.sheet_rect, self.fonts, percentage, prof_key, name, skill, Rect(x, y, 50, 50), Rect(view_x, view_y, 100, 100))
            self.prof_items.append(item)
            #x += 55
            #if x >= 590:
            #    y += 55
            #    x = 100
    
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
    def __init__(self, screen, select_item, fonts, profession_rect):
        self.screen = screen
        self.select_item = select_item
        self.fonts = fonts
        self.profession_rect = profession_rect

        # 趣味データをロード
        self.hobby_list = load_json(JSON_FOLDER, HOBBY_DATA_PATH)

        self.label = None
        self.pull = None
        self.create_item()        

    # アイテム作成
    def create_item(self):
        # フォントの設定
        font = self.fonts[0]
        small_font = self.fonts[1]

        hobby_text = "趣味"
        text_rect = font.render(hobby_text, True, BLACK).get_rect()
        self.label = Label(self.screen, font, hobby_text, self.profession_rect.right, self.profession_rect.y-text_rect.h-10, position="right")

        list_item = self.select_item if self.select_item != "" else "未選択"
        self.pull = PullDown(self.screen, small_font, Rect(440,self.label.rect.y,150,25), list(self.hobby_list), list_item, 207)
        self.pull.update_position(x=self.label.rect.right+self.label.rect.w+10, position="right")

    def draw_item(self, is_dropped):
        self.label.draw()
        self.pull.draw(is_dropped)

    def handle_mouse_hover(self, pos, is_dropped):
        if self.pull.box.rect.collidepoint(pos):
            return "あなたの趣味を選択してください"
        elif self.pull.list_box and self.pull.list_box.rect.collidepoint(pos):
            self.pull.handle_mouse_hover(pos, is_dropped)
        return None
