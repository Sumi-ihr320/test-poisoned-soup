import pygame

from constans import SHEET_SIZE
from utils import *
from ui.ui_elements import Image
from manager.sound_manager import SoundManager

class BacePage:
    def __init__(self, screen, root, player, ofset=(0, 0)):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.root = root

        self.set_font_data()

        self.create_surface()
        self.bg_img = Image(self.screen, "old_paper.jpg", x="center", y="center", size_wh=self.rect.size, parent=self)

        self.ofset = ofset

        self.player = player

        self.elements = []

        self.sound_manager = SoundManager()
        sound_check(self.sound_manager)

    # シート用のsurfaceを作る
    def create_surface(self):
        surface_size = get_new_size(self.screen_size, SHEET_SIZE)
        self.surface = pygame.Surface(surface_size)
        # テキストフレームの位置からシート位置を算出
        frame_rect = get_frame_rect(self.screen)
        self.rect = self.surface.get_rect(centerx=(self.screen.get_width()//2), bottom=frame_rect.top - 32)

    def set_font_data(self):
        font_data = (FONT_PATH, FONT_SIZ)
        small_font_data = (FONT_PATH, SMALL_SIZ)
        self.font_datas = [font_data, small_font_data]

    def add_elements(self, element):
        self.elements.append(element)
    
    def update_item_position(self, screen):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.create_surface()
        self.bg_img.update_item_position(screen, self)

    def get_global_offset(self):
        return self.rect.topleft
    
    def get_rect(self):
        return self.rect

    def pos_calculation(self, pos):
        return (pos[0]-self.rect.x, pos[1]-self.rect.y)

    def draw(self):
        self.bg_img.draw()
        for element in self.elements:
            element.draw()
        return self.surface, self.rect
