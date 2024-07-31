import sys, random, os, json
import pygame
import pygame.draw
import pygame.draw
from pygame.locals import *
import pygame_menu as pgmenu
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import datetime as dt

from data import *


SCENE_FLAG = TITLE
#SCENE_FLAG = PLAY

# キャラクターのステータスデータ
with open(STATUS_JSON_PATH,"r",encoding="utf-8_sig")as f:
    STATUS = json.load(f)
    
CharaStatus = STATUS["Hero"]    # 主人公
GirlStatus = STATUS["Girl"]     # 少女


TEXT = ""   # テキストフレームに入れるデータ

maxAlpha = 255      # alpha値 不透明
minAlpha = 0        # alpha値 透明
AlphaFlag = 0   # ブラックインアウトフラグ  0=無し 1=In 2=Out


# ロード画面（セーブ画面） -------------------------------------

# セーブファイルリスト
SavePath = PATH + SAVE
SaveFiles = os.listdir(SavePath)

# 選択されたデータ
SelectSaveData = ""

# オープニング画面 --------------------------------------------
OpeningFlag = 0     # オープニングの進行フラグ

# キャラクターシート画面 ---------------------------------------
CharaPage = True    # ページ変更用フラグ

PullDownFlag = False    # プルダウン用フラグ
PullDownItem = ""       # プルダウンアイテム記憶用

# 職業リスト
with open(PROF_JSON_PATH,"r",encoding="utf-8_sig") as f:
    ProfessionList = json.load(f)

# 技能リスト
with open(SKILL_JSOM_PATH,"r",encoding="utf-8_sig") as f:
    SkillList = json.load(f)

# 趣味リスト
with open(HOBBY_JSON_PATH,"r",encoding="utf-8_sig") as f:
    HobbyList = json.load(f)

# 本編 -------------------------------------------------------
PlaySceneFlag = 0   # 本編中のシーンフラグ
RoomFlag = CENTER       # どの部屋にいるかフラグ
DirectionFlag = NORTH   # どの方角を向いてるかフラグ
DiscoveryFlag = True    # 東の部屋奥が見えるかフラグ
KeyOpenFlag = False     # 東の部屋カギが開いてるかフラグ
BookFlag = True         # 本を見つけてるかフラグ
PoisonFlag = False      # 毒を入手してるかフラグ
inPoisonFlag = False    # スープに毒が入ってるかフラグ
# -----------------------------------------------------------


# tkinterの起動
root = tk.Tk()
# 画面中央に配置したい
sw = root.winfo_screenmmwidth()
sh = root.winfo_screenmmheight()
w = root.winfo_width()
h = root.winfo_height()
x = (sw/2) - (w/2)
y = (sh/2) - (h/2)
root.geometry("+%d+%d" % (x,y))
# tkinterの非表示
root.withdraw()

# pygame初期化,
pygame.init()
# 画面サイズ
screen = pygame.display.set_mode(DISPLAY_SIZE)
# キーリピート設定
pygame.key.set_repeat(100, 100)
# タイトルバーキャプション
pygame.display.set_caption(TITLE_TEXT)

# フォントの設定
font = pygame.font.Font(FONT_PATH, FONT_SIZ)
small_font = pygame.font.Font(FONT_PATH, SMALL_SIZ)
big_font = pygame.font.Font(FONT_PATH, BIG_SIZ)
# タイトル用のフォント
title_font = pygame.font.Font(TITLE_FONT_PATH,TITLE_SIZ)
# メニュー用フォント
contents_font = pygame.font.Font(FONT_PATH,CONTENTS_SIZ)


clock = pygame.time.Clock()


# タイトル画面作るよ
def Title():
    global SCENE_FLAG
    
    # タイトル
    title_rect = TitleRender(TITLE_TEXT,150,RED,title_font)
    start_rect = TitleRender("はじめる",280,WHITE,contents_font)
    load_rect = TitleRender("つづきから",350,WHITE,contents_font)
    setting_rect = TitleRender("設定",420,WHITE,contents_font)
    close_rect = TitleRender("おわる",490,WHITE,contents_font)
    
    contents_list = [start_rect,load_rect,setting_rect,close_rect]

    # マウスオーバーで枠を表示するよ
    key = pygame.mouse.get_pos()
    for content in contents_list:
        if content.collidepoint(key):
            pygame.draw.rect(screen,WHITE,content,1)

    for event in pygame.event.get():
        # マウスクリック時
        if event.type == MOUSEBUTTONDOWN:
            # 左ボタン
            if event.button == 1:
                if start_rect.collidepoint(event.pos):
                    SCENE_FLAG = OPENING
                elif load_rect.collidepoint(event.pos):
                    SCENE_FLAG = LOAD
                elif setting_rect.collidepoint(event.pos):
                    SCENE_FLAG = SETTING
                elif close_rect.collidepoint(event.pos):
                    Close()

        # 閉じるボタンで終了
        if event.type == QUIT:
            Close()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                Close()

# タイトル画面の文字表示用
def TitleRender(text, y, color, font):
    surface = font.render(text,True,color)
    rect = surface.get_rect()
    # 画面の中央に表示する0
    rect.centerx = DISPLAY_SIZE[0] / 2
    rect.y = y
    screen.blit(surface,rect)
    return rect

