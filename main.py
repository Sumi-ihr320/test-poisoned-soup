import pygame
from pygame.locals import *
import tkinter as tk

from constans import *
from utils import *

from manager.setting_manager import SettingManager
from manager.scene_manager import SceneManager


# tkinterの起動 ---------------------------------------------------
root = tk.Tk()
root.geometry(create_size_tkinter(root))
# tkinterの非表示
root.withdraw()

# main関数をクラス化    (chatGPT指南)
class MainApp:
    def __init__(self):
        # pygame初期化    
        pygame.init()

        # セッティングマネージャー
        self.setting_manager = SettingManager()

        # 画面サイズ等のデータロード
        self.screen = None
        self.load_data()

        # キーリピート設定
        pygame.key.set_repeat(100, 100)
        # タイトルバーキャプション
        pygame.display.set_caption(TITLE_TEXT)

        self.clock = pygame.time.Clock()

        # シーンマネージャー
        self.scene_manager = SceneManager(self.screen, root, self.setting_manager)

    # 設定ファイルをロードする
    def load_data(self):
        self.setting_manager.load_settings()
        settings = self.setting_manager.settings

        # 画面サイズ
        if settings["fullscreen"]:
            self.screen = pygame.display.set_mode(tuple(settings["resolution"]), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(tuple(settings["resolution"]))

        # ボリューム設定 

    # 画面の描写
    def run(self):
        while True:
            self.handle_events()

            # 画面を黒で塗りつぶす
            self.screen.fill(BLACK)
            
            # 現在のイベントを処理
            self.scene_manager.update()

            self.update_display()

            #self.clock.tick(60)

    # イベント取得確認
    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT:
                self.close()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.close()
                elif event.key == pygame.K_F5:
                    pygame.display.toggle_fullscreen()
                    self.setting_manager.set("fullscreen", bool(pygame.display.get_surface().get_flags()&pygame.FULLSCREEN))
            

    # 画面を更新
    def update_display(self):
        pygame.display.update() 

    # 終了処理
    def close(self):
        with TopmostManager(root):
            if messagebox.askokcancel("確認","本当に終了しますか？"):
                pygame.quit()
                sys.exit()
            else:
                pass
            
if __name__ == "__main__":
    app = MainApp()
    app.run()