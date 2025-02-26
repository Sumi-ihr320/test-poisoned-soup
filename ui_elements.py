
import random

import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog

import pygame
from pygame.locals import *

from constans import *
from utils import *
from manager.sound_manager import SoundManager

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
        self.text = text
        self.texts = self.text.splitlines()
        
        self.rect = Rect(rect)

        # 色情報
        self.in_color = in_color
        self.out_color = out_color
        self.on_color = on_color
        #self.disabled_color = GRAY
        self.text_color = text_color

        # テキスト表示用
        self.surfaces = []
        self.text_rects = []
        self.text_total_h = 0
        self.create_text()

        # コールバック関数
        self.on_click = on_click

        # ボタンが有効か無効か
        self.enabled = True

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
        # enabledがtrueかつhoverした時はon_color、それ以外のenabledがtrueの時にin_color、enabledがfalseの時はdisabled_colorにする
        #color = self.on_color if (hover and self.enabled) else (self.in_color if self.enabled else self.disabled_color)

        color = self.on_color if (hover and self.enabled) else self.in_color

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
        if not self.enabled:
            return False
        return self.rect.collidepoint(pos)

    # ボタンの有効・無効を切り替える    
    def set_enabled(self, state):
        self.enabled = state

    # 更新
    def update(self, pos, click=None):
        hover = self.is_clicked(pos)
        self.draw_button(hover)
        self.draw_text()

        if hover and click and self.enabled:
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
        self.result = self.dice_roll()

        # ダイス音を鳴らす
        self.sound_manager = SoundManager()
        self.sound()

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
    
    # 成否判定
    def check(self, threshold):
        """
        threshold: 判定の基準値
        return: 成否 (bool)
        """
        return self.result <= threshold
    
    def sound(self):
        sound_name = "ダイスを振る"
        if not self.sound_manager.sounds or sound_name not in self.sound_manager.sounds:
            self.sound_manager.load_sound(sound_name, "W-DISE.mp3")
        self.sound_manager.play(sound_name)

# コマンドメニュー
class CommandMenu:
    def __init__(self, screen, commands, start_position):
        self.screen = screen

        self.commands = commands
        self.start_x, self.start_y = start_position
        self.buttons = []
        self.create_buttons()

    # コマンドリストからボタンを作成
    def create_buttons(self):
        font = pygame.font.Font(FONT_PATH, SMALL_SIZ)
        x, y = self.start_x, self.start_y
        w, h = 120, 30

        if self.commands:
            for command in self.commands:
                button = Button(self.screen, font, command["text"], (x,y,w,h), out_color=BLACK)
                self.buttons.append({"button":button, "next_scenario": command["next"]})
                y += h

    def draw(self):
        for item in self.buttons:
            item["button"].draw()

    def handle_mouse_hover(self, pos):
        for item in self.buttons:
            item["button"].update(pos)

    def handle_click(self, pos):
        # クリックされたイベントを判定
        for item in self.buttons:
            if item["button"].is_clicked(pos):
                return item["next_scenario"]
        return None

# 主人公の名前・HP・MP・現在地を右上に表示する
class PlayerDataView:
    def __init__(self, screen, player, game_state) -> None:
        self.screen = screen
        self.font = pygame.font.Font(FONT_PATH, SMALL_SIZ)

        self.player = player
        self.room_flag = game_state.room
        self.time = str(game_state.time)     # デバッグ用

        self.status_label = None
        self.create_label()

    def create_label(self):
        name_label = Label(self.screen, self.font, self.player.name, 500, 10, position="right", color=WHITE)
        hp_label = Label(self.screen, self.font, f"HP/{self.player.HP}", 590, 10, position="right", color=WHITE)
        mp_label = Label(self.screen, self.font, f"MP/{self.player.MP}", 650, 10, position="right", color=WHITE)
        current_room_label = Label(self.screen, self.font, ROOM_NAME[self.room_flag], 770, 10, position="right", color=WHITE)
        current_time_label = Label(self.screen, self.font, self.time, 680, 10, position="right", color=WHITE)   # デバッグ用
        self.status_label = [name_label, hp_label, mp_label, current_room_label, current_time_label]

    def draw(self):
        for label in self.status_label:
            label.draw()

    def update(self, player, game_state):
        self.player = player
        self.room_flag = game_state.room
        self.time = str(game_state.time)     # デバッグ用
        self.create_label()
        self.draw()


# simpledialogの代わり(モーダルはうまくいかないがエラーメッセージの日本語化はできた)
class CustomDialog(simpledialog.Dialog):
    def __init__(self, parent, title="title", text="文字列を入力してください", input_value="", input_type=None, min_value=0, max_value=99, num=None):
        
        self.text = text    # ダイアログに表示するテキスト
        self.input_type = input_type
        self.min_value = min_value      # 入力できる最小値
        self.max_value = max_value      # 入力できる最大値
        self.num = num                  # 入力可能文字数
        self.value = tk.StringVar()
        self.value.set(input_value)
        
        super().__init__(parent, title)

    def body(self, frame):
        # ラベル作成
        label = ttk.Label(frame, text=self.text).pack(pady=10)

        # エントリー作成
        vcmd = (self.register(validate_input), "\%d", "%P", self.input_type, self.num)
        func = ime_on if self.input_type == str else ime_off
        self.entry = ttk.Entry(frame, textvariable=self.value, validate="key", validatecommand=vcmd)
        self.entry.pack(pady=10)
        self.entry.bind(sequence="ForcusIn", func=func)

        return self.entry

    # OKボタンを押したとき
    def apply(self):
        if self.validate():
            try:
                self.result = int(self.value.get())
            except ValueError:
                self.result = self.value.get()

    # 入力を検証する
    def validate(self):
        if self.input_type == int:
            if not validate_int(self.value.get()):
                with TopmostManager(self):
                    messagebox.showerror("入力エラー", f"数字を入力してください")
                return False
            
            value = int(self.value.get())
            # 値がmin-maxの間かどうかをチェックする
            if not (self.min_value <= value <= self.max_value):
                with TopmostManager(self):
                    messagebox.showerror("入力エラー", f"入力値は{self.min_value}から{self.max_value}の間で入力してください")
                return False
            
        if not validate_num(self.value.get(), self.num):
            with TopmostManager(self):
                messagebox.showerror("入力エラー", f"文字数制限を超えています")
            return False

        return True
