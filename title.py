import pygame
from pygame.locals import *

from constans import *
from utils import *
from ui.ui_elements import Label
from ui.virtual_cursor import *
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

        # キーボード操作用カーソル
        self.cursor = VirtualCursor(self.screen)
        self.use_virtual_cursor = False

        # ホバー状態を管理するフラグ
        self.hovered = False

    # フォントを設定する
    def set_font(self):
        self.title_font = setting_font(TITLE_FONT_PATH, TITLE_SIZ, self.window_size)    # タイトル用のフォント
        self.contents_font = setting_font(FONT_PATH, CONTENTS_SIZ, self.window_size)    # メニュー用フォント

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

        if self.use_virtual_cursor:
            self.cursor.draw()

    def handle_mouse_hover(self):
        # マウスオーバーで枠を表示するよ
        if self.use_virtual_cursor:
            pos = self.cursor.get_pos()
        else:
            pos = pygame.mouse.get_pos()

        hovering = False    # ホバー中を管理するフラグ

        for content in self.contents_list:
            if content.collidepoint(pos):
                hovering = True     # フラグを更新
                pygame.draw.rect(self.screen, WHITE, content, 1)

        if hovering and not self.hovered:
            self.sound_manager.play("カーソル移動")
        
        self.hovered = hovering

    # クリックイベント
    def handle_click(self, pos):
        if self.start.collidepoint(pos):
            self.sound_manager.stop("タイトル")
            self.sound_manager.play("選択")
            return "opening"
        elif self.load.collidepoint(pos):
            self.sound_manager.stop("タイトル")
            self.sound_manager.play("選択")
            return "load"
        elif self.setting.collidepoint(pos):
            self.sound_manager.stop("タイトル")
            self.sound_manager.play("選択")
            return "setting"
        elif self.close.collidepoint(pos):
            self.sound_manager.play("選択")
            Close(self.root)
        else:
            pass

    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT:
                Close(self.root)

            # キーボード押下時
            if event.type == KEYDOWN:
                if not self.use_virtual_cursor:
                    self.use_virtual_cursor = on_keybord(self.cursor)

                # ESCキーで終了
                if event.key == K_ESCAPE:
                    Close(self.root)

                # エンターキーでクリックイベント
                elif event.key == K_RETURN or event.key == K_KP_ENTER:
                    self.handle_click(self.cursor.get_pos())

            # マウスを動かした場合
            if event.type == MOUSEMOTION:
                if self.use_virtual_cursor:
                    self.use_virtual_cursor = off_keybord(self.cursor)

            # 左マウスクリック時
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)
            
        return "title"

    def update(self):
        self.draw()
        if self.use_virtual_cursor:
            handle_cursor_move(self.use_virtual_cursor, self.cursor)
        self.handle_mouse_hover()
        return self.handle_events()
