
import random

import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog

import pygame
from pygame.locals import *


from data import *
from fanction_summary import *

# ページ移動用の矢印表示するよ
class PageNavigation:
    def __init__(self, screen, position_flag=0):
        self.screen = screen
        self.position_flag = position_flag

        self.rect_dic = {RIGHT:{"x":740, "y":40, "triangle":[[750,190],[770,210],[750,230]]},
                         LEFT:{"x":20, "y":40, "triangle":[[50,190],[30,210],[50,230]]},
                         UNDER:{"x":None,"y":350,"triangle":[[380,360],[400,380],[420,360]]}}

        self.navi_img = None
        self.navi_rect = None
        self.create_image()

    # ナビゲーションの作成
    def create_image(self):
        img_path = f"{PATH}{PICTURE}navigate.png"
        self.navi_img = pygame.image.load(img_path).convert_alpha()
        if self.position_flag == UNDER:
            self.navi_img = pygame.transform.rotate(self.navi_img, 90)
            self.navi_img = pygame.transform.scale(self.navi_img, (500,40))
        else:
            self.navi_img = pygame.transform.scale(self.navi_img, (40,355))

        self.navi_rect = self.navi_img.get_rect()
        # ナビゲーションの表示
        if self.position_flag == UNDER:
            self.navi_rect.centerx = self.screen.get_width() / 2 - self.navi_rect.centerx
        else:
            self.navi_rect.centerx += self.rect_dic[self.position_flag]["x"]
        self.navi_rect.centery += self.rect_dic[self.position_flag]["y"]
    
    # 画像表示
    def draw(self):
        # バーの描画
        self.screen.blit(self.navi_img, self.navi_rect)

        # 三角形の描画
        pygame.draw.polygon(self.screen, BLACK, self.rect_dic[self.position_flag]["triangle"])
    
    def handle_click(self, pos):
        if self.navi_rect.collidepoint(pos):
            return True
        return False

# ラベル作成をクラス化するよ    (chatGPT指南)
class Label:
    def __init__(self, screen, font, text, x=0, y=0, centerx=None, centery=None, position="left", color=BLACK, background=None):
        self.screen = screen
        self.font = font
        self.text = text
        self.color = color
        self.background = background
        self.rect = self.create_label(x, y, centerx, centery, position)

    # ラベルを作る
    def create_label(self, x, y, centerx, centery, position):
        surface = self.font.render(self.text, True, self.color, self.background)
        if position == "right":
            rect = surface.get_rect(right=x, top=y)
        else:
            rect = surface.get_rect(left=x, top=y)
        if centerx:
            rect.centerx = centerx
        if centery:
            rect.centery = centery
        return rect

    # ラベルを描画する
    def draw(self):
        # 必要に応じて再描画をできる
        surface = self.font.render(self.text, True, self.color, self.background)
        self.screen.blit(surface, self.rect)

    def update_text(self, new_text):
        self.text = new_text
        self.draw()
        #surface = self.font.render(new_text, True, self.color, self.background)
        #self.screen.blit(surface, self.rect)

    def set_background_color(self, color):
        self.background = color
        self.draw()
        #surface = self.font.render(self.text, True, self.color, color)
        #self.screen.blit(surface, self.rect)
        
    # 指定した点が描画内かをチェック
    def collidepoint(self, pos):
        return self.rect.collidepoint(pos)

