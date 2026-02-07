import pygame
from pygame.locals import *

from constans import State
from utils import Close
from ui.ui_panels import TextFramePanel
from ui.log_view import LogView
from input.focus_manager import FocusManager
from manager.event_manager import EventManager
from manager.scenario_manager import ScenarioManager
from base_scene import BaseScene

# オープニング関数をクラス化    (chatGPT指南)
class OpeningScene(BaseScene):
    def __init__(self, screen, root):
        super().__init__(screen, root)

        # 画面の状態
        self.state = State.NONE

        # フォーカスマネージャー
        self.focus_manager = FocusManager(self.screen)

        # ログ表示
        self.log_view = LogView(self.screen, callback=self.log_view_close)
        self.log_view_flag = False

        # テキストフレームパネル
        enabled_flags = {"セーブ":False, "ロード":True, "ログ":True}
        self.text_frame_panel = TextFramePanel(self.screen, next_callback=self.set_state, enabled_flags=enabled_flags)

        # マネージャーを初期化
        event_manager = EventManager(self.screen, log_view=self.log_view)
        self.scenario_manager = ScenarioManager(self.screen, event_manager, "opening")


    def relayout(self, screen):
        super().relayout(screen)

    # 表示
    def draw(self):
        self.text_frame_panel.draw()
        self.scenario_manager.draw()
        self.focus_manager.draw()
        if self.log_view_flag:
            self.log_view.draw()

    # マウスオーバーイベント    
    #def handle_mouse_hover(self):
    #    key = pygame.mouse.get_pos()

    # クリックイベント
    def handle_click(self, pos):
        if self.log_view_flag:
            self.log_view.handle_click(pos)
        else:
            if self.text_frame_panel.handle_click(pos):
                return
            self.scenario_manager.on_click()
            if self.scenario_manager.is_active == False:
                self.state = State.CLOSE

    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT:
                Close(self.root)

            # ESCキーで終了
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                Close(self.root)

            action = self.focus_manager.handle_event(event)


    def update(self):
        if self.scenario_manager.is_active:
            self.scenario_manager.update()
        self.draw()
        self.handle_mouse_hover()
        self.handle_events()
        return self.next_state()

    # メニューボタン用のコールバック関数
    def set_state(self, state=State.NONE):
        self.state = state

    # ログ表示用のコールバック関数
    def log_view_close(self, flag):
        if flag:
            self.log_view_flag = False

    def next_state(self):
        if self.state == State.LOAD:
            self.state = State.NONE
            return "load"
        elif self.state == State.SETTING:
            self.state = State.NONE
            return "setting"
        elif self.state == State.LOG:
            self.log_view_flag = True
        elif self.state == State.CLOSE:
            return "charasheet"
        return "opening"
