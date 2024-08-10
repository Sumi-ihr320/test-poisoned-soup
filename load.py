import pygame
import pygame.draw
from pygame.locals import *

from data import *
from fanction_summary import *
from class_summary import *

# データロード
def Load(screen, flag ,save_files):

    window = DataWindow(screen, "load", save_files)

    for event in pygame.event.get():
        # マウスクリック時
        if event.type == MOUSEBUTTONDOWN:
            # 左ボタン
            if event.button == 1:
                if window.close_rect.collidepoint(event.pos):
                    if flag == "title":
                        return "title"
                    elif flag == "play":
                        return "play"

                for i in range(len(window.data_rect_list)):
                    if window.data_rect_list[i].collidepoint(event.pos):
                        SelectSaveData = save_files[i]
                        print(SelectSaveData)
                        
        # 閉じるボタンで終了
        if event.type == QUIT:
            Close()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                Close()

    return "load"