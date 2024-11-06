import pygame
import pygame.draw
from pygame.locals import *

from constans import *
from utils import *
from class_summary import *

# オープニング関数をクラス化    (chatGPT指南)
class Opening:
    def __init__(self, screen, root):
        self.screen = screen
        self.root = root
        self.opening_flag = 0
        self.file_path = f"{PATH}{SCENARIO}Opening.txt"
        self.texts = load_text(self.file_path).splitlines()

        # 画面の状態
        self.state = State.NONE

        self.menu = None
        self.create_menu()
    
    # 表示
    def draw(self):
        create_frame(self.screen)
        if self.menu:
            self.menu.draw()

    # メニューボタンの作成
    def create_menu(self):
        self.menu = Menu(self.screen, self.root, self.set_state, save_enabled=False)


    # テキストの描画
    def draw_text(self):
        if self.opening_flag < 2:
            TextDraw(self.screen, self.texts[self.opening_flag])
    
    def handle_mouse_hover(self):
        key = pygame.mouse.get_pos()
        for button in self.menu.buttons:
            button.update(key)

    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT:
                Close(self.root)
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                Close(self.root)

            # マウスクリック時
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.menu:
                    for button in self.menu.buttons:
                        if button.update(event.pos, True):
                            return
                self.opening_flag += 1

    def update(self):
        self.draw()
        self.draw_text()
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
        elif self.opening_flag >= 2:
            return "charasheet"
        return "opening"
