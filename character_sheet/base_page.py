import pygame

from constans import SHEET_SIZE
from utils import *
from ui.ui_elements import Image
from manager.sound_manager import SoundManager

class BacePage:
    def __init__(self, screen, root, player, ofset=(0, 0)):
        self.screen = screen
        self.window_size = screen.get_size()
        self.root = root

        self.set_font()

        self.create_surface()
        self.bg_img = Image(self.surface, "old_paper.jpg", x="center",y="center",fixed_ratio=False, size_wh=self.rect.size)

        self.ofset = ofset

        self.player = player

        self.elements = []

        self.sound_manager = SoundManager()
        sound_check(self.sound_manager)

    # シート用のsurfaceを作る
    def create_surface(self):
        surface_size = get_new_size(self.window_size, SHEET_SIZE)
        self.surface = pygame.Surface(surface_size)

        # テキストフレームの位置からシート位置を算出
        frame_rect = get_frame_rect(self.screen)
        self.rect = self.surface.get_rect(centerx=(self.screen.get_width()//2),bottom=frame_rect.top - 20)

    def set_font(self):
        font = setting_font(FONT_PATH, FONT_SIZ, self.window_size)
        small_font = setting_font(FONT_PATH, SMALL_SIZ, self.window_size)
        self.fonts = [font, small_font]

    def add_elements(self, element):
        self.elements.append(element)
    
    def update_item_position(self, screen):
        self.screen = screen
        self.window_size = screen.get_size()
        self.set_font()
        self.create_surface()
        self.bg_img = Image(self.surface, "old_paper.jpg", x="center",y="center",fixed_ratio=False, size_wh=self.rect.size)

    def pos_calculation(self, pos):
        return (pos[0]-self.rect.x, pos[1]-self.rect.y)

    def draw(self):
        self.bg_img.draw()
        for element in self.elements:
            element.draw()
        return self.surface, self.rect
