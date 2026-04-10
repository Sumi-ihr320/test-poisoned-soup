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
        self.log_view = LogView(self.screen)

        # テキストフレームパネル
        enabled_flags = {"セーブ":False, "ロード":True, "ログ":True}
        self.text_frame_panel = TextFramePanel(self.screen, self.root, next_callback=self.set_state, enabled_flags=enabled_flags)

        # マネージャーを初期化
        event_manager = EventManager(self.screen, self.root, log_view=self.log_view, text_frame_panel=self.text_frame_panel)
        self.scenario_manager = ScenarioManager(self.screen, event_manager=event_manager, scenario_id="opening")


    def register_all(self):
        if self.log_view.is_open:
            self.log_view.register_all(self.focus_manager)
        self.scenario_manager.register_all(self.focus_manager)

    def unregister_all(self):
        self.log_view.unregister_all(self.focus_manager)
        self.scenario_manager.unregister_all(self.focus_manager)

    # マウスオーバーイベント    
    #def handle_mouse_hover(self):
    #    key = pygame.mouse.get_pos()

    """
    # クリックイベント
    def handle_click(self, pos):
        if self.log_view_flag:
            self.log_view.handle_click(pos)
        else:
            if self.text_frame_panel.handle_click(pos):
                return
            self.advance_scenario()
    """
    # シナリオを先に進める
    def advance_scenario(self):
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

            result = self.focus_manager.handle_event(event)

            if result:
                # テキストフレームパネルのメニューの場合
                if result["action"] == "menu":
                    return
                
                # テキストフレームパネルのnextボタンの場合
                elif result["action"] == "next":
                    self.advance_scenario()
                    return
                
                elif result["action"] == "decide":
                    # ログ表示中にログ表示クローズボタンがクリックされた場合
                    if self.log_view.is_open:
                        if result["target"] == self.log_view.close_image:
                            self.log_view.is_open = False
            else:
                self.advance_scenario()

    def relayout(self, screen):
        super().relayout(screen)

    # 表示
    def draw(self):
        #self.text_frame_panel.draw()
        self.scenario_manager.draw()
        self.focus_manager.draw()
        self.log_view.draw()

    def update(self):
        self.handle_events()
        if self.scenario_manager.is_active:
            self.scenario_manager.update()
        self.handle_mouse_hover()
        self.draw()
        return self.next_state()

    def next_state(self):
        if self.state == State.LOAD:
            self.state = State.NONE
            return "load"
        elif self.state == State.SETTING:
            self.state = State.NONE
            return "setting"
        elif self.state == State.LOG:
            self.state = State.NONE
            self.log_view.is_open = True
        elif self.state == State.CLOSE:
            self.state = State.NONE
            return "charasheet"
        return "opening"
