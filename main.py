import random, os, json
import pygame
import pygame.draw
from pygame.locals import *
import tkinter as tk
from tkinter import messagebox

from data import *
from fanction_summary import *
from class_summary import *

from title import Title
from load import Load
from save import Save
from opening import Opening
from character_sheet import CharacterSheet

SCENE_FLAG = TITLE
#SCENE_FLAG = PLAY

# tkinterの起動 ---------------------------------------------------
root = tk.Tk()
# 画面中央に配置したい
sw, sh = root.winfo_screenmmwidth(), root.winfo_screenmmheight()
w, h = root.winfo_width(), root.winfo_height()
x = (sw/2) - (w/2)
y = (sh/2) - (h/2)
root.geometry("+%d+%d" % (x,y))
# tkinterの非表示
root.withdraw()

# pygame初期化 -----------------------------------------------
#pygame.init()
# 画面サイズ
#screen = pygame.display.set_mode(DISPLAY_SIZE)
# キーリピート設定
#pygame.key.set_repeat(100, 100)
# タイトルバーキャプション
#pygame.display.set_caption(TITLE_TEXT)

#clock = pygame.time.Clock()

"""
opning_flag = False

# タイトル画面作るよ
def Title(screen):
    global SCENE_FLAG
    global opning_flag

    if opning_flag == False:
        #back_img = PATH + PICTURE + "black.png"
        back_img = PATH + PICTURE + "central-room_north.jpg"
        background = pygame.image.load(back_img).convert_alpha()
        FadeIn(screen, background,2)
        opning_flag = True

    # タイトル
    title_rect = Label(screen, TITLE_TEXT,y=150,font=title_font,color=RED,center_flag=True,background=BLACK)
    start_rect = Label(screen, "はじめる",y=280,font=contents_font,color=WHITE,center_flag=True,background=BLACK)
    load_rect = Label(screen, "つづきから",y=350,font=contents_font,color=WHITE,center_flag=True,background=BLACK)
    setting_rect = Label(screen, "設定",y=420,font=contents_font,color=WHITE,center_flag=True,background=BLACK)
    close_rect = Label(screen, "おわる",y=490,font=contents_font,color=WHITE,center_flag=True,background=BLACK)

    contents_list = [start_rect,load_rect,setting_rect,close_rect]

    # マウスオーバーで枠を表示するよ
    key = pygame.mouse.get_pos()
    for content in contents_list:
        if content.collidepoint(key):
            pygame.draw.rect(screen, WHITE,content,1)

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

def Opening():
    global SCENE_FLAG
    global OpeningFlag

    file_path = PATH + SCENARIO + "Opening.txt"
    with open(file_path,"r",encoding="utf-8_sig") as f:
        txts = f.readlines()
    
    if OpeningFlag < 2:
        TextDraw(screen, txts[OpeningFlag])
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

    # 10個程度の保存領域からどのデータにセーブするか選択できるようにしたい

    # キャラクター名、日時でセーブデータを作る
    file_name = dir_name + CharaStatus["name"] + " " + str_now + ".json"
    data = {}
    data["CharaStatus"] = CharaStatus
    data["flag"] = {"CenterRoomFlag":CenterRoomFlag,
                    "MemoFlag":MemoFlag,
                    "EastRoomFlag":EastRoomFlag,
                    "RoomFlag":RoomFlag,
                    "DirectionFlag":DirectionFlag,
                    "DiscoveryFlag":DiscoveryFlag,
                    "KeyOpenFlag":KeyOpenFlag,
                    "BookFlag":BookFlag,
                    "PoisonFlag":PoisonFlag,
                    "SoupFlag":SoupFlag,
                    "SoupIdeaFlag":SoupIdeaFlag,
                    "GirlFlag":GirlFlag}
    
    with open(file_name,"w",encoding="utf-8_sig") as f:
        json.dump(data,f,indent=2,ensure_ascii=False)

    # キャラシ画面からセーブした際は本編に進む
    if SCENE_FLAG == CHARASE:
        SCENE_FLAG = PLAY

# データロード
def Load():
    global SCENE_FLAG
    global SelectSaveData


    window = DataWindow(screen, SaveFiles)

    for event in pygame.event.get():
        # マウスクリック時
        if event.type == MOUSEBUTTONDOWN:
            # 左ボタン
            if event.button == 1:
                if window.close_rect.collidepoint(event.pos):
                    if SCENE_FLAG == LOAD:
                        SCENE_FLAG = TITLE
                    else:
                        SCENE_FLAG == PLAY

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

# セーブロード画面作るよ
class DataWindow:
    def __init__(self, screen, list):
        self.screen = screen
        self.draw()
        self.list = list
        self.data_set(self.list)

    def draw(self):
        w = 400
        h = 500
        x = (self.screen.get_width() / 2) - (w / 2)
        y = (self.screen.get_height() / 2) - (h / 2)
        self.window_rect = Rect(x,y,w,h)
        pygame.draw.rect(self.screen, SHEET_COLOR,self.window_rect)
        pygame.draw.rect(self.screen, BLACK,self.window_rect,2)

        if SCENE_FLAG == SAVE:
            top_text = "セーブ"
            enter_text = "保存"
        else:
            top_text = "ロード"
            enter_text = "開始"
        self.top_rect = Label(self.screen, top_text, y=80, font=contents_font, center_flag=True)
        self.enter_rect = Label(self.screen, enter_text, 250, 500, contents_font)
        self.close_rect = Label(self.screen, "CLOSE", 480, 500, contents_font)
        self.rect_list = [self.enter_rect,self.close_rect]

        # マウスオーバーで枠を表示するよ
        key = pygame.mouse.get_pos()
        for rect in self.rect_list:
            if rect.collidepoint(key):
                pygame.draw.rect(self.screen, BLACK,rect,1)

    def data_set(self, datas):
        x = (self.screen.get_width() / 2) - 150
        start_y = 150
        y = start_y
        self.data_rect_list = []
        for data in datas:
            if SelectSaveData == data:
                color = WHITE
            else:
                color = SHEET_COLOR
            data_name = data.replace(".json", "")
            self.data_rect_list.append(Label(self.screen, data_name, x, y, background=color))
            y += 30

# キャラクターシート作成画面
def CharacterSheet(screen):
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

        Name = Status(screen,"名前","name","",250, 50, 150, 28,"探索者の名前を入力してください", False)
        Sex = Status(screen,"性別","sex","性別(       )",250,80,0,0,"探索者の性別をクリックで選択してください",False,False,False)
        Sex_Button = SexChange(screen,310,80,CharaStatus["sex"])
        Age = Status(screen,"年齢","age","",430,80,50,28,"探索者の年齢を入力してください",False)
        STR = Status(screen,"筋力","STR","STR(筋力)  ",250,120,40,28,"筋力の値を決めます。\n・3～6:全然筋力がない ・7～10:普通ぐらい\n・11～14:筋力に自身あり ・15～17:筋力を自慢できる\n・18:筋肉モリモリマッチョマン\nテキスト入力とダイスで決定を選択できます。",Dice_text="3D6")
        CON = Status(screen,"体力","CON","CON(体力)  ",250,152,40,28,"体力の値を決めます。\n・3～6:まったく体力ない ・7～10:ほどほど体力はある\n・11～14:それなりに体力がある\n・15～17:スポーツマン並にある ・18:元気100倍\nテキスト入力とダイスで決定を選択できます。",Dice_text="3D6")
        SIZ = Status(screen,"体格","SIZ","SIZ(体格)  ",250,184,40,28,"体格の値を決めます。\n・8～11:小柄 ・12～15:中肉中背 ・16～18:大柄\nテキスト入力とダイスで決定を選択できます。",Dice_text="2D6+6")
        DEX = Status(screen,"俊敏性","DEX","DEX(俊敏性)",250,216,40,28,"俊敏性の値を決めます。\n・3～6:鈍重 ・7～10:問題なく動ける\n・11～14:素早い動作が得意 ・15～17:その道のプロ\n・18:電光石火\nテキスト入力とダイスで決定を選択できます。",Dice_text="3D6")
        APP = Status(screen,"外見","APP","APP(外見)  ",500,120,40,28,"外見の値を決めます。\n・3～6:醜悪な容姿 ・7～10:一般的\n・11～14:整った顔立ち ・15～17:モデル並み\n・18:傾城傾国\nテキスト入力とダイスで決定を選択できます。",Dice_text="3D6")
        EDU = Status(screen,"教育","EDU","EDU(教育)  ",500,152,40,28,"教育の値を決めます。\n・6～8:中学卒業程度 ・9～11:高校卒業\n・12～15:大学卒業 ・16～19:大学院生卒業\n・20～21:研究者や科学者\nテキスト入力とダイスで決定を選択できます。",Dice_text="3D6+3")
        INT = Status(screen,"知性","INT","INT(知性)  ",500,184,40,28,"知力の値を決めます。\n・3～6:頭が悪い ・7～10:普通 ・11～14:発想豊か\n・15～17:頭脳明晰 ・18:英俊豪傑\nテキスト入力とダイスで決定を選択できます。",Dice_text="3D6")
        POW = Status(screen,"精神力","POW","POW(精神力)",500,216,40,28,"精神力の値を決めます。\n・3～6:精神に問題あり ・7～10:人並みの心臓\n・11～14:精神的にタフ ・15～17:修行僧\n・18:黄金の精神\nテキスト入力とダイスで決定を選択できます。",Dice_text="3D6")
        Luck = Status(screen,"幸運","Luck","幸運       ",250,250,40,28,"探索者の幸運度を表します。\n値はPOW x 5で決まります。",False,False)
        Idea = Status(screen,"アイデア","Idea","アイデア   ",250,282,40,28,"アイデアは直感的な能力です。\n特殊な雰囲気など、普通では気がつかないであろう物に\n気付けるかどうかの能力になります\n値はINT x 5で決まります。",False,False)
        Knowledge = Status(screen,"知識","Know","知識       ",250,314,40,28,"探索者が持っている知識量の値です。\n値はEDU x 5で決まります。",False,False)
        Avo = Status(screen,"回避","Avo","回避       ",250,346,40,28,"探索者の回避技能値です。\n値はDEX x 2で決まります。",False,False)
        DB = Status(screen,"ﾀﾞﾒｰｼﾞ･ﾎﾞｰﾅｽ","DB","DB(ﾀﾞﾒｰｼﾞ･ﾎﾞｰﾅｽ)",450,250,50,28,"小柄で筋力が無い人物だと\n与えるダメージにマイナスの補正が掛かります。\n逆に大柄で筋力がある人物では\n与えるダメージにプラスの補正が掛かります。\n値はSTR+SIZで決まります。",False,False)
        HP = Status(screen,"耐久力","HP","耐久力          ",450,282,40,28,"探索者のHPや生命力を表します。\n最大値は(CON+SIZ)÷2で決まります。",False,False)
        MP = Status(screen,"ﾏｼﾞｯｸﾎﾟｲﾝﾄ","MP","MP(ﾏｼﾞｯｸﾎﾟｲﾝﾄ)  ",450,314,40,28,"探索者のマジックポイントを表します。\n最大値はPOWと同じ数値です。",False,False)
        SAN = Status(screen,"正気度","SAN","SAN値(正気度)   ",450,346,40,28,"探索者の正気度を表します。\n最大値はPOW x 5で決まります。",False,False)

        # リストに入れて同じ処理はfor文で回せるようにするよ
        status = [Name,Sex,Age,STR,CON,SIZ,DEX,APP,EDU,INT,POW,
                  Luck,Idea,Knowledge,Avo,DB,HP,MP,SAN]
        
        # マウスオーバーでテキスト表示するよ
        key = pygame.mouse.get_pos()

        for stat in status:
            if stat.Label_rect.collidepoint(key) or stat.Input_rect.collidepoint(key):
                TextDraw(screen, stat.text)
            elif stat.Button_rect.collidepoint(key):
                TextDraw(screen, "ダイスでランダムに値を決めることができます")
    else:
        # ページ変更ゾーン
        page_navi = PageNavigation(LEFT)

        # 職業選択画面
        Profe = Profession(screen, CharaStatus["Profession"])
        # 趣味選択画面
        Hoby = Hobby()
        # キャラ作成終了ボタン
        enter_rect = Button(screen,(530,330,100,100),"キャラ作成\n終了")

        key = pygame.mouse.get_pos()
        if PullDownFlag == False:
            for prof in Profe.prof_list:
                if Profe.prof_list[prof]["rect"].collidepoint(key):
                    TextDraw(screen,f"あなたの職業を選択してください\n【{prof}】")
            if enter_rect.collidepoint(key):
                TextDraw(screen,"キャラクター作成を終了します")
        if Hoby.pull.box_rect.collidepoint(key):
            TextDraw(screen,"あなたの趣味を選択してください")

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
"""

