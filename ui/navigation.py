from typing import List, Tuple, Optional, Any
import pygame

from constans import FONT_PATH, FONT_SIZ, BLACK, WHITE, RED, Position, PATH, PICTURE
from utils import setting_font, get_scales
from ui.ui_elements import Label
from ui.ui_base import UIElement
from input.focus_manager import FocusManager

# ナビゲーション用ラベル
class NavigationLabel(Label):
    def __init__(self, screen, font_data, text: str, position_flag: str="", 
                 x: int = 0, y: int = 0, centerx: Optional[int] = None, centery: Optional[int] = None, anchor: Tuple[str, str] = ("left", "top"), 
                 text_color = BLACK, background_color = None, hover_type: str = "box", hover_line_bold: int = 1, 
                 hover_text_color = None, hover_back_color = None, 
                 hover_text: Optional[str] = None, result_type: Optional[str] = "navigation", 
                 sound_type: str = "click", row: int = 50, col: int = 0, focusable: bool = True, parent: Any = None, **kwargs):
        super().__init__(screen, font_data=font_data, text=text, x=x, y=y, centerx=centerx, centery=centery, anchor=anchor, 
                         text_color=text_color, background_color=background_color, hover_type=hover_type, hover_line_bold=hover_line_bold, hover_text_color=hover_text_color, hover_back_color=hover_back_color, 
                         hover_text=hover_text, result_type=result_type, sound_type=sound_type, row=row, col=col, 
                         focusable=focusable, parent=parent, **kwargs)

        self.position_flag = position_flag

    def handle_click(self, pos) -> bool:
        if self.collidepoint(pos):
            self.on_decide()
            return self.position_flag
        return False

# キャラシのページナビゲーション
class CharasheetNavigation:
    def __init__(self, screen, surface_rect: pygame.Rect):
        self.screen = screen

        # ナビゲーションを表示する基準となるシートや画像surfaceのrect
        self.surface_rect = surface_rect

        self.font_data = (FONT_PATH, FONT_SIZ)

        self.label_list = []
        self.navi_items = []
        self._build()

    # ナビゲーションラベルを作成
    def _build(self):
        font = setting_font(self.font_data[0], self.font_data[1], self.screen.get_size())
        font_height = font.render("→ 次へ", True, BLACK).get_height()
        y = self.surface_rect.bottom - 10 - font_height

        self.to_next = self._create_label(text="→ 次へ", position_flag="next", x=self.surface_rect.right-10, y=y, anchor=("right", "top"))
        self.to_prev = self._create_label(text="← 戻る", position_flag="prev", x=self.surface_rect.left+10, y=y, col=1)
        self.to_finalize = self._create_label(text="完了", position_flag="finalize", centerx=self.surface_rect.centerx, y=y, col=2)

        # ラベルリスト
        self.label_list = [self.to_next, self.to_prev, self.to_finalize]

        # 各位置のナビゲーションをページごとに格納するリスト
        self.navi_items = [[self.to_next],
                           [self.to_next, self.to_prev],
                           [self.to_prev, self.to_finalize]]

    # ラベル作成
    def _create_label(self, text: str, position_flag: str, x: int=0, y: int=0, centerx: Optional[int]=None,
                     anchor: Tuple[str, str]=("left", "top"), col: int=0):
        label = NavigationLabel(self.screen, font_data=self.font_data, text=text, position_flag=position_flag,
                                x=x, y=y, centerx=centerx, anchor=anchor, col=col)
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

    """
    def handle_click(self, page: int, pos: Tuple[int, int]) -> Optional[str]:
        click_set = {self.to_next: "next",
                     self.to_prev: "prev",
                     self.to_finalize:"finalize"}
        navis = self.navi_items[page]
        for navi in navis:
            if navi.collidepoint(pos):
                return click_set.get(navi, None)
        return None
    """

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

# ページ移動用の矢印表示するよ
class PageNavigation(UIElement):
    def __init__(self, screen, surface_rect: pygame.Rect, position_flag: Position=Position.RIGHT,
                 parent=None, result_type: Optional[str]="navigation", sound_type: str="click", click_rect: Optional[pygame.Rect]=None, 
                 row: int=0, col: int=0, focusable: bool=True, **kwargs):
        super().__init__(screen, parent=parent, result_type=result_type, sound_type=sound_type, click_rect=click_rect, row=row, col=col, focusable=focusable, **kwargs)

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

    def handle_click(self, pos) -> bool:
        if self.collidepoint(pos):
            self.on_decide()
            return self.position_flag
        return None

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

# メインプレイで使うナビゲーション
class MainNavigation:
    def __init__(self, screen, surface_rect: pygame.Rect):
        self.screen = screen

        # ナビゲーションを表示する基準となるシートや画像surfaceのrect
        self.surface_rect = surface_rect

        self.navi_items = {}        # 各位置のナビゲーション一覧
        for position in Position:
            self.create_navigation(position)

        self.current_navis = {}     # 現在のページに表示するナビゲーション

    # ナビゲーションの作成
    def create_navigation(self, position: Position):
        self.navi_items[position] = PageNavigation(self.screen, self.surface_rect, position)

    # 現在のページに表示するナビゲーションをセットする
    def setup_navigation(self, positions: List[Position]):
        self.current_navis.clear()
        for position in positions:
            self.current_navis[position] = self.navi_items[position]

    # 過去のフォーカスを削除して現在のnavigationのフォーカスを登録する
    def update_register(self, focus_manager: FocusManager):
        self.unregister_all(focus_manager)
        for navi in self.current_navis.values():
            focus_manager.register(navi)

    # フォーカスを全て登録する
    def register_all(self, focus_manager: FocusManager):
        for navi in self.navi_items.values():
            focus_manager.register(navi)

    # フォーカスを全て削除する
    def unregister_all(self, focus_manager: FocusManager):
        for navi in self.navi_items.values():
            if navi in focus_manager.elements:
                focus_manager.elements.remove(navi)

    def relayout(self, screen, surface_rect: pygame.Rect):
        self.screen = screen
        self.surface_rect = surface_rect
        for navi in self.navi_items.values():
            navi.relayout(screen, surface_rect)

    def draw(self):
        """現在の位置にあるナビゲーションを描画する"""
        for navi in self.current_navis.values():
            navi.draw()

