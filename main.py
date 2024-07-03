import sys, random, os, json
import pygame
import pygame.draw
from pygame.locals import *
import pygame_menu as pgmenu
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog


DISPLAY_SIZE = (800, 600)
BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (73,74,65)
RED = (183,40,46)

SHEET_COLOR = (189,183,107)
# SHEET_COLOR = (237,228,205)
SHEET_RECT = Rect(30,30,740,375)

# パスの指定
PATH = os.path.dirname(__file__)
SCENARIO = "/Scenario/"
PICTURE ="/Picture/"
MUSIC = "/Music/"

STATUS_JSON_PATH = os.path.join(PATH,"CharaStatus.json")
PROF_JSON_PATH = os.path.join(PATH,"Profession.json")
SKILL_JSOM_PATH = os.path.join(PATH,"SkillList.json")
HOBBY_JSON_PATH = os.path.join(PATH,"Hobby.json")

FONT_PATH = os.path.join(PATH,"HGRKK.TTC")
TITLE_FONT_PATH = os.path.join(PATH,"genkai-mincho.ttf")
FONT_SIZ = 22
TITLE_SIZ = 60
OPENING_SIZ = 30
SKILL_SIZ = 18
TITLE_TEXT = "毒入りスープ"

# シーン切り替えフラグ
TITLE,SETTING,OPENING,CHARASE,PLAY,ENDING,ENDCREDITS = (0,1,2,3,4,5,6)
#SCENE_FLAG = 0
SCENE_FLAG = 3

# キャラクターのステータスデータ
with open(STATUS_JSON_PATH,"r",encoding="utf-8_sig")as f:
    STATUS = json.load(f)
    CharaStatus = STATUS["Hero"]

# 職業リスト
with open(PROF_JSON_PATH,"r",encoding="utf-8_sig") as f:
    ProfessionList = json.load(f)

# 技能リスト
with open(SKILL_JSOM_PATH,"r",encoding="utf-8_sig") as f:
    SkillList = json.load(f)

# 趣味リスト
with open(HOBBY_JSON_PATH,"r",encoding="utf-8_sig") as f:
    HobbyList = json.load(f)


CharaPage = True    # ページ変更用フラグ
PullDownFlag = False    # プルダウン用フラグ
PullDownItem = ""       # プルダウンアイテム記憶用
OpeningFlag = 0
FrameRect = Rect(30,420,580,150)
DiceFrameRect = Rect(620,420,150,150)

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


# タイトル画面作るよ
def Title():
    global SCENE_FLAG
    # タイトル用のフォント
    title_font = pygame.font.Font(TITLE_FONT_PATH,TITLE_SIZ)
    # タイトル画面用に基本フォントのサイズ変更
    opening_font = pygame.font.Font(FONT_PATH,OPENING_SIZ)
    
    # タイトル
    title_rect = TitleRender(TITLE_TEXT,title_font,RED,150)
    start_rect = TitleRender("はじめる",opening_font,WHITE,280)
    load_rect = TitleRender("つづきから",opening_font,WHITE,350)
    setting_rect = TitleRender("設定",opening_font,WHITE,420)
    close_rect = TitleRender("おわる",opening_font,WHITE,490)

    for event in pygame.event.get():
        # マウスクリック時
        if event.type == MOUSEBUTTONDOWN:
            # 左ボタン
            if event.button == 1:
                if start_rect.collidepoint(event.pos):
                    SCENE_FLAG = OPENING
                elif load_rect.collidepoint(event.pos):
                    pass
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
def TitleRender(text,font,color,y):
    surface = font.render(text,True,color)
    rect = surface.get_rect()
    # 画面の中央に表示する
    rect.centerx = DISPLAY_SIZE[0] / 2
    rect.y = y
    screen.blit(surface,rect)
    return rect

