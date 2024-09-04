
import random

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
        self.navi_rect = self.draw(page_flag)

    # 画像表示
    def draw(self, page_flag):
        img = f"{PATH}{PICTURE}navigate.png"
        navi_img = pygame.image.load(img).convert_alpha()
        if page_flag == UNDER:
            navi_img = pygame.transform.rotate(navi_img, 90)
            navi_img = pygame.transform.scale(navi_img, (500,40))
        else:
            navi_img = pygame.transform.scale(navi_img, (40,355))
        navi_rect = navi_img.get_rect()
        if page_flag == RIGHT: # 右側のナビゲーション
            navi_x, navi_y = 740, 40
            triangle = [[750,190],[770,210],[750,230]]
        elif page_flag == LEFT: # 左側のナビゲーション
            navi_x, navi_y = 20, 40
            triangle = [[50,190],[30,210],[50,230]]
        else:   # 下側のナビゲーション
            navi_x = self.screen.get_width() / 2 - navi_rect.centerx
            navi_y = 350
            triangle = [[380,360],[400,380],[420,360]]

        # ナビゲーションの表示
        navi_rect.centerx += navi_x
        navi_rect.centery += navi_y
        self.screen.blit(navi_img, navi_rect)

        # 三角形の描画
        pygame.draw.polygon(self.screen, BLACK, triangle)

        return navi_rect

# ラベル作成をクラス化するよ    (chatGPT指南)
class Label:
    def __init__(self, screen, font, text, x=0, y=0, color=BLACK, center_flag=False, background=SHEET_COLOR):
        self.screen = screen
        self.font = font
        self.text = text
        self.color = color
        self.background = background
        self.rect = self.create_label(x, y, center_flag)

    # ラベルを作る
    def create_label(self, x, y, center_flag):
        surface = self.font.render(self.text, True, self.color, self.background)
        rect = surface.get_rect(left=x, top=y)
        if center_flag:
            rect.centerx = DISPLAY_SIZE[0] / 2
        self.screen.blit(surface, rect)
        return rect

    # ラベルを描画する
    def draw(self):
        # 必要に応じて再描画をできる
        surface = self.font.render(self.text, True, self.color, self.background)
        self.screen.blit(surface, self.rect)

    # 指定した点が描画内かをチェック
    def collidepoint(self, pos):
        return self.rect.collidepoint(pos)

# ボタン作成をクラス化 やってみた     (chatGPT修正)
class Button:
    def __init__(self, screen, font, rect, text, on_click=None):
        self.screen = screen
        self.font = font
        self.texts = text.splitlines()

        self.x = rect[0] + rect[2] + 5
        self.y = rect[1] -2

        # 色情報
        self.out_color = GRAY
        self.in_color = (181,181,174)
        self.on_color = BLUE
        self.text_color = BLACK

        # ボタンの幅高さ
        self.bw = 0
        self.bh = 0
        # ボタンのrect
        self.rect = None

        # テキスト表示用
        self.surfaces = []
        self.rects = []

        self.create_button()

        # コールバック関数
        self.on_click = on_click

    def create_button(self):
        self.create_text()
        self.draw_button()
        self.draw_text()

    # テキストの作成
    def create_text(self):
        tx,ty = 0, self.y
        for txt in self.texts:
            surface = self.font.render(txt, True, self.text_color)
            w = surface.get_rect().w + 8
            if self.bw < w:
                self.bw = w
            h = surface.get_rect().h + 8
            self.bh += h
            tx = self.x + int(self.bw / 2)
            ty += int(h / 2)
            text_rect = surface.get_rect(center=(tx,ty))
            ty += int(h / 2)
            self.surfaces.append(surface)
            self.rects.append(text_rect)

    # ボタンの描画
    def draw_button(self, hover=False):
        pygame.draw.rect(self.screen, self.out_color, (self.x, self.y, self.bw, self.bh))
        if hover:
            pygame.draw.rect(self.screen, self.on_color, (self.x, self.y, self.bw, self.bh))
        pygame.draw.line(self.screen, self.in_color, (self.x, self.y), (self.x+self.bw, self.y+self.bh))
        pygame.draw.line(self.screen, self.in_color, (self.x, self.y+self.bh), (self.x+self.bw, self.y))
        pygame.draw.rect(self.screen, self.in_color,(self.x+4, self.y+4, self.bw-8, self.bh-8))
        self.rect = Rect(self.x, self.y, self.bw, self.bh)

    # テキストの描画
    def draw_text(self):
        for i in range(len(self.surfaces)):
            self.screen.blit(self.surfaces[i], self.rects[i])
    
    # クリックされたときTrueを返す
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos) if self.rect else False

    # 更新
    def update(self, pos, click):
        hover = self.is_clicked(pos)
        self.draw_button(hover)
        if hover and click:
            if self.on_click:
                self.on_click() # コールバック関数を呼び出す

