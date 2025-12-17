from typing import List, Tuple
from ui.ui_elements import UIElement

class UIContainer:
    def __init__(self, screen, parent=None):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.parent = parent
        self.parent_surface = parent.surface if parent else screen

        self.children: List[UIElement] = []
        
    def add(self, child: UIElement):
        self.children.append(child)
    
    def remove(self, child: UIElement):
        if child in self.children:
            self.children.remove(child)

    def clear(self):
        self.children.clear()

    # FocusManagerとの一括登録
    def register_all(self, focus_manager):
        for c in self.children:
            if c.is_focusable():
                focus_manager.register(c)

    # FocusManagerとの一括解除
    def unregister_all(self, focus_manager):
        for c in self.children:
            if c in focus_manager.elements:
                focus_manager.elements.remove(c)

    def draw(self):
        for c in self.children:
            c.draw()

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        for c in self.children:
            if c.handle_click(pos):
                return True
        return False

    def handle_mouse_hover(self, pos: tuple[int, int]):
        for c in self.children:
            c.handle_mouse_hover(pos)
    
    def relayout(self, screen, parent=None):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.parent = parent
        self.parent_surface = parent.surface if parent else screen
        for c in self.children:
            c.relayout(screen, parent)
    
        
                    
        