# ボタン作成をクラス化 やってみた     (chatGPT修正)
class Button:
    def __init__(self, screen, font, text, rect, on_click=None, text_color=BLACK, in_color=WHITE, out_color=GRAY, on_color=BLUE):
        self.screen = screen
        self.font = font
        self.texts = text.splitlines()
        
        self.rect = Rect(rect)

        # 色情報
        self.in_color = in_color
        self.out_color = out_color
        self.on_color = on_color
        self.text_color = text_color

        # テキスト表示用
        self.surfaces = []
        self.text_rects = []
        self.text_total_h = 0
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

        # 文字列の高さの合計がボタンの高さより高ければそれをボタンの高さにする
        if total_h > self.rect.h:
            self.rect.h = total_h

        self.text_total_h = total_h

    # ボタンの描画
    def draw_button(self, hover=False):
        color = self.on_color if hover else self.in_color

        # ボタンの内側
        pygame.draw.rect(self.screen, color, self.rect)
        # ボタンの外枠
        pygame.draw.rect(self.screen, self.out_color, self.rect, 2)

    # テキストの描画
    def draw_text(self):
        current_y = self.rect.y + ((self.rect.h - self.text_total_h) // 2)
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
        self.label = None
        if self.label_text:
            self.create_label()
    
    # ラベルの作成
    def create_label(self):
        self.label = Label(self.screen, self.font, self.label_text, centerx=self.rect.centerx, centery=self.rect.centery)

    # ボックスの描画
    def draw_box(self):
        # 入力ボックス
        pygame.draw.rect(self.screen, self.color, self.rect)
        # 下線
        pygame.draw.line(self.screen, BLACK, (self.rect.x, self.rect.y+self.rect.h-1), (self.rect.x+self.rect.w-1, self.rect.y+self.rect.h-1),
                         self.line_bold)
        
        # ラベルがあれば描写
        if self.label:
            self.label.draw()

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

    # ラベルの更新
    def update_label(self, new_text):
        self.label_text = new_text
        self.create_label()

    def get_value(self):
        # ラベルに表示されている文字を、数字ならintにしてそうでないなら文字列として返す
        try:
            val = int(self.label_text)
        except ValueError:
            val = self.label_text
        return val

# 画像表示をクラス化するよ
class Image:
    def __init__(self, screen, path, size, x=0, y=0, centerx=None, centery=None ,line_flag=False, line_width=1, bg_flag=False, area=None):
        self.screen = screen

        self.img, self.rect = self.create_image(path, size)
        self.set_rect(x, y, centerx, centery)

        self.bg_flag = bg_flag
        self.line_flag = line_flag
        self.line_width = line_width
        self.area = area

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
    def set_rect(self, x, y, centerx, centery):
        # 位置を変更する
        if x == "center":
            self.rect.centerx = self.screen.get_width() // 2
        elif centerx:
            self.rect.centerx = centerx
        else:
            self.rect.centerx += x
        if y == "center":
            self.rect.centery = self.screen.get_height() // 2
        elif centery:
            self.rect.centery = centery
        else:
            self.rect.centery += y

    # 画像を表示するよ
    def draw(self):
        # 背景を白にする場合
        if self.bg_flag:
            pygame.draw.rect(self.screen, WHITE, self.rect)

        # 画像の描写
        self.screen.blit(self.img, self.rect, area=self.area)

        # 画像の枠を描画する場合
        if self.line_flag:
            pygame.draw.rect(self.screen, BLACK, self.rect, self.line_width)

# 箱をクラスにするよ (主にプルダウンで使ってるよ)
class Box:
    def __init__(self, screen, x, y, w, h):
        self.screen = screen
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = Rect(x, y, w, h)

    def draw(self):
        pygame.draw.rect(self.screen, GRAY, self.rect)
        pygame.draw.rect(self.screen, WHITE, (self.x+1, self.y+1, self.w-2, self.h-2))

# プルダウン機能をクラス化できないかな？
class PullDown:
    def __init__(self, screen, font, rect, item_list, label_text="", pd_h=285):
        self.screen = screen
        self.font = font

        # プルダウンする前のボックス
        self.box = None
        self.triangle = None        # ボックスに表示される ▼
        self.create_box(Rect(rect))

        # ボックスに表示される文字
        self.label_text = label_text
        self.label = None
        if label_text:
            self.create_label()

        # プルダウンに表示するリスト
        self.item_list = item_list

        # プルダウンボックスのアイテムの位置のリスト
        self.items = []
        self.pd_h = pd_h            # プルダウンボックスの最大高さ
        self.list_box = None

    # ボックス作るよ
    def create_box(self, rect):
        self.box = Box(self.screen, rect.x, rect.y, rect.w, rect.h)

        # 三角作るよ
        self.triangle = Label(self.screen, self.font, "▼", rect.right-5, centery=rect.centery, position="right")
    
    # 表示するラベル作るよ
    def create_label(self):
        self.label = Label(self.screen, self.font, self.label_text, x=self.box.rect.x+5, centery=self.box.rect.centery)

    # ボックスの表示
    def draw(self, is_dropped):
        # ボックスと▼
        self.box.draw()
        self.triangle.draw()

        # テキストがあればテキスト
        if self.label:
            self.label.draw()

        if is_dropped:
            self.draw_list_box()

    # ラベルの更新
    def update_label(self, new_text):
        self.label_text = new_text
        self.create_label()

    # プルダウン押した時に表示される項目表示したいよ
    def create_pulldown_list(self):
        x = self.box.rect.x
        y = self.box.rect.y + self.box.rect.h
        self.create_list(self.item_list, x, y)

    # リストを作成する
    def create_list(self, list, x, y):
        w = self.box.rect.w
        self.items.clear()  # 以前のアイテムをクリア
        lis_rect = None     # クリック感知の範囲は文字の範囲だけではなく少し広い範囲に設定するためのリスト用rect
        y_initial = y   # 最初のy位置を記録
        current_x, current_y = x+1, y   # 現在の位置
        max_w = w       # 横に広がった際の幅
        for item in list:
            surface = self.font.render(item, True, BLACK)
            rect = surface.get_rect(left=current_x,top=current_y)
            # 項目名とそのsurface, rectを辞書に登録していく
            lis_rect = Rect(rect.x, rect.y, w, rect.h)
            self.items.append((item, surface, lis_rect))

            # 表示位置を下にずらす
            current_y += rect.h + 1
            
            # プルダウンボックスより下は隣に表示する
            if current_y >= (y_initial + self.pd_h):
                current_x += w
                max_w += w
                current_y = y_initial

        # リストボックスを作る
        self.list_box = Box(self.screen, x, y_initial, max_w+2, self.pd_h+1)

    # リストボックスを表示する
    def draw_list_box(self, hover_item=""):
        self.create_pulldown_list()
        self.list_box.draw()
        for item, surface, rect in self.items:
            # hoverされてる時は背景色を変える
            if item == hover_item:
                pygame.draw.rect(self.screen, BLUE, rect)
            else:
                pygame.draw.rect(self.screen, WHITE, rect)
            # テキストを描画
            self.screen.blit(surface, rect)

    # マウスオーバーで重なってるアイテムを取得    
    def check_mouse_hover(self, pos):
        for item, surface, rect in self.items:
            if rect.collidepoint(pos):
                return item
        return None

    # クリック時の動作
    def handle_click(self, pos, is_dropped):
        if is_dropped:
            if self.list_box and self.list_box.rect.collidepoint(pos):
                for item, surface, lis_rect in self.items:
                    if lis_rect.collidepoint(pos):
                        return item
        return None
    
    # マウスオーバー時の動作
    def handle_mouse_hover(self, pos, is_dropped):
        if is_dropped:
            hover_item = self.check_mouse_hover(pos)
            if hover_item:
                self.draw_list_box(hover_item)

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

    def __init__(self, screen, root, name, status_name, label_name, status, x, y, w, h, text="", button_flag=True, input_flag=True, box_flag=True, dice_text=""):
        self.screen = screen
        self.root = root
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)

        self.name = name                # ステータスの名前
        self.status_name = status_name  # CharaStatusでの名前
        self.label_name = label_name if label_name != "" else self.name     # 実際に表示する名前（スペースなどで位置調整する場合があるため）
        self.text = text                # 説明文
        self.dice_text = dice_text      # ダイスボタンに表示するテキスト
        self.status_label = Label(self.screen, self.font, self.label_name, x, y)    # ラベル作成

        # ステータスの値
        self.status = status

        # 入力可能かのフラグ
        self.input_flag = input_flag
        self.input = None   # 初期化
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
        self.input = InputBox(self.screen, self.font, Rect(input_x, input_y, w, h), str(self.status), self.input_flag)

    # ダイスボタンを作成
    def create_dice_button(self):
        # インプットボックスがあればその位置、なければラベルの位置
        rect = self.input.rect.copy() if self.input else self.status_label.rect.copy()
        # その幅分隣
        rect.x = rect.x + rect.w + 5
        self.button = Button(self.screen, self.font, self.dice_text, rect, self.dice_process)

    def draw(self):
        self.status_label.draw()
        if self.input:
            self.input.draw_box()
        if self.button:
            self.button.draw()

    # 入力ボックスの最大値最小値を決めるよ
    def determine_input_range(self, edu):
        min, max = 0, self.MAX_STATUS_VALUE

        # 最大値最小値を決めるよ
        if self.status_name == "age":
            min = edu + 6

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
    def input_process(self, edu):
        min, max = self.determine_input_range(edu)
        value_type = type(self.status)
        num = 2 if value_type == int else None
        CustomDialog(self.root, self.name, f"あなたの{self.name}を入力してください", value_type, min, max, num, self.handle_input)
        
    # カスタムダイアログに入力された値を取得してラベルを更新する
    def handle_input(self, value):
        if value is not None:
            if self.input:
                self.input.update_label(f"{value}")

    # ダイス処理まとめるよ
    def dice_process(self):
        dice = DiceRoll(self.dice_text)
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
        return Label(self.screen, self.font, text, x, y, color=color, background=background)

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

        #self.show_img_flag = False
        
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
    def __init__(self, screen, is_dropped, select_item):
        self.screen = screen
        self.is_dropped = is_dropped
        self.select_item = select_item

        self.set_data()
        self.draw_item()        

    # 趣味データをロード
    def set_data(self):
        self.hobby_list = load_json(HOBBY_DATA_PATH)
   
    def draw_item(self):
        # フォントの設定
        font = pygame.font.Font(FONT_PATH, FONT_SIZ)
        small_font = pygame.font.Font(FONT_PATH, SMALL_SIZ)
        
        label = Label(self.screen, font, "趣味", 548, 175)
        label.draw()
        listitem = self.select_item if self.select_item != "" else "未選択"
        self.pull = PullDown(self.screen, small_font, (440,200,150,25), list(self.hobby_list), listitem, 207)
        self.pull.draw(self.is_dropped)

    def handle_mouse_hover(self, pos, is_dropped):
        if self.pull.box.rect.collidepoint(pos):
            return "あなたの趣味を選択してください"
        elif self.pull.list_box and self.pull.list_box.rect.collidepoint(pos):
            self.pull.handle_mouse_hover(pos, is_dropped)
        return None