def Opening():
    global SCENE_FLAG
    global OpeningFlag

    if OpeningFlag == 0:
        TextDraw("この物語はクトゥルフ神話TRPGを元に作成しています。")
    elif OpeningFlag == 1:
        TextDraw("まずは探索者を作成しましょう。")
    
    for event in pygame.event.get():
        # マウスクリック時
        if event.type == MOUSEBUTTONDOWN:
            # 左ボタン
            if event.button == 1:
                if OpeningFlag == 0:
                    OpeningFlag = 1
                elif OpeningFlag == 1:
                    SCENE_FLAG = CHARASE

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
    def __init__(self, page_flag):
        # ナビゲーションの位置
        self.navi_rect = self.image(page_flag)

    def image(self, page_flag):
        img = "navigate.png"
        navi_img = pygame.image.load(PATH + PICTURE + img).convert_alpha()
        navi_img = pygame.transform.scale(navi_img, (40,355))
        navi_rect = navi_img.get_rect()
        if page_flag: # ステータス画面の時
            navi_rect.centerx += 750
            navi_rect.centery += 40
            screen.blit(navi_img, navi_rect)
            # 三角形の描画
            pygame.draw.polygon(screen,BLACK,[[760,190],[780,210],[760,230]])
        else: # 職業画面の時
            navi_rect.centerx += 20
            navi_rect.centery += 40
            screen.blit(navi_img, navi_rect)
            pygame.draw.polygon(screen,BLACK,[[50,190],[30,210],[50,230]])
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
                    if status_name == "DB":
                        st = CharaStatus["STR"] + CharaStatus["SIZ"]
                        if 2 <= st <= 12:
                            self.status = "-1D6"
                        elif 13 <= st <= 16:
                            self.status = "-1D4"
                        elif 25 <= st <= 32:
                            self.status = "+1D4"
                        elif 33 <= st <= 40:
                            self.status = "+1D6"                        
                        else:
                            self.status = "0"
                    elif status_name == "Luck":
                        self.status = CharaStatus["POW"] * 5
                    elif status_name == "Idea":
                        self.status = CharaStatus["INT"] * 5
                    elif status_name == "Know":
                        self.status = CharaStatus["EDU"] * 5
                        if self.status > 99:
                            self.status = 99
                    elif status_name == "Avo":
                        self.status = CharaStatus["DEX"] * 2
                    elif status_name == "HP":
                         self.status = round((CharaStatus["CON"] + CharaStatus["SIZ"]) / 2)
                    elif status_name == "SAN":
                        self.status = CharaStatus["POW"] * 5
                    elif status_name == "MP":
                        self.status = CharaStatus["POW"]
                    else:
                        self.status = CharaStatus[status_name]
                    Label(str(self.status),self.Input_rect.x+2,self.Input_rect.y+2)
        else:
            self.Input_rect = self.Label_rect

        if max_flag:
            self.Input2_rect = self.Input_rect

        # ダイスボタンを表示するフラグ
        if Button_flag:
            self.Button_rect = self.DiceButton(self.Input_rect,Dice_text)
        else:
            self.Button_rect = self.Input_rect
    
    # 入力ボックスの処理まとめるよ
    def InputProcess(self):
        min=0
        max=99
        # 最大値最小値を決めるよ
        if self.status_name == "age":
            min = CharaStatus["EDU"] + 6
        elif self.status_name == "Dura":
            max = CharaStatus["Dura_max"]
        elif self.status_name == "MP":
            max = CharaStatus["MP_max"]
        elif self.status_name == "SAN":
            max = CharaStatus["SAN_max"]
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

    # ダイスボタン作るよ    
    def DiceButton(self, rect, text):
        out_color = GRAY
        in_color = (181,181,174)
        text_color = BLACK
        surface = font.render(text, True, text_color,in_color)
        x = rect[0] + rect[2] + 5
        y = rect[1] -2 
        w = surface.get_rect().w + 8
        h = surface.get_rect().h + 8
        pygame.draw.rect(screen, out_color, (x, y, w, h))
        pygame.draw.line(screen, in_color, (x, y), (x+w,y+h))
        pygame.draw.line(screen, in_color, (x,y+h), (x+w,y))
        text_rect = surface.get_rect(left=x+4, top=y+4)
        screen.blit(surface, text_rect)
        return Rect(x,y,w,h)
    
    # ダイス処理まとめるよ
    def DiceProcess(self):
        val = DiceRool(self.dice_text)
        CharaStatus[self.status_name] = val
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
        x,y = 160,230
        self.prof_list = ProfessionList
        for prof in list(self.prof_list):
            name = self.prof_list[prof]["name"]
            img_path = PATH + PICTURE + "prof_" + name + ".png"
            rect = image(img_path, 0.1, x, y, line=True, background=True)
            self.prof_list[prof]["rect"] = rect
            x += 55
            if x >= 650:
                y += 55
                x = 160

    def image(self, prof):
        data = self.prof_list[prof]
        name = data["name"]
        img_path = PATH + PICTURE + "prof_" + name + ".png"
        x,y = 160,40
        rect = image(img_path, 0.35 , x, y, line=True, background=True)
        lrx = rect.x + rect.w + 5
        label_rect = Label(f"【{prof}】", lrx, y, font)

