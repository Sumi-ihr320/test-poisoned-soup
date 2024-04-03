import sys, random, os
import pygame
from pygame.locals import *
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog


DISPLAY_SIZE = (800, 600)
BLACK = (0,0,0)
WHITE = (255,255,255)
SHEET_COLOR = (189,183,107)

# パスの指定
PATH = os.path.dirname(__file__)
SCENARIO = "/Scenario/"
PICTURE ="/Picture/"
MUSIC = "/Music/"

FONT_PATH = os.path.join(PATH,"HGRKK.TTC")
# FONT_NAME = "hgskyokashotai"
FONT_SIZ = 22
TITLE = "毒入りスープ"

# 初期化,
pygame.init()
# 画面サイズ
screen = pygame.display.set_mode(DISPLAY_SIZE)
# キーリピート設定
pygame.key.set_repeat(100, 100)
# タイトルバーキャプション
pygame.display.set_caption(TITLE)
# フォントの設定
font = pygame.font.Font(FONT_PATH, FONT_SIZ)
#font = pygame.font.SysFont(FONT_NAME, FONT_SIZ)


# 主人公のステータスデータ
CharaStatus = {"name":"", "age":0, "sex":True,
               "STR":0, "CON":0, "SIZ":0, "DEX":0,
               "APP":0, "EDU":0, "INT":0, "POW":0,
               "Luck":0, "Dura":0, "MOV":8,
               "DB":"", "MP":0, "SAN":0,}

CharaPage = True # ページ変更用フラグ

# ファイルの読み込み
#f = open(PATH + SCENARIO + '\CharacterSheet_01.txt', 'r', encoding='UTF-8')
#Parameter_list = f.read()
#f.close


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
    def __init__(self, name, x, y, w, h, status_name="", text="",  Button_flag=True, Input_flag=True, Box_flag=True,  Dice_text=""):
        self.name = name
        self.x = x
        self.y = y
        self.text = text
        self.status_name = status_name
        self.dice_text = Dice_text
        self.Label_rect = self.Label(name,x,y)
        if Box_flag:
            self.Input_rect = self.InputBox((x,y,w,h),Input_flag)
            if status_name != "sex":
                if status_name in CharaStatus:
                    if status_name == "Dura":
                         self.status = round(CharaStatus["CON"] + CharaStatus["SIZ"] / 2)
                    elif status_name == "DB":
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
                    elif status_name == "Luck" or status_name == "SAN":
                        self.status = CharaStatus["POW"] * 5
                    elif status_name == "MP":
                        self.status = CharaStatus["POW"]
                    else:
                        self.status = CharaStatus[status_name]
                    self.InputLabel(str(self.status))
        else:
            self.Input_rect = self.Label_rect
        if Button_flag:
            self.Button_rect = self.DiceButton(self.Input_rect,Dice_text)
        else:
            self.Button_rect = self.Input_rect
        
    # ラベル作るよ
    def Label(self, name, x, y):
        color = BLACK
        surface = font.render(name, True, color)
        rect = surface.get_rect(left=x, top=y)
        screen.blit(surface, rect)
        return Rect(rect)

    # 入力ボックス作るよ
    def InputBox(self, rect, flag=True):
        if flag:
            color = (255,248,220)
        else:
            color = SHEET_COLOR
        x = rect[0] + self.Label_rect.w + 5
        y = rect[1] -4
        w = rect[2] 
        h = rect[3] 
        pygame.draw.rect(screen, color, (x, y, w, h))
        pygame.draw.line(screen,BLACK,(x,y+h-1),(x+w-1,y+h-1),2)
        return Rect(x,y,w,h)
    
    # 値を表示したいよ
    def InputLabel(self, text):
        surface = font.render(str(text),True,BLACK)
        rect = surface.get_rect(left=self.Input_rect.x+2,top=self.Input_rect.y+2)
        screen.blit(surface, rect)

    # 入力ボックスの処理まとめるよ
    def InputProcess(self, title):
        val = InputGet(self.status_name,title,'あなたの' + title + 'を入力してください')
        if val != None:
            self.InputLabel(val)

    # ダイスボタン作るよ    
    def DiceButton(self, rect, text):
        out_color = (73,74,65)
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
        self.InputLabel(str(val))


