from typing import List, Tuple, Any
import pygame

from constans import SHEET_SIZE, FONT_PATH, FONT_SIZ, SMALL_SIZ
from utils import get_new_size
from ui.ui_elements import Image
from input.focus_manager import FocusManager
from models.characters import Player

class BasePage:
    def __init__(self, screen, root, text_frame_rect: pygame.Rect, player: Player, offset: Tuple[int, int]=None):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.root = root

        self.text_frame_rect = text_frame_rect

        self.setting_font_data()

        self.create_surface_and_rect()
        self.bg_img = Image(self.screen, "old_paper.jpg", x="center", y="center", size_wh=SHEET_SIZE, parent=self)

        self.offset = offset if offset else (self.rect.x, self.rect.y)

        self.player = player

        self.elements = []

    # シート用のsurfaceを作る
    def create_surface_and_rect(self):
        surface_size = get_new_size(self.screen_size, SHEET_SIZE)
        self.surface = pygame.Surface(surface_size)
        # テキストフレームの位置からシート位置を算出
        self.rect = self.surface.get_rect(centerx=(self.screen.get_width()//2), bottom=self.text_frame_rect.top - 32)

    # フォントデータの設定
    def setting_font_data(self):
        font_data: Tuple[str, int] = (FONT_PATH, FONT_SIZ)
        small_font_data: Tuple[str, int] = (FONT_PATH, SMALL_SIZ)
        self.font_datas: List[Tuple[str, int]] = [font_data, small_font_data]

    # 要素を追加
    def add_elements(self, element: Any):
        self.elements.append(element)

    # すべての要素をフォーカスマネージャーに登録
    def register_all(self, focus_manager: FocusManager):
        for element in self.elements:
            if hasattr(element, "register_all"):
                element.register_all(focus_manager)
            else:
                focus_manager.register(element)

    # すべての要素をフォーカスマネージャーから削除
    def unregister_all(self, focus_manager: FocusManager):
        for element in self.elements:
            if hasattr(element, "unregister_all"):
                element.unregister_all(focus_manager)
            else:
                focus_manager.elements.remove(element)
    
    # 画面サイズ変更時の画面再配置
    def relayout(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.create_surface_and_rect()
        self.bg_img.relayout(screen, self)

    def get_global_offset(self):
        return self.offset
    
    def get_rect(self):
        return self.rect

    # 座標を計算してグローバル座標を返す
    def pos_calculation(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        return (pos[0]-self.offset[0], pos[1]-self.offset[1])

    def draw(self) -> Tuple[pygame.Surface, pygame.Rect]:
        self.bg_img.draw()
        for element in self.elements:
            element.draw()
        return self.surface, self.rect