# 部屋を作るよ
class Room:
    def __init__(self, screen):
        self.screen = screen
        # 現在地のファイル名一覧
        self.img_paths = self.file_path()
        # 部屋画像を表示するエリア
        self.area_rect = Rect(0,0,820,375)
        # 部屋画像の表示
        self.room_img, self.room_rect = self.image(self.img_paths["Room"],SHEET_RECT.y,area=self.area_rect,center_flag=True,room_flag=True)
        # 電気が消えているときは暗い画像を表示する
        if LightFlag == False:
            black_img, black_rect = self.image(self.img_paths["LightOff"],SHEET_RECT.y,area=self.area_rect,center_flag=True,room_flag=True)
        # 部屋にあるアイテムの配置
        self.item(self.img_paths)
    
    # ファイル名取得するよ
    def file_path(self):
        paths = {}
        path = PATH + PICTURE
        if RoomFlag == CENTER:
            room_path = path + "central-room_"
            paths["LightOff"] = room_path + "LightOff.png"
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

    # 画像表示するよ
    def image(self, path, y, x=0, size=0.19, area=None, center_flag=False, room_flag=False, line_flag=False):
        # 画像の読み込み＆アルファ化(透明化)
        img = pygame.image.load(path).convert_alpha()
        # 画像の縮小
        img = pygame.transform.rotozoom(img, 0, size)

        # 画像の位置取得
        rect = img.get_rect()
        # 画像の位置を変更する
        if center_flag:
            # 画面中央に置きたい場合
            rect.centerx = self.screen.get_width() / 2
        else:
            rect.centerx += x
        rect.centery += y

        # 部屋のimgの場合はメインsurfaceに、部屋のアイテムは部屋のsurfaceに
        if room_flag:
            self.screen.blit(img, rect, area=area)
            # 枠を描写する場合
            if line_flag:
                if line_flag == True:
                    pygame.draw.rect(self.screen, BLACK, rect, 2)
            return img, rect
        else:
            self.room_img.blit(img, rect, area=area)
            return rect

    # アイテム表示するよ
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

    # アイテムクリックのイベント決めるよ
    def event(self, rect):
        if rect == self.soup_rect:
            img_path = PATH + PICTURE + "soup_" + SoupFlag + ".png"
            y = self.area_rect.y + (self.area_rect / 2)
            img, img_rect = self.image(img_path, y, size=0.5, center_flag=True, line_flag=True)
            
