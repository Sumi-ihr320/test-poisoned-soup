
from ui.overlays.overlay_view import OverlayView, OverlayCloseButton

class InventoryView(OverlayView):
    def __init__(self, screen):
        super().__init__(screen)

        self.create_close_button()

    def create_close_button(self):
        self.close_button = OverlayCloseButton(self.screen, x=self.screen_size[0] -20, y=20)
        self.add(self.close_button)
