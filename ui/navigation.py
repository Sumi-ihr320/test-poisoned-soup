from typing import List, Tuple, Optional
import pygame

from constans import FONT_PATH, FONT_SIZ, BLACK, RED, Position, PATH, PICTURE
from utils import setting_font, get_scales
from ui.ui_elements import Label
from ui.ui_base import UIElement
from input.focus_manager import FocusManager

# キャラシのページナビゲーション
class CharasheetNavigation:
    def __init__(self, screen, surface_rect: pygame.Rect):
        self.screen = screen

        # ナビゲーションを表示する基準となるシートや画像surfaceのrect
        self.surface_rect = surface_rect

        self.font_data = (FONT_PATH, FONT_SIZ)

        self.label_list = []
        self.navi_items = []
        self.create_labels()

    # ラベル群を作成
    def create_labels(self):
        font = setting_font(self.font_data[0], self.font_data[1], self.screen.get_size())
        font_height = font.render("→ 次へ", True, BLACK).get_height()
        y = self.surface_rect.bottom - 10 - font_height

        self.to_next = self.create_label(text="→ 次へ", x=self.surface_rect.right-10, y=y, anchor=("right", "top"))
        self.to_prev = self.create_label(text="← 戻る", x=self.surface_rect.left+10, y=y, col=1)
        self.to_finalize = self.create_label(text="完了", centerx=self.surface_rect.centerx, y=y, col=2)

        # ラベルリスト
        self.label_list = [self.to_next, self.to_prev, self.to_finalize]

        # 各位置のナビゲーションをページごとに格納するリスト
        self.navi_items = [[self.to_next],
                           [self.to_next, self.to_prev],
                           [self.to_prev, self.to_finalize]]

    # ラベル作成
    def create_label(self, text: str, x: int=0, y: int=0, centerx: Optional[int]=None,
                     anchor: Tuple[str, str]=("left", "top"), col: int=0):
        label = Label(self.screen, font_data=self.font_data, text=text, 
                      x=x, y=y, centerx=centerx, anchor=anchor,
                      hover_back_color=None,
                      focusable=True, row=50, col=col)
        return label

    # フォーカスマネージャーに登録
    def register_focus(self, page: int, focus_manager: FocusManager):
        for navi in self.navi_items[page]:
            focus_manager.register(navi)

    # フォーカスマネージャーから削除
    def unregister_focus(self, page: int, focus_manager: FocusManager):
        for navi in self.navi_items[page]:
            if navi in focus_manager.elements:
                focus_manager.elements.remove(navi)

    def handle_click(self, page: int, pos: Tuple[int, int]) -> Optional[str]:
        click_set = {self.to_next: "next",
                     self.to_prev: "prev",
                     self.to_finalize:"finalize"}
        navis = self.navi_items[page]
        for navi in navis:
            if navi.collidepoint(pos):
                return click_set.get(navi, None)
        return None

    def relayout(self, screen, surface_rect: pygame.Rect):
        self.screen = screen
        self.surface_rect = surface_rect
        for label in self.label_list:
            label.relayout(screen)

    def draw(self, page: int):
        navis = self.navi_items[page]
        for navi in navis:
            navi.draw()
            pygame.draw.rect(self.screen, RED, navi.rect, 2)    # デバッグ用