def Opening():
    global SCENE_FLAG
    global OpeningFlag

    file_path = PATH + SCENARIO + "00_Opening.txt"
    with open(file_path,"r",encoding="utf-8_sig") as f:
        txts = f.readlines()
    
    if OpeningFlag < 2:
        TextDraw(txts[OpeningFlag])
    else:
        SCENE_FLAG = CHARASE

    for event in pygame.event.get():
        # マウスクリック時
        if event.type == MOUSEBUTTONDOWN:
            # 左ボタン
            if event.button == 1:
                OpeningFlag += 1

        # 閉じるボタンで終了
        if event.type == QUIT:
            Close()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                Close()

# 終了処理をまとめるよ
def Close():
    if messagebox.askokcancel("確認","本当に終了しますか？"):
        pygame.quit()
        sys.exit()
    else:
        pass

# ページ移動用の矢印表示するよ
class PageNavigation:
    def __init__(self, page_flag=0):

        self.navi_rect = self.image(page_flag)
            
    def image(self, page_flag):
        img = "navigate.png"
        navi_img = pygame.image.load(PATH + PICTURE + img).convert_alpha()
        if page_flag == UNDER:
            navi_img = pygame.transform.rotate(navi_img,90)
            navi_img = pygame.transform.scale(navi_img,(500,40))
        else:
            navi_img = pygame.transform.scale(navi_img, (40,355))
        navi_rect = navi_img.get_rect()
        if page_flag == RIGHT: # 右側のナビゲーション
            navi_x = 740
            navi_y = 40
            triangle = [[750,190],[770,210],[750,230]]
        elif page_flag == LEFT: # 左側のナビゲーション
            navi_x = 20
            navi_y = 40
            triangle = [[50,190],[30,210],[50,230]]
        else:   # 下側のナビゲーション
            navi_x = screen.get_width() / 2 - navi_rect.centerx
            navi_y = 350
            triangle = [[380,360],[400,380],[420,360]]

        navi_rect.centerx += navi_x
        navi_rect.centery += navi_y
        screen.blit(navi_img, navi_rect)
        # 三角形の描画
        pygame.draw.polygon(screen,BLACK,triangle)

        return navi_rect

# ステータス作るよ
class Status:
    def __init__(self, name, status_name, label_name, x, y, w, h, text="",  Button_flag=True, Input_flag=True, Box_flag=True,  Dice_text=""):
        self.name = name    # ステータスの名前
        self.status_name = status_name  # CharaStatusでの名前
        if label_name != "":    # 実際に表示する名前（スペースなどで位置調整する場合があるため）
            self.label_name = label_name
        else:
            self.label_name = self.name
        self.text = text    # 説明文
        self.dice_text = Dice_text  # ダイスボタンに表示するテキスト
        self.Label_rect = Label(self.label_name,x,y)    # ラベル作成
        self.Input_flag = Input_flag    # インプットボタンの入力ができるかのフラグ
        max_flag = False    # 最大値と現在値が存在するフラグ
        if Box_flag:    # インプットボックスを作るかのフラグ
            self.Input_rect = InputBox((x+self.Label_rect.w,y,w,h),self.Input_flag)
            if status_name != "sex":
                if status_name in CharaStatus:
                    self.status = CharaStatus[status_name]
                    Label(str(self.status),self.Input_rect.x+2,self.Input_rect.y+2)
        else:
            self.Input_rect = self.Label_rect

        if max_flag:
            self.Input2_rect = self.Input_rect

        # ダイスボタンを表示するフラグ
        if Button_flag:
            self.Button_rect = Button(self.Input_rect,Dice_text)
        else:
            self.Button_rect = self.Input_rect
    
    # ステータスの自動計算
    def AutoCalculation(self, name):
        if name == "STR" or name == "SIZ" or name == "CON":
            if name != "CON":
                # ダメージボーナスの計算
                st = CharaStatus["STR"] + CharaStatus["SIZ"]
                if 2 <= st <= 12:
                    val = "-1D6"
                elif 13 <= st <= 16:
                    val = "-1D4"
                elif 25 <= st <= 32:
                    val = "+1D4"
                elif 33 <= st <= 40:
                    val = "+1D6"
                else:
                    val = "0"
                CharaStatus["DB"] = val

            if name != "STR":
                # HPの計算
                val = round((CharaStatus["CON"] + CharaStatus["SIZ"]) / 2)
                CharaStatus["HP"] = val

        elif name == "POW":
            # MP、幸運、SAN値の計算
            CharaStatus["MP"] = CharaStatus["POW"]
            val = CharaStatus["POW"] * 5
            CharaStatus["Luck"] = val
            CharaStatus["SAN"] = val

        elif name == "INT":
            # アイデアの計算
            val = CharaStatus["INT"] * 5
            CharaStatus["Idea"] = val

        elif name == "EDU":
            # 知識の計算
            val = CharaStatus["EDU"] * 5
            if val > 99:
                val = 99
            CharaStatus["Know"] = val
        
        elif name == "DEX":
           # 回避の計算
           val = CharaStatus["DEX"] * 2
           CharaStatus["Avo"] = val
 
    # 入力ボックスの処理まとめるよ
    def InputProcess(self):
        min=0
        max=99
        # 最大値最小値を決めるよ
        if self.status_name == "age":
            min = CharaStatus["EDU"] + 6
        elif self.dice_text != "":
            min = int(self.dice_text[0])
            max = int(self.dice_text[2]) * min
            if len(self.dice_text) > 3:
                if self.dice_text[3] == "+":
                    min += int(self.dice_text[4])
                    max += int(self.dice_text[4])
                else:
                    min -= int(self.dice_text[4])
                    max -= int(self.dice_text[4])
                    
        val = InputGet(self.status_name,self.name,'あなたの' + self.name + 'を入力してください',min,max)
        if val != None:
            Label(str(val),self.Input_rect.x+2, self.Input_rect.y+2)
            CharaStatus[self.status_name] = val
            self.AutoCalculation(self.status_name)

    # ダイス処理まとめるよ
    def DiceProcess(self):
        val = DiceRool(self.dice_text)
        CharaStatus[self.status_name] = val
        self.AutoCalculation(self.status_name)
        Label(str(val),self.Input_rect.x+2,self.Input_rect.y+2)