# simpledialogの代わり
class CustomDialog:
    def __init__(self, root, title="title", text="文字列を入力してください", type=str, min=0, max=99, num=None, callback=None):
        self.root = root
        self.root.deiconify()   # root を表示する
        self.root.lift()        # 他のウィンドウよりも前面に表示
        
        self.dialog = tk.Toplevel(root)
        self.dialog.title(title)
        self.dialog.attributes("-topmost", True)
        self.dialog.grab_set()  # フォーカスをこのウィンドウに固定
        self.dialog.protocol("WM_DELETE_WINDOW", self.close)

        self.text = text
        self.type = type
        self.min = min
        self.max = max
        self.num = num
        self.callback = callback
        self.value = tk.IntVar() if self.type == int else tk.StringVar()
        self.create_widget(self.dialog)

        # ダイアログを中央に
        self.dialog.geometry(create_size_tkinter(self.dialog))
        self.dialog.transient(root)

    def create_widget(self, parent):
        # フレーム
        frm_top = self.create_frame(parent, "top")
        frm_bottom = self.create_frame(parent, "top")

        frm_left = self.create_frame(frm_bottom, "left")
        frm_right = self.create_frame(frm_bottom, "left")
    
        # ラベル作成
        label = ttk.Label(frm_top, text=self.text)
        label.pack(pady=10, side="top")

        # エントリー作成
        vcmd = (self.dialog.register(validate_input), "%P", self.type, self.num)
        self.entry = ttk.Entry(frm_top, textvariable=self.value, validate="key", validatecommand=vcmd)
        self.entry.pack(pady=10, side="top")
        self.entry.focus()

        # ボタン作成
        self.ok = self.create_button(frm_left, "OK", self.on_ok)
        self.cancel = self.create_button(frm_right, "キャンセル", self.on_cancel)
    
    # フレーム作成
    def create_frame(self, parent, side):
        frame = ttk.Frame(parent)
        frame.pack(pady=10, side=side)
        return frame
        
    # ボタン作成
    def create_button(self, parent, text, command):
        button = ttk.Button(parent, text=text, command=command)
        button.pack(anchor="center")
        return button

    # OKボタンを押したとき
    def on_ok(self):
        value = self.value.get() if self.value.get() else None
        if value:
            if self.type == int:
                if not self.check_value(value):
                    return
        self.callback(value)
        self.close()

    # キャンセルボタンを押したとき
    def on_cancel(self):
        self.callback(None)
        self.close()

    # 閉じる
    def close(self):
        self.dialog.destroy()   # ダイアログを閉じる
        self.root.withdraw()    # rootを非表示にする

    # 値がmin-maxの間かどうかをチェックする
    def check_value(self, value):
        if self.min <= value <= self.max:
            return True
        else:
            with TopmostManager(self.dialog):
                messagebox.showerror("入力エラー", f"入力値は{self.min}から{self.max}の間で入力してください")
            return False
        