# フェードイン試し用
def FadeIn(screen, clock, background, speed=1):
    alpha = 255
    while alpha >= 0:
        background.set_alpha(alpha)
        screen.fill(BLACK)
        screen.blit(background,(20,20))
        pygame.display.flip()
        alpha -= speed
        clock.tick(60)

# シナリオ表示用
def Scenario(screen):
    text = ""
    room_name = ""
    room_number = str(RoomFlag)
    item_name = ""
    flag_name = ""
    if RoomFlag == CENTER:
        room_name = "_Center_room_"
        if CenterRoomFlag < 5:
            flag_name = str(CenterRoomFlag)
        else:
            pass

    file_name = ScenarioPath + room_number + room_name + item_name + flag_name + ".txt"
    if os.path.isfile(file_name):
        with open(file_name,"r",encoding="utf-8_sig") as f:
            text = f.read()
    TextDraw(screen, text)

# プレイ画面
def MainPlay(screen):
    global RoomFlag
    global CenterRoomFlag
    global EastRoomFlag
    global DirectionFlag
    global DiscoveryFlag
    global AlphaFlag

    #if PlaySceneFlag == 0:
    #    pygame.time.wait(500)

    # 部屋の表示
    room = Room()

    # 文章の表示
    Scenario()

    # ナビゲーションバーの表示
    if RoomFlag == CENTER:
        right_navi = PageNavigation(screen, RIGHT)
        left_navi = PageNavigation(screen,LEFT)
    else:
        under_nave = PageNavigation(screen,UNDER)

    """
    if CenterRoomFlag == 0:
        # フェードイン試し用
        back_img = PATH + PICTURE + "black.png"
        background = pygame.image.load(back_img).convert_alpha()
        FadeIn(screen, background,2)
        CenterRoomFlag += 1
    """

    for event in pygame.event.get():
        # マウスクリック時
        if event.type == MOUSEBUTTONDOWN:
            # 左ボタン
            if event.button == 1:
                if RoomFlag == CENTER:
                    if CenterRoomFlag < 5:
                        CenterRoomFlag += 1
                    else:
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


