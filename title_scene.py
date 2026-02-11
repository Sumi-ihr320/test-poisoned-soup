import pygame
from pygame.locals import *

from constans import FONT_PATH, TITLE_FONT_PATH, CONTENTS_SIZ, TITLE_SIZ, TITLE_TEXT, SOUND_LIST, WHITE, BLACK, RED, State
from utils import Close
from ui.ui_elements import Label
from input.focus_manager import FocusManager
from input.input_mode_manager import input_mode_manager
from manager.sound_manager import sound_manager
from base_scene import BaseScene

# タイトル関数をクラス化
class TitleScene(BaseScene):
    def __init__(self, screen, root, setting_manager):
        super().__init__(screen, root)

        # 設定マネージャー
        self.setting_manager = setting_manager

        # フォーカスの設定
        self.focus_manager = FocusManager(self.screen)

        # フォント設定
        self.set_font_data()

        # 表示するアイテムの作成
        self.contents_list = []
        self.create_item()

        # サウンド設定
        self.sound()

        # ホバー状態を管理するフラグ
        self.hovered = False

        # マウスが何かアイテムを選択しているかどうか
        self.mouse_focus = None

        # キーボードモードかマウスモードか
        input_mode_manager.load_mode(self.setting_manager)
        self.focus_manager.setting_mode(input_mode_manager.get_mode())

    # フォントデータを設定する
    def set_font_data(self):
        self.title_font_data = (TITLE_FONT_PATH, TITLE_SIZ)    # タイトル用のフォント
        self.contents_font_data = (FONT_PATH, CONTENTS_SIZ)    # メニュー用フォント

    # アイテムを作成
    def create_item(self):
        # 画面中央の算出
        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2

        # タイトル
        self.title = Label(self.screen, font_data=self.title_font_data, text=TITLE_TEXT, 
                           centerx=center_x, centery=center_y-130, anchor=("center","center"), 
                           text_color=RED, background_color=BLACK)
        
        self.start = self.create_button_label(text="はじめる", centery=center_y)
        self.load = self.create_button_label(text="つづきから", centery=center_y+70)
        self.setting = self.create_button_label(text="設定", centery=center_y+140)
        self.close = self.create_button_label(text="おわる", centery=center_y+210)

        self.label_items = [self.title, self.start, self.load, self.setting, self.close]

    # ボタン用ラベルを作成する
    def create_button_label(self, text: str, centery: int) -> Label:
        center_x = self.screen.get_width() // 2
        label = Label(self.screen, font_data=self.contents_font_data, text=text, 
                      centerx=center_x, centery=centery, anchor=("center","center"), 
                      text_color=WHITE, background_color=BLACK, 
                      hover_type="line",
                      sound_type="select", focusable=True)
        self.focus_manager.register(label)
        self.contents_list.append(label)
        return label

    # 画面サイズ変更時に呼び出す
    def relayout(self, screen):
        super().relayout(screen)
        for label in self.label_items:
            label.relayout(screen)

    def sound(self):
        # サウンドデータの読み込み
        for item in SOUND_LIST:
            sound_manager.load_sound(item["name"], item["path"], item["loop"])

        # 音量
        sound_manager.set_volume("タイトル", 0.5)
        sound_manager.set_volume("カーソル移動", 2)

        # 再生
        sound_manager.play("タイトル")

    def draw(self):
        # タイトルとメニューを描画
        self.title.draw()
        for content in self.contents_list:
            content.draw()

        self.focus_manager.draw()

    # マウスオーバーイベント
    #def handle_mouse_hover(self):
        # マウスオーバーで枠を表示するよ
        #pos = pygame.mouse.get_pos()

    #    self.mouse_focus = None

    #    for content in self.contents_list:
    #        content.handle_mouse_hover(pos)


    def on_focus_decide(self, element):
        if element is self.start:
            sound_manager.stop("タイトル")
            self.state = State.CLOSE

        elif element is self.load:
            sound_manager.stop("タイトル")
            self.state = State.LOAD

        elif element is self.setting:
            sound_manager.stop("タイトル")
            self.state = State.SETTING

        elif element is self.close:
            Close(self.root)


    # クリックイベント
    def handle_click(self, pos):
        if self.start.handle_click(pos):
            sound_manager.stop("タイトル")
            print(f"{self.start.texts}:{pos}")  # デバッグ用 
            self.state = State.CLOSE

        elif self.load.handle_click(pos):
            sound_manager.stop("タイトル")
            print(f"{self.load.texts}:{pos}")  # デバッグ用 
            self.state = State.LOAD

        elif self.setting.handle_click(pos):
            sound_manager.stop("タイトル")
            #sound_manager.play("選択")
            print(f"{self.setting.texts}:{pos}")  # デバッグ用
            self.state = State.SETTING

        elif self.close.handle_click(pos):
            print(f"{self.close.texts}:{pos}")  # デバッグ用 
            Close(self.root)
        else:
            pass

    # イベント
    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT:
                Close(self.root)

            # キーボード押下時 ESCキーで終了
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                Close(self.root)

            action = self.focus_manager.handle_event(event)

            if action == "decide":
                focusad = self.focus_manager.get_focused()
                if focusad:
                    self.on_focus_decide(focusad)

    # 更新            
    def update(self):
        self.draw()
        self.handle_mouse_hover()
        self.handle_events()
        return self.next_state()

    # 次のステージ
    def next_state(self):
        if self.state == State.LOAD:
            self.state = State.NONE
            return "load"
        elif self.state == State.SETTING:
            self.state = State.NONE
            return "setting"
        elif self.state == State.CLOSE:
            return "opening"
        return "title"
