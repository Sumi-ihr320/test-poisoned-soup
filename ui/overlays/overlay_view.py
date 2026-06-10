import pygame

from constans import BLACK
from ui.ui_container import UIContainer

class OverlayView(UIContainer):
    def __init__(self, screen):
        super().__init__(screen, parent=None)

        self.is_open = False

        self.create_surface()

    # surfaceを作成する
    def create_surface(self):
        self.size = self.screen.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(BLACK)
        self.surface.set_alpha(200)

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def relayout(self, screen, parent=None):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.parent = parent
        self.parent_surface = parent.surface if parent and hasattr(parent, "surface") else screen

        self.create_surface()

    def draw(self):
        if not self.is_open:
            return
        
        self.screen.blit(self.surface, (0, 0))
        super().draw()