# 趣味選択画面作るよ
class Hobby:
    def __init__(self):
        skill_font = pygame.font.Font(FONT_PATH, SKILL_SIZ)
        if PullDownItem == "":
            self.listitem = "趣味"
        else:
            self.listitem = PullDownItem
        self.pull = PullDown((495,200,150,25),self.listitem,list(HobbyList),skill_font,207)

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

    CharaStatus["skill"] = {}
    prof = CharaStatus["Profession"]
    skills = ProfessionList[prof]["skill"]
    max = CharaStatus["EDU"] * 20
    if max > 0:
        i = max
        for skill in skills:
            percent = skills[skill] / 100
            bonus = int(max * percent)
            if skill == "回避":
                data = CharaStatus["Avo"]
            data = SkillList[skill]
            result = data + bonus
            surplus = 0
            if result > 90:
                surplus = result - 90
                result = 90
            if skill == "回避":
                CharaStatus["Avo"] = result
            else:
                CharaStatus["skill"][skill] = result
            i -= bonus + surplus
            if i < 0:
                print("数字が足りません")
        
        if i > 0:
            lists = {}
            for skill in CharaStatus["skill"]:
                value = CharaStatus["skill"][skill]
                if value != 90:
                    if value + i < 90:
                        lists[skill] = value
            select = random.choice(list(lists))
            CharaStatus["skill"][select] += i
            
# 選択した趣味から主人公のステータスにデータを入れるよ
def HobyDataIn():
    hobby = PullDownItem
    my_skills = CharaStatus["skill"]
    skills = HobbyList[hobby]
    max = CharaStatus["INT"] * 10

# キャラクターシート作成画面
def CharacterSheet():
    global CharaStatus
    global CharaPage
    global PullDownFlag
    global PullDownItem

    Sheet_exit = False # キャラシ作成画面を終わるフラグ（未実装）
    # clock = pygame.time.Clock()
    
    menu = pgmenu.Menu("",740,375)

    # シートの描画
    pygame.draw.rect(screen, SHEET_COLOR, SHEET_RECT)

    # ページ変更ゾーン
    page_navi = PageNavigation(CharaPage)

    # ステータスの表示
    if CharaPage:
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
        # 職業選択画面
        Profe = Profession(CharaStatus["Profession"])
        # 趣味選択画面
        Hoby = Hobby()

        key = pygame.mouse.get_pos()
        for prof in Profe.prof_list:
            if Profe.prof_list[prof]["rect"].collidepoint(key):
                TextDraw(f"あなたの職業を選択してください\n【{prof}】")
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


def frame():
    pygame.draw.rect(screen, WHITE, FrameRect,3)

# ダイスを表示する為のフレーム
def DiceFrame():
    pygame.draw.rect(screen, WHITE, DiceFrameRect,3)

def main():
    # 画面の描写
    while True:
        # 画面を黒で塗りつぶす
        screen.fill(BLACK) 
        if SCENE_FLAG == TITLE:
            Title()
        elif SCENE_FLAG == SETTING:
            pass
        elif SCENE_FLAG == ENDCREDITS:
            pass
        else:
            frame()
            DiceFrame()
            if SCENE_FLAG == CHARASE:
                CharacterSheet()
            if SCENE_FLAG == OPENING:
                Opening()
         
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