# 選んだ性別によって画像が変わるようにするよ
class SexChange:
    def __init__(self, x, y, flag):
        self.sex_flag = flag
        if flag:
            self.man_rect = self.Butoon("男",x,y,True)
            self.woman_rect = self.Butoon("女",x+40,y,False)
        else:
            self.man_rect = self.Butoon("男",x,y,False)
            self.woman_rect = self.Butoon("女",x+40,y,True)
        self.Image(flag)

    # ボタン作るよ
    def Butoon(self, name, x, y, flag):
        push_color = (106,93,33)
        no_push_color = SHEET_COLOR
        if flag:
            background = push_color
            color = WHITE
        else:
            background = no_push_color
            color = BLACK
        surface = font.render(name, True, color, background)
        rect = surface.get_rect(left=x, top=y)
        screen.blit(surface, rect)
        return Rect(rect)

    # 画像表示するよ    
    def Image(self,flag):
        if flag:
            img = "silhouette_man.png"
        else:
            img = "silhouette_woman.png"
        img_path = PATH + PICTURE + img
        self.image_rect = image(img_path,0.5,40,40,True,2)

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

# 職業選択画面作るよ
class Profession:
    def __init__(self, prof):
        self.list_image()
        if prof != "":
            self.image(prof)

    def list_image(self):
        x,y = 100,230
        self.prof_list = ProfessionList
        for prof in list(self.prof_list):
            name = self.prof_list[prof]["name"]
            img_path = PATH + PICTURE + "prof_" + name + ".png"
            rect = image(img_path, 0.1, x, y, line=True, background=True)
            self.prof_list[prof]["rect"] = rect
            x += 55
            if x >= 590:
                y += 55
                x = 100

    def image(self, prof):
        data = self.prof_list[prof]
        name = data["name"]
        skill_list = data["skill"]
        img_path = PATH + PICTURE + "prof_" + name + ".png"
        x,y = 100,40
        rect = image(img_path, 0.35 , x, y, line=True, background=True)
        lrx = rect.x + rect.w + 5
        name_rect = Label(f"【{prof}】", lrx, y, font)
        skill_x, skill_y = lrx + 10, y + 30
        skill_rect = Label("所持技能： ", skill_x, skill_y, small_font)
        sk_x, sk_y = skill_x + 10, skill_y + skill_rect.h + 10
        sx, sy = sk_x, sk_y
        for skill in skill_list:
            rect = Label(skill, sx, sy, small_font)
            sx += rect.w + 10
            if sx > 530:
                sx = sk_x
                sy += rect.h + 10

# 趣味選択画面作るよ
class Hobby:
    def __init__(self):
        self.label_rect = Label("趣味", 545, 175)
        if PullDownItem == "":
            self.listitem = "未選択"
        else:
            self.listitem = PullDownItem
        self.pull = PullDown((435,200,150,25),self.listitem,list(HobbyList),small_font,207)

# プルダウン機能をクラス化できないかな？
class PullDown:
    def __init__(self, rect, text, list, font=font, pd_h=285):
        self.font = font
        self.box_rect = self.Box(rect)
        self.box_text = self.Label(text, self.box_rect)
        self.list = list

        # プルダウンボックスのアイテムの位置のリスト{item:rect}
        self.items = {}

        if PullDownFlag:
            self.pd_rect = self.PullDown(self.box_rect, pd_h)
            self.PullDownList(self.pd_rect)

    # ボックス作るよ
    def Box(self,rect):
        x = rect[0] + 5
        y = rect[1]
        w = rect[2]
        h = rect[3]
        Box(x,y,w,h)

        # 三角作るよ
        tx = x + w -25
        ty = y + 3
        triangle_rect = Label("▼",tx,ty,self.font)

        return Rect(x,y,w,h)

    # プルダウンボックスに表示される文字列を描画するよ
    def Label(self,text,rect):
        surface = self.font.render(str(text),True,BLACK)
        rect = surface.get_rect(left=rect[0]+4,top=rect[1]+4)
        screen.blit(surface, rect)
        return text
    
    # プルダウン押した時に表示されるボックス作るよ
    def PullDown(self, rect, ph):
        x = rect[0]
        y = rect[1] + rect[3]
        w = rect[2] 
        h = rect[3] + ph
        Box(x,y,w,h)
        return Rect(x,y,w,h)

    # プルダウン押した時に表示される項目表示したいよ
    def PullDownList(self, rect):
        x = rect.x + 3
        y = rect.y + 3
        self.ListDraw(self.list,x,y,self.pd_rect.w)

    # 同じ処理だったのでまとめた
    def ListDraw(self,list,x,y,w):
        ly = y
        i = 0
        for item in list:
            i += 1
            # 項目表示
            surface = self.font.render(item,True,BLACK)
            rect = surface.get_rect(left=x,top=y)
            screen.blit(surface,rect)

            # 項目名とそのrectを辞書に登録していく
            lis_rect = Rect(rect.x,rect.y,w,rect.h)
            self.items[item] = lis_rect

            # 表示位置を下にずらす
            y += rect.h + 1

            # 仕切り線を引く
            pygame.draw.line(screen,BLACK,(x-2,y),(x+w-4,y))
            
            # プルダウンボックスより下は隣に表示する
            if y >= (self.pd_rect.y+self.pd_rect.h-rect.h):
                x += x + w
                y = ly
                # 隣にプルダウンボックスを作る
                self.PullDown(Rect(x-3,self.box_rect.y,self.box_rect.w,self.box_rect.h),150)
        lh = y - ly
        self.List_rect = Rect(x,ly,w,lh)
        return 