# インプットボックスをクラス化するよ
class InputBox:
    def __init__(self, screen, rect, input_flag=True, line_bold=2):
        self.screen = screen
        # ボックスのカラーの設定
        self.color = WHITE if input_flag else SHEET_COLOR
        self.x = rect[0] + 5
        self.y = rect[1] - 4
        self.w, self.h = rect[2], rect[3]
        self.rect = Rect(self.x, self.y, self.w, self.h)
        self.line_bold = line_bold
        
        self.draw_box()
    
    # ボックスの描画
    def draw_box(self):
        # 入力ボックス
        pygame.draw.rect(self.screen, self.color, self.rect)
        # 下線
        pygame.draw.line(self.screen, BLACK, (self.x, self.y+self.h-1), (self.x+self.w-1, self.y+self.h-1),
                         self.line_bold)

# 画像表示をクラス化するよ
class Image:
    def __init__(self, screen, path, size, x, y, line_flag=False, line_width=1, bg_flag=False):
        self.screen = screen

        self.img, self.rect = self.create_image(path, size)
        self.set_rect(x, y)
        self.view_image(bg_flag, line_flag, line_width)

    # イメージを作成するよ
    def create_image(self, path, size):
        # 画像の読み込み＆アルファ化(透明化)
        img = pygame.image.load(path).convert_alpha()
        # 画像の縮小
        img = pygame.transform.rotozoom(img, 0, size)
        # 画像の位置取得
        rect = img.get_rect()
        return img, rect
        
    # 配置をセットするよ
    def set_rect(self, x, y):
        # 位置を変更する
        if x == "center":
            self.rect.centerx = self.screen.get_width() // 2 
        else:
            self.rect.centerx += x
        if y == "center":
            self.rect.centery = self.screen.get_height() // 2
        else:
            self.rect.centery += y

    # 画像を表示するよ
    def view_image(self, bg_flag, line_flag, line_width):
        # 背景を白にする場合
        if bg_flag:
            pygame.draw.rect(self.screen, WHITE, self.rect)

        # 画像の描写
        self.screen.blit(self.img, self.rect)

        # 画像の枠を描画する場合
        if line_flag:
            pygame.draw.rect(self.screen, BLACK, self.rect, line_width)
 
# プルダウン機能をクラス化できないかな？
class PullDown:
    def __init__(self, screen, font, rect, text, list, pd_h=285):
        self.screen = screen
        self.font = font

        self.box_rect = self.create_box(rect)
        # プルダウンボックスに最初に表示される文字を表示するよ
        self.label = Label(self.screen, self.font, str(text), rect[0]+4, rect[1]+4)
        self.list = list

        # プルダウンボックスのアイテムの位置のリスト{item:rect}
        self.items = {}
        self.pd_h = pd_h
        self.list_box = None

        if PullDownFlag:
            self.create_pulldown_list()

    # ボックス作るよ
    def create_box(self,rect):
        x = rect[0] + 5
        y, w, h = rect[1], rect[2], rect[3]
        Box(x, y, w, h)

        # 三角作るよ
        tx = x + w -25
        ty = y + 3
        triangle = Label(self.screen, self.font, "▼", tx, ty, background=WHITE)
        return Rect(x,y,w,h)
    
    # プルダウン押した時に表示される項目表示したいよ
    def create_pulldown_list(self):
        x = self.box_rect.x + 3
        y = self.box_rect.y + self.box_rect.h + 3
        self.draw_list(self.list, x, y)

    # リストを表示する
    def draw_list(self, list, x, y):
        w = self.box_rect.w
        ly = y
        lis_rect = None
        for item in list:
            # 項目作成
            surface = self.font.render(item, True, BLACK)
            rect = surface.get_rect(left=x,top=y)

            # 項目名とそのsurface, rectを辞書に登録していく
            lis_rect = Rect(rect.x, rect.y, w, rect.h)
            self.items = {item: (surface, lis_rect)}

            # 表示位置を下にずらす
            y += rect.h + 1
            
            # プルダウンボックスより下は隣に表示する
            if y >= (ly + self.pd_h):
                x += x + w
                y = ly
        lh = y - ly

        # リストボックスを作って文字を表示する
        self.list_box = Box(self.screen, x, ly, w, lh)
        for item in self.items:
            self.screen.blit(self.items[item][0], self.items[item][1])

