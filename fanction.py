import sys, random
import pygame
import pygame.draw
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

# ラベル作成を分離するよ
def Label(name, x=0, y=0, font=font, color=BLACK, center_flag=False, background=SHEET_COLOR):
    surface = font.render(name, True, color, background)
    rect = surface.get_rect(left=x, top=y)
    if center_flag:
        rect.centerx = DISPLAY_SIZE[0] / 2
    screen.blit(surface, rect)
    return Rect(rect)

# ボタン作成を分離
def Button(rect, text, font=font):
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
    pygame.draw.rect(screen,in_color,(x+4, y+4, bw-8, bh-8))
    for i in range(len(surfaces)):
        screen.blit(surfaces[i], rects[i])
    return Rect(x,y,bw,bh)

# 入力ボックス作成を分離するよ
def InputBox(rect, flag=True, line_bold=2): 
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
    pygame.draw.line(screen,BLACK,(x,y+h-1),(x+w-1,y+h-1),line_bold)
    return Rect(x,y,w,h)

# 画像表示を分離するよ
def Image(path, size, x, y, line_flag=False, line_width=1, background=False, center_flag=False):
    # 画像の読み込み＆アルファ化(透明化)
    img = pygame.image.load(path).convert_alpha()
    # 画像の縮小
    img = pygame.transform.rotozoom(img, 0, size)
    # 画像の位置取得
    rect = img.get_rect()
    # 画像の位置を変更する
    if center_flag:
        rect.centerx = screen.get_width() / 2
    else:
        rect.centerx += x
    rect.centery += y
    # 背景を白にする場合
    if background == True:
        pygame.draw.rect(screen,WHITE,rect)
    # 画像の描写
    screen.blit(img, rect)
    # 画像の枠を描画する場合
    if line_flag == True:
        pygame.draw.rect(screen,BLACK,rect,line_width)

    return rect

# プルダウンボックス作るの分離するよ
def PullDownBox(rect, font=font):
    x = rect[0] + 5
    y = rect[1]
    w = rect[2]
    h = rect[3]
    Box(x,y,w,h)

    # 三角作るよ
    triangle_rect = Label("▼",x+w-25,y+4,background=WHITE)

    return Rect(x,y,w,h)

# 入力ボックスっぽい箱作るよ
def Box(x,y,w,h):
    pygame.draw.rect(screen,GRAY,(x,y,w,h))
    pygame.draw.rect(screen, WHITE, (x+1, y+1, w-2, h-2))

# テキストフレームに文字を表示するよ
def TextDraw(text):
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
def DiceRool(dice_text=""):
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
