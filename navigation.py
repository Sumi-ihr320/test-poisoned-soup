import pygame

from constans import *

class Navigation:
    def __init__(self, screen, surface_rect):
        self.screen = screen

        # ナビゲーションを表示する基準となるシートや画像surfaceのrect
        self.surface_rect = surface_rect

        self.navi_items = {}    # 各位置のナビゲーションを格納する辞書

    def setup_navigation(self, positions):
        """表示する位置を指定してナビゲーションを初期化する"""
        self.navi_items.clear()
        
        for position in positions:
            self.navi_items[position] = PageNavigation(self.screen, self.surface_rect, position)

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
    def __init__(self, screen, surface_rect, position_flag=0):
        self.screen = screen

        # 基準となる画像等surfaceのrect
        self.surface_rect = surface_rect

        # どの位置にナビゲーションを設置するのかのフラグ
        self.position_flag = position_flag

        self.window_rect = self.screen.get_rect()

        self.navi_img = None
        self.navi_rect = None
        self.create_image()
        self.position_calculation()
        self.triangle_position_calculation()

    # ナビゲーションの作成
    def create_image(self):
        img_path = f"{PATH}{PICTURE}navigate.png"
        self.navi_img = pygame.image.load(img_path).convert_alpha()

        w_percent, h_percent = RATIO[self.window_rect.size]
        if self.position_flag == Position.UNDER:
            self.navi_img = pygame.transform.rotate(self.navi_img, 90)
            self.navi_img = pygame.transform.scale(self.navi_img, (int(500*w_percent),int(40*h_percent)))
        else:
            self.navi_img = pygame.transform.scale(self.navi_img, (int(40*w_percent),int(355*h_percent)))

    # ナビゲーションの場所を計算
    def position_calculation(self):
        self.navi_rect = self.navi_img.get_rect()

        # x位置
        if self.position_flag == Position.UNDER:
            self.navi_rect.center = (self.screen.get_widht() // 2, self.surface_rect.bottom - 10)
        else:
            half_width = self.navi_rect.width // 2
            self.navi_rect.x = self.surface_rect.right - (half_width) if self.position_flag == Position.RIGHT else self.surface_rect.left - (half_width)
            self.navi_rect.centery = self.surface_rect.centery

        #center_y = self.screen.get_height() // 2
        #self.navi_rect.centery = center_y + 50 if self.position_flag == Position.UNDER else center_y - 30

    # 三角形の場所を計算する
    def triangle_position_calculation(self):
        # 基本の三角形
        triangle_dict = {Position.RIGHT:([-10,-20], [10,0], [-10,20]),
                         Position.LEFT:([10,-20],[-10,0],[10, 20]),
                         Position.UNDER:([-20,-10],[0, 10], [20, -10])}
        basic_position = triangle_dict[self.position_flag]
        self.triangle_position = []
        center_x, center_y = self.navi_rect.center
        w_percent, h_percent = RATIO[self.window_rect.size]
        for l in basic_position:
            position = []
            position.append((l[0]*w_percent)+center_x)
            position.append((l[1]*h_percent)+center_y)
            self.triangle_position.append(position)
    
    # 画像表示
    def draw(self):
        # バーの描画
        self.screen.blit(self.navi_img, self.navi_rect)

        # 三角形の描画
        pygame.draw.polygon(self.screen, BLACK, self.triangle_position)

    
    def handle_click(self, pos):
        if self.navi_rect.collidepoint(pos):
            return True
        return False
