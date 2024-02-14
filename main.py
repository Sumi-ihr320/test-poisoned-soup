import sys, random
import pygame
from pygame.locals import *

DISPLAY_SIZE = (800, 600)
BLACK = (0,0,0)
WHITE = (255,255,255)
SHEET_COLOR = (189,183,107)
PATH = "c:\poisoned-soup"
SCENARIO = "\Scenario"
PICTURE ="\Picture"
MUSIC = "\Music"

# 初期化,
pygame.init()
# 画面サイズ
screen = pygame.display.set_mode(DISPLAY_SIZE)
# タイトルバーキャプション
pygame.display.set_caption("毒入りスープ")
# フォントの設定
font = pygame.font.Font(None, 36)

#ファイルの読み込み
f = open(PATH + SCENARIO + '\CharacterSheet_01.txt', 'r', encoding='UTF-8')
Parameter_list = f.readlines()
f.close

def Opening():
    pass

def CharacterSheet():
    # シートの描画
    pygame.draw.rect(screen, SHEET_COLOR, Rect(30,30,740,360))
    text = "テスト"
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(100,100))
    screen.blit(text_surface, text_rect)

    # プレイヤー画像の読み込み
    player = pygame.image.load(PATH + PICTURE + "\silhouette_man.png")
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
        # 閉じるボタンで終了
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(BLACK) # 画面を黒で塗りつぶす

        CharacterSheet()
        frame()

        pygame.display.update() # 画面を更新


if __name__ == "__main__":
    main()
