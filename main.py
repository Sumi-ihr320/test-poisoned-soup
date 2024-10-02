import pygame
import pygame.draw
from pygame.locals import *
import tkinter as tk

from data import *
from fanction_summary import *
from class_summary import *

from title import Title
from save_or_load import Save_or_Load
from opening import Opening
from character_sheet import CharacterSheet
from playing import MainPlay


# tkinterの起動 ---------------------------------------------------
root = tk.Tk()
# 画面中央に配置したい
sw, sh = root.winfo_screenmmwidth(), root.winfo_screenmmheight()
w, h = root.winfo_width(), root.winfo_height()
x = (sw - w) // 2
y = (sh - h) // 2
root.geometry(f"+{x}+{y}")
# tkinterの非表示
root.withdraw()

# main関数をクラス化    (chatGPT指南)
class MainApp:
    def __init__(self):
        # pygame初期化    
        pygame.init()
        # 画面サイズ
        self.screen = pygame.display.set_mode(DISPLAY_SIZE)
        # キーリピート設定
        pygame.key.set_repeat(100, 100)
        # タイトルバーキャプション
        pygame.display.set_caption(TITLE_TEXT)

        self.clock = pygame.time.Clock()

        self.event_name = "title"
        #self.event_name = "charasheet"
        #self.event_name = "play"

        # イベントマップ
        self.event_map = {"title": Title(self.screen),
                          "opening": Opening(self.screen),
                          "charasheet": CharacterSheet(self.screen),
                          "play": MainPlay}

    # 画面の描写
    def run(self):
        while True:
            self.handle_events()

            # 画面を黒で塗りつぶす
            self.screen.fill(BLACK)
            
            # 現在のイベントを処理
            self.process_event()

            self.update_display()

            self.clock.tick(60)

    # イベント取得確認
    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT:
                self.close()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                self.close()

    # 現在のイベントを処理
    def process_event(self):
        if self.event_name in self.event_map:
            event = self.event_map[self.event_name]
            if self.event_name == "title":
                self.event_name = event.update()
                if self.event_name == "load":
                    self.event_map["load"] = Save_or_Load(self.screen, "load", "title")

            elif self.event_name == "opening":
                self.event_name = event.update()

            elif self.event_name == "charasheet":
                self.event_name = event.update()
                if self.event_name == "save":
                    self.create_save(event)

            elif self.event_name == "save":
                self.event_name, self.save_data = self.event_map["save"].update()

            elif self.event_name == "load":
                self.event_name, self.save_data = self.event_map["load"].update()
                if self.event_name == "play" and self.save_data:
                    self.event_map["play"] = MainPlay(self.screen, self.save_data)

            elif self.event_name == "play":
                self.event_name = self.event_map["play"].update()
                if self.event_name == "save":
                    self.create_save(event)
                elif self.event_name == "load":
                    self.save_data = event.save_data
                    self.event_map["load"] = Save_or_Load(self.screen, "load", "play", self.save_data)
            else:
                self.event_name = event(self.screen)

    # セーブデータを取得してイベントマップを更新
    def create_save(self, event):
        self.save_data = event.save_data
        self.event_map["save"] = Save_or_Load(self.screen, "save", "play", self.save_data)

    # 画面を更新
    def update_display(self):
        pygame.display.update() 

    # 終了処理
    def close(self):
        if messagebox.askokcancel("確認","本当に終了しますか？"):
            pygame.quit()
            sys.exit()
        else:
            pass
            
if __name__ == "__main__":
    #main()
    app = MainApp()
    app.run()