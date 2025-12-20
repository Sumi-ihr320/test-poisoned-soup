import pygame
from pygame.locals import *

from constans import *
from utils import *
from core.game_state import *
#from ui.menu import MenuController
from ui.ui_panels import TextFramePanel
from manager.event_manager import EventManager
from manager.scenario_manager import ScenarioManager

# エンディング
class Ending:
    def __init__(self, screen, root, save_data=None):
        self.screen = screen
        self.root = root
        self.save_data = save_data

        self.flags = Flags().from_dict(save_data["flags"])

        # 画面の状態
        self.state = State.NONE

        # マネージャーを初期化
        event_manager = EventManager(self.screen, flags=self.flags)
        self.scenario_manager = ScenarioManager(self.screen, event_manager, "ending")
        
        # メニューボタン
        #self.menu_controller = MenuController(self.screen, self.root, self.set_state)
        self.text_frame_panel = TextFramePanel(self.screen, next_callback=self.set_state())
    
    # 表示
    def draw(self):
        #create_frame(self.screen)
        #self.menu_controller.draw()
        self.text_frame_panel.draw()
        self.scenario_manager.draw()
    
    def handle_mouse_hover(self):
        key = pygame.mouse.get_pos()
        self.menu_controller.handle_mouse_hover(key)

    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                Close(self.root)

            # マウスクリック時
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_controller.handle_click(event.pos):
                    return
                self.scenario_manager.on_click()
                if self.scenario_manager.is_active == False:
                    self.state = State.CLOSE

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
