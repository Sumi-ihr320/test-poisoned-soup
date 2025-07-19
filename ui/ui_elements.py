
import random

import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog

import pygame
from pygame.locals import *

from constans import *
from utils import *
from manager.sound_manager import SoundManager

# ラベル
class Label:
    def __init__(self, screen, font, text, x=0, y=0, centerx=None, centery=None, ofset=(0, 0), position="left", color=BLACK, background=None):
        self.screen = screen
        self.font = font
        self.text = text

        self.ofset = ofset
        self.color = color
        self.background = background
        self.position = position

        # 画面サイズを取得（初期サイズ）
        self.screen_width, self.screen_height = self.screen.get_size()

        # ラベルの描画領域を作成
        self.surface = None
        self.rect = None
        self.create_label(x, y, centerx, centery)

    # ラベルを作る
    def create_label(self, x=None, y=None, centerx=None, centery=None):
        self.surface = self.font.render(self.text, True, self.color, self.background)
        self.set_position(x, y, centerx, centery, self.position)

    # 表示位置を変更する
    def set_position(self, x=None, y=None, centerx=None, centery=None, position="left"):
        ox, oy = self.ofset
        if position == "right":
            rect = self.surface.get_rect(right=x-ox, top=y+oy)
        else:
            rect = self.surface.get_rect(left=x+ox, top=y+ox)

        if centerx:
            rect.centerx = centerx
        if centery:
            rect.centery = centery

        self.rect = rect

    # ラベルを描画する
    def draw(self):
        # 必要に応じて再描画をできる
        surface = self.font.render(self.text, True, self.color, self.background)
        self.screen.blit(surface, self.rect)

    def update_text(self, new_text):
        self.text = new_text
        self.draw()

    def set_background_color(self, color):
        self.background = color
        self.draw()
        
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

        # クリック音
        self.sound_manager = SoundManager()
        sound_check(self.sound_manager)

        # hover状態を記録するフラグ
        self.hovered = False

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
        if hover and not self.hovered:  # 初めてホバーした時
            self.sound_manager.play("カーソル移動")
        self.hovered = hover

        self.draw_button(hover)
        self.draw_text()

        if hover and click and self.enabled:
            if self.on_click:
                self.sound_manager.play("クリック")
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
        if self.input_flag:
            pygame.draw.rect(self.screen, self.color, self.rect)
        # 下線
        pygame.draw.line(self.screen, BLACK, (self.rect.x, self.rect.y+self.rect.h-1), (self.rect.x+self.rect.w-1, self.rect.y+self.rect.h-1),
                         self.line_bold)
        
        # ラベルがあれば描写
        if self.label:
            self.label.draw()

    # 色を更新するメソッド
    def update_color(self):
        self.color = WHITE if self.input_flag else None

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
    
    def collidepoint(self, pos):
        return self.rect.collidepoint(pos)

# 画像表示をクラス化するよ
class Image:
    def __init__(self, screen, path, scale=None, x=0, y=0, centerx=None, centery=None ,line_flag=False, line_width=1, bg_flag=False,
                 fixed_ratio=True, size_wh=None, position=None):
        self.screen = screen
        path = f"{PATH}{PICTURE}{path}"

        self.scale = scale                  # 比率を変えない拡大縮小率
        self.fixed_ratio = fixed_ratio      # 比率を保つか、保たないか
        self.size_wh = size_wh              # 縦横サイズ指定

        self.img, self.rect = self.create_image(path)
        self.set_rect(x, y, centerx, centery, position)

        self.bg_flag = bg_flag
        self.line_flag = line_flag
        self.line_width = line_width

    # イメージを作成するよ
    def create_image(self, path):
        try:
            # 画像の読み込み＆アルファ化(透明化)
            self.original_img = pygame.image.load(path).convert_alpha()

            scaled_img = self.set_transform(self.original_img)
            
            # 画像の位置取得
            rect = scaled_img.get_rect()
            return scaled_img, rect
        except pygame.error as e:
            print(f"Error loading image: {e}")

    
    # 画像のサイズ変更
    def set_transform(self, img):
        if self.fixed_ratio and self.scale:
            scaled_img = pygame.transform.rotozoom(img, 0, self.scale)
        elif not self.fixed_ratio and self.size_wh:
            scaled_img = pygame.transform.smoothscale(img, self.size_wh)
        else:
            print("Warning: サイズ指定が不十分なため、画像を変更せずに使用します。")
            scaled_img = img

        return scaled_img

    # 配置をセットするよ
    def set_rect(self, x, y, centerx, centery, position="left"):
        # 位置を変更する
        if x == "center":
            self.rect.centerx = self.screen.get_width() // 2
        elif centerx:
            self.rect.centerx = centerx
        else:
            if position == "right":
                self.rect.right = x
            else:
                self.rect.left = x
        if y == "center":
            self.rect.centery = self.screen.get_height() // 2
        elif centery:
            self.rect.centery = centery
        else:
            if position == "bottom":
                self.rect.bottom = y
            else:
                self.rect.top = y

    # 縮小サイズを変更するよ
    def set_scale(self, new_scale=None, new_size=None):
        if new_scale:
            self.img = pygame.transform.rotozoom(self.original_img, 0, new_scale)
        elif new_size:
            self.img = pygame.transform.smoothscale(self.original_img, new_size)
        self.rect = self.img.get_rect(center=self.rect.center)

    # 画像を切り抜くよ
    def cat_image(self, cat_rect):
        self.img = self.original_img.subsurface(cat_rect).copy()
        self.img = self.set_transform(self.img)
        self.rect = self.img.get_rect(topleft=self.rect.topleft)

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

