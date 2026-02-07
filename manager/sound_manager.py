import pygame

from constans import PATH, SOUND

class SoundManager:
    def __init__(self):
        # サウンドミキサー初期化
        pygame.mixer.init()
        
        self.sounds = {}

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

sound_manager = SoundManager()