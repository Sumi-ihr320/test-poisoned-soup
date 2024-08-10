import pygame
import pygame.draw
from pygame.locals import *

from data import *
from fanction_summary import *


# セーブロード画面作るよ
class DataWindow:
    def __init__(self, screen, flag, list):
        # 基本データ
        self.screen = screen
        self.flag = flag
        self.list = list

        # フォントの設定
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)                    # 基本フォント
        self.contents_font = pygame.font.Font(FONT_PATH,CONTENTS_SIZ)        # メニュー用フォント

        # 画面表示       
        self.draw()
        self.data_set(self.list)

    # データ表示ボックスを表示
    def draw(self):
        w = 400
        h = 500
        x = (self.screen.get_width() / 2) - (w / 2)
        y = (self.screen.get_height() / 2) - (h / 2)
        self.window_rect = Rect(x,y,w,h)
        pygame.draw.rect(self.screen, SHEET_COLOR,self.window_rect)
        pygame.draw.rect(self.screen, BLACK,self.window_rect,2)

        if self.flag == "save":
            top_text = "セーブ"
            enter_text = "保存"
        else:
            top_text = "ロード"
            enter_text = "開始"

        self.top_rect = Label(self.screen, self.contents_font, top_text, y=80, center_flag=True)
        self.enter_rect = Label(self.screen, self.contents_font, enter_text, 250, 500)
        self.close_rect = Label(self.screen, self.contents_font, "CLOSE", 480, 500)
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
            self.data_rect_list.append(Label(self.screen, self.font, data_name, x, y, background=color))
            y += 30

# ページ移動用の矢印表示するよ
class PageNavigation:
    def __init__(self, screen, page_flag=0):
        self.screen = screen
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
            navi_x = self.screen.get_width() / 2 - navi_rect.centerx
            navi_y = 350
            triangle = [[380,360],[400,380],[420,360]]

        navi_rect.centerx += navi_x
        navi_rect.centery += navi_y
        self.screen.blit(navi_img, navi_rect)
        # 三角形の描画
        pygame.draw.polygon(self.screen, BLACK,triangle)

        return navi_rect

# プルダウン機能をクラス化できないかな？
class PullDown:
    def __init__(self, screen, font, rect, text, list, pd_h=285):
        self.screen = screen
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
        triangle_rect = Label(self.screen, self.font, "▼", tx, ty, background=WHITE)

        return Rect(x,y,w,h)

    # プルダウンボックスに表示される文字列を描画するよ
    def Label(self, text, rect):
        surface = self.font.render(str(text),True,BLACK)
        rect = surface.get_rect(left=rect[0]+4,top=rect[1]+4)
        self.screen.blit(surface, rect)
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
            self.screen.blit(surface,rect)

            # 項目名とそのrectを辞書に登録していく
            lis_rect = Rect(rect.x,rect.y,w,rect.h)
            self.items[item] = lis_rect

            # 表示位置を下にずらす
            y += rect.h + 1

            # 仕切り線を引く
            pygame.draw.line(self.screen, BLACK,(x-2,y),(x+w-4,y))
            
            # プルダウンボックスより下は隣に表示する
            if y >= (self.pd_rect.y+self.pd_rect.h-rect.h):
                x += x + w
                y = ly
                # 隣にプルダウンボックスを作る
                self.PullDown(Rect(x-3,self.box_rect.y,self.box_rect.w,self.box_rect.h),150)
        lh = y - ly
        self.List_rect = Rect(x,ly,w,lh)
        return 

