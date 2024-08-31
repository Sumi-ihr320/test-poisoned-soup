import sys, random
import pygame
from pygame.locals import *
from tkinter import simpledialog
from tkinter import messagebox

from data import *


# 終了処理をまとめるよ
def Close():
    if messagebox.askokcancel("確認","本当に終了しますか？"):
        pygame.quit()
        sys.exit()
    else:
        pass

# フレームの表示
def Frame(screen):
    # テキストフレーム
    pygame.draw.rect(screen, WHITE, FRAME_RECT,3)
    # ダイスフレーム
    pygame.draw.rect(screen, WHITE, DICE_FRAME_RECT,3)

""""
# ラベル作成を分離するよ
def Label(screen, font, text, x=0, y=0, color=BLACK, center_flag=False, background=SHEET_COLOR):
    surface = font.render(text, True, color, background)
    rect = surface.get_rect(left=x, top=y)
    if center_flag:
        rect.centerx = DISPLAY_SIZE[0] / 2
    screen.blit(surface, rect)
    return Rect(rect)
"""
# ラベル作成をクラス化するよ    (chatGPT指南)
class Label:
    def __init__(self, screen, font, text, x=0, y=0, color=BLACK, center_flag=False, background=SHEET_COLOR):
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
        self.screen.blit(surface, rect)
        return rect

    # ラベルを描画する
    def draw(self):
        # 必要に応じて再描画をできる
        surface = self.font.render(self.text, True, self.color, self.background)
        self.screen.blit(surface, self.rect)

    # 指定した点が描画内かをチェック
    def collidepoint(self, pos):
        return self.rect.collidepoint(pos)
    
# ボタン作成を分離
"""
def Button(screen, font, rect, text):
    out_color = GRAY
    in_color = (181,181,174)
    text_color = BLACK
    texts = text.splitlines()
    surfaces = []
    rects = []
    x = rect[0] + rect[2] + 5
    y = rect[1] -2
    tx,ty = 0,y
    bw,bh = 0,0
    for txt in texts:
        surface = font.render(txt, True, text_color)
        w = surface.get_rect().w + 8
        if bw < w:
            bw = w
        h = surface.get_rect().h + 8
        bh += h
        tx = x + int(bw / 2)
        ty += int(h / 2)
        text_rect = surface.get_rect(center=(tx,ty))
        ty += int(h / 2)
        surfaces.append(surface)
        rects.append(text_rect)
    pygame.draw.rect(screen, out_color, (x, y, bw, bh))
    pygame.draw.line(screen, in_color, (x, y), (x+bw,y+bh))
    pygame.draw.line(screen, in_color, (x,y+bh), (x+bw,y))
    pygame.draw.rect(screen, in_color,(x+4, y+4, bw-8, bh-8))
    for i in range(len(surfaces)):
        screen.blit(surfaces[i], rects[i])
    return Rect(x,y,bw,bh)
"""
# ボタン作成をクラス化 やってみた     (chatGPT修正)
class Button:
    def __init__(self, screen, font, rect, text, on_click=None):
        self.screen = screen
        self.font = font
        self.texts = text.splitlines()

        self.x = rect[0] + rect[2] + 5
        self.y = rect[1] -2

        # 色情報
        self.out_color = GRAY
        self.in_color = (181,181,174)
        self.on_color = BLUE
        self.text_color = BLACK

        # ボタンの幅高さ
        self.bw = 0
        self.bh = 0
        # ボタンのrect
        self.rect = None

        # テキスト表示用
        self.surfaces = []
        self.rects = []

        self.create_button()

        # コールバック関数
        self.on_click = on_click

    def create_button(self):
        self.create_text()
        self.draw_button()
        self.draw_text()

    # テキストの作成
    def create_text(self):
        tx,ty = 0, self.y
        for txt in self.texts:
            surface = self.font.render(txt, True, self.text_color)
            w = surface.get_rect().w + 8
            if self.bw < w:
                self.bw = w
            h = surface.get_rect().h + 8
            self.bh += h
            tx = self.x + int(self.bw / 2)
            ty += int(h / 2)
            text_rect = surface.get_rect(center=(tx,ty))
            ty += int(h / 2)
            self.surfaces.append(surface)
            self.rects.append(text_rect)

    # ボタンの描画
    def draw_button(self, hover=False):
        pygame.draw.rect(self.screen, self.out_color, (self.x, self.y, self.bw, self.bh))
        if hover:
            pygame.draw.rect(self.screen, self.on_color, (self.x, self.y, self.bw, self.bh))
        pygame.draw.line(self.screen, self.in_color, (self.x, self.y), (self.x+self.bw, self.y+self.bh))
        pygame.draw.line(self.screen, self.in_color, (self.x, self.y+self.bh), (self.x+self.bw, self.y))
        pygame.draw.rect(self.screen, self.in_color,(self.x+4, self.y+4, self.bw-8, self.bh-8))
        self.rect = Rect(self.x, self.y, self.bw, self.bh)

    # テキストの描画
    def draw_text(self):
        for i in range(len(self.surfaces)):
            self.screen.blit(self.surfaces[i], self.rects[i])
    
    # クリックされたときTrueを返す
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos) if self.rect else False

    # 更新
    def update(self, pos, click):
        hover = self.is_clicked(pos)
        self.draw_button(hover)
        if hover and click:
            if self.on_click:
                self.on_click() # コールバック関数を呼び出す
        
