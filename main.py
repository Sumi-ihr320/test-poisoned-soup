import sys, random
import pygame
from pygame.locals import *
import tkinter as tk
from tkinter import messagebox


DISPLAY_SIZE = (800, 600)
BLACK = (0,0,0)
WHITE = (255,255,255)
SHEET_COLOR = (189,183,107)
PATH = "c:\poisoned-soup"
SCENARIO = "\Scenario"
PICTURE ="\Picture"
MUSIC = "\Music"
FONT_NAME = "hgskyokashotai"
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
font = pygame.font.SysFont(FONT_NAME, FONT_SIZ)

COLOR_ACTIVE = pygame.Color('dodgerblue2')
COLOR_INACTIVE = pygame.Color('lightskyblue3')

''' # フォントリスト取得
font_list = []
for x in pygame.font.get_fonts():
    font_list.append(x)
# たまに空の要素が含まれるので、削除しておく
font_list = [s for s in font_list if s != ""]
# リスト初期位置 ここの数字を変えると途中からプレビュー見れる
i = 0
'''

# ファイルの読み込み
#f = open(PATH + SCENARIO + '\CharacterSheet_01.txt', 'r', encoding='UTF-8')
#Parameter_list = f.read()
#f.close

class Button:
    def __init__(self, x, y, w, h, text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (200,200,200)
        self.text = text
        self.txt_surface = font.render(text, True, self.color)
        self.active = False

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 0)
        self.txt_surface = font.render(self.text, True, BLACK)
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y +5))
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False

    def onClick(self):
        r = self.active
        self.active = False
        return r
    
class InputBox:
    def __init__(self, x, y, w, h, text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = font.render(text, True, self.color)
        self.active = False
    
    def handle_event(self, event):
        r = ""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    r = self.text
                    self.text = ""
                elif event.key == pygame.K_DELETE:
                    pass
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = font.render(self.text, True, self.color)
        return r
    
    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width
    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

def Opening():
    pass

def Label(name, color, x, y):
    title = name
    surface = font.render(title, True, color)
    rect = surface.get_rect(left=x, top=y)
    screen.blit(surface, rect)

def sexButton(name, x, y, flag):
    push_color = (106,93,33)
    no_push_color = SHEET_COLOR
    if flag:
        background = push_color
        color = WHITE
    else:
        background = no_push_color
        color = BLACK
    title = name
    surface = font.render(title, True, color, background)
    rect = surface.get_rect(left=x, top=y)
    screen.blit(surface, rect)  
    
    
    
def CharacterSheet():
    SexFlag = True
    clock = pygame.time.Clock()
    # シートの描画
    pygame.draw.rect(screen, SHEET_COLOR, Rect(30,30,740,360))
    Label("名前",BLACK,250,50)
    Label("性別(       )",BLACK,250,80)
    sexButton("男",310,80,SexFlag)
    sexButton("女",350,80,SexFlag)
    Label("年齢",BLACK,450,80)
    Label("STR(筋力)",BLACK,250,120)
    Label("CON(体力)",BLACK,250,150)
    Label("SIZ(体格)",BLACK,250,180)
    Label("DEX(俊敏性)",BLACK,250,210)
    Label("APP(外見)",BLACK,450,120)
    Label("EDU(教育)",BLACK,450,150)
    Label("INT(知性)",BLACK,450,180)
    Label("POW(精神力)",BLACK,450,210)
    Label("幸運",BLACK,250,250)
    Label("耐久力",BLACK,250,280)
    Label("MOV(移動率)",BLACK,250,310)
    Label("DB(ダメージ・ボーナス)",BLACK,450,250)
    Label("MP(マジックポイント)",BLACK,450,280)
    Label("SAN値(正気度)",BLACK,450,310)
    

    '''
    input_box_name = InputBox(280, 100, 140, 32)
    button_name = Button(280, 140, 140, 32, "名前")
    input_boxes = [input_box_name]
    buttons = [button_name]

    exit_sw = False
    while not exit_sw:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_sw = True
            for n, box in enumerate(input_boxes):
                r = box.handle_event(event)
                if r != "":
                    buttons[n].text = r
            for box in input_boxes:
                box.update()
            for b in buttons:
                b.handle_event(event)
            for b in buttons:
                b.update()
        for box in input_boxes:
            box.draw(screen)
        for b in buttons:
            b.draw(screen)
        for b in buttons:
            if b.onClick():
                print(b.text+ " hit")
        pygame.display.flip()
        clock.tick(30)
        '''

    # プレイヤー画像の読み込み
    if SexFlag == True:
        player = pygame.image.load(PATH + PICTURE + "\silhouette_man.png")
    else:
        player = pygame.image.load(PATH + PICTURE + "\silhouette_woman.png")
    # 画像のアルファ化(透明化)
    player.convert_alpha()
    # 画像の縮小
    player = pygame.transform.rotozoom(player, 0, 0.5)
    # 画像の位置取得
    rect_player = player.get_rect()
    #画像の位置を変更する
    rect_player.centerx += 40
    rect_player.centery += 40
    
    print(rect_player)

    # 画像の描写
    screen.blit(player, rect_player)

    # プレイヤー画像の枠の描画
    pygame.draw.rect(screen, BLACK, rect_player, 2)


def frame():
    pygame.draw.rect(screen, WHITE, Rect(30,420,740,150),3)

def main():
    # 画面の描写
    while True:
        # 画面を黒で塗りつぶす
        screen.fill(BLACK) 

        ''' フォントリスト確認用
        try:
            global i

            # フォント設定
            font = pygame.font.SysFont(font_list[i], 30)

            # 表示文字設定
            name = font.render("{}".format(font_list[i]) + "(" + str(i+1) + "/" + str(len(font_list)+1) + ")", True, WHITE)
            numb = font.render("1234567890", True, WHITE)
            asci = font.render("ABCDEFGHIJKLMNOPQRSTUVWXYZ", True, WHITE)
            japn = font.render("あいうえおアイウエオ勝敗決着！？",True, WHITE)

            # 画面表示位置
            screen.blit(name,[20, 20])
            screen.blit(numb, [20, 70])
            screen.blit(asci, [20, 120])
            screen.blit(japn, [20, 170])
        
        except FileNotFoundError:
            print("無効なフォント")
            i += 1

        except IndexError:

            # プレビュー終了時に表示。適当な日本語フォントを指定しておく
            font = pygame.font.SysFont("hgs教科書体", 30)
            numb = font.render("全フォントのプレビュー終了！ 計" + str(len(font_list)+1), True, WHITE)
            screen.blit(numb, [20, 70])
        '''

        CharacterSheet()
         
        frame()

        # 画面を更新
        pygame.display.update() 

        # イベント取得
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT:
                    if messagebox.askokcancel("確認","本当に終了しますか？"):
                        pygame.quit()
                        sys.exit()
                    else:
                        break
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if messagebox.askokcancel("確認","本当に終了しますか？"):
                        pygame.quit()
                        sys.exit()
                    else:
                        break
                    

                

                ''' # フォント変更
                if event.key == K_UP and i > 0:
                    i -= 1
                if event.key == K_DOWN and i < len(font_list)-1:
                    i += 1
                '''

            
if __name__ == "__main__":
    main()
