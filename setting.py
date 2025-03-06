import pygame
import pygame.draw
from pygame.locals import *

from constans import *
from utils import *
from ui_elements import Label
from manager.sound_manager import SoundManager

# 設定ページ
class Settings:
    def __init__(self, screen, root):
        self.screen = screen
        self.root = root

        # フォントの設定
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)                    # 基本フォント
        self.contents_font = pygame.font.Font(FONT_PATH,CONTENTS_SIZ)        # メニュー用フォント

        self.create_window()
        self.create_item()

        # サウンド設定
        self.sound_manager = SoundManager()
        sound_check(self.sound_manager)

        # ホバー状態を管理するフラグ
        self.hovered = False

    def create_window(self):
        w, h = 700, 500
        x = (self.screen.get_width() / 2) - (w / 2)
        y = (self.screen.get_height() / 2) - (h / 2)
        window_rect = Rect(x,y,w,h)
        pygame.draw.rect(self.screen, SETTING_COLOR, window_rect)
        pygame.draw.rect(self.screen, GRAY, window_rect, 2)
        line_rect = Rect(x+2, y+2, w-4, h-4)
        pygame.draw.rect(self.screen, GRAY, line_rect, 2)

    def create_item(self):
        self.title = Label(self.screen, self.contents_font, "設定", y=150, centerx=WINDOW_CENTER_X, color=BLACK)

        self.start = Label(self.screen, self.contents_font, "はじめる", y=280, centerx=WINDOW_CENTER_X, color=WHITE, background=BLACK)
        self.load = Label(self.screen, self.contents_font, "つづきから", y=350, centerx=WINDOW_CENTER_X, color=WHITE, background=BLACK)
        self.setting = Label(self.screen, self.contents_font, "設定", y=420, centerx=WINDOW_CENTER_X, color=WHITE, background=BLACK)
        self.close = Label(self.screen, self.contents_font, "おわる", y=490, centerx=WINDOW_CENTER_X, color=WHITE, background=BLACK)

        self.contents_list = [self.start, self.load, self.setting, self.close]

    def draw(self):
        self.create_window()
        # タイトルとメニューを描画
        self.title.draw()
        for content in self.contents_list:
            content.draw()

    def handle_mouse_hover(self):
        # マウスオーバーで枠を表示するよ
        pos = pygame.mouse.get_pos()
        hovering = False    # ホバー中を管理するフラグ

        for content in self.contents_list:
            if content.collidepoint(pos):
                hovering = True     # フラグを更新
                pygame.draw.rect(self.screen, WHITE, content, 1)

        if hovering and not self.hovered:
            self.sound_manager.play("カーソル移動")
        
        self.hovered = hovering

    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT:
                Close(self.root)
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                Close(self.root)

            # 左マウスクリック時
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                print(event.pos)    # デバッグ用
                if self.start.rect.collidepoint(event.pos):
                    self.sound_manager.play("選択")
                    return "opening"
                elif self.load.rect.collidepoint(event.pos):
                    self.sound_manager.play("選択")
                    return "load"
                elif self.setting.rect.collidepoint(event.pos):
                    self.sound_manager.play("選択")
                    return "setting"
                elif self.close.rect.collidepoint(event.pos):
                    self.sound_manager.play("選択")
                    Close(self.root)
                else:
                    pass
            
        return "setting"

    def update(self):
        self.draw()
        self.handle_mouse_hover()
        return self.handle_events()
