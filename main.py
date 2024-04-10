import sys, random, os
import pygame
from pygame.locals import *
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

# パスの指定
PATH = os.path.dirname(__file__)
SCENARIO = "/Scenario/"
PICTURE ="/Picture/"
MUSIC = "/Music/"

FONT_PATH = os.path.join(PATH,"HGRKK.TTC")
FONT_SIZ = 22
SKILL_SIZ = 18
TITLE_TEXT = "毒入りスープ"

# シーン切り替えフラグ
TITLE,SETTING,OPENING,CHARASE,PLAY,ENDING,ENDCREDITS = (0,1,2,3,4,5,6)
#SCENE_FLAG = 0
SCENE_FLAG = 3

# 主人公のステータスデータ
CharaStatus = {"name":"", "age":0, "sex":True,
               "STR":0, "CON":0, "SIZ":0, "DEX":0,
               "APP":0, "EDU":0, "INT":0, "POW":0,
               "Luck":0,"Idea":0,"Know":0,"MOV":8,"DB":"",
               "Dura":0,"Dura_max":0,"MP":0,"MP_max":0,"SAN":0,"SAN_max":0,
               "Profession1":"未選択","Profession2":"","skill":{}}

ProfessionList = {"未選択":[],
                  "医師":["アニマルセラピスト","看護師","救急救命士","形成外科医","精神科医","闇医者"],
                  "エンジニア":[],"狂信者":[],
                  "警察官":["海上保安官","科学捜査研究員","山岳救助隊員","消防士"],
                  "芸術家":["芸術家","ダンサー","デザイナー","ファッション系芸術家"],
                  "古物研究家":[],"コンピューター技術者":[],"作家":[],
                  "自衛官":["陸上自衛隊員","海上自衛隊員(艦上勤務)","自衛隊パイロット(陸海空)","民間軍事会社メンバー"],
                  "ジャーナリスト":[],"宗教家":[],"商店主／店員":[],
                  "私立探偵":[],"水産業従事者":[],"スポーツ選手":[],
                  "大学教授":["冒険家教授","評論家"],
                  "タレント":["アイドル、音楽タレント","アナウンサー","コメディアン","スポーツタレント","テレビ・コメンテーター","俳優","プロデューサー、マネージャー"],
                  "超心理学者":["ゴーストハンター","占い師、スピリチュアリスト、霊媒師"],
                  "ディレッタント":[],"ドライバー":[],"農林業従事者":[],"パイロット":[],
                  "ビジネスマン":["執事・メイド","セールスマン"],
                  "法律家":[],"放浪者":[],
                  "暴力団組員":[],"ミュージシャン":[],"メンタルセラピスト":[]}

SkillList = {"言いくるめ":5,"医学":5,"運転(自動車)":20,"応急手当":30,"オカルト":5,"回避":2,
             "化学":1,"鍵開け":1,"隠す":15,"隠れる":15,"機械修理":20,
             "聞き耳":25,"クトゥルフ神話":0,"芸術":5,"経理":10,"考古学":1,
             "コンピューター":1,"忍び歩き":10,"写真術":10,"重機械操作":1,"乗馬":5,
             "信用":15,"心理学":5,"人類学":1,"水泳":25,"製作":5,
             "精神分析":1,"生物学":1,"説得":15,"操縦":1,"地質学":1,
             "跳躍":25,"追跡":10,"電気修理":10,"電子工学":1,"天文学":1,
             "投擲":25,"登攀":40,"図書館":25,"ナビゲート":10,"値切り":5,
             "博物学":10,"物理学":1,"変装":1,"法律":5,
             "他の言語(英語)":1,"他の言語(ラテン語)":1,"他の言語(ドイツ語)":1,"他の言語(中国語)":1,"他の言語(韓国語)":1,"他の言語(ロシア語)":1,"他の言語(日本語)":1,
             "母国語":5,"マーシャルアーツ":1,"目星":25,"薬学":1,"歴史":20,
             "キック":25,"組みつき":25,"こぶし":50,"頭突き":10,
             "拳銃":20,"サブマシンガン":15,"ショットガン":30,"マシンガン":15,"ライフル":25}

CharaPage = True # ページ変更用フラグ
PullDownFlag = 0

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



# ファイルの読み込み
#f = open(PATH + SCENARIO + '\CharacterSheet_01.txt', 'r', encoding='UTF-8')
#Parameter_list = f.read()
#f.close


# タイトル画面作るよ
def Title():
    global SCENE_FLAG
    # タイトル用のフォント
    font_path = os.path.join(PATH,"genkai-mincho.ttf")
    title_font = pygame.font.Font(font_path,60)
    # タイトル画面用に基本フォントのサイズ変更
    opening_font = pygame.font.Font(FONT_PATH,30)
    
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
    pass

