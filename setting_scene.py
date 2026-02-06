import pygame
from pygame.locals import *

from constans import *
from utils import *
from ui.ui_elements import Label, PullDown, Image
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
        self.create_item()

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
    def create_item(self):
        # タイトル
        title = Label(self.screen, font_data=self.title_font_data, text="設定", x=self.window_rect.x+30, y=self.window_rect.top+30, text_color=BLACK)

        # サイズ
        size_label = Label(self.screen, font_data=self.contents_font_data, text="・画面サイズ", x=self.window_rect.x+50, y=self.window_rect.top+110, text_color=BLACK)
        puludown_label = "フルスクリーン" if self.is_fullscreen() else (self.select_size if self.select_size else "800x600")
        self.size_pulldown = PullDown(self.screen, font_data=self.font_data, rect=Rect(size_label.rect.right+50, size_label.rect.top, 200, 45), item_list=list(SIZE_MAP), label_text=puludown_label, pd_h=500)

        # 音量
        volume_label = Label(self.screen, font_data=self.contents_font_data, text="・音量", x=self.window_rect.x+50, y=self.window_rect.top+200, text_color=BLACK)
        main_volume_label = Label(self.screen, font_data=self.font_data, text="メイン", x=volume_label.rect.right+50, y=volume_label.rect.top)
        self.music_volume_label = Label(self.screen, font_data=self.font_data, text="曲", x=main_volume_label.rect.top, y=main_volume_label.rect.bottom+10)
        self.music_volume_list = self.copy_volume_list(self.music_volume_label.rect.y)
        se_volume_label = Label(self.screen, font_data=self.font_data, text="SE", x=main_volume_label.rect.top, y=self.music_volume_label.rect.bottom+10)
        self.se_volume_list = self.copy_volume_list(se_volume_label.rect.y)
        volume_int_labels = self.create_volume_int_label()

        self.other_label = Label(self.screen, font_data=self.contents_font_data, text="・他",x=self.window_rect.x+50, y=self.window_rect.top+370, text_color=BLACK)
        
        self.set = Label(self.screen, font_data=self.contents_font_data, text="決定", y=self.window_rect.bottom-50, centerx=self.window_rect.centerx - 50, text_color=BLACK, sound_type="select")
        self.close = Label(self.screen, font_data=self.contents_font_data, text="戻る", y=self.window_rect.bottom-50, centerx=self.window_rect.centerx + 50, text_color=BLACK, sound_type="select")

        self.label_list = [title, size_label, volume_label, main_volume_label, self.music_volume_label, se_volume_label, self.other_label]
        self.label_list += volume_int_labels
        self.image_list = self.music_volume_list + self.se_volume_list
        self.button_list = [self.set, self.close]
        self.item_list = self.label_list + self.button_list + [self.size_pulldown] + self.image_list

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
        if self.select_size == "フルスクリーン":
            if not self.is_fullscreen():
                screen_size = self.screen.get_size()
                pygame.display.set_mode(screen_size, pygame.FULLSCREEN)
                self.setting_manager.set("fullscreen", True)
        else:
            screen_size = SIZE_MAP.get(self.select_size, (800, 600))
            if self.fullscreen or screen_size != self.screen.get_size():
                pygame.display.set_mode(screen_size)
                self.setting_manager.set("fullscreen", False)
                self.setting_manager.set("resolution", list(screen_size))
                self.setting_manager.set("str_resolution", self.select_size)

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
            button.draw(type="line", back_color=WHITE)

        # プルダウンを描画
        self.size_pulldown.draw(self.is_pulldown_open)

    def handle_mouse_hover(self):
        # マウスオーバーで枠を表示するよ
        pos = pygame.mouse.get_pos()

        if self.is_pulldown_open:
            self.size_pulldown.handle_mouse_hover(pos, self.is_pulldown_open)
        
        if self.size_pulldown.box.collidepoint(pos):
            #hovering = True
            pygame.draw.rect(self.screen, BLACK, self.size_pulldown.box.rect, 2)

        for button in self.button_list:
            button.handle_mouse_hover(pos)

    def handle_events(self):
        for event in pygame.event.get():
            # 左マウスクリック時
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # プルダウンのクリック処理
                if self.size_pulldown.collidepoint(event.pos):
                    sound_manager.play("クリック")
                    self.is_pulldown_open = not self.is_pulldown_open
                
                # プルダウンが開いている時
                if self.is_pulldown_open:
                    self.select_size = self.size_pulldown.handle_click(event.pos, self.is_pulldown_open)
                    if self.select_size:
                        sound_manager.play("クリック")
                        self.size_pulldown.update_label(self.select_size)
                        self.is_pulldown_open = False

                if self.close.handle_click(event.pos):
                    return self.before_event, self.setting_manager
                elif self.set.handle_click(event.pos):
                    self.set_data()
                    return self.before_event, self.setting_manager

        return "setting", self.setting_manager
            
    def update(self):
        self.draw()
        self.handle_mouse_hover()        
        return self.handle_events()
