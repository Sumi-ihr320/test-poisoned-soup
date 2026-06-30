from dataclasses import dataclass

import pygame

@dataclass
class SlideSheet:
    surface: pygame.Surface
    rect: pygame.Rect

class SheetSlideState:
    def __init__(self, page_count: int, slide_width: int):

        self.page_count = page_count
        self.slide_width = slide_width

        # 現在のページ
        self.current_page: int = 0

        # 次のページ
        self.target_page: int = 0

        self.is_sliding: bool = False

        self.slide_offset: int = 0
        self.slide_speed: int = 40        

    def set_page_count(self, page_count: int):
        self.page_count = page_count

    def set_slide_offset(self, offset: int):
       self.slide_offset = offset 

    def get_current_page(self):
        return self.current_page

    def get_target_page(self):
        return self.target_page

    def set_current_page(self, page: int):
        if self.is_valid_page(page):
            self.current_page = page
    
    def set_target_page(self, page: int):
        if self.is_valid_page(page):
            self.target_page = page

    def is_valid_page(self, page: int) -> bool:
        if 0 <= page < self.page_count:
            return True
        return False

    def reset_page(self):
        self.current_page = 0

    def set_sliding(self, flag: bool):
        self.is_sliding = flag
 
    # 次のページを表示
    def next_page(self):
        if self.current_page < self.page_count - 1:
            self.target_page = self.current_page + 1
            self.is_sliding = True
    
    # 前のページを表示
    def prev_page(self):
        if self.current_page > 0:
            self.target_page = self.current_page - 1
            self.is_sliding = True

    def update(self):
        # スライドアニメーションの進行
        if self.is_sliding:
            direction = 1 if self.target_page > self.current_page else -1
            self.slide_offset += self.slide_speed * direction

            # 1ページ分スライドしきったら
            if abs(self.slide_offset) >= self.slide_width:
                self.current_page = self.target_page
                self.slide_offset = 0
                self.is_sliding = False


class SheetSlideRenderer:
    def __init__(self, screen):
            self.screen = screen

    def draw(self, state: SheetSlideState, current_sheet: SlideSheet, target_sheet: SlideSheet=None):
        current_x = current_sheet.rect.x - state.slide_offset
        self.screen.blit(current_sheet.surface, (current_x, current_sheet.rect.y))

        if state.is_sliding and target_sheet:
            direction = 1 if state.target_page > state.current_page else -1
            if direction > 0:
                target_x = current_sheet.rect.right - state.slide_offset 
            else:
                target_x = current_sheet.rect.left - current_sheet.rect.width - state.slide_offset
            self.screen.blit(target_sheet.surface, (target_x, target_sheet.rect.y))