# 終了処理をまとめるよ
def Close():
    if messagebox.askokcancel("確認","本当に終了しますか？"):
        pygame.quit()
        sys.exit()
    else:
        pass

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
            self.Input_rect = self.InputBox((x+self.Label_rect.w,y,w,h),self.Input_flag)
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
                    elif status_name == "Dura":
                         self.status = round((CharaStatus["CON"] + CharaStatus["SIZ"]) / 2)
                         max_flag = True
                         CharaStatus["Dura_max"] = self.status
                    elif status_name == "SAN":
                        self.status = CharaStatus["POW"] * 5
                        max_flag = True
                        CharaStatus["SAN_max"] = self.status
                    elif status_name == "MP":
                        self.status = CharaStatus["POW"]
                        max_flag = True
                        CharaStatus["MP_max"] = self.status
                    else:
                        self.status = CharaStatus[status_name]
                    if max_flag:
                        rect = (x+self.Label_rect.w+self.Input_rect.w,y,w,h)
                        self.Input2_rect = self.InputBox(rect,False)
                        self.InputLabel(str(self.status),self.Input2_rect.x,self.Input2_rect.y)
                        if CharaStatus[self.status_name] == 0:
                            self.status = self.status
                        else:
                            self.status = CharaStatus[self.status_name]
                
                    self.InputLabel(str(self.status),self.Input_rect.x,self.Input_rect.y)
        else:
            self.Input_rect = self.Label_rect

        if max_flag:
            self.Input2_rect = self.Input_rect

        # ダイスボタンを表示するフラグ
        if Button_flag:
            self.Button_rect = self.DiceButton(self.Input_rect,Dice_text)
        else:
            self.Button_rect = self.Input_rect
        
    # 入力ボックス作るよ
    def InputBox(self, rect, flag=True):
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
        pygame.draw.line(screen,BLACK,(x,y+h-1),(x+w-1,y+h-1),2)
        return Rect(x,y,w,h)
    
    # 値を表示したいよ
    def InputLabel(self, text, x, y):
        surface = font.render(str(text),True,BLACK)
        rect = surface.get_rect(left=x+2,top=y+2)
        screen.blit(surface, rect)

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
            self.InputLabel(val,self.Input_rect.x, self.Input_rect.y)
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
        self.InputLabel(str(val),self.Input_rect.x,self.Input_rect.y)

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
        # 画像の読み込み＆アルファ化(透明化)
        chara = pygame.image.load(PATH + PICTURE + img).convert_alpha()
        # 画像の縮小
        chara = pygame.transform.rotozoom(chara, 0, 0.5)
        # 画像の位置取得
        rect = chara.get_rect()
        #画像の位置を変更する
        rect.centerx += 40
        rect.centery += 40
        # 画像の描写
        screen.blit(chara, rect)
        # プレイヤー画像の枠の描画
        pygame.draw.rect(screen, BLACK, rect, 2)

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

# ページ移動用の矢印表示するよ
class PageNavigation:
    def __init__(self, page_flag):
        # ナビゲーションの位置
        self.navi_rect = self.image(page_flag)

    def image(self, page_flag):
        img = "navigate.png"
        navi_img = pygame.image.load(PATH + PICTURE + img).convert_alpha()
        navi_img = pygame.transform.scale(navi_img, (40,340))
        navi_rect = navi_img.get_rect()
        if page_flag: # ステータス画面の時
            navi_rect.centerx += 750
            navi_rect.centery += 40
            screen.blit(navi_img, navi_rect)
            # 三角形の描画
            pygame.draw.polygon(screen,BLACK,[[760,180],[780,200],[760,220]])
        else: # 職業画面の時
            navi_rect.centerx += 20
            navi_rect.centery += 40
            screen.blit(navi_img, navi_rect)
            pygame.draw.polygon(screen,BLACK,[[50,180],[30,200],[50,220]])
        return navi_rect

# ラベル作成を分離するよ
def Label(name, x, y):
    color = BLACK
    surface = font.render(name, True, color)
    rect = surface.get_rect(left=x, top=y)
    screen.blit(surface, rect)
    return Rect(rect)

# 職業選択画面作るよ
class Profession:
    def __init__(self, name, x, y, w, h, flag):
        self.Name = name
        self.Label_rect = Label(name,x,y)
        self.PullDown_rect = self.PullDownBox((x+self.Label_rect.w+5,y-4,w,h))
        self.Box_text = self.BoxLabel(CharaStatus["Profession1"],self.PullDown_rect)
        self.PullDown2_rect = self.PullDownBox((self.PullDown_rect.x + self.PullDown_rect.w+5,y-4,w,h))
        self.PullDown_flag = flag
        if CharaStatus["Profession2"] != "":
            self.Box2_text = self.BoxLabel(CharaStatus["Profession2"],self.PullDown2_rect)
        if PullDownFlag == 1:
            pd_rect = self.PullDown(self.PullDown_rect)
            self.PullDownList(pd_rect)
        elif PullDownFlag == 2:
            self.PullDown(self.PullDown2_rect)


    # プルダウンボックス作るよ
    def PullDownBox(self, rect):
        x = rect[0] + 5
        y = rect[1]
        w = rect[2]
        h = rect[3]
        Box(x,y,w,h)

        # 三角作るよ
        triangle = font.render("▼",True,BLACK)
        tri_rect = triangle.get_rect(right=x+w-2,top=y+4)
        screen.blit(triangle, tri_rect)

        return Rect(x,y,w,h)
    
    # プルダウンボックスに表示される文字列を描画するよ
    def BoxLabel(self,text,rect):
        surface = font.render(str(text),True,BLACK)
        rect = surface.get_rect(left=rect[0]+4,top=rect[1]+4)
        screen.blit(surface, rect)
        return text
    
    # プルダウン押した時に表示されるボックス作りたいよ
    def PullDown(self,rect):
        x = rect[0]
        y = rect[1] + rect[3]
        w = rect[2]
        h = rect[3] + 250
        pygame.draw.rect(screen,GRAY,(x,y,w,h))
        pygame.draw.rect(screen, WHITE, (x+1, y+1, w-2, h-2))
        return Rect(x,y,w,h)

    # プルダウン押した時に表示される項目表示したいよ
    def PullDownList(self,rect):
        x = rect.x + 3
        y = rect.y + 3
        for profes in ProfessionList:
            prof = font.render(profes,True,BLACK)
            pr_rect = prof.get_rect(left=x,top=y)
            screen.blit(prof,pr_rect)
            y += pr_rect.h

    

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

