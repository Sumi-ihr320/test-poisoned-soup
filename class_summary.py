
import random

import pygame
from pygame.locals import *

from data import *
from fanction_summary import *

# セーブロード画面作るよ
class DataWindow:
    def __init__(self, screen, flag, list):
        # 基本データ
        self.screen = screen
        self.flag = flag
        self.list = list

        # 選択したデータ
        self.select_data = None

        # フォントの設定
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)                    # 基本フォント
        self.contents_font = pygame.font.Font(FONT_PATH,CONTENTS_SIZ)        # メニュー用フォント

        # 画面表示       
        self.draw()
        self.data_set(self.list)

    # データ表示ボックスを表示
    def draw(self):
        w = 400
        h = 500
        x = (self.screen.get_width() / 2) - (w / 2)
        y = (self.screen.get_height() / 2) - (h / 2)
        self.window_rect = Rect(x,y,w,h)
        pygame.draw.rect(self.screen, SHEET_COLOR,self.window_rect)
        pygame.draw.rect(self.screen, BLACK,self.window_rect,2)

        if self.flag == "save":
            top_text = "セーブ"
            enter_text = "保存"
        else:
            top_text = "ロード"
            enter_text = "開始"

        self.top = Label(self.screen, self.contents_font, top_text, y=80, center_flag=True)
        self.enter = Label(self.screen, self.contents_font, enter_text, 250, 500)
        self.close = Label(self.screen, self.contents_font, "CLOSE", 480, 500)
        self.lbl_list = [self.enter,self.close]

        # マウスオーバーで枠を表示するよ
        key = pygame.mouse.get_pos()
        for lbl in self.lbl_list:
            if lbl.rect.collidepoint(key):
                pygame.draw.rect(self.screen, BLACK, lbl.rect, 1)

    def data_set(self, datas):
        x = (self.screen.get_width() / 2) - 150
        start_y = 150
        y = start_y
        self.data_lbl_list = []
        for data in datas:
            if self.select_data == data:
                color = WHITE
            else:
                color = SHEET_COLOR
            data_name = data.replace(".json", "")
            self.data_lbl_list.append(Label(self.screen, self.font, data_name, x, y, background=color))
            y += 30

# ページ移動用の矢印表示するよ
class PageNavigation:
    def __init__(self, screen, page_flag=0):
        self.screen = screen
        self.navi_rect = self.draw(page_flag)

    # 画像表示
    def draw(self, page_flag):
        img = f"{PATH}{PICTURE}navigate.png"
        navi_img = pygame.image.load(img).convert_alpha()
        if page_flag == UNDER:
            navi_img = pygame.transform.rotate(navi_img, 90)
            navi_img = pygame.transform.scale(navi_img, (500,40))
        else:
            navi_img = pygame.transform.scale(navi_img, (40,355))
        navi_rect = navi_img.get_rect()
        if page_flag == RIGHT: # 右側のナビゲーション
            navi_x, navi_y = 740, 40
            triangle = [[750,190],[770,210],[750,230]]
        elif page_flag == LEFT: # 左側のナビゲーション
            navi_x, navi_y = 20, 40
            triangle = [[50,190],[30,210],[50,230]]
        else:   # 下側のナビゲーション
            navi_x = self.screen.get_width() / 2 - navi_rect.centerx
            navi_y = 350
            triangle = [[380,360],[400,380],[420,360]]

        # ナビゲーションの表示
        navi_rect.centerx += navi_x
        navi_rect.centery += navi_y
        self.screen.blit(navi_img, navi_rect)

        # 三角形の描画
        pygame.draw.polygon(self.screen, BLACK, triangle)

        return navi_rect
    
    def handle_click(self, pos):
        if self.navi_rect.collidepoint(pos):
            return True

