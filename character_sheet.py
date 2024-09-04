import pygame
import pygame.draw
from pygame.locals import *

from data import *
from fanction_summary import *
from class_summary import *

# キャラクターシート作成画面
def CharacterSheet(screen):
    global CharaStatus
    global CharaPage
    global PullDownFlag
    global PullDownItem
    
    # シートの描画
    pygame.draw.rect(screen, SHEET_COLOR, SHEET_RECT)
    font = pygame.font.Font(FONT_PATH, FONT_SIZ)
    
    # ステータスの表示
    if CharaPage:
        # ページ変更ゾーン
        page_navi = PageNavigation(screen, RIGHT)

        Name = Status(screen,"名前","name","",250, 50, 150, 28,"探索者の名前を入力してください", False)
        Sex = Status(screen,"性別","sex","性別(       )",250,80,0,0,"探索者の性別をクリックで選択してください", False, False, False)
        Sex_Button = SexChange(screen,310,80,CharaStatus["sex"])
        Age = Status(screen,"年齢","age","",430,80,50,28,"探索者の年齢を入力してください", False)
        STR = Status(screen,"筋力","STR","STR(筋力)  ",250,120,40,28,"筋力の値を決めます。\n・3～6:全然筋力がない ・7～10:普通ぐらい\n・11～14:筋力に自身あり ・15～17:筋力を自慢できる\n・18:筋肉モリモリマッチョマン\nテキスト入力とダイスで決定を選択できます。",dice_text="3D6")
        CON = Status(screen,"体力","CON","CON(体力)  ",250,152,40,28,"体力の値を決めます。\n・3～6:まったく体力ない ・7～10:ほどほど体力はある\n・11～14:それなりに体力がある\n・15～17:スポーツマン並にある ・18:元気100倍\nテキスト入力とダイスで決定を選択できます。",dice_text="3D6")
        SIZ = Status(screen,"体格","SIZ","SIZ(体格)  ",250,184,40,28,"体格の値を決めます。\n・8～11:小柄 ・12～15:中肉中背 ・16～18:大柄\nテキスト入力とダイスで決定を選択できます。",dice_text="2D6+6")
        DEX = Status(screen,"俊敏性","DEX","DEX(俊敏性)",250,216,40,28,"俊敏性の値を決めます。\n・3～6:鈍重 ・7～10:問題なく動ける\n・11～14:素早い動作が得意 ・15～17:その道のプロ\n・18:電光石火\nテキスト入力とダイスで決定を選択できます。",dice_text="3D6")
        APP = Status(screen,"外見","APP","APP(外見)  ",500,120,40,28,"外見の値を決めます。\n・3～6:醜悪な容姿 ・7～10:一般的\n・11～14:整った顔立ち ・15～17:モデル並み\n・18:傾城傾国\nテキスト入力とダイスで決定を選択できます。",dice_text="3D6")
        EDU = Status(screen,"教育","EDU","EDU(教育)  ",500,152,40,28,"教育の値を決めます。\n・6～8:中学卒業程度 ・9～11:高校卒業\n・12～15:大学卒業 ・16～19:大学院生卒業\n・20～21:研究者や科学者\nテキスト入力とダイスで決定を選択できます。",dice_text="3D6+3")
        INT = Status(screen,"知性","INT","INT(知性)  ",500,184,40,28,"知力の値を決めます。\n・3～6:頭が悪い ・7～10:普通 ・11～14:発想豊か\n・15～17:頭脳明晰 ・18:英俊豪傑\nテキスト入力とダイスで決定を選択できます。",dice_text="3D6")
        POW = Status(screen,"精神力","POW","POW(精神力)",500,216,40,28,"精神力の値を決めます。\n・3～6:精神に問題あり ・7～10:人並みの心臓\n・11～14:精神的にタフ ・15～17:修行僧\n・18:黄金の精神\nテキスト入力とダイスで決定を選択できます。",dice_text="3D6")
        Luck = Status(screen,"幸運","Luck","幸運       ",250,250,40,28,"探索者の幸運度を表します。\n値はPOW x 5で決まります。",False, False)
        Idea = Status(screen,"アイデア","Idea","アイデア   ",250,282,40,28,"アイデアは直感的な能力です。\n特殊な雰囲気など、普通では気がつかないであろう物に\n気付けるかどうかの能力になります\n値はINT x 5で決まります。", False, False)
        Knowledge = Status(screen,"知識","Know","知識       ",250,314,40,28,"探索者が持っている知識量の値です。\n値はEDU x 5で決まります。",False, False)
        Avo = Status(screen,"回避","Avo","回避       ",250,346,40,28,"探索者の回避技能値です。\n値はDEX x 2で決まります。",False, False)
        DB = Status(screen,"ﾀﾞﾒｰｼﾞ･ﾎﾞｰﾅｽ","DB","DB(ﾀﾞﾒｰｼﾞ･ﾎﾞｰﾅｽ)",450,250,50,28,"小柄で筋力が無い人物だと\n与えるダメージにマイナスの補正が掛かります。\n逆に大柄で筋力がある人物では\n与えるダメージにプラスの補正が掛かります。\n値はSTR+SIZで決まります。", False, False)
        HP = Status(screen,"耐久力","HP","耐久力          ",450,282,40,28,"探索者のHPや生命力を表します。\n最大値は(CON+SIZ)÷2で決まります。",False, False)
        MP = Status(screen,"ﾏｼﾞｯｸﾎﾟｲﾝﾄ","MP","MP(ﾏｼﾞｯｸﾎﾟｲﾝﾄ)  ",450,314,40,28,"探索者のマジックポイントを表します。\n最大値はPOWと同じ数値です。",False, False)
        SAN = Status(screen,"正気度","SAN","SAN値(正気度)   ",450,346,40,28,"探索者の正気度を表します。\n最大値はPOW x 5で決まります。",False, False)

        # リストに入れて同じ処理はfor文で回せるようにするよ
        status = [Name, Sex, Age, STR, CON, SIZ, DEX, APP, EDU, INT, POW,
                  Luck, Idea, Knowledge, Avo, DB, HP, MP, SAN]
        
        # マウスオーバーでテキスト表示するよ
        key = pygame.mouse.get_pos()

        for stat in status:
            if stat.label.rect.collidepoint(key):
                TextDraw(screen, stat.text)
            elif stat.input:
                if stat.input.rect.collidepoint(key):
                    TextDraw(screen, stat.text)
            elif stat.button:
                if stat.button.collidepoint(key):
                    TextDraw(screen, "ダイスでランダムに値を決めることができます")
    else:
        # ページ変更ゾーン
        page_navi = PageNavigation(screen, LEFT)

        # 職業選択画面
        Profe = Profession(screen, CharaStatus["Profession"])
        # 趣味選択画面
        Hoby = Hobby(screen)

        # キャラ作成終了ボタン
        end_button = Button(screen, font, (530,330,100,100), "キャラ作成\n終了")

        key = pygame.mouse.get_pos()
        if PullDownFlag == False:
            for prof in Profe.prof_list:
                if Profe.prof_list[prof]["rect"].collidepoint(key):
                    TextDraw(screen, f"あなたの職業を選択してください\n【{prof}】")
            if end_button.rect.collidepoint(key):
                TextDraw(screen,"キャラクター作成を終了します")
        if Hoby.pull.box_rect.collidepoint(key):
            TextDraw(screen, "あなたの趣味を選択してください")

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
                            if stat.input:
                                if stat.input.rect.collidepoint(event.pos):
                                    if stat.input_flag:
                                        stat.InputProcess()
                            # ダイスボタン
                            elif stat.button:
                                if stat.button.rect.collidepoint(event.pos):
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
                            if Hoby.pull.items[item][1].collidepoint(event.pos):
                                PullDownItem = item
                                PullDownFlag = False
                        PullDownFlag = False

                    elif end_button.rect.collidepoint(event.pos):
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
    return "charasheet", ""

class CharacterSheet:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)

        self.draw_sheet()        
        self.draw_frame()

        self.page_navi = None   # 初期化
        self.sex_button = None
        self.status_items = []  # ステータスのアイテム一覧

    # jsonファイルを取ってくる
    def call_data(self):
        file_path = f"{PATH}{JSON_FOLDER}Status.json"
        return load_json(file_path)

    # キャラステータス作成画面を作る
    def create_status_page(self):
        # ナビゲーションバーを作る
        self.page_navi = PageNavigation(self.screen, RIGHT)

        status_json = self.call_data()
        for status in status_json:            
            item = Status(self.screen, status["name"], status, status["view_name"],
                          status["x"], status["y"], status["w"], status["h"], status["text"],
                          status["button_flag"], status["input_flag"], status["box_flag"], status["dice_text"])
            self.status_items.append(item)
            if status == "sex":
                self.sex_button = SexChange(self.screen, 310, 80, CharaStatus["sex"])

    # シートの描画
    def draw_sheet(self):
        pygame.draw.rect(self.screen, SHEET_COLOR, SHEET_RECT)
        
    # テキストフレームの表示
    def draw_frame(self):
        create_frame(self.screen)

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
        return "save", "play"
    