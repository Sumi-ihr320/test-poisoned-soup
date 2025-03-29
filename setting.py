import pygame
import pygame.draw
from pygame.locals import *

from constans import *
from utils import *
from ui_elements import Label, PullDown
from manager.sound_manager import SoundManager

# 設定ページ
class Settings:
    def __init__(self, screen, root, manager, before_event):
        self.screen = screen
        self.root = root
        self.manager = manager
        self.before_event = before_event

        # 画面サイズ
        self.window_size = self.screen.get_size()

        # フォントの設定
        self.set_font()

        self.fullscreen = self.manager.settings.get("fullscreen")

        self.select_size = self.manager.settings.get("str_resolution")
        self.is_pulldown_open = False    # プルダウン用のフラグ

        self.create_surface()
        self.create_window()
        self.create_item()

        # サウンド設定
        self.sound_manager = SoundManager()
        sound_check(self.sound_manager)

        # ホバー状態を管理するフラグ
        self.hovered = False

    # フォントの設定
    def set_font(self):
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)                    # 基本フォント
        self.contents_font = pygame.font.Font(FONT_PATH,CONTENTS_SIZ)        # メニュー用フォント
        self.title_font = pygame.font.Font(FONT_PATH, TITLE_SIZ)             # 表題用フォント

    # 画面がフルスクリーンかを確認する
    def is_fullscreen(self):
        return bool(pygame.display.get_surface().get_flags()&pygame.FULLSCREEN)

    # ウィンドウ用surfaceを作成
    def create_surface(self):
        self.window_surface = pygame.Surface((700, 500))
        self.window_rect = self.window_surface.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))

    # ウィンドウの背景を描画する
    def create_window(self):
        self.window_surface.fill(SETTING_COLOR)
        pygame.draw.rect(self.window_surface, GRAY, self.window_surface.get_rect(), 2)
        pygame.draw.rect(self.window_surface, GRAY, pygame.Rect(4, 4, 692, 492), 2)

    # 画面サイズ変更時にポジションを更新する
    def update_item_position(self):
        self.window_rect = self.window_surface.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        self.create_item()

    # 画面のUIを描画する
    def create_item(self):
        self.title = Label(self.screen, self.title_font, "設定", x=self.window_rect.x+30, y=self.window_rect.top+30, color=BLACK)

        self.size = Label(self.screen, self.contents_font, "・画面サイズ", x=self.window_rect.x+50, y=self.window_rect.top+110, color=BLACK)
        puludown_label = "フルスクリーン" if self.is_fullscreen() else (self.select_size if self.select_size else "800x600")
        self.size_pulldown = PullDown(self.screen, self.font, (self.window_rect.x+250, self.window_rect.top+100, 200, 45), list(SIZE_MAP), puludown_label)
        
        self.volume = Label(self.screen, self.contents_font, "・音量", x=self.window_rect.x+50, y=self.window_rect.top+200, color=BLACK)
        self.other = Label(self.screen, self.contents_font, "・他",x=self.window_rect.x+50, y=self.window_rect.top+370, color=BLACK)
        
        self.set = Label(self.screen, self.contents_font, "決定", y=self.window_rect.bottom-50, centerx=self.window_rect.centerx - 50, color=BLACK)
        self.close = Label(self.screen, self.contents_font, "戻る", y=self.window_rect.bottom-50, centerx=self.window_rect.centerx + 50, color=BLACK)

        self.label_list = [self.title, self.size, self.volume, self.other]
        self.button_list = [self.set, self.close]

    def set_data(self):
        if self.select_size == "フルスクリーン":
            if not self.is_fullscreen():
                screen_size = self.screen.get_size()
                pygame.display.set_mode(screen_size, pygame.FULLSCREEN)
                self.manager.set("fullscreen", True)
        else:
            screen_size = SIZE_MAP.get(self.select_size, (800, 600))
            if self.fullscreen or screen_size != self.screen.get_size():
                pygame.display.set_mode(screen_size)
                self.manager.set("fullscreeen", False)
                self.manager.set("resolution", list(screen_size))
                self.manager.set("str_resolution", self.select_size)

    def draw(self):
        # ウィンドウを描画
        self.screen.blit(self.window_surface, self.window_rect.topleft)

        # ラベルを描画
        for label in self.label_list:
            label.draw()

        # ボタンを描画
        for button in self.button_list:
            button.draw()

        # プルダウンを描画
        self.size_pulldown.draw(self.is_pulldown_open)


    def handle_mouse_hover(self):
        # マウスオーバーで枠を表示するよ
        pos = pygame.mouse.get_pos()
        hovering = False    # ホバー中を管理するフラグ

        if self.is_pulldown_open:
            self.size_pulldown.handle_mouse_hover(pos, self.is_pulldown_open)
        
        if self.size_pulldown.box.rect.collidepoint(pos):
            hovering = True
            pygame.draw.rect(self.screen, BLACK, self.size_pulldown.box.rect, 2)

        for button in self.button_list:
            if button.collidepoint(pos):
                hovering = True     # フラグを更新
                pygame.draw.rect(self.screen, WHITE, button, 1)

        if hovering and not self.hovered:
            self.sound_manager.play("カーソル移動")
        
        self.hovered = hovering

    def handle_events(self):
        for event in pygame.event.get():
            # 左マウスクリック時
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # プルダウンのクリック処理
                if self.size_pulldown.box.rect.collidepoint(event.pos):
                    self.sound_manager.play("クリック")
                    self.is_pulldown_open = not self.is_pulldown_open
                
                # プルダウンが開いている時
                if self.is_pulldown_open:
                    self.select_size = self.size_pulldown.handle_click(event.pos, self.is_pulldown_open)
                    if self.select_size:
                        self.sound_manager.play("クリック")
                        self.size_pulldown.update_label(self.select_size)
                        self.is_pulldown_open = False

                if self.close.rect.collidepoint(event.pos):
                    return self.before_event, self.manager
                elif self.set.rect.collidepoint(event.pos):
                    self.set_data()
                    return self.before_event, self.manager

        return "setting", self.manager
            
    def update(self):
        self.draw()
        self.handle_mouse_hover()        
        return self.handle_events()