# ラベル作成を分離するよ
def Label(name, x, y, font=font):
    color = BLACK
    surface = font.render(name, True, color)
    rect = surface.get_rect(left=x, top=y)
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
def image(path, size, x, y, line=False, line_width=1, background=False):
    # 画像の読み込み＆アルファ化(透明化)
    img = pygame.image.load(path).convert_alpha()
    # 画像の縮小
    img = pygame.transform.rotozoom(img, 0, size)
    # 画像の位置取得
    rect = img.get_rect()
    # 画像の位置を変更する
    rect.centerx += x
    rect.centery += y
    # 背景を白にする場合
    if background == True:
        pygame.draw.rect(screen,WHITE,rect)
    # 画像の描写
    screen.blit(img, rect)
    # 画像の枠を描画する場合
    if line == True:
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
    triangle_rect = Label("▼",x+w-25,y+4,font)

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
            
# 答えと余りを算出する計算式を関数にしてみた
def Calculation(a, b, max=None):
    surplus = 0
    result = a + b
    if max is not None:
        if result > max:
            surplus = result - max
            result = max
    return result, surplus
        
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

# キャラ作成終了ボタンを押した際の挙動を作るよ
def CharaEndButton():
    texts = []
    for status in CharaStatus:
        if CharaStatus[status] == "" or CharaStatus[status] == 0:
            if status == "name":
                texts.append("名前が入力されていません")
            elif status == "age":
                texts.append("年齢が入力されていません")
            elif status == "STR" or status == "CON" or status == "SIZ" or status == "DEX" or status == "APP" or status == "EDU" or status == "INT" or status == "POW":
                texts.append(status + "が入力されていません")
            elif status == "Profession":
                texts.append("職業が選択されていません")
    if PullDownItem == "":
        texts.append("趣味が選択されていません")
    else:
        HobyDataIn()
    if texts != []:
        text = "\n".join(texts)
        messagebox.showerror("未入力",text)
    else:
        Save()

# データセーブ
def Save():
    global SCENE_FLAG

    # 今日の日付と時間を取得
    now = dt.datetime.now()
    str_now = now.strftime("%Y-%m-%d_%H-%M-%S")

    # セーブフォルダが無ければ作る
    dir_name = PATH + SAVE
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    # キャラクター名、日時でセーブデータを作る
    file_name = dir_name + CharaStatus["name"] + " " + str_now + ".json"
    data = {}
    data["CharaStatus"] = CharaStatus
    with open(file_name,"w",encoding="utf-8_sig") as f:
        json.dump(data,f,indent=2,ensure_ascii=False)

    # キャラシ画面からセーブした際は本編に進む
    if SCENE_FLAG == CHARASE:
        SCENE_FLAG = PLAY
        
# データロード
def Load():
    global SCENE_FLAG
    global SelectSaveData

    window = LoadWindow(SaveFiles)

    # マウスオーバーで枠を表示するよ
    key = pygame.mouse.get_pos()
    for rect in window.rect_list:
        if rect.collidepoint(key):
            pygame.draw.rect(screen,BLACK,rect,1)
    
    for rect in window.data_rect_list:
        if rect.collidepoint(key):
            pygame.draw.rect(screen,BLACK,rect,1)

    for event in pygame.event.get():
        # マウスクリック時
        if event.type == MOUSEBUTTONDOWN:
            # 左ボタン
            if event.button == 1:
                if window.close_rect.collidepoint(event.pos):
                    SCENE_FLAG = TITLE

                for i in range(len(window.data_rect_list)):
                    if window.data_rect_list[i].collidepoint(event.pos):
                        SelectSaveData = SaveFiles[i]
                        print(SelectSaveData)
                        

        # 閉じるボタンで終了
        if event.type == QUIT:
            Close()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                Close()

    