# キャラクターシート作成画面
def CharacterSheet():
    global CharaStatus
    global CharaPage
    global PullDownFlag
    global PullDown2Flag

    Sheet_exit = False # キャラシ作成画面を終わるフラグ（未実装）
    # clock = pygame.time.Clock()

    # シートの描画
    pygame.draw.rect(screen, SHEET_COLOR, Rect(30,30,740,360))

    # ページ変更ゾーン
    page_navi = PageNavigation(CharaPage)

    # ステータスの表示
    if CharaPage:
        Name = Status("名前","name","",250, 50, 150, 28,"探索者の名前を入力してください", False)
        Sex = Status("性別","sex","性別(       )",250,80,0,0,"探索者の性別をクリックで選択してください",False,False,False)
        Sex_Button = SexChange(310,80,CharaStatus["sex"])
        Age = Status("年齢","age","",450,80,50,28,"探索者の年齢を入力してください",False)
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
        MOV = Status("移動率","MOV","MOV(移動率)",250,346,40,28,"探索者の移動率です。",False,False)
        DB = Status("ﾀﾞﾒｰｼﾞ･ﾎﾞｰﾅｽ","DB","DB(ﾀﾞﾒｰｼﾞ･ﾎﾞｰﾅｽ)",450,250,50,28,"小柄で筋力が無い人物だと\n与えるダメージにマイナスの補正が掛かります。\n逆に大柄で筋力がある人物では\n与えるダメージにプラスの補正が掛かります。\n値はSTR+SIZで決まります。",False,False)
        Durability = Status("耐久力","Dura","耐久力          ",450,282,40,28,"探索者のHPや生命力を表します。\n最大値は(CON+SIZ)÷2で決まります。",False)
        MP = Status("ﾏｼﾞｯｸﾎﾟｲﾝﾄ","MP","MP(ﾏｼﾞｯｸﾎﾟｲﾝﾄ)  ",450,314,40,28,"探索者のマジックポイントを表します。\n最大値はPOWと同じ数値です。",False)
        SAN = Status("正気度","SAN","SAN値(正気度)   ",450,346,40,28,"探索者の正気度を表します。\n最大値はPOW x 5で決まります。",False)

        # リストに入れて同じ処理はfor文で回せるようにするよ
        status = [Name,Sex,Age,STR,CON,SIZ,DEX,APP,EDU,INT,POW,
                  Luck,Idea,Knowledge,MOV,DB,Durability,MP,SAN]
        
        # マウスオーバーでテキスト表示するよ
        key = pygame.mouse.get_pos()
        for stat in status:
            if stat.Label_rect.collidepoint(key) or stat.Input_rect.collidepoint(key):
                TextDraw(stat.text)
            elif stat.Button_rect.collidepoint(key):
                TextDraw("ダイスでランダムに値を決めることができます")
    else:
        Skill_rect = Label("技能",70,90)
        pygame.draw.line(screen,BLACK,(120,100),(750,100),2)
        Profe = Profession("職業",70,50,300,32,PullDownFlag)

        # 文字サイズを小さくする
        skill_font = pygame.font.Font(FONT_PATH,SKILL_SIZ)
        # 技能一覧を描写する
        for skill in SkillList:
            pass

    
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

                    # プルダウン表示うまくいってません
                    if Profe.PullDown_rect.collidepoint(event.pos):
                        if PullDownFlag == 1:
                            PullDownFlag == 0
                        else:
                            PullDownFlag = 1
                    if Profe.PullDown2_rect.collidepoint(event.pos):
                        if PullDownFlag == 2:
                            PullDownFlag = 0
                        else:
                            PullDownFlag = 2
            
        if event.type == MOUSEMOTION:
            if CharaPage:
                pass

        # 閉じるボタンで終了
        if event.type == QUIT:
            Close()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                Close()


def frame():
    pygame.draw.rect(screen, WHITE, Rect(30,420,580,150),3)

# ダイスを表示する為のフレーム
def DiceFrame():
    pygame.draw.rect(screen, WHITE, Rect(620,420,150,150),3)

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