# 箱をクラスにするよ (主にプルダウンで使ってるよ)
class Box:
    def __init__(self, screen, rect):
        self.screen = screen
        self.rect = rect

    def draw(self):
        pygame.draw.rect(self.screen, GRAY, self.rect)
        pygame.draw.rect(self.screen, WHITE, (self.rect.x+1, self.rect.y+1, self.rect.w-2, self.rect.h-2))

# プルダウン機能をクラス化できないかな？
class PullDown:
    def __init__(self, screen, font, rect, item_list, label_text="", pd_h=285):
        self.screen = screen
        self.font = font

        # 文字の最初の位置
        self.rect = rect

        # プルダウンに表示するリスト
        self.item_list = item_list

        # ボックスに表示される文字
        self.label_text = label_text

        # ボックスと文字の間
        self.padding = 10

        # ボックスのrectを算出
        adjusted_rect = self.get_max_width()

        # プルダウンする前のボックス
        self.box = None
        self.triangle = None        # ボックスに表示される ▼
        self.create_box(adjusted_rect)

        self.label = None
        if label_text:
            self.create_label()

        # プルダウンボックスのアイテムの位置のリスト
        self.items = []
        self.pd_h = pd_h            # プルダウンボックスの最大高さ
        self.list_box = None

        self.sound_manager = SoundManager()
        sound_check(self.sound_manager)
        self.hovered = False

    # ボックスの最大幅を取得
    def get_max_width(self):
        max_text_width = max(self.font.size(text)[0] for text in self.item_list + [self.label_text])
        triangle_width = self.font.size("▼")[0]
        box_width = max_text_width + triangle_width + self.padding * 3
        box_height = self.font.get_height() + self.padding * 2
        return Rect(self.rect.x - self.padding, self.rect.y - self.padding, box_width, box_height)

    # ボックス作るよ
    def create_box(self, rect):
        self.box = Box(self.screen, rect)

        # 三角作るよ
        self.triangle = Label(self.screen, self.font, "▼", rect.right-self.padding, centery=rect.centery, position="right")
    
    # 表示するラベル作るよ
    def create_label(self):
        self.label = Label(self.screen, self.font, self.label_text, x=self.box.rect.x+5, centery=self.box.rect.centery)

    # 表示位置を変更する
    def update_position(self, x=None, y=None, centerx=None, centery=None, position="left"):
        if x:
            if position == "right":
                self.rect.right = x-self.box.rect.width

            else:
                self.rect.x = x

        if y:
            if position == "bottom":
                self.rect.bottom = y-self.box.rect.height
            else:
                self.rect.y = y

        if centerx:
            self.rect.centerx = centerx
        if centery:
            self.rect.centery = centery

        adjusted_rect = self.get_max_width() 
        self.create_box(adjusted_rect)

        if self.label_text:
            self.create_label()

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
        self.create_list(self.item_list, self.rect.x, (self.box.rect.y + self.box.rect.h))

    # リストを作成する
    def create_list(self, list, x, y):
        w = self.box.rect.w
        self.items.clear()  # 以前のアイテムをクリア
        lis_rect = None     # クリック感知の範囲は文字の範囲だけではなく少し広い範囲に設定するためのリスト用rect
        y_initial = y   # 最初のy位置を記録
        current_x, current_y = x, y+self.padding   # 現在の位置
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
            if current_y >= (y_initial + self.pd_h - (self.padding * 2)):
                current_x += w
                max_w += w
                current_y = y_initial + self.padding
        
        # ボックスのサイズよりリストの量が少なければボックスサイズをリストのサイズに合わせる
        if max_w == self.box.rect.w:
            box_heigth = current_y - y_initial
            if box_heigth and box_heigth < self.pd_h:
                self.pd_h = box_heigth + self.padding

        # リストボックスを作る
        self.list_box = Box(self.screen, Rect(x-self.padding, y_initial, max_w+(self.padding*2), self.pd_h+1))

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

    def collidepoint(self, pos):
        return self.box.rect.collidepoint(pos)

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
        self.window_size = self.screen.get_size()

        self.commands = commands
        self.start_x, self.start_y = start_position
        self.buttons = []
        self.create_buttons()

    # コマンドリストからボタンを作成
    def create_buttons(self):
        font = setting_font(FONT_PATH, SMALL_SIZ, self.window_size)
        x, y = self.start_x, self.start_y
        h = 30

        # コマンドの中で最も長いwidthを取得する
        max_width = 120     # 最小値
        if self.commands:
            for command in self.commands:
                text_surface = font.render(command["text"], True, BLACK)
                text_width = text_surface.get_width() + 10
                max_width = max(max_width, text_width)

        if self.commands:
            for command in self.commands:
                button = Button(self.screen, font, command["text"], (x,y,max_width,h), out_color=BLACK)
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

