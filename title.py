import pygame
import pygame.draw
from pygame.locals import *

from data import *
from fanction_summary import *
from class_summary import *


# タイトル画面作るよ
def Title(screen):
    # フォントの設定
    title_font = pygame.font.Font(TITLE_FONT_PATH,TITLE_SIZ)    # タイトル用のフォント
    contents_font = pygame.font.Font(FONT_PATH,CONTENTS_SIZ)    # メニュー用フォント

    # タイトル
    title_rect = Label(screen, title_font, TITLE_TEXT, y=150, color=RED, center_flag=True, background=BLACK)
    start_rect = Label(screen, contents_font, "はじめる", y=280, color=WHITE, center_flag=True, background=BLACK)
    load_rect = Label(screen, contents_font, "つづきから", y=350, color=WHITE, center_flag=True, background=BLACK)
    setting_rect = Label(screen, contents_font, "設定", y=420, color=WHITE, center_flag=True, background=BLACK)
    close_rect = Label(screen, contents_font, "おわる", y=490, color=WHITE, center_flag=True, background=BLACK)

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
                    return "opening", ""
                elif load_rect.collidepoint(event.pos):
                    return "load", "title"
                elif setting_rect.collidepoint(event.pos):
                    return "setting", ""
                elif close_rect.collidepoint(event.pos):
                    Close()
                else:
                    pass

        # 閉じるボタンで終了
        if event.type == QUIT:
            Close()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                Close()
    
    return "title", ""