# ラベル作成をクラス化するよ    (chatGPT指南)
class Label:
    def __init__(self, screen, font, text, x=0, y=0, color=BLACK, center_flag=False, background=None):
        self.screen = screen
        self.font = font
        self.text = text
        self.color = color
        self.background = background
        self.rect = self.create_label(x, y, center_flag)

    # ラベルを作る
    def create_label(self, x, y, center_flag):
        surface = self.font.render(self.text, True, self.color, self.background)
        rect = surface.get_rect(left=x, top=y)
        if center_flag:
            rect.centerx = DISPLAY_SIZE[0] / 2
        return rect

    # ラベルを描画する
    def draw(self):
        # 必要に応じて再描画をできる
        surface = self.font.render(self.text, True, self.color, self.background)
        self.screen.blit(surface, self.rect)

    def update_text(self, new_text):
        surface = self.font.render(new_text, True, self.color, self.background)
        self.screen.blit(surface, self.rect)

    # 指定した点が描画内かをチェック
    def collidepoint(self, pos):
        return self.rect.collidepoint(pos)

# ボタン作成をクラス化 やってみた     (chatGPT修正)
class Button:
    def __init__(self, screen, font, rect, text, on_click=None):
        self.screen = screen
        self.font = font
        self.texts = text.splitlines()
        
        self.rect = Rect(rect)

        # 色情報
        self.out_color = GRAY
        self.in_color = WHITE
        self.on_color = BLUE
        self.text_color = BLACK

        # テキスト表示用
        self.surfaces = []
        self.text_rects = []

        self.create_button()

        # コールバック関数
        self.on_click = on_click

    def create_button(self):
        self.create_text()
        self.draw()

    # テキストの作成
    def create_text(self):
        total_h = 0
        for txt in self.texts:
            surface = self.font.render(txt, True, self.text_color)
            rect = surface.get_rect()
            self.surfaces.append(surface)
            self.text_rects.append(rect)
            if rect.w > self.rect.w:
                self.rect.w = rect.w + 4
            total_h += rect.h        

        if total_h > self.rect.h:
            self.rect.h = total_h

    # ボタンの描画
    def draw_button(self, hover=False):
        color = self.on_color if hover else self.in_color

        # ボタンの内側
        pygame.draw.rect(self.screen, color, self.rect)
        # ボタンの外枠
        pygame.draw.rect(self.screen, self.out_color, self.rect, 2)

    # テキストの描画
    def draw_text(self):
        current_y = self.rect.top + 2
        for i, surface in enumerate(self.surfaces):
            text_rect = self.text_rects[i]
            text_rect.center = (self.rect.centerx, current_y + text_rect.h // 2)
            self.screen.blit(surface, text_rect)
            current_y += text_rect.h + 2

    # 描画する
    def draw(self):
        self.draw_button()
        self.draw_text()

    # クリックされたときTrueを返す
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    # 更新
    def update(self, pos, click=None):
        hover = self.is_clicked(pos)
        self.draw_button(hover)
        self.draw_text()

        if hover:
            if click:
                if self.on_click:
                    self.on_click() # コールバック関数を呼び出す
            return True
        else:
            return False

# インプットボックスをクラス化するよ    ラベル表示機能を付けるよ(chatGPT指南)
class InputBox:
    def __init__(self, screen, font, rect, label_text="", input_flag=True, line_bold=2):
        self.screen = screen
        self.font = font

        self.input_flag = input_flag
        self.rect = rect
        self.line_bold = line_bold
        
        # ボックスのカラーの設定
        self.update_color()

        # ラベルの設定
        self.label_text = label_text
        self.label_surface = None
        self.label_rect = None
        if self.label_text:
            self.create_label()
    
    # ラベルの作成
    def create_label(self):
        self.label_surface = self.font.render(self.label_text, True, BLACK)
        self.label_rect = self.label_surface.get_rect(center=(self.rect.centerx, self.rect.centery))

    # ボックスの描画
    def draw_box(self):
        # 入力ボックス
        pygame.draw.rect(self.screen, self.color, self.rect)
        # 下線
        pygame.draw.line(self.screen, BLACK, (self.rect.x, self.rect.y+self.rect.h-1), (self.rect.x+self.rect.w-1, self.rect.y+self.rect.h-1),
                         self.line_bold)
        
        # ラベルがあれば描写
        if self.label_surface:
            self.screen.blit(self.label_surface, self.label_rect)

    # 色を更新するメソッド
    def update_color(self):
        self.color = WHITE if self.input_flag else SHEET_COLOR

    # フラグを設定して再描画できるようにする
    def set_input_flag(self, flag):
        self.input_flag = flag
        self.update_color()

    # ボックスの描画を更新
    def update(self):
        self.draw_box()

    def update_label(self, new_text):
        self.label_text = new_text
        self.create_label()

# 画像表示をクラス化するよ
class Image:
    def __init__(self, screen, path, size, x, y, line_flag=False, line_width=1, bg_flag=False):
        self.screen = screen

        self.img, self.rect = self.create_image(path, size)
        self.set_rect(x, y)

        self.bg_flag = bg_flag
        self.line_flag = line_flag
        self.line_width = line_width

    # イメージを作成するよ
    def create_image(self, path, size):
        try:
            # 画像の読み込み＆アルファ化(透明化)
            img = pygame.image.load(path).convert_alpha()
            # 画像の縮小
            img = pygame.transform.rotozoom(img, 0, size)
            # 画像の位置取得
            rect = img.get_rect()
            return img, rect
        except pygame.error as e:
            print(f"Error loading image: {e}")
        
    # 配置をセットするよ
    def set_rect(self, x, y):
        # 位置を変更する
        if x == "center":
            self.rect.centerx = self.screen.get_width() // 2 
        else:
            self.rect.centerx += x
        if y == "center":
            self.rect.centery = self.screen.get_height() // 2
        else:
            self.rect.centery += y

    # 画像を表示するよ
    def draw(self):
        # 背景を白にする場合
        if self.bg_flag:
            pygame.draw.rect(self.screen, WHITE, self.rect)

        # 画像の描写
        self.screen.blit(self.img, self.rect)

        # 画像の枠を描画する場合
        if self.line_flag:
            pygame.draw.rect(self.screen, BLACK, self.rect, self.line_width)

# 箱をクラスにするよ
class Box:
    def __init__(self, screen, x, y, w, h):
        self.screen = screen
        self.rect = self.draw_box(x, y, w, h)

    def draw_box(self, x, y, w, h):
        pygame.draw.rect(self.screen, GRAY,(x, y, w, h))
        pygame.draw.rect(self.screen, WHITE, (x+1, y+1, w-2, h-2))
        return Rect(x, y, w, h)

# プルダウン機能をクラス化できないかな？
class PullDown:
    def __init__(self, screen, font, rect, text, item_list, pd_h=285):
        self.screen = screen
        self.font = font

        self.box_rect = self.create_box(rect)
        # プルダウンボックスに最初に表示される文字を表示するよ
        self.label = Label(self.screen, self.font, str(text), rect[0]+5, rect[1]+4, background=WHITE)
        self.label.draw()
        self.item_list = item_list

        # 現在表示されているアイテム
        self.selected_item = ""

        # プルダウンボックスのアイテムの位置のリスト
        self.items = []
        self.pd_h = pd_h            # プルダウンボックスの最大高さ
        self.list_box = None

        self.is_dropped = False     # プルダウンが開いているかのフラグ

    # ボックス作るよ
    def create_box(self,rect):
        x = rect[0] + 5
        y, w, h = rect[1], rect[2], rect[3]
        box = Box(self.screen, x, y, w, h)

        # 三角作るよ
        tx = x + w -25
        ty = y + 3
        triangle = Label(self.screen, self.font, "▼", tx, ty, background=WHITE)
        triangle.draw()
        return box.rect
    
    def toggle_pulldown_list(self):
        self.is_dropped = not self.is_dropped
        print(f"Dropdown toggled: {self.is_dropped}")  # トグルの状態を表示  
        if self.is_dropped:
            self.create_pulldown_list()

    # プルダウン押した時に表示される項目表示したいよ
    def create_pulldown_list(self):
        x = self.box_rect.x + 3
        y = self.box_rect.y + self.box_rect.h + 3
        self.draw_list(self.item_list, x, y)

    # リストを表示する
    def draw_list(self, list, x, y):
        w = self.box_rect.w
        self.items.clear()  # 以前のアイテムをクリア
        lis_rect = None     # クリック感知の範囲は文字の範囲だけではなく少し広い範囲に設定するためのリスト用rect
        y_initial = y   # 最初のy位置を記録
        current_x, current_y = x, y   # 現在の位置
        max_w = w       # 横に広がった際の幅
        for item in list:
            # 項目作成
            surface = self.font.render(item, True, BLACK)
            rect = surface.get_rect(left=current_x,top=current_y)
            # 項目名とそのsurface, rectを辞書に登録していく
            lis_rect = Rect(rect.x, rect.y, w, rect.h)
            self.items.append((item, surface, lis_rect))

            # 表示位置を下にずらす
            current_y += rect.h + 1
            
            # プルダウンボックスより下は隣に表示する
            if current_y >= (y_initial + self.pd_h):
                current_x += current_x + w
                max_w += w
                current_y = y_initial

        # リストボックスを作って文字を表示する
        self.list_box = Box(self.screen, x, y_initial, max_w, self.pd_h)
        for item, surface, rect in self.items:
            self.screen.blit(surface, rect)

    def handle_click(self, pos):
        print(f"Handling click at position: {pos}")  # クリック位置の確認 
        if self.is_dropped:
            if self.list_box.rect.collidepoint(pos):
                print("Dropdown is open and click detected inside the dropdown.") 
                for item, surface, lis_rect in self.items:
                    if lis_rect.collidepoint(pos):
                        print(f"Item selected: {item}")  # 選択されたアイテムの確認
                        self.selected_item = item   # 選択されたアイテムを保持
                        self.label.text = f"{item}" # 表示されるラベルを更新
                        self.is_dropped = False     # プルダウンを閉じる
                        break
            else:
                print("Click detected outside the dropdown, keeping it open.") 
                return
        else:
            print("Dropdown is closed, handling other clicks.")
            return
    
    def is_open(self):
        return self.is_dropped

# ダイスロールをクラス化するよ（画像表示はやめとこうかなって悩んでるよ）
class DiceRoll:
    def __init__(self, dice_text):
        self.text = dice_text

        # 個数、何面、プラスαのアイテム
        self.pieces, self.dice, self.plus_item = dice_confirmation(self.text)
        # 計算結果
        self.val = self.dice_roll()
    
    # ダイスロールの計算
    def dice_roll(self):
        val = 0
        # ランダムで数字を出して個数分＋する
        for _ in range(self.pieces):
            val += random.randint(1, self.dice)
        
        # プラスα文字列があった場合は計算する
        if self.plus_item:
            index = self.plus_item.end()
            item_num = int(self.text[index])
            val = val + item_num if self.plus_item.group() == "+" else val - item_num
        return val

# ステータス作るよ
class Status:
    MAX_STATUS_VALUE = 99

    def __init__(self, screen, name, status_name, label_name, x, y, w, h, text="", button_flag=True, input_flag=True, box_flag=True, dice_text=""):
        self.screen = screen
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)

        self.name = name                # ステータスの名前
        self.status_name = status_name  # CharaStatusでの名前
        self.label_name = label_name if label_name != "" else self.name     # 実際に表示する名前（スペースなどで位置調整する場合があるため）
        self.text = text                # 説明文
        self.dice_text = dice_text      # ダイスボタンに表示するテキスト
        self.status_label = Label(self.screen, self.font, self.label_name, x, y)    # ラベル作成

        # ステータスの値 初期化
        if self.status_name == "name" and self.status_name == "sex":
            self.status = ""
        else:
            self.status = 0

        # 入力可能かのフラグ
        self.input_flag = input_flag
        self.input = None   # 初期化
        self.input_label = None
        if box_flag:    # インプットボックスを作るかのフラグ
            self.create_input(x, y, w, h)

        self.button = None  # 初期化
        if button_flag: # ダイスボタンを作るかのフラグ
            self.create_dice_button()

    # インプットボックスを作成
    def create_input(self, x, y, w, h):
        # ステータスラベルの隣
        input_x = x + self.status_label.rect.w + 5
        input_y = y - 4     # ラベルより大きいので少し上に
        if self.status_name != "sex" and self.status_name in CharaStatus:
            self.status = CharaStatus[self.status_name]
        self.input = InputBox(self.screen, self.font, Rect(input_x, input_y, w, h), str(self.status), self.input_flag)

    # ダイスボタンを作成
    def create_dice_button(self):
        # インプットボックスがあればその位置、なければラベルの位置
        rect = self.input.rect.copy() if self.input else self.status_label.rect.copy()
        # その幅分隣
        rect.x = rect.x + rect.w + 5
        # ボタンのほうがインプットボックスや元のラベルより大きいので少し上に表示する
        rect.y = rect.y - 2
        self.button = Button(self.screen, self.font, rect, self.dice_text, self.dice_process)

    def draw(self):
        self.status_label.draw()
        if self.input:
            self.input.draw_box()
        if self.button:
            self.button.draw()

    # ステータスの自動計算
    def auto_calculation(self, name):
        calculations = {"STR": [self.calculation_damege_bonus],
                        "SIZ": [self.calculation_damege_bonus, self.calculation_health_point],
                        "CON": [self.calculation_health_point],
                        "POW": [self.calculation_power_related],
                        "INT": [self.calculation_idea],
                        "EDU": [self.calculation_educated_point],
                        "DEX": [self.calculation_avoid_point]}

        if name in calculations:
            for calculation in calculations[name]:
                calculation()

    # ダメージボーナスの計算
    def calculation_damege_bonus(self):
        st = CharaStatus["STR"] + CharaStatus["SIZ"]
        if 2 <= st <= 12:       val = "-1D6"
        elif 13 <= st <= 16:    val = "-1D4"
        elif 25 <= st <= 32:    val = "+1D4"
        elif 33 <= st <= 40:    val = "+1D6"
        else:                   val = "0"
        CharaStatus["DB"] = val

    # HPの計算
    def calculation_health_point(self):
        CharaStatus["HP"] = (CharaStatus["CON"] + CharaStatus["SIZ"]) // 2

    # POW 関連の計算
    def calculation_power_related(self):
        # MP、幸運、SAN値の計算
        CharaStatus["MP"] = CharaStatus["POW"]
        val = CharaStatus["POW"] * 5
        CharaStatus["Luck"] = val
        CharaStatus["SAN"] = val

    # アイデアの計算
    def calculation_idea(self):
        CharaStatus["Idea"] = CharaStatus["INT"] * 5

    # 知識の計算
    def calculation_educated_point(self):
        val = CharaStatus["EDU"] * 5
        CharaStatus["Know"] = val if val < 99 else 99
        
    # 回避の計算
    def calculation_avoid_point(self):
        CharaStatus["Avo"] = CharaStatus["DEX"] * 2

    # 入力ボックスの最大値最小値を決めるよ
    def determine_input_range(self):
        min, max = 0, self.MAX_STATUS_VALUE

        # 最大値最小値を決めるよ
        if self.status_name == "age":
            min = CharaStatus["EDU"] + 6

        elif self.dice_text:
            pieces, dice, plus_item = dice_confirmation(self.dice_text)
            min, max = pieces, dice * pieces
            if plus_item:
                num = int(self.dice_text[-1])
                if plus_item.group() == "+":
                    min += num
                    max += num
                else:
                    min -= num
                    max -= num
        return min, max
    
    # 入力ボックスの処理まとめるよ
    def input_process(self):
        min, max = self.determine_input_range()

        val = self.input_get(min, max)
        if val is not None:
            if self.input:
                self.input.update_label(f"{val}")
            CharaStatus[self.status_name] = val
            self.auto_calculation(self.status_name)

    # インプットボックスの処理をまとめるよ
    def input_get(self, min=0, max=100):
        # 表示項目
        title = self.name
        text = f"あなたの{self.name}を入力してください"
        txt = CharaStatus[self.status_name]

        if type(txt) == str:
            val = simpledialog.askstring(title, text, initialvalue=txt)
        elif type(txt) == int:
            val = simpledialog.askinteger(title, text, initialvalue=txt, minvalue=min, maxvalue=max)
        if val != None:
            CharaStatus[self.status_name] = val
        return val

    # ダイス処理まとめるよ
    def dice_process(self):
        dice = DiceRoll(self.dice_text)
        CharaStatus[self.status_name] = dice.val
        self.auto_calculation(self.status_name)
        self.input.update_label(f"{dice.val}")

    def handle_mouse_hover(self, pos):
        if self.status_label.rect.collidepoint(pos):
            return self.text
        elif self.input and self.input.rect.collidepoint(pos):
            return self.text
        elif self.button and self.button.rect.collidepoint(pos):
            return "ダイスでランダムに値を決めることができます"
        return None