# 入力ボックス作成を分離するよ
"""
def InputBox(screen, rect, flag=True, line_bold=2): 
    if flag:
        # color = (255,248,220)
        color = WHITE
    else:
        color = SHEET_COLOR
    x = rect[0] + 5
    y = rect[1] - 4
    w = rect[2] 
    h = rect[3] 
    pygame.draw.rect(screen, color, (x, y, w, h))
    pygame.draw.line(screen, BLACK,(x,y+h-1),(x+w-1,y+h-1),line_bold)
    return Rect(x,y,w,h)
"""
# インプットボックスをクラス化するよ
class InputBox:
    def __init__(self, screen, rect, input_flag=True, line_bold=2):
        self.screen = screen
        # ボックスのカラーの設定
        self.color = WHITE if input_flag else SHEET_COLOR
        self.x = rect[0] + 5
        self.y = rect[1] - 4
        self.w, self.h = rect[2], rect[3]
        self.rect = Rect(self.x, self.y, self.w, self.h)
        self.line_bold = line_bold
        
        self.draw_box()
    
    # ボックスの描画
    def draw_box(self):
        # 入力ボックス
        pygame.draw.rect(self.screen, self.color, self.rect)
        # 下線
        pygame.draw.line(self.screen, BLACK, (self.x, self.y+self.h-1), (self.x+self.w-1, self.y+self.h-1),
                         self.line_bold)

""""
# 画像表示を分離するよ
def Image(screen, path, size, x, y, line=False, line_width=1, bg=False, x_center=False, y_center=False):
    img, rect = CreateImage(path, size)
    rect = SetRect(screen, rect, x, y, x_center,y_center)
    ImageView(screen, img, rect, bg, line, line_width)
    return rect

# 画像を表示するよ
def ImageView(screen, img, rect, bg=False, line=False, line_width=1):
    # 背景を白にする場合
    if bg:
        pygame.draw.rect(screen, WHITE, rect)

    # 画像の描写
    screen.blit(img, rect)

    # 画像の枠を描画する場合
    if line:
        pygame.draw.rect(screen, BLACK, rect, line_width)

# 位置を真ん中にしたい場合等
def SetRect(screen, rect, x=0, y=0, x_center=False, y_center=False):
    # 位置を変更する
    if x_center:
        rect.centerx = screen.get_width() / 2
    else:
        rect.centerx += x
    if y_center:
        rect.centery = screen.get_height() / 2
    else:
        rect.centery += y
    return rect

# 画像表示のsurface作成とrect.getまでをまとめる ※描画前に配置等変更したいパターンが多いため
def CreateImage(path, size):

    # 画像の読み込み＆アルファ化(透明化)
    img = pygame.image.load(path).convert_alpha()
    # 画像の縮小
    img = pygame.transform.rotozoom(img, 0, size)
    # 画像の位置取得
    rect = img.get_rect()

    return img, rect
"""
# 画像表示をクラス化するよ
class Image:
    def __init__(self, screen, path, size, x, y, line_flag=False, line_width=1, bg_flag=False):
        self.screen = screen

        # 初期化
        self.img = None
        self.rect = None

        self.create_image(path, size)
        self.set_rect(x, y)
        self.view_image(bg_flag, line_flag, line_width)

    # イメージを作成するよ
    def create_image(self, path, size):
        # 画像の読み込み＆アルファ化(透明化)
        self.img = pygame.image.load(path).convert_alpha()
        # 画像の縮小
        self.img = pygame.transform.rotozoom(self.img, 0, size)
        # 画像の位置取得
        self.rect = self.img.get_rect()
        
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
    def view_image(self, bg_flag, line_flag, line_width):
        # 背景を白にする場合
        if bg_flag:
            pygame.draw.rect(self.screen, WHITE, self.rect)

        # 画像の描写
        self.screen.blit(self.img, self.rect)

        # 画像の枠を描画する場合
        if line_flag:
            pygame.draw.rect(self.screen, BLACK, self.rect, line_width)


