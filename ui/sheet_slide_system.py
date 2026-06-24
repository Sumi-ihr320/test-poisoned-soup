from typing import Optional, List, Tuple, Any

import pygame

from character_sheet.base_page import BasePage

class SheetSlideSystem:
    def __init__(self, screen, pages: Optional[List[Any]]):

        self.screen = screen
        self.screen_size = screen.get_size()

        self.pages = pages

        # 現在のページ
        self.current_page: int = 0

        # 次のページ
        self.target_page: int = 1

        self.is_sliding: bool = False

        self.slide_offset: int = 0
        self.slide_speed: int = 40        

    def set_pages(self, pages: List[Any]):
        self.pages = pages

    def set_slide_offset(self, offset: int):
       self.slide_offset = offset 

    def get_current_page(self):
        return self.current_page

    def get_target_page(self):
        return self.target_page

    def set_current_page(self, page: int):
        self.current_page = page
    
    def set_target_page(self, page: int):
        self.target_page = page

    def clear_page(self):
        self.current_page = 0

    def chenge_sliding(self, flag: bool):
        self.is_sliding = flag
 
    # 次のページを表示
    def next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.target_page = self.current_page + 1
            self.is_sliding = True
    
    # 前のページを表示
    def prev_page(self):
        if self.current_page > 0:
            self.target_page = self.current_page - 1
            self.is_sliding = True

    def draw(self, current_surface_and_rect: Tuple[pygame.Surface, pygame.Rect], target_surface_and_rect: Tuple[pygame.Surface, pygame.Rect]):
        current, current_rect = current_surface_and_rect
        current_x = current_rect.x - self.slide_offset
        self.screen.blit(current, (current_x, current_rect.y))

        if self.is_sliding:
            target, target_rect = target_surface_and_rect
            target_x = self.screen_size[0] - self.slide_offset if self.target_page > self.current_page else - self.screen_size[0] - self.slide_offset
            self.screen.blit(target, (target_x, target_rect.y))

    def update(self):
        # スライドアニメーションの進行
        if self.is_sliding:
            direction = 1 if self.target_page > self.current_page else -1
            self.slide_offset += self.slide_speed * direction

            # 1ページ分スライドしきったら
            if abs(self.slide_offset) >= self.screen_size[0]:
                self.current_page = self.target_page
                self.slide_offset = 0
                self.is_sliding = False