# 部屋の型を作るよ
class Room:
    # 部屋画像の縮小パーセンテージ
    SIZE = 0.19
    def __init__(self, screen, room, direction="", room2_flag=False):
        self.screen = screen
        self.room2_flag = room2_flag    # 二つ目の部屋画像を表示するかのフラグ

        # 部屋画像を表示するエリア
        self.area_rect = ROOM_AREA
        
        # ファイル名一覧
        self.room_path = create_file_path("room", room, direction)
        self.room2_path = create_file_path("room2", room, direction)
        self.scenario_list = create_scenario_path(room=room)

        # 部屋画像の作成
        self.img = Image(self.screen, self.room_path, size=self.SIZE, x="center", y=30, area=self.area_rect)
        self.img2 = Image(self.screen, self.room2_path, size=self.SIZE, x="center", y=30, area=self.area_rect) if self.room2_path else None

        # 部屋にあるアイテムの作成
        self.items = []
        self.items_draw_list = []
        self.items_select_list= []
        self.create_item(self.img.img, room, direction)

    # 画像表示するよ
    def draw(self):
        # フラグが立っていればroom_img2を表示する
        if self.room2_flag and self.img2:
            self.img2.draw()
        else:
            self.img.draw()

        if self.items_draw_list:
            for item in self.items_draw_list:
                item.draw()

    # 部屋のアイテムを作成する
    def create_item(self, surface, room, direction):
        if room == "center":
            self.light = Item(surface, "Light", room, "", "center", 24)
            self.soup = Item(surface, "Soup", room, "", "center", 224)
            directions = ["north","east","south","west"]
            position = {"north":{"tablex":"center","tabley":189,
                                 "memox":306,"memoy":237},
                        "east":{"tablex":229,"tabley":212,
                                "memox":"center","memoy":253},
                        "south":{"tablex":"center","tabley":223,
                                 "memox":392,"memoy":237},
                        "west":{"tablex":260,"tabley":213,
                                "memox":"center","memoy":223}
            }
            center_door_name = f"{direction}Door"
            index = directions.index(direction)
            left_index = index - 1
            left_direct = directions[left_index]
            left_door_name = f"{left_direct}Door"
            right_index = index + 1
            if right_index > len(directions) - 1:
                right_index = 0
            right_direct = directions[right_index]
            rigth_door_name = f"{right_direct}Door"
            self.center_door = Item(surface, center_door_name, room, direction, "center", 82)
            self.left_door = Item(surface, left_door_name, room, direction, 86, 63)
            self.right_door = Item(surface, rigth_door_name, room, direction, 568, 64)
            self.table = Item(surface, "Table", "center", direction, position[direction]["tablex"], position[direction]["tabley"])
            self.center_memo = Item(surface, "centerMemo", "center", direction, position[direction]["memox"], position[direction]["memoy"])
            self.items_draw_list = [self.center_door, self.left_door, self.right_door, self.table, self.light, self.soup, self.center_memo]
            self.items_select_list = [self.light, self.soup, self.center_memo, self.table, self.center_door, self.left_door, self.right_door]
        elif room == "north":
            self.under_storage = Item(surface, "UnderSinkStorage", "north", "", 325, 250)
            self.cooktop = Item(surface, "Cooktop", "north", "", 225, 226)
            self.sink = Item(surface, "Sink", "north", "", 468, 216)
            self.top_storage = Item(surface, "TopSinkStorage", "north", "", 325, 100)
            self.pot = Item(surface, "Pot", "north", "", 290, 203)
            self.storage = Item(surface, "Storage", "north", "", 560, 225)
            self.cupboard = Item(surface, "CupBoard", "north", "", 36, 30)
            self.fridge = Item(surface, "Fridge", "north", "", 628, 39)
            self.items_draw_list = [self.under_storage, self.cooktop, self.sink, self.top_storage, self.pot, self.storage, self.cupboard, self.fridge]
            self.items_select_list = [self.pot, self.sink, self.cooktop, self.under_storage, self.top_storage, self.storage, self.cupboard, self.fridge]
        elif room == "east":
            self.corpse = Item(surface, "Corpse", "east", "", 437, 218)
            self.east_memo = Item(surface, "eastMemo", "east", "", 277, 259)
            self.items_draw_list = [self.corpse, self.east_memo]
            self.items_select_list = [self.east_memo, self.corpse]
        elif room == "south":
            self.statue = Item(surface, "StoneStatue", "south", "",287, 69)
            self.slate1 = Item(surface, "Slate1", "south", "", 213, 156)
            self.slate2 = Item(surface, "Slate2", "south", "", 479, 156)
            self.items_draw_list = [self.statue, self.slate1, self.slate2]
            self.items_select_list = [self.statue, self.slate1, self.slate2]
        else:
            self.bookshelf = Item(surface, "BookShelf", "west", "", 36, 30)
            self.chandle = Item(surface, "Candle", "west", "", 350, 223)
            self.book = Item(surface, "Book", "west", "", 298, 246)
            self.items_draw_list = [self.bookshelf, self.chandle, self.book]
            self.items_select_list = [self.book, self.chandle, self.bookshelf]

