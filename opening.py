import pygame
from pygame.locals import *

from constans import *
from utils import *
from ui.menu import MenuController, update_menu
from manager.event_manager import EventManager
from manager.scenario_manager import ScenarioManager

# オープニング関数をクラス化    (chatGPT指南)
class Opening:
    def __init__(self, screen, root):
        self.screen = screen
        self.root = root

        # 画面の状態
        self.state = State.NONE

        # マネージャーを初期化
        event_manager = EventManager(self.screen)
        self.scenario_manager = ScenarioManager(self.screen, event_manager, "opening")
        
        # メニューボタン
        self.menu_controller = MenuController(self.screen, self.root, self.set_state, save_enabled=False)
    
    # 表示
    def draw(self):
        create_frame(self.screen)
        self.menu_controller = update_menu(self.screen, self.menu_controller)
        self.menu_controller.draw()
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
        elif self.state == State.SETTING:
            self.state = State.NONE
            return "setting"
        elif self.state == State.CLOSE:
            return "charasheet"
        return "opening"
