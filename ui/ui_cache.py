from typing import Tuple, Optional
import pygame

# surfasceをキャッシュに保存しそこから取ってくるクラス
class SurfaceCache:
    def __init__(self):
        self._cache = {}

    def get_surface(self, font: pygame.font.Font, text: str, 
                    color: Tuple[int, int, int], back_color: Optional[Tuple[int, int, int]]=None):
        key = (id(font), text, color, back_color)
        surf = self._cache.get(key)
        if surf is None:
            surf = font.render(text, True, color, back_color)
            self._cache[key] = surf
        return surf

    def clear(self):
        self._cache.clear()

# 画像ファイルのキャッシュ
class ImageCache:
    def __init__(self):
        self.cache = {}

    def load(self, path: str):
        if path not in self.cache:
            try:
                # 画像の読み込み＆アルファ化(透明化)
                self.cache[path] = pygame.image.load(path).convert_alpha()
            except pygame.error as e:
                print(f"Error loading image: {e}")
        return self.cache[path]
