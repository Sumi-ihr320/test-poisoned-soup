import pygame
import pygame.draw
from pygame.locals import *

from data import *
from fanction_summary import *
from class_summary import *

# オープニング関数をクラス化    (chatGPT指南)
class Opening:
    def __init__(self, screen):
        self.screen = screen
        self.opening_flag = 0
        self.file_path = f"{PATH}{SCENARIO}Opening.txt"
        self.texts = load_texts(self.file_path)
    
    # テキストフレームの表示
    def draw_frame(self):
        create_frame(self.screen)

    # テキストの描画
    def draw_text(self):
        if self.opening_flag < 2:
            TextDraw(self.screen, self.texts[self.opening_flag])
    
    def handle_events(self):
        for event in pygame.event.get():
            # マウスクリック時
            if event.type == MOUSEBUTTONDOWN:
                # 左ボタン
                if event.button == 1:
                    self.opening_flag += 1

    def update(self):
        self.draw_frame()
        self.draw_text()
        self.handle_events()
        return self.next_state()

    def next_state(self):
        if self.opening_flag >= 2:
            return "charasheet", ""
        return "opening", ""
