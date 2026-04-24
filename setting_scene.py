import pygame
from pygame.locals import *

from constans import SIZE_MAP, FONT_PATH, SMALL_SIZ, CONTENTS_SIZ, TITLE_SIZ, SETTING_COLOR, GRAY, BLACK, WHITE
from utils import get_new_size
from ui.ui_elements import Label, Image
from ui.ui_pull_down import PullDown
from input.focus_manager import FocusManager
from manager.sound_manager import sound_manager
from base_scene import BaseScene

# 設定ページ
class SettingScene(BaseScene):
    def __init__(self, screen, root, setting_manager, before_event):
        super().__init__(screen, root)
        self.setting_manager = setting_manager
        self.before_event = before_event

        # フォントデータの設定
        self.set_font_data()

        self.load_data()
        self.is_pulldown_open = False    # プルダウン用のフラグ

        # 音量用画像のリスト
        self.create_img_list()

        self.create_surface()
        self.create_window()
        self.build()

        self.focus_manager = FocusManager(self.screen)

        # ホバー状態を管理するフラグ
        self.hovered = False

    # フォントデータの設定
    def set_font_data(self):
        self.small_font_data = (FONT_PATH, SMALL_SIZ)             # 小さいフォント
        self.font_data = (FONT_PATH, SMALL_SIZ)                   # 基本フォント
        self.contents_font_data = (FONT_PATH, CONTENTS_SIZ)       # メニュー用フォント
        self.title_font_data = (FONT_PATH, TITLE_SIZ)             # 表題用フォント

    # 画面がフルスクリーンかを確認する
    def is_fullscreen(self):
        return bool(pygame.display.get_surface().get_flags()&pygame.FULLSCREEN)

    # ウィンドウ用surfaceを作成
    def create_surface(self):
        surface_size = get_new_size(self.screen_size, (700, 500))
        self.window_surface = pygame.Surface(surface_size)
        self.window_rect = self.window_surface.get_rect(center=(self.screen_size[0]//2, self.screen_size[1]//2))

    # ウィンドウの背景を描画する
    def create_window(self):
        self.window_surface.fill(SETTING_COLOR)
        pygame.draw.rect(self.window_surface, GRAY, self.window_surface.get_rect(), 2)
        pygame.draw.rect(self.window_surface, GRAY, pygame.Rect(4, 4, self.window_rect.w-8, self.window_rect.h-8), 2)

    # 画面のUIを描画する
    def build(self):
        # タイトル
        title = Label(self.screen, font_data=self.title_font_data, text="設定", x=self.window_rect.x+30, y=self.window_rect.top+30, text_color=BLACK)

        # サイズ
        size_label = Label(self.screen, font_data=self.contents_font_data, text="・画面サイズ", x=self.window_rect.x+50, y=self.window_rect.top+110, text_color=BLACK)
        puludown_label = "フルスクリーン" if self.is_fullscreen() else (self.select_size if self.select_size else "800x600")
        self.size_pulldown = PullDown(self.screen, font_data=self.font_data, rect=Rect(size_label.rect.right+50, size_label.rect.top, 200, 45), 
                                      item_list=list(SIZE_MAP), label_text=puludown_label, pd_h=500, 
                                      focusable=True, row=0)

        # 音量
        volume_label = Label(self.screen, font_data=self.contents_font_data, text="・音量", x=self.window_rect.x+50, y=self.window_rect.top+200, text_color=BLACK)
        main_volume_label = Label(self.screen, font_data=self.font_data, text="メイン", x=volume_label.rect.right+50, y=volume_label.rect.top)
        self.music_volume_label = Label(self.screen, font_data=self.font_data, text="曲", x=main_volume_label.rect.top, y=main_volume_label.rect.bottom+10)
        self.music_volume_list = self.copy_volume_list(self.music_volume_label.rect.y)
        se_volume_label = Label(self.screen, font_data=self.font_data, text="SE", x=main_volume_label.rect.top, y=self.music_volume_label.rect.bottom+10)
        self.se_volume_list = self.copy_volume_list(se_volume_label.rect.y)
        volume_int_labels = self.create_volume_int_label()

        self.other_label = Label(self.screen, font_data=self.contents_font_data, text="・他",x=self.window_rect.x+50, y=self.window_rect.top+370, text_color=BLACK)
        
        self.set = self.create_button_label(text="決定", y=self.window_rect.bottom-50, centerx=self.window_rect.centerx - 50, col=0)
        self.close = self.create_button_label(text="戻る", y=self.window_rect.bottom-50, centerx=self.window_rect.centerx + 50, col=1)

        self.label_list = [title, size_label, volume_label, main_volume_label, self.music_volume_label, se_volume_label, self.other_label]
        self.label_list += volume_int_labels
        self.image_list = self.music_volume_list + self.se_volume_list
        self.button_list = [self.set, self.close]
        self.item_list = self.label_list + self.button_list + [self.size_pulldown] + self.image_list

    # ボタンラベルの作成
    def create_button_label(self, text: str, y: int, centerx: int, col: int=0):
        label = Label(self.screen, font_data=self.contents_font_data, 
                      text=text, y=y, centerx=centerx, 
                      text_color=BLACK, hover_type="line", hover_back_color=WHITE, 
                      sound_type="select", focusable=True, row=100, col=col)
        return label

    # 音量用imageリストの作成
    def create_img_list(self):
        self.volume_img_list = []
        for i in range(1, 21):
            if i % 2 == 0:
                num = str(i)
                path = f"Volume{num.zfill(2)}.png"
                self.volume_img_list.append(Image(self.screen, path=path, scale=0.3))

    # 各音量用imageの作成
    def copy_volume_list(self, y):
        x = self.music_volume_label.rect.right+25
        new_list = self.volume_img_list.copy()
        for img in new_list:
            img.x, img.y = x, y
            img.set_rect(img.rect)
        return new_list

    # 音量用ラベルの上に表示する目盛り的なやつ
    def create_volume_int_label(self):
        label_0 = Label(self.screen, font_data=self.small_font_data, text="0", x=self.music_volume_list[0].rect.x, y=self.music_volume_list[0].rect.y-20)
        label_50 = Label(self.screen, font_data=self.small_font_data, text="50", centerx=self.music_volume_list[0].rect.centerx, y=label_0.rect.y)
        label_100 = Label(self.screen, font_data=self.small_font_data, text="100", x=self.music_volume_list[0].rect.right, y=label_0.rect.y)
        return [label_0, label_50, label_100]

    # データをロードする
    def load_data(self):
        self.fullscreen = self.setting_manager.get("fullscreen")
        self.select_size = self.setting_manager.get("str_resolution")
        self.music_volume_value = self.setting_manager.get("music_volume")
        self.se_volume_value = self.setting_manager.get("se_volume")

    # データを設定する
    def set_data(self):
        select_size = self.size_pulldown.selected_item 
        if select_size == "フルスクリーン":
            if not self.is_fullscreen():
                screen_size = self.screen.get_size()
                pygame.display.set_mode(screen_size, pygame.FULLSCREEN)
                self.setting_manager.set("fullscreen", True)
        else:
            screen_size = SIZE_MAP.get(select_size, (800, 600))
            if self.fullscreen or screen_size != self.screen.get_size():
                pygame.display.set_mode(screen_size)
                self.setting_manager.set("fullscreen", False)
                self.setting_manager.set("resolution", list(screen_size))
                self.setting_manager.set("str_resolution", select_size)

    def register_all(self):
        self.focus_manager.register(self.size_pulldown)
        for button in self.button_list:
            self.focus_manager.register(button)

    def unregister_all(self):
        if self.size_pulldown in self.focus_manager.elements:
            self.focus_manager.elements.remove(self.size_pulldown)
        for button in self.button_list:
            if button in self.focus_manager.elements:
                self.focus_manager.elements.remove(button)

    def handle_mouse_hover(self):
        # マウスオーバーで枠を表示するよ
        pos = pygame.mouse.get_pos()
        self.size_pulldown.handle_mouse_hover(pos)

        for button in self.button_list:
            button.handle_mouse_hover(pos)

    def handle_events(self):
        for event in pygame.event.get():
            # 左マウスクリック時
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # プルダウンのクリック処理
                if self.size_pulldown.handle_click(event.pos):
                    return "setting", self.setting_manager
                if self.close.handle_click(event.pos):
                    return self.before_event, self.setting_manager
                elif self.set.handle_click(event.pos):
                    self.set_data()
                    return self.before_event, self.setting_manager

        return "setting", self.setting_manager

    # 画面サイズ変更時にポジションを更新する
    def relayout(self, screen):
        super().relayout(screen)
        self.create_surface()
        self.create_window()
        for item in self.item_list:
            item.relayout(screen)

    def draw(self):
        # ウィンドウを描画
        self.screen.blit(self.window_surface, self.window_rect.topleft)

        # ラベルを描画
        for label in self.label_list:
            label.draw()

        # 画像を描画
        self.music_volume_list[self.music_volume_value].draw()
        self.se_volume_list[self.se_volume_value].draw()

        # ボタンを描画
        for button in self.button_list:
            button.draw()

        # プルダウンを描画
        self.size_pulldown.draw()

    def update(self):
        self.draw()
        self.handle_mouse_hover()        
        return self.handle_events()
