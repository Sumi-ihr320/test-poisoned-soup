import pygame

from constans import BLACK
from ui.ui_container import UIContainer
from ui.ui_elements import Image

class OverlayCloseButton(Image):
    def __init__(self, screen, path="close_button.png", cache = None, scale = 0.2, x = 0, y = 0, centerx = None, centery = None, line_flag = False, line_width = 1, bg_flag = False, size_wh = None, anchor = ("right", "top"), 
                 parent = None, action = "close", result_type = None, sound_type = "click", row = 0, col = 0, focusable = True, hover_text = None, **kwargs):
        super().__init__(screen, path, cache, scale, x, y, centerx, centery, line_flag, line_width, bg_flag, size_wh, anchor, parent, result_type, sound_type, row, col, focusable, hover_text, **kwargs)
        self.action = action

    def handle_click(self, pos):
        if self.collidepoint(pos):
            self.on_decide()
            return self.action
        return None

class OverlayView(UIContainer):
    def __init__(self, screen, parent=None):
        super().__init__(screen, parent=parent)

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

    def handle_click(self, result: str):
        selected_action = result

        if selected_action == "close":
            self.close()
        
        return selected_action

    def draw(self):
        if not self.is_open:
            return
        
        self.screen.blit(self.surface, (0, 0))
        super().draw()