class LoadWindow:
    def __init__(self, list):
        self.draw()
        self.list = list
        self.data_set(self.list)

    def draw(self):
        w = 400
        h = 500
        x = (screen.get_width() / 2) - (w / 2)
        y = (screen.get_height() / 2) - (h / 2)
        self.window_rect = Rect(x,y,w,h)
        pygame.draw.rect(screen,SHEET_COLOR,self.window_rect)
        pygame.draw.rect(screen,BLACK,self.window_rect,2)

        self.top_rect = TitleRender("ロード", 80, BLACK, contents_font)
        self.start_rect = Label("開始", 250, 500, contents_font)
        self.close_rect = Label("CLOSE", 480, 500, contents_font)
        self.rect_list = [self.start_rect,self.close_rect]
       
    def data_set(self,datas):
        x = (screen.get_width() / 2) - 150
        start_y = 150
        y = start_y
        color = SHEET_COLOR
        self.data_rect_list = []
        for data in datas:
            if SelectSaveData == data:
                color = WHITE
            data_name = data.replace(".json", "")
            self.data_rect_list.append(Label(data_name, x, y, font))
            y += 30

    def label(name, x, y, color):
        color = BLACK
        surface = font.render(name, True, color)
        rect = surface.get_rect(left=x, top=y)
        screen.blit(surface, rect)
        return Rect(rect)