# アイテムの型を作るよ
class Item:
    # アイテム画像の縮小パーセンテージ
    SIZE = 0.19
    def __init__(self, screen, name, room, direction, x, y, big_size=None):
        self.screen = screen
        self.name = name    # アイテム名

        # ファイルパス
        self.path = create_file_path(name, room, direction)

        # 画像
        self.img = Image(self.screen, self.path, self.SIZE, x, y)

        # シナリオファイルパス
        self.scenario_path_list = create_scenario_path(item=name)

        # クリック時画像パス
        self.big_img_path_list = create_item_path(name)
        self.big_imgs = []
        self.create_images()

    def create_images(self):
        if self.big_img_path_list:
            for path in self.big_img_path_list:
                self.big_imgs.append(Image(self.screen, path, 0.35, x="center", centery=200, line_flag=True, bg_flag=True))
        elif self.name == "Light":
            self.big_imgs.append(Image(self.screen, self.path, 0.35, x="center", centery=200, line_flag=True, bg_flag=True))

    def draw(self, is_selected=None, img_number=0):
        self.img.draw()
        if is_selected:
            if self.big_imgs:
                self.big_imgs[img_number].draw()
        pygame.draw.rect(self.screen, BLACK, self.img.rect, 1)  # デバッグ用

    def handle_click(self, pos):
        if self.img.rect.collidepoint(pos):
            return True
        return False

        # 表示するテキスト
        return self.scenario_path_list
    
        # 起こるイベント
        pass

# メニュー作るよ
class Menu:
    def __init__(self, screen, root) -> None:
        self.screen = screen
        self.root = root
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)
        self.rect = MENU_FRAME_RECT.copy()

        self.buttons = []
        self.create_button()

    # ボタン作成
    def create_button(self):
        save_button = Button(self.screen, self.font,"セーブ", Rect(self.rect.x, self.rect.y, self.rect.w,50), self.save_event, WHITE, BLACK, WHITE, GRAY)
        load_button = Button(self.screen, self.font,"ロード", Rect(self.rect.x, self.rect.y+50, self.rect.w,50), self.load_event, WHITE, BLACK, WHITE, GRAY)
        end_button = Button(self.screen, self.font,"終了", Rect(self.rect.x, self.rect.y+100, self.rect.w,50), self.save_event, WHITE, BLACK, WHITE, GRAY)
        self.buttons = [save_button, load_button, end_button]

    def save_event(self):
        pass
    
    def load_event(self):
        pass

    def end_event(self):
        Close(self.root)

    def draw(self):
        for button in self.buttons:
            button.draw()