# 選んだ性別によって画像が変わるようにするよ
class SexChange:
    def __init__(self, x, y, flag):
        self.x = x
        self.y = y
        self.sex_flag = flag
        if self.sex_flag:
            self.man_rect = self.Butoon("男",x,y,True)
            self.woman_rect = self.Butoon("女",x+40,y,False)
        else:
            self.man_rect = self.Butoon("男",x,y,False)
            self.woman_rect = self.Butoon("女",x+40,y,True)
        self.Image()

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
    def Image(self):
        if self.sex_flag:
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

 
def CharacterSheet():
    global CharaStatus
    global CharaPage
    Sheet_exit = False # キャラシ作成画面を終わるフラグ（未実装）
    # clock = pygame.time.Clock()

    # シートの描画
    pygame.draw.rect(screen, SHEET_COLOR, Rect(30,30,740,360))

    # ページ変更ゾーン
    page_navi = PageNavigation(CharaPage)

    # ステータスの表示
    if CharaPage:
        Name = Status("名前",250, 50, 150, 28,"name","", False)
        Sex = Status("性別(       )",250,80,0,0,"sex","",False,False,False)
        Sex_Button = SexChange(310,80,CharaStatus["sex"])
        Age = Status("年齢",450,80,50,28,"age","",False)
        STR = Status("STR(筋力)  ",250,120,50,28,"STR",Dice_text="3D6")
        CON = Status("CON(体力)  ",250,152,50,28,"CON",Dice_text="3D6")
        SIZ = Status("SIZ(体格)  ",250,184,50,28,"SIZ",Dice_text="2D6+6")
        DEX = Status("DEX(俊敏性)",250,216,50,28,"DEX",Dice_text="3D6")
        APP = Status("APP(外見)  ",500,120,50,28,"APP",Dice_text="3D6")
        EDU = Status("EDU(教育)  ",500,152,50,28,"EDU",Dice_text="3D6+3")
        INT = Status("INT(知性)  ",500,184,50,28,"INT",Dice_text="3D6")
        POW = Status("POW(精神力)",500,216,50,28,"POW",Dice_text="3D6")
        Luck = Status("幸運       ",250,250,50,28,"Luck","",False,False)
        MOV = Status("MOV(移動率)",250,282,50,28,"MOV","",False,False)
        DB = Status("DB(ﾀﾞﾒｰｼﾞ･ﾎﾞｰﾅｽ)",250,314,50,28,"DB","",False,False)
        Durability = Status("耐久力        ",500,250,50,28,"Dura","",False)
        MP = Status("MP(ﾏｼﾞｯｸﾎﾟｲﾝﾄ)",500,282,50,28,"MP","",False)
        SAN = Status("SAN値(正気度) ",500,314,50,28,"SAN","",False)
    else:
        SexChange.Image(CharaStatus["sex"])
        # Profession = Status("職業",250,50,150,28,"")
        
    
    for event in pygame.event.get():
        # マウスクリック時
        if event.type == MOUSEBUTTONDOWN:
            # 左ボタン
            if event.button == 1:
                # １ページ目だったら
                if CharaPage:
                    # 男ボタン
                    if Sex_Button.man_rect.collidepoint(event.pos):
                        CharaStatus["sex"] = True
                    # 女ボタン
                    elif Sex_Button.woman_rect.collidepoint(event.pos):
                        CharaStatus["sex"] = False
                    # 名前のインプットボックス
                    elif Name.Button_rect.collidepoint(event.pos):
                        Name.InputProcess('名前')
                    # 年齢のインプットボックス
                    elif Age.Button_rect.collidepoint(event.pos):
                        Age.InputProcess('年齢')
                    # STRのインプットボックス
                    elif STR.Input_rect.collidepoint(event.pos):
                        STR.InputProcess('筋力')
                    # STRのダイスボタン
                    elif STR.Button_rect.collidepoint(event.pos):
                        STR.DiceProcess()
                    # CONのインプットボックス
                    elif CON.Input_rect.collidepoint(event.pos):
                        CON.InputProcess('体力')
                    # CONのダイスボタン
                    elif CON.Button_rect.collidepoint(event.pos):
                        CON.DiceProcess()
                    # SIZのインプットボックス
                    elif SIZ.Input_rect.collidepoint(event.pos):
                        SIZ.InputProcess('体格')
                    # SIZのダイスボタン
                    elif SIZ.Button_rect.collidepoint(event.pos):
                        SIZ.DiceProcess()
                    # DEXのインプットボックス
                    elif DEX.Input_rect.collidepoint(event.pos):
                        DEX.InputProcess('俊敏性')
                    # DEXのダイスボタン
                    elif DEX.Button_rect.collidepoint(event.pos):
                        DEX.DiceProcess()
                    # APPのインプットボックス
                    elif APP.Input_rect.collidepoint(event.pos):
                        APP.InputProcess('外見')
                    # APPのダイスボタン
                    elif APP.Button_rect.collidepoint(event.pos):
                        APP.DiceProcess()
                    # EDUのインプットボックス
                    elif EDU.Input_rect.collidepoint(event.pos):
                        EDU.InputProcess('教育')
                    # EDUのダイスボタン
                    elif EDU.Button_rect.collidepoint(event.pos):
                        EDU.DiceProcess()
                    # INTのインプットボックス
                    elif INT.Input_rect.collidepoint(event.pos):
                        INT.InputProcess('知性')
                    # INTのダイスボタン
                    elif INT.Button_rect.collidepoint(event.pos):
                        INT.DiceProcess()
                    # POWのインプットボックス
                    elif POW.Input_rect.collidepoint(event.pos):
                        POW.InputProcess('精神力')
                    # POWのダイスボタン
                    elif POW.Button_rect.collidepoint(event.pos):
                        POW.DiceProcess()
                    # POWのインプットボックス
                    elif POW.Input_rect.collidepoint(event.pos):
                        POW.InputProcess('精神力')
                    '''
                    # 耐久力のインプットボックス
                    elif Durability.Input_rect.collidepoint(event.pos):
                        Durability.InputProcess('耐久力')
                    # 正気度のインプットボックス
                    elif SAN.Input_rect.collidepoint(event.pos):
                        SAN.InputProcess('正気度')
                    # MPのインプットボックス
                    elif MP.Input_rect.collidepoint(event.pos):
                        MP.InputProcess('ﾏｼﾞｯｸﾎﾟｲﾝﾄ')
                    '''
                # ページ移動
                elif page_navi.navi_rect.collidepoint(event.pos):
                    CharaPage = False
                else:
                    break
            else:
                # ページ移動
                if page_navi.navi_rect.collidepoint(event.pos):
                    CharaPage = True
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

def DiceFrame():
    pygame.draw.rect(screen, WHITE, Rect(620,420,150,150),3)

def main():
    # 画面の描写
    while True:
        # 画面を黒で塗りつぶす
        screen.fill(BLACK) 

        CharacterSheet()
         
        frame()
        DiceFrame()

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