# ステータス作るよ
class Status:
    def __init__(self, screen, name, status_name, label_name, x, y, w, h, text="",  Button_flag=True, Input_flag=True, Box_flag=True,  Dice_text=""):

        self.screen = screen
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)

        self.name = name    # ステータスの名前
        self.status_name = status_name  # CharaStatusでの名前
        if label_name != "":    # 実際に表示する名前（スペースなどで位置調整する場合があるため）
            self.label_name = label_name
        else:
            self.label_name = self.name
        self.text = text    # 説明文
        self.dice_text = Dice_text  # ダイスボタンに表示するテキスト
        self.Label_rect = Label(self.screen, self.font, self.label_name, x, y)    # ラベル作成
        self.Input_flag = Input_flag    # インプットボタンの入力ができるかのフラグ
        max_flag = False    # 最大値と現在値が存在するフラグ
        if Box_flag:    # インプットボックスを作るかのフラグ
            self.Input_rect = InputBox(screen, (x+self.Label_rect.w,y,w,h), self.Input_flag)
            if status_name != "sex":
                if status_name in CharaStatus:
                    self.status = CharaStatus[status_name]
                    if self.Input_flag:
                        background = WHITE
                    else:
                        background = SHEET_COLOR
                    Label(screen,self.font,str(self.status),self.Input_rect.x+2,self.Input_rect.y+2,background=background)
        else:
            self.Input_rect = self.Label_rect

        if max_flag:
            self.Input2_rect = self.Input_rect

        # ダイスボタンを表示するフラグ
        if Button_flag:
            self.Button_rect = Button(screen, self.font, self.Input_rect, Dice_text)
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
            Label(self.screen, self.font, str(val), self.Input_rect.x+2, self.Input_rect.y+2)
            CharaStatus[self.status_name] = val
            self.AutoCalculation(self.status_name)

    # ダイス処理まとめるよ
    def DiceProcess(self):
        val = DiceRool(self.dice_text)
        CharaStatus[self.status_name] = val
        self.AutoCalculation(self.status_name)
        Label(self.screen, self.font, str(val), self.Input_rect.x+2, self.Input_rect.y+2)

# 選んだ性別によって画像が変わるようにするよ
class SexChange:
    def __init__(self, screen, x, y, flag):
        self.screen = screen
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)
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
        surface = self.font.render(name, True, color, background)
        rect = surface.get_rect(left=x, top=y)
        self.screen.blit(surface, rect)
        return Rect(rect)

    # 画像表示するよ    
    def Image(self,flag):
        if flag:
            img = "silhouette_man.png"
        else:
            img = "silhouette_woman.png"
        img_path = PATH + PICTURE + img
        self.image_rect = Image(self.screen,img_path,0.5,40,40,True,2)

# 職業選択画面作るよ
class Profession:
    def __init__(self, screen, prof):
        self.screen = screen
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)
        self.small_font = pygame.font.Font(FONT_PATH, SMALL_SIZ)

        self.list_image()
        if prof != "":
            self.image(prof)

    def list_image(self):
        x,y = 100,230
        self.prof_list = ProfessionList
        for prof in list(self.prof_list):
            name = self.prof_list[prof]["name"]
            img_path = PATH + PICTURE + "prof_" + name + ".png"
            rect = Image(img_path, 0.1, x, y, line=True, background=True)
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
        rect = Image(self.screen, img_path, 0.35 , x, y, line=True, background=True)
        lrx = rect.x + rect.w + 5
        name_rect = Label(self.screen, self.font, f"【{prof}】", lrx, y)
        skill_x, skill_y = lrx + 10, y + 30
        skill_rect = Label(self.screen, self.small_font, "所持技能： ", skill_x, skill_y)
        sk_x, sk_y = skill_x + 10, skill_y + skill_rect.h + 10
        sx, sy = sk_x, sk_y
        for skill in skill_list:
            rect = Label(self.screen, self.small_font, skill, sx, sy)
            sx += rect.w + 10
            if sx > 530:
                sx = sk_x
                sy += rect.h + 10

# 趣味選択画面作るよ
class Hobby:
    def __init__(self, screen):
        # フォントの設定
        font = pygame.font.Font(FONT_PATH, FONT_SIZ)
        small_font = pygame.font.Font(FONT_PATH, SMALL_SIZ)

        self.label_rect = Label(screen, font, "趣味", 545, 175)
        if PullDownItem == "":
            self.listitem = "未選択"
        else:
            self.listitem = PullDownItem
        self.pull = PullDown(screen, small_font, (435,200,150,25), self.listitem, list(HobbyList), 207)

