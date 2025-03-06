import pygame

from constans import *

class SoundManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False  # 初期化フラグ
        return cls._instance

    def __init__(self):
        if not self._initialized:  # 初回のみ初期化
            # サウンドミキサー初期化
            pygame.mixer.init()
        
            self.sounds = {}

            self._initialized = True   # 初期化済みフラグを設定

    # サウンドをロードして辞書に登録
    def load_sound(self, name, path, loop=False):
        file_path = f"{PATH}{SOUND}{path}"
        sound = pygame.mixer.Sound(file_path)
        self.sounds[name] = {"sound":sound, "loop":loop}
    
    # サウンドを再生
    def play(self, name):
        if name in self.sounds:
            sound = self.sounds[name]["sound"]
            loop = -1 if self.sounds[name]["loop"] else 0
            sound.play(loops=loop)

    def set_volume(self, name, volume):
        self.sounds[name]["sound"].set_volume(volume)

    # サウンドを停止
    def stop(self, name):
        self.sounds[name]["sound"].stop()

    # 全てのサウンドを停止
    def stop_all(self):
        pygame.mixer.stop()