# 選んだ性別によって画像が変わるようにするよ
class SexChange:
    def __init__(self, screen, x, y, flag, image_x=40, image_y=40):
        self.screen = screen
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)

        # フラグがtrueなら男、falseなら女が選択されている
        self.man = self.create_button("男", x, y, flag)
        self.woman = self.create_button("女", x+40, y, not flag)

        # 画像を作成
        self.image_x = image_x
        self.image_y = image_y
        self.man_image = self.create_image(True)
        self.woman_image = self.create_image(False)

    # ボタン作るよ
    def create_button(self, text, x, y, flag):
        push_color = (106,93,33)
        no_push_color = SHEET_COLOR
        
        # 背景色と文字色をフラグによって変える
        background = push_color if flag else no_push_color
        color = WHITE if flag else BLACK
        return Label(self.screen, self.font, text, x, y, color, background=background)

    # 画像作るよ
    def create_image(self, flag):
        sex = "man" if flag else "woman"
        img_path = f"{PATH}{PICTURE}silhouette_{sex}.png"
        return Image(self.screen, img_path, 0.5, self.image_x, self.image_y, line_flag=True, line_width=2)

    # 性別が変わった時にボタンの状態を更新する
    def update_sex(self, flag):
        self.man = self.create_button("男", self.man.rect.x, self.man.rect.y, flag)
        self.woman = self.create_button("女", self.woman.rect.x, self.woman.rect.y, not flag)

    # 描画するよ
    def draw(self, flag):
        self.man.draw()
        self.woman.draw()
        if flag:
            self.man_image.draw()
        else:
            self.woman_image.draw()

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

        self.show_img_flag = False
        
    # 画像インスタンスを作成
    def load_img(self, x, y, size):
        try:
            return Image(self.screen, self.path, size, x, y, line_flag=True, bg_flag=True)
        except FileNotFoundError:
            print(f"Error: 画像が見つかりません - {self.path}")
            return None

    # 画像を表示
    def image_draw(self):
        if self.small_img:
            self.small_img.draw()
        if self.show_img_flag and self.big_img:
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
            self.show_img_flag = not self.show_img_flag     # クリックすると逆の状態になる
            CharaStatus["Profession"] = self.name
            ProfDataIn()
            return True
        else:
            return False

# 職業選択画面作るよ
class ProfessionSelecter:
    def __init__(self, screen):
        self.screen = screen
        self.prof_items = []
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


# 趣味選択画面作るよ
class HobbySelecter:
    def __init__(self, screen):
        self.screen = screen

        self.set_data()
        self.draw_item()        

    # 趣味データをロード
    def set_data(self):
        self.hobby_list = load_json(HOBBY_DATA_PATH)
        self.select_item = ""
   
    def draw_item(self):
        # フォントの設定
        font = pygame.font.Font(FONT_PATH, FONT_SIZ)
        small_font = pygame.font.Font(FONT_PATH, SMALL_SIZ)
        
        label = Label(self.screen, font, "趣味", 545, 175)
        label.draw()
        listitem = self.select_item if self.select_item != "" else "未選択"
        self.pull = PullDown(self.screen, small_font, (435,200,150,25), listitem, list(self.hobby_list), 207)
        self.select_item = self.pull.selected_item

    def handle_mouse_hover(self, pos):
        if self.pull.box_rect.collidepoint(pos):
            return "あなたの趣味を選択してください"
        return None