# キャラクターシート作成画面
def CharacterSheet():
    global CharaStatus
    global CharaPage
    global PullDownFlag
    global PullDownItem

    
    # シートの描画
    pygame.draw.rect(screen, SHEET_COLOR, SHEET_RECT)

    # ステータスの表示
    if CharaPage:
        # ページ変更ゾーン
        page_navi = PageNavigation(RIGHT)

        Name = Status("名前","name","",250, 50, 150, 28,"探索者の名前を入力してください", False)
        Sex = Status("性別","sex","性別(       )",250,80,0,0,"探索者の性別をクリックで選択してください",False,False,False)
        Sex_Button = SexChange(310,80,CharaStatus["sex"])
        Age = Status("年齢","age","",430,80,50,28,"探索者の年齢を入力してください",False)
        STR = Status("筋力","STR","STR(筋力)  ",250,120,40,28,"筋力の値を決めます。\n・3～6:全然筋力がない ・7～10:普通ぐらい\n・11～14:筋力に自身あり ・15～17:筋力を自慢できる\n・18:筋肉モリモリマッチョマン\nテキスト入力とダイスで決定を選択できます。",Dice_text="3D6")
        CON = Status("体力","CON","CON(体力)  ",250,152,40,28,"体力の値を決めます。\n・3～6:まったく体力ない ・7～10:ほどほど体力はある\n・11～14:それなりに体力がある\n・15～17:スポーツマン並にある ・18:元気100倍\nテキスト入力とダイスで決定を選択できます。",Dice_text="3D6")
        SIZ = Status("体格","SIZ","SIZ(体格)  ",250,184,40,28,"体格の値を決めます。\n・8～11:小柄 ・12～15:中肉中背 ・16～18:大柄\nテキスト入力とダイスで決定を選択できます。",Dice_text="2D6+6")
        DEX = Status("俊敏性","DEX","DEX(俊敏性)",250,216,40,28,"俊敏性の値を決めます。\n・3～6:鈍重 ・7～10:問題なく動ける\n・11～14:素早い動作が得意 ・15～17:その道のプロ\n・18:電光石火\nテキスト入力とダイスで決定を選択できます。",Dice_text="3D6")
        APP = Status("外見","APP","APP(外見)  ",500,120,40,28,"外見の値を決めます。\n・3～6:醜悪な容姿 ・7～10:一般的\n・11～14:整った顔立ち ・15～17:モデル並み\n・18:傾城傾国\nテキスト入力とダイスで決定を選択できます。",Dice_text="3D6")
        EDU = Status("教育","EDU","EDU(教育)  ",500,152,40,28,"教育の値を決めます。\n・6～8:中学卒業程度 ・9～11:高校卒業\n・12～15:大学卒業 ・16～19:大学院生卒業\n・20～21:研究者や科学者\nテキスト入力とダイスで決定を選択できます。",Dice_text="3D6+3")
        INT = Status("知性","INT","INT(知性)  ",500,184,40,28,"知力の値を決めます。\n・3～6:頭が悪い ・7～10:普通 ・11～14:発想豊か\n・15～17:頭脳明晰 ・18:英俊豪傑\nテキスト入力とダイスで決定を選択できます。",Dice_text="3D6")
        POW = Status("精神力","POW","POW(精神力)",500,216,40,28,"精神力の値を決めます。\n・3～6:精神に問題あり ・7～10:人並みの心臓\n・11～14:精神的にタフ ・15～17:修行僧\n・18:黄金の精神\nテキスト入力とダイスで決定を選択できます。",Dice_text="3D6")
        Luck = Status("幸運","Luck","幸運       ",250,250,40,28,"探索者の幸運度を表します。\n値はPOW x 5で決まります。",False,False)
        Idea = Status("アイデア","Idea","アイデア   ",250,282,40,28,"アイデアは直感的な能力です。\n特殊な雰囲気など、普通では気がつかないであろう物に\n気付けるかどうかの能力になります\n値はINT x 5で決まります。",False,False)
        Knowledge = Status("知識","Know","知識       ",250,314,40,28,"探索者が持っている知識量の値です。\n値はEDU x 5で決まります。",False,False)
        Avo = Status("回避","Avo","回避       ",250,346,40,28,"探索者の回避技能値です。\n値はDEX x 2で決まります。",False,False)
        DB = Status("ﾀﾞﾒｰｼﾞ･ﾎﾞｰﾅｽ","DB","DB(ﾀﾞﾒｰｼﾞ･ﾎﾞｰﾅｽ)",450,250,50,28,"小柄で筋力が無い人物だと\n与えるダメージにマイナスの補正が掛かります。\n逆に大柄で筋力がある人物では\n与えるダメージにプラスの補正が掛かります。\n値はSTR+SIZで決まります。",False,False)
        HP = Status("耐久力","HP","耐久力          ",450,282,40,28,"探索者のHPや生命力を表します。\n最大値は(CON+SIZ)÷2で決まります。",False,False)
        MP = Status("ﾏｼﾞｯｸﾎﾟｲﾝﾄ","MP","MP(ﾏｼﾞｯｸﾎﾟｲﾝﾄ)  ",450,314,40,28,"探索者のマジックポイントを表します。\n最大値はPOWと同じ数値です。",False,False)
        SAN = Status("正気度","SAN","SAN値(正気度)   ",450,346,40,28,"探索者の正気度を表します。\n最大値はPOW x 5で決まります。",False,False)

        # リストに入れて同じ処理はfor文で回せるようにするよ
        status = [Name,Sex,Age,STR,CON,SIZ,DEX,APP,EDU,INT,POW,
                  Luck,Idea,Knowledge,Avo,DB,HP,MP,SAN]
        
        # マウスオーバーでテキスト表示するよ
        key = pygame.mouse.get_pos()

        for stat in status:
            if stat.Label_rect.collidepoint(key) or stat.Input_rect.collidepoint(key):
                TextDraw(stat.text)
            elif stat.Button_rect.collidepoint(key):
                TextDraw("ダイスでランダムに値を決めることができます")
    else:
        # ページ変更ゾーン
        page_navi = PageNavigation(LEFT)

        # 職業選択画面
        Profe = Profession(CharaStatus["Profession"])
        # 趣味選択画面
        Hoby = Hobby()
        # キャラ作成終了ボタン
        enter_rect = Button((530,330,100,100),"キャラ作成\n終了")

        key = pygame.mouse.get_pos()
        if PullDownFlag == False:
            for prof in Profe.prof_list:
                if Profe.prof_list[prof]["rect"].collidepoint(key):
                    TextDraw(f"あなたの職業を選択してください\n【{prof}】")
            if enter_rect.collidepoint(key):
                TextDraw("キャラクター作成を終了します")
        if Hoby.pull.box_rect.collidepoint(key):
            TextDraw("あなたの趣味を選択してください")

    
    for event in pygame.event.get():
        # マウスクリック時
        if event.type == MOUSEBUTTONDOWN:
            # 左ボタン
            if event.button == 1:
                # １ページ目だったら
                if CharaPage:
                    # ページ移動
                    if page_navi.navi_rect.collidepoint(event.pos):
                        CharaPage = False
                    # 男ボタン
                    elif Sex_Button.man_rect.collidepoint(event.pos):
                        CharaStatus["sex"] = True
                    # 女ボタン
                    elif Sex_Button.woman_rect.collidepoint(event.pos):
                        CharaStatus["sex"] = False                                        

                    else:
                        # 他のステータスをリストでまとめた
                        for stat in status:
                            # インプットボックス
                            if stat.Input_rect.collidepoint(event.pos):
                                if stat.Input_flag:
                                    stat.InputProcess()
                            # ダイスボタン
                            elif stat.Button_rect.collidepoint(event.pos):
                                stat.DiceProcess()                        
                else:
                    # ページ移動
                    if page_navi.navi_rect.collidepoint(event.pos):
                        CharaPage = True
                        PullDownFlag = 0

                    # プルダウン表示
                    elif Hoby.pull.box_rect.collidepoint(event.pos):
                        if PullDownFlag:
                            PullDownFlag = False
                        else:
                            PullDownFlag = True

                    elif PullDownFlag:
                        for item in Hoby.pull.items:
                            if Hoby.pull.items[item].collidepoint(event.pos):
                                PullDownItem = item
                                PullDownFlag = False
                        PullDownFlag = False

                    elif enter_rect.collidepoint(event.pos):
                        CharaEndButton()

                    else:
                        for prof in Profe.prof_list:
                            rect = Profe.prof_list[prof]["rect"]
                            if rect.collidepoint(event.pos):
                                CharaStatus["Profession"] = prof
                                ProfDataIn()
            
        

        # 閉じるボタンで終了
        if event.type == QUIT:
            Close()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                Close()

