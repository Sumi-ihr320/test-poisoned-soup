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

SHEET_COLOR = (189,183,107)

# パスの指定
PATH = os.path.dirname(__file__)
SCENARIO = "/Scenario/"
PICTURE ="/Picture/"
MUSIC = "/Music/"

FONT_PATH = os.path.join(PATH,"HGRKK.TTC")
# FONT_NAME = "hgskyokashotai"
FONT_SIZ = 22
SKILL_SIZ = 18
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
               "DB":"", "MP":0, "SAN":0,
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
PullDownFlag = False # プルダウン表示フラグ
PullDown2Flag = False

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
        #self.x = x
        #self.y = y
        self.text = text
        self.status_name = status_name
        self.dice_text = Dice_text
        self.Label_rect = Label(name,x,y)
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
        self.InputLabel(str(val))

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
    def __init__(self, name, x, y, w, h):
        self.Name = name
        self.Label_rect = Label(name,x,y)
        self.PullDown_rect = self.PullDownBox((x+self.Label_rect.w+5,y-4,w,h))
        self.Box_text = self.BoxLabel(CharaStatus["Profession1"],self.PullDown_rect)
        self.PullDown2_rect = self.PullDownBox((self.PullDown_rect.x + self.PullDown_rect.w+5,y-4,w,h))
        if CharaStatus["Profession2"] != "":
            self.Box2_text = self.BoxLabel(CharaStatus["Profession2"],self.PullDown2_rect)

    # プルダウンボックス作るよ
    def PullDownBox(self, rect):
        x = rect[0] + 5
        y = rect[1]
        w = rect[2]
        h = rect[3]
        pygame.draw.rect(screen,GRAY,(x,y,w,h))
        pygame.draw.rect(screen, WHITE, (x+1, y+1, w-2, h-2))

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
def PullDown(rect):
    x = rect[0]
    y = rect[1] + rect[3]
    w = rect[2]
    h = rect[3] + 200
    pygame.draw.rect(screen,GRAY,(x,y,w,h))
    pygame.draw.rect(screen, WHITE, (x+1, y+1, w-2, h-2))



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
        Profe = Profession("職業",70,50,300,32)
        Skill_rect = Label("技能",70,90)
        pygame.draw.line(screen,BLACK,(120,100),(750,100),2)

        # 文字サイズを小さくする
        skill_font = pygame.font.Font(FONT_PATH,SKILL_SIZ)
        # 技能一覧を描写する
        for skill in SkillList:
            pass

        # プルダウンどうやったら表示される？
        if PullDownFlag:
            PullDown(Profe.PullDown_rect)
        if PullDown2Flag:
            PullDown(Profe.PullDown2_rect)

    
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
                else:
                    # ページ移動
                    if page_navi.navi_rect.collidepoint(event.pos):
                        CharaPage = True

                    # プルダウン表示うまくいってません
                    if Profe.PullDown_rect.collidepoint(event.pos):
                        if PullDownFlag:
                            PullDownFlag = False
                        else:
                            PullDownFlag == True
                    if Profe.PullDown2_rect.collidepoint(event.pos):
                        if PullDownFlag:
                            PullDownFlag = False
                        else:
                            PullDownFlag == True
            
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
