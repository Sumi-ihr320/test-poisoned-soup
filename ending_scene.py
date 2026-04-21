import pygame
from pygame.locals import *

from constans import State
from utils import Close
from core.game_state import Flags
from ui.ui_panels import TextFramePanel
from input.focus_manager import FocusManager
from manager.event_manager import EventManager
from manager.scenario_manager import ScenarioManager
from base_scene import BaseScene

# エンディング
class EndingScene(BaseScene):
    def __init__(self, screen, root, save_data=None):
        super().__init__(screen, root)
        self.save_data = save_data

        self.flags = Flags().from_dict(save_data["flags"])

        # マネージャーを初期化
        event_manager = EventManager(self.screen, flags=self.flags)
        self.scenario_manager = ScenarioManager(self.screen, event_manager, "ending")
        
        # メニューボタン
        enabled_flags = {"セーブ": False, "ロード": True, "ログ": True}
        self.text_frame_panel = TextFramePanel(self.screen, on_scene_state_change_callback=self.on_scene_state_change_requested, enabled_flags=enabled_flags)

        # フォーカスマネージャー
        self.focus_manager = FocusManager(self.screen)
    
    # 表示
    def draw(self):
        self.text_frame_panel.draw()
        self.scenario_manager.draw()
        self.focus_manager.draw()
    
    #def handle_mouse_hover(self):
    #    key = pygame.mouse.get_pos()

    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                Close(self.root)

            action = self.focus_manager.handle_event(event)

            if action is None:
                # マウスクリック時
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    self.scenario_manager.on_click()
                    if self.scenario_manager.is_active == False:
                        self.state = State.CLOSE

    def update(self):
        if self.scenario_manager.is_active:
            self.scenario_manager.update()
        self.draw()
        #self.handle_mouse_hover()
        self.handle_events()
        return self.next_state()

    def next_state(self):
        if self.state == State.LOAD:
            self.state = State.NONE
            return "load"
        elif self.state == State.SAVE:
            self.state = State.NONE
            return "save"
        elif self.state == State.CLOSE:
            return "title"
        return "ending"