# 主人公の名前・HP・MPを左上、現在地を右上に表示する
class PlayerDataView:
    def __init__(self, screen, room_surface_rect, player, girl, game_state, flags):
        self.screen = screen
        self.window_size = self.screen.get_size()
        self.room_surface_rect = room_surface_rect

        self.font = setting_font(FONT_PATH, SMALL_SIZ, self.window_size)

        self.player = player
        self.room_flag = game_state.room
        self.time = str(game_state.time)     # デバッグ用

        self.girl = girl
        self.girl_fellow = flags.get_flag("girl", "fellow")
        self.girl_alive = flags.get_flag("girl", "girl_alive")

        self.create_surface()

        self.create_image()

        self.status_labels = None
        self.setting_labels()

    # surfaceを作成する
    def create_surface(self):
        #self.size = (300, 100)
        if self.girl_fellow and not self.girl_alive:
            width = 400
        else:
            width = 200
        height = 150
        self.size = (width, height)

        self.size = get_new_size(self.window_size, self.size)
        self.bg_surface = pygame.Surface(self.size)
        self.rect = self.bg_surface.get_rect()

        self.bg_surface.fill(BLACK)
        self.bg_surface.set_alpha(100)

    # imageを作成する
    def create_image(self):
        h_percent = RATIO[self.window_size][1]
        size = 0.4 * h_percent

        self.player_img = Image(self.screen, self.player.image, size, self.rect.x+10, self.rect.y+10, line_flag=True, bg_flag=True)
        self.player_img.cat_image(pygame.Rect(100, 50, 200, 300))

        if not self.girl_alive:
            girl_img = "Girl_pale_downcast_eyes_dark.png"
        else:
            girl_img = self.girl.image
        self.girl_img = Image(self.screen, girl_img, size, 0, 0, line_flag=True, bg_flag=True)
        self.girl_img.cat_image(pygame.Rect(50, 0, 200, 300))

        self.girl_img.set_rect(x=self.player_img.rect.x+self.player_img.rect.w+100, y=self.player_img.rect.y, centerx=None, centery=None)

    def setting_labels(self):
        player_labels = self.create_label(self.player, self.player_img)
        girl_labels = self.create_label(self.girl, self.girl_img)

        current_room_label = Label(self.screen, self.font, ROOM_NAME[self.room_flag], self.room_surface_rect.right, self.room_surface_rect.y - 30, position="right", color=WHITE)
        current_time_label = Label(self.screen, self.font, self.time, current_room_label.rect.x - 10, current_room_label.rect.y, position="right", color=WHITE)   # デバッグ用

        self.status_labels = player_labels
        if self.girl_fellow or not self.girl_alive:
            self.status_labels += girl_labels
        self.status_labels += [current_room_label, current_time_label]

    def create_label(self, character, character_img):
        margin = 5
        name_label = Label(self.screen, self.font, character.name, character_img.rect.x + character_img.rect.w + 10, character_img.rect.y + margin, color=WHITE)
        hp_label = Label(self.screen, self.font, f"HP/{character.HP}", name_label.rect.x, name_label.rect.y + name_label.rect.h + margin, color=WHITE)
        mp_label = Label(self.screen, self.font, f"MP/{character.MP}", name_label.rect.x, hp_label.rect.y + hp_label.rect.h + margin, color=WHITE)
        return [name_label, hp_label, mp_label]

    def draw(self):
        self.screen.blit(self.bg_surface, self.rect.topleft)

        if self.player_img:
            self.player_img.draw()
        if self.girl_img and self.girl_fellow:
            self.girl_img.draw()

        for label in self.status_labels:
            label.draw()

    def update(self, player, girl, game_state, flags):
        self.player = player
        self.girl = girl
        self.room_flag = game_state.room
        self.time = str(game_state.time)     # 時間表示：デバッグ用

        # 少女の生死によって表示を変更する
        new_girl_alive = flags.get_flag("girl", "alive")
        if self.girl_alive != new_girl_alive:
            self.create_image()
        self.girl_alive = new_girl_alive

        # 少女のフォローの可否によって表示を変更する
        new_girl_fellow = flags.get_flag("girl", "fellow")
        if self.girl_fellow != new_girl_fellow:
            self.create_surface()
        self.girl_fellow = new_girl_fellow

        
        self.status_labels = None
        self.setting_labels()
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
