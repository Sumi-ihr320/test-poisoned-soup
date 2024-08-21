import random, os, json
import pygame
import pygame.draw
from pygame.locals import *
import tkinter as tk
from tkinter import messagebox

from data import *
from fanction_summary import *
from class_summary import *

from title import Title
from load import Load
from save import Save
from opening import Opening
from character_sheet import CharacterSheet
from playing import MainPlay

SCENE_FLAG = TITLE
#SCENE_FLAG = PLAY

# tkinterの起動 ---------------------------------------------------
root = tk.Tk()
# 画面中央に配置したい
sw, sh = root.winfo_screenmmwidth(), root.winfo_screenmmheight()
w, h = root.winfo_width(), root.winfo_height()
x = (sw/2) - (w/2)
y = (sh/2) - (h/2)
root.geometry("+%d+%d" % (x,y))
# tkinterの非表示
root.withdraw()


def main():
    # pygame初期化    
    pygame.init()
    # 画面サイズ
    screen = pygame.display.set_mode(DISPLAY_SIZE)
    # キーリピート設定
    pygame.key.set_repeat(100, 100)
    # タイトルバーキャプション
    pygame.display.set_caption(TITLE_TEXT)

    clock = pygame.time.Clock()

    #event_name = "title"
    event_name = "play"
    event_flag = ""

    # 画面の描写
    while True:
        # 画面を黒で塗りつぶす
        screen.fill(BLACK)

        if event_name == "title":
            event_name, event_flag = Title(screen)
        elif event_name == "load":
            event_name = Load(screen, event_flag, SelectSaveData)
        elif event_name == "save":
            event_name = Save(screen, event_flag, SelectSaveData)
        elif event_name == "opening":
            event_name = Opening(screen)
        elif event_name == "charasheet":
            event_name, event_flag = CharacterSheet(screen)
        elif event_name == "play":
            event_name, event_flag = MainPlay(screen)

        """
        if SCENE_FLAG == TITLE:
            Title(screen)
        elif SCENE_FLAG == LOAD:
            Load()
        elif SCENE_FLAG == SETTING:
            pass
        elif SCENE_FLAG == ENDCREDITS:
            pass
        else:
            clock = pygame.time.Clock()
            frame()
            DiceFrame()
            if SCENE_FLAG == PLAY:
                MainPlay()
            if SCENE_FLAG == CHARASE:
                CharacterSheet()
            if SCENE_FLAG == OPENING:
                Opening()
            clock.tick(60)

        """
        clock.tick(60)

        # 画面を更新
        pygame.display.update() 


            
if __name__ == "__main__":
    main()