# 部屋を作るよ
class Room:
    def __init__(self):
        img_paths = self.file_path()
        self.room_img, self.room_rect = self.image(img_paths["Room"],SHEET_RECT.y,area=Rect(0,0,820,375),center_flag=True,room_flag=True)
        self.item(img_paths)
        
    def file_path(self):
        paths = {}
        path = PATH + PICTURE
        if RoomFlag == CENTER:
            room_path = path + "central-room_"
            paths["Light"] = room_path + "Light.png"
            paths["Soup"] = room_path + "Soup.png"
            if DirectionFlag == NORTH:
                room_direct_path = room_path + "north"
                paths["Door1"] = room_direct_path + "_WestDoor.png"
                paths["Door2"] = room_direct_path + "_NorthDoor.png"
                paths["Door3"] = room_direct_path + "_EastDoor.png"
            elif DirectionFlag == EAST:
                room_direct_path = room_path + "east"
                paths["Door1"] = room_direct_path + "_NorthDoor.png"
                paths["Door2"] = room_direct_path + "_EastDoor.png"
                paths["Door3"] = room_direct_path + "_SouthDoor.png"
            elif DirectionFlag == WEST:
                room_direct_path = room_path + "west"
                paths["Door1"] = room_direct_path + "_SouthDoor.png"
                paths["Door2"] = room_direct_path + "_WestDoor.png"
                paths["Door3"] = room_direct_path + "_NorthDoor.png"
            elif DirectionFlag == SOUTH:
                room_direct_path = room_path + "south"
                paths["Door1"] = room_direct_path + "_EastDoor.png"
                paths["Door2"] = room_direct_path + "_SouthDoor.png"
                paths["Door3"] = room_direct_path + "_WestDoor.png"
            paths["Room"] = room_direct_path + ".jpg"
            paths["Memo"] = room_direct_path + "_Memo.png"
            paths["Table"] = room_direct_path + "_Table.png"
        else:
            if RoomFlag == NORTH:
                room_path = path + "north-room"
                paths["Cooktop"] = room_path + "_Cooktop.png"
                paths["Pot"] = room_path + "_Pot.png"
                paths["CupBoard"] = room_path + "_CupBoard.png"
                paths["Fridge"] = room_path + "_Fridge.png"
                paths["Sink"] = room_path + "_Sink.png"
                paths["Storage"] = room_path + "_Storage.png"
                paths["TopSinkStorage"] = room_path + "_TopSinkStorage.png"
                paths["UnderSinkStorage"] = room_path + "_UnderSinkStorage.png"
                
            elif RoomFlag == EAST:
                if DiscoveryFlag:
                    room_path = path + "east-room"
                    paths["Corpse"] = room_path + "_Corpse.png"
                    paths["Memo"] = room_path + "_Memo.png"
                else:
                    room_path = path + "black-room"
            elif RoomFlag == SOUTH:
                room_path = path + "south-room"
                paths["StoneStatue"] = room_path + "_StoneStatue.png"
                paths["Slate1"] = room_path + "_Slate_01.png"
                paths["Slate2"] = room_path + "_Slate_02.png"
            elif RoomFlag == WEST:
                room_path = path + "west-room"
                paths["BookShelf"] = room_path + "_BookShelf.png"
                paths["Candle"] = room_path + "_Candle.png"
                if BookFlag:
                    paths["Book"] = room_path + "_Book.png"
                    room_path += "_PicupBook"
            paths["Room"] = room_path + ".jpg"


        return paths

    def image(self, path, y, x=0, area=None, center_flag=False, room_flag=False):
        size = 0.19

        # 画像の読み込み＆アルファ化(透明化)
        img = pygame.image.load(path).convert_alpha()
        # 画像の縮小
        img = pygame.transform.rotozoom(img, 0, size)

        # 画像の位置取得
        rect = img.get_rect()
        # 画像の位置を変更する
        if center_flag:
            # 画面中央に置きたい場合
            rect.centerx = screen.get_width() / 2
        else:
            rect.centerx += x
        rect.centery += y

        # 部屋のimgの場合はメインsurfaceに、部屋のアイテムは部屋のsurfaceに
        if room_flag:
            screen.blit(img, rect, area=area)
            return img, rect
        else:
            self.room_img.blit(img, rect, area=area)
        return rect

    def item(self, paths):
        if RoomFlag == CENTER:
            self.left_door_rect = self.image(paths["Door1"],93,121)
            self.center_door_rect = self.image(paths["Door2"],112,center_flag=True)
            self.right_door_rect = self.image(paths["Door3"],94,603)
            self.light_rect = self.image(paths["Light"],54,center_flag=True)
            tablex,memox = 0,0
            table_flag,memo_flag = False,False
            if DirectionFlag == NORTH:
                tabley, table_flag = 219, True
                memoy, memox = 267, 341
            elif DirectionFlag == EAST:
                tabley, tablex = 242, 264
                memoy, memo_flag = 283, True
            elif DirectionFlag == SOUTH:
                tabley, table_flag = 253, True
                memoy, memox = 267, 427
            elif DirectionFlag == WEST:
                tabley, tablex = 243, 295
                memoy, memo_flag = 253, True
            self.table_rect = self.image(paths["Table"],tabley,tablex,center_flag=table_flag)
            self.memo_rect = self.image(paths["Memo"],memoy,memox,center_flag=memo_flag)
            self.soup_rect = self.image(paths["Soup"],254,center_flag=True)
        elif RoomFlag == NORTH:
            self.under_storage_rect = self.image(paths["UnderSinkStorage"],250,325)
            self.cooktop_rect = self.image(paths["Cooktop"],226,225)
            self.sink_rect = self.image(paths["Sink"],216,468)
            self.top_storage_rect = self.image(paths["TopSinkStorage"],100,325)
            self.pot_rect = self.image(paths["Pot"],203,290)
            self.storage_rect = self.image(paths["Storage"],225,560)
            self.cupboard_rect = self.image(paths["CupBoard"],30,36)
            self.fridge_rect = self.image(paths["Fridge"],39,628)
        elif RoomFlag == EAST:
            if DiscoveryFlag:
                self.corpse_rect = self.image(paths["Corpse"],218,437)
                self.memo_rect = self.image(paths["Memo"],259,277)
        elif RoomFlag == WEST:
            self.bookshelf_rect = self.image(paths["BookShelf"],30,36)
            self.chandle_rect = self.image(paths["Candle"],223,350)
            if BookFlag:
                self.book_rect = self.image(paths["Book"],246,298)
        else:
            self.statue_rect = self.image(paths["StoneStatue"],69,287)
            self.slate1_rect = self.image(paths["Slate1"],156,213)
            self.slate2_rect = self.image(paths["Slate2"],156,479)

    def event(self):
        pass

