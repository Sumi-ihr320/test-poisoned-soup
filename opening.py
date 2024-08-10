import pygame
import pygame.draw
from pygame.locals import *

from data import *
from fanction_summary import *
from class_summary import *

# オープニング
def Opening(screen):
    global OpeningFlag

    # フレームの表示
    Frame(screen)

    file_path = PATH + SCENARIO + "Opening.txt"
    with open(file_path,"r",encoding="utf-8_sig") as f:
        txts = f.readlines()
    
    if OpeningFlag < 2:
        TextDraw(screen, txts[OpeningFlag])
    else:
        return "charasheet"

    for event in pygame.event.get():
        # マウスクリック時
        if event.type == MOUSEBUTTONDOWN:
            # 左ボタン
            if event.button == 1:
                OpeningFlag += 1

        # 閉じるボタンで終了
        if event.type == QUIT:
            Close()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                Close()

    return "opening"