# プルダウンボックス作るの分離するよ
def PullDownBox(screen, rect, font):
    x = rect[0] + 5
    y = rect[1]
    w = rect[2]
    h = rect[3]
    Box(x,y,w,h)

    # 三角作るよ
    triangle_rect = Label(screen,font,"▼",x+w-25,y+4,background=WHITE)

    return Rect(x,y,w,h)

# 入力ボックスっぽい箱作るよ
def Box(screen, x,y,w,h):
    pygame.draw.rect(screen, GRAY,(x,y,w,h))
    pygame.draw.rect(screen, WHITE, (x+1, y+1, w-2, h-2))

# テキストフレームに文字を表示するよ
def TextDraw(screen, text):
    # フォントの設定
    font = pygame.font.Font(FONT_PATH, FONT_SIZ)

    texts = []
    y = 435
    texts = text.splitlines()
    for txt in texts:
        surface = font.render(txt,True,WHITE)
        rect = surface.get_rect(left=45,top=y)
        screen.blit(surface,rect)
        y += 25

# インプットボックスの処理をまとめるよ
def InputGet(name, title, text, min=0, max=100):
    txt = CharaStatus[name]
    if type(txt) == str:
        val = simpledialog.askstring(title,text,initialvalue=txt)
    elif type(txt) == int:
        val = simpledialog.askinteger(title,text,initialvalue=txt,minvalue=min,maxvalue=max)
    if val != None:
        CharaStatus[name] = val
    return val

# ダイスの挙動をまとめるよ
def DiceRool(screen, dice_text=""):
    if dice_text != "":
        pieces = int(dice_text[0])
        dice = int(dice_text[2])
        if dice == 3 or dice == 4:
            img = "dice_3-4.png"
        elif dice == 6:
            img = "dice_6.png"
        elif dice == 10:
            img = "dice_6.png"
        else:
            img = "dice_8-20.png"
        # ダイスの画像を表示したいけどうまくいかないのでとりあえず放置
        dice_img = pygame.image.load(PATH + PICTURE + img).convert_alpha()
        dice_img = pygame.transform.rotozoom(dice_img, 0, 0.5)
        rect = dice_img.get_rect()
        x = 500
        y = 700
        w = rect.w
        h = rect.h
        val = 0
        for i in range(pieces):
            val += random.randint(1, dice)
            screen.blit(dice_img, (x,y,w,h))
            x -= w + 10
        if len(dice_text) > 3:
            if dice_text[3] == "+":
                val += int(dice_text[4])
            else:
                val -= int(dice_text[4])
        pygame.time.delay(100)
        return val

# 答えと余りを算出する計算式を関数にしてみた
def Calculation(a, b, max=None):
    surplus = 0
    result = a + b
    if max is not None:
        if result > max:
            surplus = result - max
            result = max
    return result, surplus