# ダイスロールをクラス化するよ（画像表示はやめとこうかなって悩んでるよ）
class DiceRoll:
    def __init__(self, dice_text):
        self.text = dice_text

        # 個数、何面、プラスαのアイテム
        self.pieces, self.dice, self.plus_item = dice_confirmation(self.text)
        # 計算結果
        self.val = self.dice_roll()
    
    # ダイスロールの計算
    def dice_roll(self):
        val = 0
        # ランダムで数字を出して個数分＋する
        for _ in range(self.pieces):
            val += random.randint(1, self.dice)
        
        # プラスα文字列があった場合は計算する
        if self.plus_item:
            index = self.plus_item.end() + 1
            item_num = int(self.text[index])
            val = val + item_num if self.plus_item.group() == "+" else val - item_num
        return val

# ステータス作るよ
class Status:
    def __init__(self, screen, name, status_name, label_name, x, y, w, h, text="", button_flag=True, input_flag=True, box_flag=True, dice_text=""):
        self.screen = screen
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)

        self.name = name                # ステータスの名前
        self.status_name = status_name  # CharaStatusでの名前
        self.label_name = label_name if label_name != "" else self.name     # 実際に表示する名前（スペースなどで位置調整する場合があるため）
        self.text = text                # 説明文
        self.dice_text = dice_text      # ダイスボタンに表示するテキスト
        self.label = Label(self.screen, self.font, self.label_name, x, y)    # ラベル作成

        self.input = None   # 初期化
        self.input_flag = input_flag
        if box_flag:    # インプットボックスを作るかのフラグ
            self.create_input(x, y, w, h, input_flag)

        self.button = None  # 初期化
        if button_flag: # ダイスボタンを作るかのフラグ
            self.create_dice_button()

    # インプットボックスを作成
    def create_input(self, x, y, w, h, input_flag):
        self.input = InputBox(self.screen, (x+self.label.rect.w, y, w, h), input_flag)
        if self.status_name != "sex" and self.status_name in CharaStatus:
            self.status = CharaStatus[self.status_name]
            bg = WHITE if input_flag else SHEET_COLOR
            stat_label = Label(self.screen,self.font, str(self.status), self.input.rect.x+2, self.input.rect.y+2, background=bg)

    # ダイスボタンを作成
    def create_dice_button(self):
        rect = self.input.rect if self.input else self.label.rect
        self.button = Button(self.screen, self.font, rect, self.dice_text)
    
    # ステータスの自動計算
    def AutoCalculation(self, name):
        if name == "STR" or name == "SIZ" or name == "CON":
            if name != "CON":
                # ダメージボーナスの計算
                st = CharaStatus["STR"] + CharaStatus["SIZ"]
                if 2 <= st <= 12:       val = "-1D6"
                elif 13 <= st <= 16:    val = "-1D4"
                elif 25 <= st <= 32:    val = "+1D4"
                elif 33 <= st <= 40:    val = "+1D6"
                else:                   val = "0"
                CharaStatus["DB"] = val

            if name != "STR":
                # HPの計算
                CharaStatus["HP"] = (CharaStatus["CON"] + CharaStatus["SIZ"]) // 2

        elif name == "POW":
            # MP、幸運、SAN値の計算
            CharaStatus["MP"] = CharaStatus["POW"]
            val = CharaStatus["POW"] * 5
            CharaStatus["Luck"] = val
            CharaStatus["SAN"] = val

        elif name == "INT":
            # アイデアの計算
            CharaStatus["Idea"] = CharaStatus["INT"] * 5

        elif name == "EDU":
            # 知識の計算
            val = CharaStatus["EDU"] * 5
            CharaStatus["Know"] = val if val < 99 else 99
        
        elif name == "DEX":
           # 回避の計算
           CharaStatus["Avo"] = CharaStatus["DEX"] * 2
 
    # 入力ボックスの処理まとめるよ
    def InputProcess(self):
        min, max = 0, 99
        # 最大値最小値を決めるよ
        if self.status_name == "age":
            min = CharaStatus["EDU"] + 6
        elif self.dice_text != "":
            pieces, dice, plus_item = dice_confirmation(self.dice_text)
            min, max = pieces, dice * pieces
            if plus_item:
                num = int(self.dice_text[-1])
                if plus_item.group() == "+":
                    min += num
                    max += num
                else:
                    min -= num
                    max -= num
        val = InputGet(self.status_name, self.name, f"あなたの{self.name}を入力してください", min, max)
        if val != None:
            label = Label(self.screen, self.font, f"{val}", self.input.rect.x+2, self.input.rect.y+2)
            CharaStatus[self.status_name] = val
            self.AutoCalculation(self.status_name)

    # ダイス処理まとめるよ
    def DiceProcess(self):
        dice = DiceRoll(self.dice_text)
        CharaStatus[self.status_name] = dice.val
        self.AutoCalculation(self.status_name)
        Label(self.screen, self.font, str(dice.val), self.input.rect.x+2, self.input.rect.y+2)

