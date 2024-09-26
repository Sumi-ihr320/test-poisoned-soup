import pygame
import pygame.draw
from pygame.locals import *

from data import *
from fanction_summary import *
from class_summary import *


# タイトル関数をクラス化    (chatGPT指南)
class Title:
    def __init__(self, screen):
        self.screen = screen
        # フォントの設定
        self.title_font = pygame.font.Font(TITLE_FONT_PATH,TITLE_SIZ)    # タイトル用のフォント
        self.contents_font = pygame.font.Font(FONT_PATH,CONTENTS_SIZ)    # メニュー用フォント

        # タイトル
        self.title = Label(self.screen, self.title_font, TITLE_TEXT, y=150, centerx=WINDOW_CENTER_X, color=RED, background=BLACK)
        self.start = Label(self.screen, self.contents_font, "はじめる", y=280, centerx=WINDOW_CENTER_X, color=WHITE, background=BLACK)
        self.load = Label(self.screen, self.contents_font, "つづきから", y=350, centerx=WINDOW_CENTER_X, color=WHITE, background=BLACK)
        self.setting = Label(self.screen, self.contents_font, "設定", y=420, centerx=WINDOW_CENTER_X, color=WHITE, background=BLACK)
        self.close = Label(self.screen, self.contents_font, "おわる", y=490, centerx=WINDOW_CENTER_X, color=WHITE, background=BLACK)

        self.contents_list = [self.start, self.load, self.setting, self.close]

    def draw(self):
        # タイトルとメニューを描画
        self.title.draw()
        for content in self.contents_list:
            content.draw()

    def handle_mouse_hover(self):
        # マウスオーバーで枠を表示するよ
        key = pygame.mouse.get_pos()
        for content in self.contents_list:
            if content.collidepoint(key):
                pygame.draw.rect(self.screen, WHITE, content, 1)

    def handle_events(self):
        for event in pygame.event.get():
            # 左マウスクリック時
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.start.rect.collidepoint(event.pos):
                    return "opening", ""
                elif self.load.rect.collidepoint(event.pos):
                    return "load", "title"
                elif self.setting.rect.collidepoint(event.pos):
                    return "setting", ""
                elif self.close.rect.collidepoint(event.pos):
                    Close()
                else:
                    pass
            
        return "title", ""

    def update(self):
        self.draw()
        self.handle_mouse_hover()
        return self.handle_events()
