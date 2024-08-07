import pygame
import pygame.draw
from pygame.locals import *

from data import *
from fanction import *


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
        triangle_rect = Label("▼",tx,ty,self.font,background=WHITE)

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
                    if self.Input_flag:
                        background = WHITE
                    else:
                        background = SHEET_COLOR
                    Label(str(self.status),self.Input_rect.x+2,self.Input_rect.y+2,background=background)
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
        self.image_rect = Image(img_path,0.5,40,40,True,2)

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
        rect = Image(img_path, 0.35 , x, y, line=True, background=True)
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

