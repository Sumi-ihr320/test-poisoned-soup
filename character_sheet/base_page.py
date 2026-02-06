import pygame

from constans import SHEET_SIZE, FONT_PATH, FONT_SIZ, SMALL_SIZ
from utils import get_new_size
from ui.ui_elements import Image

class BacePage:
    def __init__(self, screen, root, text_frame_rect, player, offset=None):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.root = root

        self.text_frame_rect = text_frame_rect

        self.set_font_data()

        self.create_surface_and_rect()
        self.bg_img = Image(self.screen, "old_paper.jpg", x="center", y="center", size_wh=self.rect.size, parent=self)

        self.offset = offset if offset else (self.rect.x, self.rect.y)

        self.player = player

        self.elements = []

    # シート用のsurfaceを作る
    def create_surface_and_rect(self):
        surface_size = get_new_size(self.screen_size, SHEET_SIZE)
        self.surface = pygame.Surface(surface_size)
        # テキストフレームの位置からシート位置を算出
        self.rect = self.surface.get_rect(centerx=(self.screen.get_width()//2), bottom=self.text_frame_rect.top - 32)

    def set_font_data(self):
        font_data = (FONT_PATH, FONT_SIZ)
        small_font_data = (FONT_PATH, SMALL_SIZ)
        self.font_datas = [font_data, small_font_data]

    def add_elements(self, element):
        self.elements.append(element)
    
    def relayout(self, screen):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.create_surface_and_rect()
        self.bg_img.relayout(screen, self)

    def get_global_offset(self):
        return self.offset
    
    def get_rect(self):
        return self.rect

    def pos_calculation(self, pos):
        return (pos[0]-self.offset[0], pos[1]-self.offset[1])

    def draw(self):
        self.bg_img.draw()
        for element in self.elements:
            element.draw()
        return self.surface, self.rect