# 選んだ性別によって画像が変わるようにするよ
class SexChange:
    def __init__(self, screen, x, y, flag):
        self.screen = screen
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)

        # flag が True なら男、False なら女
        woman_flag = False if flag else True

        self.man_rect = self.create_butoon(x, y, flag)
        self.woman_rect = self.create_butoon(x+40, y, woman_flag)

        self.image = None   # 初期化
        self.view_image(flag)

    # ボタン作るよ
    def create_butoon(self, x, y, flag):
        push_color = (106,93,33)
        no_push_color = SHEET_COLOR
        
        # テキストと背景色と文字色をフラグによって変える
        text = "男" if flag else "女"
        background = push_color if flag else no_push_color
        color = WHITE if flag else BLACK
        
        return text_view(self.screen, self.font, text, color, background, x, y)

    # 画像表示するよ    
    def view_image(self,flag):
        sex = "man" if flag else "woman"
        img_path = f"{PATH}{PICTURE}silhouette_{sex}.png"
        self.image = Image(self.screen, img_path, 0.5, 40, 40, line_flag=True, line_width=2)

# 職業選択画面作るよ
class Profession:
    def __init__(self, screen, prof):
        self.screen = screen
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)
        self.small_font = pygame.font.Font(FONT_PATH, SMALL_SIZ)

        self.list_image()
        if prof != "":
            self.view_image(prof)

    # 一覧の表示
    def list_image(self):
        x, y = 100, 230
        self.prof_list = ProfessionList
        for prof in list(self.prof_list):
            name = self.prof_list[prof]["name"]
            img_path = f"{PATH}{PICTURE}prof_{name}.png"
            img = Image(self.screen, img_path, 0.1, x, y, line_flag=True, bg_flag=True)
            self.prof_list[prof]["rect"] = img.rect
            x += 55
            if x >= 590:
                y += 55
                x = 100

    # 選択された職業を表示
    def view_image(self, prof):
        data = self.prof_list[prof]
        name = data["name"]
        skill_list = data["skill"]
        img_path = f"{PATH}{PICTURE}prof_{name}.png"
        x, y = 100, 40

        # 画像インスタンス
        img = Image(self.screen, img_path, 0.35 , x, y, line_flag=True, bg_flag=True)
        lrx = img.rect.x + img.rect.w + 5
        # ラベルインスタンス
        lbl_name = Label(self.screen, self.font, f"【{prof}】", lrx, y)
        skill_x, skill_y = lrx + 10, y + 30
        lbl_skill = Label(self.screen, self.small_font, "所持技能： ", skill_x, skill_y)
        sk_x, sk_y = skill_x + 10, skill_y + lbl_skill.rect.h + 10
        sx, sy = sk_x, sk_y
        for skill in skill_list:
            skill_label = Label(self.screen, self.small_font, skill, sx, sy)
            sx += skill_label.rect.w + 10
            if sx > 530:
                sx = sk_x
                sy += skill_label.rect.h + 10

# 趣味選択画面作るよ
class Hobby:
    def __init__(self, screen):
        # フォントの設定
        font = pygame.font.Font(FONT_PATH, FONT_SIZ)
        small_font = pygame.font.Font(FONT_PATH, SMALL_SIZ)

        self.label = Label(screen, font, "趣味", 545, 175)
        if PullDownItem == "":
            self.listitem = "未選択"
        else:
            self.listitem = PullDownItem
        self.pull = PullDown(screen, small_font, (435,200,150,25), self.listitem, list(HobbyList), 207)

