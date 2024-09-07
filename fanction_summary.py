import sys, re, random
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

# フレームの作成
def create_frame(screen):
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

# 箱作るよ
"""
def Box(screen, x, y, w, h):
    pygame.draw.rect(screen, GRAY,(x, y, w, h))
    pygame.draw.rect(screen, WHITE, (x+1, y+1, w-2, h-2))
    return Rect(x, y, w, h)
"""

# テキストを描画
def text_view(screen, font, text, color, bg, x, y):
    surface = font.render(text, True, color, bg)
    rect = surface.get_rect(left=x, top=y)
    screen.blit(surface, rect)
    return rect

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

# テキストファイルのロード
def load_texts(file_path):
    with open(file_path, "r", encoding="utf-8_sig") as f:
        return f.readlines()
    
# jsonファイルのロード
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8_sig") as f:
        return json.load(f)

# インプットボックスの処理をまとめるよ
def InputGet(name, title, text, min=0, max=100):
    txt = CharaStatus[name]
    if type(txt) == str:
        val = simpledialog.askstring(title, text, initialvalue=txt)
    elif type(txt) == int:
        val = simpledialog.askinteger(title, text, initialvalue=txt, minvalue=min, maxvalue=max)
    if val != None:
        CharaStatus[name] = val
    return val

# ダイスの挙動をまとめるよ
""""
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
"""

# 選択した職業から主人公のステータスにデータを入れるよ
def ProfDataIn():
    global CharaStatus

    # 入力されている技能をリセット
    CharaStatus["skill"] = {}
    CharaStatus["Avo"] = CharaStatus["DEX"] * 2
    # 職業から設定されている技能一覧を取得
    prof = CharaStatus["Profession"]
    skills = ProfessionList[prof]["skill"]
    # 加算できる技能ポイントを算出する
    max = CharaStatus["EDU"] * 20
    if max > 0:
        i = max
        for skill in skills:
            # 各技能に割り振られているパーセンテージを出す
            percent = skills[skill]
            # 技能ポイントをパーセンテージ分算出
            bonus = int(max * (percent / 100))
            # 基本技能ポイント
            if skill == "回避":
                data = CharaStatus["Avo"]
            else:
                data = SkillList[skill]
            # 計算する
            result, surplus = Calculation(data, bonus, 90)
            # 主人公のステータスにポイントを入力
            if skill == "回避":
                CharaStatus["Avo"] = result
            else:
                CharaStatus["skill"][skill] = result
            # 技能ポイント - 使用した技能ポイント + 余りの技能ポイント
            i = i - bonus + surplus

            # 技能ポイントが足りなかった場合
            if i < 0:
                print("技能ポイントが足りません")
                break

        # 全ての技能ポイント割り振り後にポイントが余った場合
        if i > 0:
            # ポイントが0になるまで繰り返す
            while i > 0:
                lists = {}
                # スキルリストから90以下のスキルをリスト化する
                for skill in CharaStatus["skill"]:
                    point = CharaStatus["skill"][skill]
                    if point < 90:
                        lists[skill] = point
                if len(lists) > 0:
                    # リストの数よりポイントが多い場合
                    if len(lists) < i:
                        # リストの数でポイントを割る
                        quotient = int(i / len(lists))
                        
                        # 計算していく
                        for skill in lists:
                            point = lists[skill]
                            result, surplus = Calculation(point, quotient, 90)
                            CharaStatus["skill"][skill] = result
                            i = i - quotient + surplus
                    else:
                        select = random.choice(list(lists))
                        CharaStatus["skill"][select]  += i
                        i -= i
                   
# 選択した趣味から主人公のステータスにデータを入れるよ
def HobyDataIn():
    global CharaStatus

    hobby = PullDownItem
    my_skills = CharaStatus["skill"]
    skills = HobbyList[hobby]
    max = CharaStatus["INT"] * 10
    percent = [70,30]
    if max > 0:
        point = max
        for i in range(len(skills)):
            skill = skills[i]
            # 基本技能ポイント
            if skill in my_skills:
                data = my_skills[skill]
            else:
                data = SkillList[skill]
            # 技能ポイントをパーセンテージ分算出
            bonus = int(max * (percent[i] / 100))
            # 計算する
            result, surplus = Calculation(data,bonus,90)
            # スキルに値を入れる
            CharaStatus["skill"][skill] = result
            # 残りのポイントを算出
            point = point - bonus + surplus

        if point > 0:
            for i in range(len(skills)):
                skill = skills[i]
                data = my_skills[skill]
                result,surplus = Calculation(data,point,90)
                CharaStatus["skill"][skills[i]] = result
                point = surplus

# "〇D〇" のテキストから何個のダイスか、何面ダイスか、+〇、-〇が付いてるかを抽出する
def dice_confirmation(text):
    # テキストに+か-が入っているか確認
    plus_item = re.search(r"\+|\-", text)
    cut_index = plus_item.start-1 if plus_item else 0
    pieces = text[0]
    dice = text[2:] if cut_index == 0 else text[2:cut_index]
    return int(pieces), int(dice), plus_item

# 答えと余りを算出する計算式を関数にしてみた
def Calculation(a, b, max=None):
    surplus = 0
    result = a + b
    if max is not None:
        if result > max:
            surplus = result - max
            result = max
    return result, surplus
