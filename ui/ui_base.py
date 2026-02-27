import re
from typing import List, Tuple, Optional

import pygame

from constans import BLACK, WHITE
from utils import pos_to_local, pos_to_global, setting_font, parse_color_tags, get_scales
from ui.ui_cache import SurfaceCache
from manager.sound_manager import sound_manager

# 各エレメントの基礎となるもの(基礎クラス)
class UIElement:
    def __init__(self, screen, parent=None, 
                 sound_type: str="click", click_rect: Optional[pygame.Rect]=None, 
                 row: int=0, col: int=0, focusable: bool=False,
                 hover_text: Optional[str]=None, **kwargs):
        self.screen = screen
        self.screen_size = screen.get_size()

        self.parent = parent

        self.parent_surface = parent.surface if parent is not None else screen

        self.rect = None
        self.click_rect = click_rect

        self.sound_type = sound_type

        self.row = row
        self.col = col
        self.focusable = focusable

        self.hovered = False
        self.focused = False

        self.hover_text = hover_text

        super().__init__(**kwargs)

    # フォーカス制御 ------------------------------------------
    def set_focus(self, value: bool):
        self.focused = value
        self.on_focus() if value else self.on_blur()

    # フォーカスされた時の処理（継承先でオーバーライド可能）
    def on_focus(self):
        self.focused = True

    # フォーカスが外れた時の処理（継承先でオーバーライド可能）
    def on_blur(self):
        self.focused = False

    def is_focusable(self):
        return self.focusable
    
    # 決定音を鳴らす
    def on_decide(self):
        if self.sound_type == "click":
            sound_manager.play("クリック")
        elif self.sound_type == "select":
            sound_manager.play("選択")
    
    # ホバー制御 ------------------------------------------
    def set_hover(self, value: bool):
        self.hovered = value

    # 描画・更新 -------------------------------------------
    # UI描画処理 -- 継承先で実装
    def draw(self):
        raise NotImplementedError

    # UI更新処理（キー入力やマウス操作の処理）
    def update(self):
        pass

    # 衝突判定 ---------------------------------------------
    # 指定した点が描画内かをチェック
    def collidepoint(self, pos) -> bool:
        # もしクリック範囲の指定があれば
        if self.click_rect:
            return self.click_rect.collidepoint(pos_to_local(pos, self.parent))
        else:
            return self.rect.collidepoint(pos_to_local(pos, self.parent))
    
    # 中心点を取得
    def get_center(self) -> Tuple[int, int]:
        return pos_to_global(self.rect.center, self.parent)

    # イベント系 -------------------------------------------
    # マウスクリックやホバーの処理（必要に応じてオーバーライド）
    def handle_mouse_event(self, event):
        pass

    # マウスオーバー時に音を鳴らす
    def handle_mouse_hover(self, pos):
        hover = self.collidepoint(pos)
        if hover and not self.hovered:  # 初めてホバーした時
            sound_manager.play("カーソル移動")
        self.hovered = hover

        # もしhover_textがあれば、ホバーしてる際にそれを返す
        if self.hover_text and hover:
            return self.hover_text
        return None

    # クリックした時にはクリック音を鳴らす
    def handle_click(self, pos) -> bool:
        if self.collidepoint(pos):
            self.on_decide()
            return True
        return False
    
    def relayout(self, screen, parent=None):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.parent = parent
        self.parent_surface = parent.surface if parent is not None else screen

# テキスト表示クラス
class TextBase:
    def __init__(self, font_data: Tuple[str, int], text: str, 
                 text_color: Tuple[int, int, int]=BLACK, background_color: Optional[Tuple[int, int, int]]=None, **kwargs):
        self.font_path = font_data[0]
        self.font_size = font_data[1]
        self.font = pygame.font.Font(self.font_path, self.font_size)

        self.cache = SurfaceCache()

        self.texts = text.splitlines()
        self.text_color = text_color
        self.background_color = background_color

        #self.update_text_surface()
        super().__init__(**kwargs)

    def update_text_surface(self, color: Optional[Tuple[int, int, int]]=None, back_color: Optional[Tuple[int, int, int]]=None):
        if color is None:
            color = self.text_color
        if back_color is None:
            back_color = self.background_color
        self.text_surfaces = []
        self.max_width, self.max_height = 0, 0
        for text in self.texts:
            surface = self.cache.get_surface(self.font, text, color, back_color)
            self.text_surfaces.append(surface)
            width, height = surface.get_size()
            if self.max_width < width:
                self.max_width = width
            self.max_height += height
        
    def set_text(self, text: str):
        self.texts = text.splitlines()
        self.update_text_surface()

    def set_text_color(self, color: Tuple[int, int, int]):
        self.text_color = color
        self.update_text_surface()

    def set_background_color(self, color: Tuple[int, int, int]):
        self.background_color = color
        self.update_text_surface()

    def set_font(self, new_font: pygame.font.Font):
        self.font = new_font
        self.update_text_surface()

    def resize_font(self, screen_size: Tuple[int, int]):
        self.font = setting_font(self.font_path, self.font_size, screen_size)
        self.update_text_surface()

