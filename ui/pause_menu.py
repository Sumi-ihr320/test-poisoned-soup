import pygame

from constans import BLACK

class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.is_open = False
        self.menu_options = ["ステータス", "アイテム", "少女に声をかける", "閉じる"]

        self.create_surface()

    def create_surface(self):
        self.size = self.screen.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(BLACK)
        self.surface.set_alpha(50)

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def draw(self):
        if not self.is_open:
            return
        
        self.screen.blit(self.surface, (0, 0))
