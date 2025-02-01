import pygame

from constans import *

class Navigation:
    def __init__(self, screen):
        self.screen = screen
        self.navi_items = {}    # 各位置のナビゲーションを格納する辞書

    def setup_navigation(self, positions):
        """表示する位置を指定してナビゲーションを初期化する"""
        self.navi_items.clear()
        
        for position in positions:
            self.navi_items[position] = PageNavigation(self.screen, position)

    def draw(self):
        """現在の位置にあるナビゲーションを描画する"""
        for navi in self.navi_items.values():
            navi.draw()

    def handle_click(self, pos):
        """ナビゲーションのクリック処理"""
        for position, navi in self.navi_items.items():
            if navi.handle_click(pos):
                return position
        return None

# ページ移動用の矢印表示するよ
class PageNavigation:
    def __init__(self, screen, position_flag=0):
        self.screen = screen
        self.position_flag = position_flag

        self.rect_dic = {Position.RIGHT:{"x":740, "y":40, "triangle":[[750,190],[770,210],[750,230]]},
                         Position.LEFT:{"x":20, "y":40, "triangle":[[50,190],[30,210],[50,230]]},
                         Position.UNDER:{"x":None,"y":350,"triangle":[[380,360],[400,380],[420,360]]}}

        self.navi_img = None
        self.navi_rect = None
        self.create_image()

    # ナビゲーションの作成
    def create_image(self):
        img_path = f"{PATH}{PICTURE}navigate.png"
        self.navi_img = pygame.image.load(img_path).convert_alpha()
        if self.position_flag == Position.UNDER:
            self.navi_img = pygame.transform.rotate(self.navi_img, 90)
            self.navi_img = pygame.transform.scale(self.navi_img, (500,40))
        else:
            self.navi_img = pygame.transform.scale(self.navi_img, (40,355))

        self.navi_rect = self.navi_img.get_rect()
        # ナビゲーションの表示
        if self.position_flag == Position.UNDER:
            self.navi_rect.centerx = WINDOW_CENTER_X
        else:
            self.navi_rect.centerx += self.rect_dic[self.position_flag]["x"]
        self.navi_rect.centery += self.rect_dic[self.position_flag]["y"]
    
    # 画像表示
    def draw(self):
        # バーの描画
        self.screen.blit(self.navi_img, self.navi_rect)

        # 三角形の描画
        pygame.draw.polygon(self.screen, BLACK, self.rect_dic[self.position_flag]["triangle"])
    
    def handle_click(self, pos):
        if self.navi_rect.collidepoint(pos):
            return True
        return False
