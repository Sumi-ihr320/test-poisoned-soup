import pygame
import pygame.draw
from pygame.locals import *

from constans import *
from utils import *
from ui_elements import Label
from manager.sound_manager import SoundManager

# タイトル関数をクラス化    (chatGPT指南)
class Title:
    def __init__(self, screen, root, setting_manager):
        self.screen = screen
        self.root = root

        self.setting_manager = setting_manager

        # 現在の画面サイズ
        self.window_size = self.screen.get_size()

        # フォント設定
        self.set_font()

        # 表示するアイテムの作成
        self.create_item()

        # サウンド設定
        self.sound_manager = SoundManager()
        self.sound()

        # ホバー状態を管理するフラグ
        self.hovered = False

    # フォントを設定する
    def set_font(self):        
        # フォントサイズの計算に画面の縦サイズの比率を使う
        h_percent = RATIO[self.window_size][1]

        # フォントの設定
        self.title_font = pygame.font.Font(TITLE_FONT_PATH, int(TITLE_SIZ * h_percent))    # タイトル用のフォント
        self.contents_font = pygame.font.Font(FONT_PATH, int(CONTENTS_SIZ * h_percent))    # メニュー用フォント

    # アイテムを作成
    def create_item(self):
        # 画面中央の算出
        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2

        # タイトル
        self.title = Label(self.screen, self.title_font, TITLE_TEXT, centerx=center_x, centery=center_y-130, color=RED, background=BLACK)
        self.start = Label(self.screen, self.contents_font, "はじめる", centerx=center_x,centery=center_y, color=WHITE, background=BLACK)
        self.load = Label(self.screen, self.contents_font, "つづきから", centerx=center_x, centery=center_y+70, color=WHITE, background=BLACK)
        self.setting = Label(self.screen, self.contents_font, "設定", centerx=center_x, centery=center_y+140, color=WHITE, background=BLACK)
        self.close = Label(self.screen, self.contents_font, "おわる", centerx=center_x, centery=center_y+210, color=WHITE, background=BLACK)

        self.contents_list = [self.start, self.load, self.setting, self.close]

    # 画面サイズ変更時に呼び出す
    def update_item_position(self):
        self.window_size = self.screen.get_size()
        self.set_font()
        self.create_item()

    def sound(self):
        # ロード
        self.sound_manager.load_sound("タイトル", "arashinoyokan.mp3", True)
        self.sound_manager.load_sound("選択", "Choice.mp3")
        self.sound_manager.load_sound("カーソル移動", "Move.mp3")

        # 音量
        self.sound_manager.set_volume("タイトル", 0.5)
        self.sound_manager.set_volume("カーソル移動", 2)

        # 再生
        self.sound_manager.play("タイトル")

    def draw(self):
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
                    self.sound_manager.stop("タイトル")
                    self.sound_manager.play("選択")
                    return "opening"
                elif self.load.rect.collidepoint(event.pos):
                    self.sound_manager.stop("タイトル")
                    self.sound_manager.play("選択")
                    return "load"
                elif self.setting.rect.collidepoint(event.pos):
                    self.sound_manager.stop("タイトル")
                    self.sound_manager.play("選択")
                    return "setting"
                elif self.close.rect.collidepoint(event.pos):
                    self.sound_manager.play("選択")
                    Close(self.root)
                else:
                    pass
            
        return "title"

    def update(self):
        self.draw()
        self.handle_mouse_hover()
        return self.handle_events()