# サイズ変更するmixin
class ResizableMixin:
    def __init__(self, **kwargs):
        self.base_rect = None   # 初期配置（元サイズ）
        super().__init__(**kwargs)
    
    def set_base_rect(self, rect: pygame.Rect):
        if self.base_rect is None:
            self.base_rect = rect.copy()

    def resize(self, screen_size: Tuple[int, int], anchor: Tuple[str, str]=("left", "top"), scale_mode: str="free") -> Optional[pygame.Rect]:
        """
        anchor: 固定する基準点（left, right, center / top, bottom, center）
        scale_mode: free→縦横別々, aspect→アスペクト比固定 
        """
        if not self.base_rect:
            return None
        
        scale_x, scale_y, aspect_scale = get_scales(screen_size)

        if scale_mode == "aspect":
            sx = sy = aspect_scale
        else:
            sx, sy = scale_x, scale_y

        new_rect = pygame.Rect(0, 0, int(self.base_rect.w * sx), int(self.base_rect.h * sy))

        if anchor[0] == "center":
            new_rect.centerx = int(self.base_rect.centerx * sx)
        elif anchor[0] == "right":
            new_rect.right = int(self.base_rect.right * sx)
        else:
            new_rect.x = int(self.base_rect.x * sx)

        if anchor[1] == "center":
            new_rect.centery = int(self.base_rect.centery * sy)
        elif anchor[1] == "bottom":
            new_rect.bottom = int(self.base_rect.bottom * sy)
        else:
            new_rect.y = int(self.base_rect.y * sy)

        return new_rect

# rect変更できるクラス
class RectSettingBase(ResizableMixin):
    def __init__(self, x: int=0, y: int=0, centerx: Optional[int]=None, centery: Optional[int]=None, 
                 anchor: Tuple[str, str]=("left", "top"), **kwargs):
        self.x = x
        self.y = y
        self.centerx = centerx
        self.centery = centery
        self.anchor = anchor
        super().__init__(**kwargs)

    def set_rect(self, rect: pygame.Rect) -> pygame.Rect:
        if self.x == "center":
            self.centerx = self.parent_surface.get_rect().centerx
        
        if self.centerx:
            rect.centerx = self.centerx
        
        else:
            if self.anchor[0] == "right":
                rect.right = self.x
            else:
                rect.left = self.x

        if self.y == "center":
            self.centery = self.parent_surface.get_rect().centery

        if self.centery:
            rect.centery = self.centery
        else:
            if self.anchor[1] == "bottom":
                rect.bottom = self.y
            else:
                rect.top = self.y
        return rect

# 高度なテキスト表示
class RichTextRenderer:
    def __init__(self, surface_cache: SurfaceCache):
        self.cache = surface_cache
        pass

    # テキストを色分けや画面幅などで行を変えたりいろいろして行ごとの塊を作る
    def layout_paragraphs(self, paragraphs: List[str], font: pygame.font.Font, max_width: int, 
                          default_color: Tuple[int, int, int]=WHITE) -> List[List[Tuple[str, Tuple[int, int, int], int]]]:
        """
        paragrapths: list[str]  (各段落は改行で分けられたもの)
        戻り値: lines: list of [(text, color, x), ...] (行ごと)
        """
        lines = []
        line_h = font.get_height()
        for para in paragraphs:
            segs = parse_color_tags(para)
            cur_line = []
            cur_x = 0

            for seg_text, color in segs:
                # 優先は単語単位で折り返す
                words = re.split(r'(\s+)', seg_text)    # 空白も保持
                for w in words:
                    if w == "":
                        continue
                    
                    # 幅チェック: すでに cur_x がある時の幅
                    test_w = self.cache.get_surface(font, w, color).get_width()
                    if cur_x + test_w < max_width or cur_x == 0:
                        # そのまま追加 (同じ色はマージせずチャンクとして追加)
                        cur_line.append((w, color, cur_x))
                        cur_x += test_w
                    else:
                        # 改行してから入れる
                        lines.append(cur_line)
                        cur_line = []

                        # word が長すぎて max_width に収まらない => 文字ごとに分割
                        if test_w > max_width:
                            # 文字単位で折る(単語が長い場合)
                            buf = ""
                            buf_x = 0
                            for ch in w:
                                test = buf + ch
                                tw = self.cache.get_surface(font, test, color).get_width()
                                if buf_x + tw <= max_width or buf == "":
                                    buf = test
                                else:
                                    cur_line.append((buf, color, buf_x))
                                    lines.append(cur_line)
                                    cur_line = []
                                    buf = ch
                                    buf_x = 0
                            if buf:
                                cur_line.append((buf, color, buf_x))
                                cur_x = buf_x + self.cache.get_surface(font, buf, color).get_width()
                        else:
                            # 普通に次行の先頭に置く
                            cur_line.append((w, color, 0))
                            cur_x = test_w
            # 段落の終わりで行を確定(空行も1行分として残す)
            lines.append(cur_line)
        return lines
    
    # surface化(各surfaceとx位置y位置、トータルのwidthとheightを返す)
    def build_surface(self, lines: List[List[Tuple[str, Tuple[int, int, int], int]]], font: pygame.font.Font) -> Tuple[List[Tuple[pygame.Surface, int, int]], int, int]:
        """
        lines -> (rendered_list, max_w, total_h)
        rendered_list: [(surface, x, y), ...]
        """
        rendered = []
        y = 0
        line_h = font.get_height()
        max_w = 0
        for line in lines:
            for text, color, x in line:
                surf = self.cache.get_surface(font, text, color)
                rendered.append((surf, x, y))
                max_w = max(max_w, x + surf.get_width())
            y += line_h
        total_h = y
        return rendered, max_w, total_h