def main():
    # pygame初期化    
    pygame.init()
    # 画面サイズ
    screen = pygame.display.set_mode(DISPLAY_SIZE)
    # キーリピート設定
    pygame.key.set_repeat(100, 100)
    # タイトルバーキャプション
    pygame.display.set_caption(TITLE_TEXT)

    clock = pygame.time.Clock()

    event_name = "title"
    event_flag = ""

    # 画面の描写
    while True:
        # 画面を黒で塗りつぶす
        screen.fill(BLACK)

        if event_name == "title":
            event_name, event_flag = Title(screen)
        elif event_name == "load":
            event_name = Load(screen, event_flag, SelectSaveData)
        elif event_name == "save":
            event_name = Save(screen, event_flag, SelectSaveData)
        elif event_name == "opening":
            event_name = Opening(screen)
        elif event_name == "charasheet":
            event_name, event_flag = CharacterSheet(screen)

        """
        if SCENE_FLAG == TITLE:
            Title(screen)
        elif SCENE_FLAG == LOAD:
            Load()
        elif SCENE_FLAG == SETTING:
            pass
        elif SCENE_FLAG == ENDCREDITS:
            pass
        else:
            clock = pygame.time.Clock()
            frame()
            DiceFrame()
            if SCENE_FLAG == PLAY:
                MainPlay()
            if SCENE_FLAG == CHARASE:
                CharacterSheet()
            if SCENE_FLAG == OPENING:
                Opening()
            clock.tick(60)

        """
        clock.tick(60)

        # 画面を更新
        pygame.display.update() 


            
if __name__ == "__main__":
    main()