def BlackSurface():
    black = pygame.Surface(DISPLAY_SIZE)
    if AlphaFlag == 1:
        black.set_alpha(minAlpha)
    elif AlphaFlag == 2:
        black.set_alpha(maxAlpha)
    black.blit(screen, FILL_RECT)

# プレイ画面
def MainPlay():
    global RoomFlag
    global PlaySceneFlag
    global DirectionFlag
    global DiscoveryFlag
    global AlphaFlag

    #if PlaySceneFlag == 0:
    #    pygame.time.wait(500)

    # 部屋の表示
    room = Room()

    if RoomFlag == 0:
        AlphaFlag = 1
        BlackSurface()

    # ナビゲーションバーの表示
    if RoomFlag == CENTER:
        right_navi = PageNavigation(RIGHT)
        left_navi = PageNavigation(LEFT)
    else:
        under_nave = PageNavigation(UNDER)

    for event in pygame.event.get():
        # マウスクリック時
        if event.type == MOUSEBUTTONDOWN:
            # 左ボタン
            if event.button == 1:
                if RoomFlag == CENTER:
                    # 部屋の向き移動
                    if right_navi.navi_rect.collidepoint(event.pos):
                        if DirectionFlag == NORTH:
                            DirectionFlag = EAST
                        elif DirectionFlag == EAST:
                            DirectionFlag = SOUTH
                        elif DirectionFlag == SOUTH:
                            DirectionFlag = WEST
                        else:
                            DirectionFlag = NORTH
                    elif left_navi.navi_rect.collidepoint(event.pos):
                        if DirectionFlag == NORTH:
                            DirectionFlag = WEST
                        elif DirectionFlag == EAST:
                            DirectionFlag = NORTH
                        elif DirectionFlag == SOUTH:
                            DirectionFlag = EAST
                        else:
                            DirectionFlag = SOUTH
                    # 真ん中のドア
                    elif room.center_door_rect.collidepoint(event.pos):
                        if DirectionFlag == NORTH:
                            RoomFlag = NORTH
                        elif DirectionFlag == WEST:
                            RoomFlag = WEST
                        elif DirectionFlag == EAST:
                            RoomFlag = EAST
                        else:
                            RoomFlag = SOUTH
                    # 左のドア
                    elif room.left_door_rect.collidepoint(event.pos):
                        if DirectionFlag == NORTH:
                            RoomFlag = WEST
                        elif DirectionFlag == WEST:
                            RoomFlag = SOUTH
                        elif DirectionFlag == EAST:
                            RoomFlag = NORTH
                        else:
                            RoomFlag = EAST
                    # 右のドア
                    elif room.right_door_rect.collidepoint(event.pos):
                        if DirectionFlag == NORTH:
                            RoomFlag = EAST
                        elif DirectionFlag == WEST:
                            RoomFlag = NORTH
                        elif DirectionFlag == EAST:
                            RoomFlag = SOUTH
                        else:
                            RoomFlag = WEST
                else:
                    if under_nave.navi_rect.collidepoint(event.pos):
                        # 真ん中の部屋に戻る
                        RoomFlag = CENTER



        # 閉じるボタンで終了
        if event.type == QUIT:
            Close()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                Close()

def frame():
    pygame.draw.rect(screen, WHITE, FRAME_RECT,3)

# ダイスを表示する為のフレーム
def DiceFrame():
    pygame.draw.rect(screen, WHITE, DICE_FRAME_RECT,3)

def main():
    global AlphaFlag
    global minAlpha
    global maxAlpha

    # 画面の描写
    while True:
        # 画面を黒で塗りつぶす
        screen.fill(BLACK)
        if SCENE_FLAG == TITLE:
            Title()
        elif SCENE_FLAG == LOAD:
            Load()
        elif SCENE_FLAG == SETTING:
            pass
        elif SCENE_FLAG == ENDCREDITS:
            pass
        else:
            clock = pygame.time.Clock()
            clock.tick(60)
            frame()
            DiceFrame()

            if SCENE_FLAG == PLAY:
                MainPlay()
            if SCENE_FLAG == CHARASE:
                CharacterSheet()
            if SCENE_FLAG == OPENING:
                Opening()
        
        """
        if AlphaFlag == 1:
            minAlpha += 5
            if minAlpha >= 255:
                AlphaFlag = 0
                min_alpha = 0
        elif AlphaFlag == 2:
            maxAlpha -= 5
            if maxAlpha <= 0:
                AlphaFlag = 0
                maxAlpha = 255
        """
        # 画面を更新
        pygame.display.update() 

        # イベント取得
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT:
                Close()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    Close()
                    
            
if __name__ == "__main__":
    main()