# メインプレイで使うナビゲーション
class MainNavigation:
    def __init__(self, screen, surface_rect: pygame.Rect):
        self.screen = screen

        # ナビゲーションを表示する基準となるシートや画像surfaceのrect
        self.surface_rect = surface_rect

        self.navi_items = {}    # 各位置のナビゲーションを格納する辞書
        for position in Position:
            self.create_navigation(position)

    # ナビゲーションの作成
    def create_navigation(self, position: Position):
        self.navi_items[position] = PageNavigation(self.screen, self.surface_rect, position)

    def set_up_navigation(self, positions: List[Position]):
        


    # 過去のフォーカスを削除して新しいフォーカスを登録する
    def update_register(self, focus_manager: FocusManager):


    # フォーカスを全て登録する
    def register_all(self, focus_manager: FocusManager):
        for navi in self.navi_items.values():
            focus_manager.register(navi)

    # フォーカスを全て削除する
    def unregister_all(self, focus_manager: FocusManager):
        for navi in self.navi_items.values():
            focus_manager.elements.remove(navi)

    def relayout(self, screen, surface_rect: pygame.Rect):
        self.screen = screen
        self.surface_rect = surface_rect
        for navi in self.navi_items.values():
            navi.relayout(screen, surface_rect)

    def draw(self):
        """現在の位置にあるナビゲーションを描画する"""
        for navi in self.navi_items.values():
            navi.draw()

    def handle_click(self, pos: Tuple[int, int]) -> Optional[Position]:
        """ナビゲーションのクリック処理"""
        for position, navi in self.navi_items.items():
            if navi.handle_click(pos):
                return position
        return None

# ページ移動用の矢印表示するよ
class PageNavigation(UIElement):
    def __init__(self, screen, surface_rect: pygame.Rect, position_flag: Position=Position.RIGHT,
                 parent=None, sound_type="click", click_rect=None, row=0, col=0, focusable=True, **kwargs):
        super().__init__(screen, parent, sound_type, click_rect, row, col, focusable, **kwargs)

        # 基準となる画像等surfaceのrect
        self.surface_rect = surface_rect

        # どの位置にナビゲーションを設置するのかのフラグ
        self.position_flag = position_flag

        # 画像の設定
        self.navi_img = None
        self.load_image()
        self.set_scale()

        # 三角形の基本情報
        self.triangle_dict = {Position.RIGHT:([-10,-20], [10,0], [-10,20]),
                              Position.LEFT:([10,-20],[-10,0],[10, 20]),
                              Position.UNDER:([-20,-10],[0, 10], [20, -10])}

        # 位置の設定
        self.rect = None
        self.position_calculation()
        self.triangle_position_calculation()

    # ナビゲーション用画像のロード
    def load_image(self):
        img_path = f"{PATH}{PICTURE}navigate.png"
        self.navi_img = pygame.image.load(img_path).convert_alpha()

    # 画像サイズの変更
    def set_scale(self):
        scale_x, scale_y, _ = get_scales(self.screen_size)
        if self.position_flag == Position.UNDER:
            self.navi_img = pygame.transform.rotate(self.navi_img, 90)
            self.navi_img = pygame.transform.scale(self.navi_img, (int(500*scale_x),int(40*scale_y)))
        else:
            self.navi_img = pygame.transform.scale(self.navi_img, (int(40*scale_x),int(355*scale_y)))

    # ナビゲーションの場所を計算
    def position_calculation(self):
        self.rect = self.navi_img.get_rect()

        # x位置
        if self.position_flag == Position.UNDER:
            self.rect.center = (self.screen.get_width() // 2, self.surface_rect.bottom - 10)
        else:
            self.rect.centerx = self.surface_rect.right if self.position_flag == Position.RIGHT else self.surface_rect.left
            self.rect.centery = self.surface_rect.centery

    # 三角形の場所を計算する
    def triangle_position_calculation(self):
        basic_position = self.triangle_dict[self.position_flag]
        self.triangle_position = []
        scale_x, scale_y, _ = get_scales(self.screen_size)
        center_x, center_y = self.rect.center
        for l in basic_position:
            position = []
            position.append((l[0]*scale_x)+center_x)
            position.append((l[1]*scale_y)+center_y)
            self.triangle_position.append(position)

    def relayout(self, screen, surface_rect: pygame.Rect):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.surface_rect = surface_rect
        self.set_scale()
        self.position_calculation()
        self.triangle_position_calculation()

    # 画像表示
    def draw(self):
        # バーの描画
        self.screen.blit(self.navi_img, self.rect)

        # 三角形の描画
        pygame.draw.polygon(self.screen, BLACK, self.triangle_position)

