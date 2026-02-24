import re
from typing import Tuple, Any, Optional, Callable, Union

import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox

import pygame
from pygame.locals import *

from constans import *
from utils import *
from manager.sound_manager import sound_manager

# 各エレメントの基礎となるもの(基礎クラス)
class UIElement:
    def __init__(self, screen, parent=None, 
                 sound_type: str="click", click_rect: Optional[pygame.Rect]=None, 
                 row: int=0, col: int=0, focusable: bool=False, **kwargs):
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

# surfasceをキャッシュに保存しそこから取ってくるクラス
class SurfaceCache:
    def __init__(self):
        self._cache = {}

    def get_surface(self, font: pygame.font.Font, text: str, 
                    color: Tuple[int, int, int], back_color: Optional[Tuple[int, int, int]]=None):
        key = (id(font), text, color, back_color)
        surf = self._cache.get(key)
        if surf is None:
            surf = font.render(text, True, color, back_color)
            self._cache[key] = surf
        return surf

    def clear(self):
        self._cache.clear()

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

# ラベル
class Label(UIElement, RectSettingBase, TextBase):
    def __init__(self, screen, font_data: Tuple[str, int], text: str, 
                 x: int=0, y: int=0, centerx: Optional[int]=None, centery: Optional[int]=None, anchor: Tuple[str, str]=("left", "top"), 
                 text_color: Tuple[int, int, int]=BLACK, background_color: Optional[Tuple[int, int, int]]=None, 
                 hover_type: str="box", hover_line_bold: int=1, hover_text_color: Optional[Tuple[int, int, int]]=None, 
                 hover_back_color: Tuple[int, int, int]=WHITE,
                 sound_type: str="click", row: int=0, col: int=0, focusable: bool=False, parent: Optional[Any]=None, **kwargs):
        super().__init__(screen=screen, parent=parent, sound_type=sound_type, row=row, col=col, focusable=focusable, 
                         font_data=font_data, text=text, x=x, y=y, centerx=centerx, centery=centery, anchor=anchor, 
                         text_color=text_color, background_color=background_color, **kwargs)
        self.hover_type = hover_type
        self.hover_line_bold = hover_line_bold
        self.hover_text_color = hover_text_color
        self.hover_back_color = hover_back_color
        self.update_text_surface()

    def update_text_surface(self, color: Optional[Tuple[int, int, int]]=None):
        super().update_text_surface(color)
        self.rect = Rect(self.x, self.y, self.max_width, self.max_height)
        self.rect = self.set_rect(self.rect)
        self.set_base_rect(self.rect)

    # ラベルを描画する
    def draw(self):
        # マウスオーバー時背景に四角を描く
        if self.hovered or self.focused:
            rect = self.click_rect if self.click_rect else self.rect
            if self.hover_type == "box":
                pygame.draw.rect(self.parent_surface, self.hover_back_color, rect)
            elif self.hover_type == "line":
                pygame.draw.rect(self.parent_surface, self.hover_back_color, rect, self.hover_line_bold)

        # マウスオーバー時文字色を変える(入力があれば)
        color = self.text_color if not self.hovered else (self.hover_text_color if self.hover_text_color else self.text_color)
        self.update_text_surface(color)

        # 必要に応じて再描画をできる
        self.draw_text()

    def draw_text(self):
        current_y = self.rect.y
        for surface in self.text_surfaces:
            if self.anchor[0] == "right":
                text_rect = surface.get_rect(topright=(self.rect.right, current_y))
            else:
                text_rect = surface.get_rect(topleft=(self.rect.x, current_y))
            self.parent_surface.blit(surface, text_rect)
            current_y += text_rect.h + 2

    # スクリーンサイズ変更によるアップデート
    def relayout(self, screen, parent=None):
        super().relayout(screen, parent)
        self.rect = self.resize(self.screen_size)
        self.resize_font(self.screen_size)

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

# テキストフレームに表示する用のラベル
class TextFrameLabel(UIElement):
    def __init__(self, screen, frame_rect: pygame.Rect, parent: Optional[Any]=None, font_data: Tuple[str, int]=(FONT_PATH, FONT_SIZ), 
                 padding: int=10, row: int=0, col: int=0, focusable: bool=False, **kwargs):
        super().__init__(screen=screen, parent=parent, row=row, col=col, focusable=focusable, **kwargs)
        self.frame_rect = frame_rect
        self.font_data = font_data
        self.padding = padding

        # managers
        self.cache = SurfaceCache()
        self.renderer = RichTextRenderer(self.cache)

        # font
        self.font = setting_font(font_data[0], font_data[1], self.screen.get_size())

        # 表示データ
        self.rendered = []
        self.total_h = 0
        self.max_w = 0

        # テキストデータ(外から set_textで入れる)
        self.paragraphs = []

        # 最初に一度組み立て
        self.rebuild()

    # テキストを新しくセット
    def set_text(self, text: Optional[str]):
        if text is None:
            text = ""
        self.paragraphs = text.splitlines()
        self.rebuild()

    def rebuild(self):
        """
        段落 -> 折り返しレイアウト -> build -> rendered を作る
        """
        maxw = max(1, self.frame_rect.width - self.padding * 2)
        
        # layout
        lines = self.renderer.layout_paragraphs(self.paragraphs, self.font, maxw)

        # build_surface
        self.rendered, self.max_w, self.total_h = self.renderer.build_surface(lines, self.font)

    def relayout(self, screen, frame_rect: pygame.Rect, parent: Optional[Any]=None):
        super().relayout(screen, parent)
        self.frame_rect = frame_rect
        self.font = setting_font(self.font_data[0], self.font_data[1], screen.get_size())
        self.cache.clear()
        self.rebuild()
    
    def draw(self):
        ox = self.frame_rect.x + self.padding
        oy = self.frame_rect.y + self.padding
        visible_h = self.frame_rect.height - self.padding * 2

        for surf, x, y in self.rendered:
            if y >= visible_h:
                # この行がフレーム下端以降なら描画しない
                continue
            self.parent_surface.blit(surf, (ox + x, oy + y))

# ボタン
class Button(UIElement, ResizableMixin, TextBase):
    def __init__(self, screen, font_data: Tuple[str, int], text: str, rect: pygame.Rect, on_click: Optional[Callable]=None, 
                 text_color: Tuple[int, int, int]=BLACK, in_color: Tuple[int, int, int]=WHITE, out_color: Tuple[int, int, int]=GRAY, on_color: Tuple[int, int, int]=BLUE, 
                 parent: Optional[Any]=None, sound_type: str="click", row: int=0, col: int=0, focusable: bool=False, **kwargs):
        super().__init__(screen=screen, parent=parent, sound_type=sound_type, row=row, col=col, focusable=focusable, font_data=font_data, text=text, text_color=text_color, **kwargs)

        self.rect = Rect(rect)
        self.set_base_rect(self.rect)

        self.update_text_surface()

        # 色情報
        self.in_color = in_color
        self.out_color = out_color
        self.on_color = on_color

        # コールバック関数
        self.on_click = on_click

    # テキストの作成
    def update_text_surface(self):
        super().update_text_surface()

        # 文字列の最大幅がボタンの幅より大きければそれをボタンの幅にする
        if self.max_width > self.rect.w:
            self.rect.w = self.max_width + 4

        # 文字列の最大高さがボタンの高さより高ければそれをボタンの高さにする
        if self.max_height > self.rect.h:
            self.rect.h = self.max_height

    # ボタンの描画
    def draw_button(self):
        # マウスオーバー時ボタンの色を変える
        color = self.on_color if self.hovered else self.in_color

        # ボタンの内側
        pygame.draw.rect(self.parent_surface, color, self.rect)
        # ボタンの外枠
        pygame.draw.rect(self.parent_surface, self.out_color, self.rect, 2)

    # テキストの描画
    def draw_text(self):
        current_y = self.rect.y + ((self.rect.h - self.max_height) // 2)
        for surface in self.text_surfaces:
            h = surface.get_height()
            text_rect = surface.get_rect(center=(self.rect.centerx, current_y + h // 2))
            self.parent_surface.blit(surface, text_rect)
            current_y += h + 2

    # rectを設定する
    def set_rect(self, rect: pygame.Rect):
        self.rect = Rect(rect)
        self.set_base_rect(self.rect)
        self.update_text_surface()

    # 描画する
    def draw(self):
        self.draw_button()
        self.draw_text()

    # クリックされたときTrueを返す
    def is_clicked(self, pos):
        return self.collidepoint(pos)
    
    def handle_click(self, pos) -> bool:
        if self.is_clicked(pos):
            if self.sound_type == "click":
                sound_manager.play("クリック")
            else:
                sound_manager.play("選択")
            self.on_click() # コールバック関数を呼び出す
            return True
        return False
    
    # スクリーンサイズ変更によるアップデート
    def relayout(self, screen, parent=None):
        super().relayout(screen, parent)
        self.rect = self.resize(self.screen_size)
        self.resize_font(self.screen_size)

class ImageCache:
    def __init__(self):
        self.cache = {}

    def load(self, path: str):
        if path not in self.cache:
            try:
                # 画像の読み込み＆アルファ化(透明化)
                self.cache[path] = pygame.image.load(path).convert_alpha()
            except pygame.error as e:
                print(f"Error loading image: {e}")
        return self.cache[path]

# 画像表示
class Image(UIElement, RectSettingBase):
    def __init__(self, screen, path: str, cache: ImageCache=None, scale: float=None, 
                 x: int=0, y: int=0, centerx: Optional[int]=None, centery: Optional[int]=None, 
                 line_flag: bool=False, line_width: int=1, bg_flag: bool=False, size_wh: Optional[Tuple[int, int]]=None, 
                 anchor: Tuple[str, str]=("left", "top"), parent: Optional[Any]=None, sound_type: str="click", 
                 row: int=0, col: int=0, focusable: bool=False, **kwargs):
        super().__init__(screen=screen, parent=parent, sound_type=sound_type, row=row, col=col, focusable=focusable, x=x, y=y, centerx=centerx, centery=centery, anchor=anchor, **kwargs)

        path = f"{PATH}{PICTURE}{path}"
        self.cache = cache

        self.scale = scale                  # 比率を変えない拡大縮小率
        self.size_wh = size_wh              # 縦横サイズ指定

        self.original_img = None
        self.img = None
        self.rect = None
        self.create_image(path)
        self.rect = self.set_rect(self.rect)
        self.set_base_rect(self.rect)
    
        self.bg_flag = bg_flag
        self.line_flag = line_flag
        self.line_width = line_width

    # イメージを作成するよ
    def create_image(self, path: str):
        self.load_image(path)
        # サイズ変更
        self.set_transform()
        # 画像の位置取得
        self.rect = self.img.get_rect()

    # 画像の読み込み
    def load_image(self, path: str):
        if self.cache:
            self.original_img = self.cache.load(path)
        else:
            try:
                # 画像の読み込み＆アルファ化(透明化)
                self.original_img = pygame.image.load(path).convert_alpha()
            except pygame.error as e:
                print(f"Error loading image: {e}")

    # 画像のサイズ変更
    def set_transform(self, img: Optional[pygame.Surface]=None, scale: Optional[float]=None, size: Optional[Tuple[int, int]]=None):
        # 指定が無ければオリジナルイメージ
        if img is None:
            img = self.original_img

        # 指定が無ければ既定のサイズ
        if scale is None and size is None:
            scale = self.scale
            size = self.size_wh

        if scale:
            self.img = pygame.transform.rotozoom(img, 0, scale)
        elif size:
            self.img = pygame.transform.smoothscale(img, size)
        else:
            print("Warning: サイズ指定が不十分なため、画像を変更せずに使用します。")
            self.img = img

    # 縮小サイズを変更するよ
    def set_scale(self, new_scale: Optional[float]=None, new_size: Optional[Tuple[int, int]]=None):
        if new_scale:
            self.set_transform(scale=new_scale)
        elif new_size:
            self.set_transform(size=new_size)
        self.rect = self.img.get_rect(center=self.rect.center)

    # 位置をセットする（x,y座標、主にカーソル用)
    def set_position(self, x: Optional[int]=None, y: Optional[int]=None, centerx: Optional[int]=None, centery: Optional[int]=None, 
                     global_coords: bool=True):
        """
        global_coords=Trueの場合はスクリーン座標。Falseの場合は親座標として扱う
        """
        # グローバル座標を親座標に変換する
        if global_coords and self.parent is not None:
            if hasattr(self.parent, "get_global_offset"):
                ox, oy = self.parent.get_global_offset()
            else:
                # parentがscreenならoffset 0
                ox, oy = (0, 0)
            px = None if centerx is not None else (x - ox if x is not None else None)
            py = None if centery is not None else (y - oy if y is not None else None)
            pcx = centerx - ox if centerx is not None else None
            pcy = centery - oy if centery is not None else None
        
        else:
            # すでに親座標が渡されている場合
            px, py, pcx, pcy = x, y, centerx, centery

        # rectがNoneの場合は作る
        if self.rect is None:
            self.rect = self.img.get_rect()

        # anchorに応じて位置を設定
        if pcx is not None:
            self.rect.centerx = int(pcx)
        elif px is not None:
            if self.anchor[0] == "right":
                self.rect.right = int(px)
            elif self.anchor[0] == "center":
                self.rect.centerx = int(px)
            else:
                self.rect.x = int(px)

        if pcy is not None:
            self.rect.centery = int(pcy)
        elif py is not None:
            if self.anchor[1] == "bottom":
                self.rect.bottom = int(py)
            elif self.anchor[1] == "center":
                self.rect.centery = int(py)
            else:
                self.rect.y = int(py)
        
        #必要ならベース矩形を更新
        self.set_base_rect(self.rect)

    # 画像を切り抜くよ
    def cat_image(self, cat_rect: pygame.Rect):
        self.img = self.original_img.subsurface(cat_rect).copy()
        self.set_transform(img=self.img)
        self.rect = self.img.get_rect(topleft=self.rect.topleft)

    # 画像を表示するよ
    def draw(self):
        # 背景を白にする場合
        if self.bg_flag:
            pygame.draw.rect(self.parent_surface, WHITE, self.rect)

        # 画像の描写
        self.parent_surface.blit(self.img, self.rect)

        # 画像の枠を描画する場合
        if self.line_flag:
            pygame.draw.rect(self.parent_surface, BLACK, self.rect, self.line_width)

    # スクリーンサイズ変更によるアップデート
    def relayout(self, screen, parent=None):
        super().relayout(screen, parent)
        new_rect = self.resize(self.screen_size)
        if new_rect is None:
            self.set_base_rect(self.rect)
            new_rect = self.resize(self.screen_size)

        if self.scale:
            _, _, aspect_scale = get_scales(self.screen_size)
            new_scale = self.scale * aspect_scale
            self.set_scale(new_scale=new_scale)
            self.rect = self.img.get_rect()
            self.rect.topleft = (new_rect.x, new_rect.y)

        elif self.size_wh:
            new_size = get_new_size(self.screen_size, self.size_wh)
            self.set_scale(new_size=new_size)
            self.rect = self.img.get_rect()
            self.rect.topleft = (new_rect.x, new_rect.y)

        else:
            self.set_scale(new_size=(new_rect.w, new_rect.h))
            self.rect = new_rect

# ラベルの作成、再配置を共通化
class HasLabelBase:
    def __init__(self, label_text: Optional[str], label_padding: int=8, label_anchor: str="midleft", **kwargs):
        self.label_text = label_text
        self.label_padding = label_padding
        self.label_anchor = label_anchor    # "center", "midleft", "midright"などrectのアンカー
        self.label = None
        super().__init__(**kwargs)

    # Labelを作成
    def ensure_label(self, screen, font_data: Tuple[str, int], parent: Optional[Any]=None):
        if self.label is None and self.label_text is not None:
            # 初回のみ作成
            self.label = Label(screen, font_data, self.label_text, x=0, y=0, parent=parent)
        elif self.label:
            self.label.set_text(self.label_text)
    
    # 親側のrectに対してラベルを配置
    def place_label_to_rect(self, host_rect: pygame.Rect) -> None:
        if not self.label:
            return
        
        # ラベルのサーフェイス更新(幅・高さが必要)
        self.label.update_text_surface()

        # ラベルの描画矩形
        text_w, text_h = self.label.max_width, self.label.max_height
        r = pygame.Rect(0, 0, text_w, text_h)

        # アンカーに合わせて座標を決める
        if self.label_anchor == "center":
            r.center = host_rect.center
        elif self.label_anchor == "midright":
            r.midright = (host_rect.right - self.label_padding, host_rect.centery)
        else:
            r.midleft = (host_rect.left + self.label_padding, host_rect.centery)

        # Label自身がrectを持つので更新
        self.label.x = r.x
        self.label.y = r.y
        self.label.rect = r

# ボックス描画を共通化
class BoxStyleBase:
    def __init__(self, fill_color: Optional[Tuple[int, int, int]]=None, border_color: Optional[Tuple[int, int, int]]=BLACK, 
                 border_width: int=2, under_line: bool=False, **kwargs):
        self.fill_color = fill_color
        self.border_color = border_color
        self.border_width = border_width
        self.under_line = under_line
        super().__init__(**kwargs)

    # ボックスを描画する
    def draw_box_rect(self, parent, rect: pygame.Rect):
        if self.fill_color is not None:
            pygame.draw.rect(parent, self.fill_color, rect)

        if self.under_line:
            pygame.draw.line(parent, self.border_color, (rect.x, rect.bottom-1), (rect.right-1, rect.bottom-1), self.border_width)

        else:
            pygame.draw.rect(parent, self.border_color, rect, self.border_width)

# インプットボックス
class InputBox(UIElement, HasLabelBase, BoxStyleBase, ResizableMixin):
    def __init__(self, screen, root, font_data: Tuple[str, int], rect: pygame.Rect, label_text: str="", 
                 input_flag: bool=True, line_bold: int=2, 
                 sound_type: str="click", row: int=0, col: int=0, focusable: bool=False, parent: Optional[Any]=None, **kwargs):
        super().__init__(screen=screen, parent=parent, sound_type=sound_type, row=row, col=col, focusable=focusable, label_text=label_text, label_padding=10, label_anchor="center", fill_color=WHITE if input_flag else None, border_width=line_bold, under_line=True, **kwargs)
        self.root = root

        self.font_data = font_data
        self.font = pygame.font.Font(self.font_data[0], self.font_data[1])

        self.rect = rect
        self.set_base_rect(self.rect)

        self.input_flag = input_flag
        
        # 1度だけラベルを作成
        self.create_label()

    # ラベルを作成
    def create_label(self):
        self.ensure_label(self.screen, self.font_data, self.parent)
        self.place_label_to_rect(self.rect)

    # フラグを設定して背景色を変える
    def set_input_flag(self, flag: bool):
        self.input_flag = flag
        self.fill_color = WHITE if flag else None

    # ラベルの更新
    def update_label(self, new_text: str):
        self.label_text = new_text
        self.create_label()

    # ラベルに表示されている値を取得する
    def get_value(self) -> Union[int, str]:
        # ラベルに表示されている文字を、数字ならintにしてそうでないなら文字列として返す
        try:
            return int(self.label_text)
        except ValueError:
            return self.label_text

    # 入力処理
    def input_process(self, title, text, min, max, value_type, num_characters):
        # カスタムダイアログに入力された値を取得してラベルを更新する
        with TopmostManager(self.root):
            dialog = CustomDialog(self.root, title, f"{text}を入力してください", self.label_text, value_type, min, max, num_characters)
            value = dialog.result

        if value is not None:
            self.update_label(f"{value}")

    # 描画
    def draw(self):
        # 入力ボックス
        self.draw_box_rect(self.parent_surface, self.rect)
        
        # ラベルがあれば描写
        if self.label:
            self.place_label_to_rect(self.rect)
            self.label.draw()

    # フォントサイズ変更
    def resize_font(self, screen_size: Tuple[int, int]):
        self.font = setting_font(self.font_data[0], self.font_data[1], screen_size)
        self.create_label()

    # スクリーンサイズ変更によるアップデート
    def relayout(self, screen, parent=None):
        super().relayout(screen, parent)
        self.rect = self.resize(self.screen_size)
        self.resize_font(self.screen_size)

# 箱をクラスにするよ (主にプルダウンで使ってるよ)
class Box(UIElement):
    def __init__(self, screen, rect: pygame.Rect, parent: Optional[Any]=None, row: int=0, col: int=0, focusable: bool=False, **kwargs):
        super().__init__(screen, parent, row, col, focusable, **kwargs)
        self.rect = rect

    def draw(self):
        pygame.draw.rect(self.parent_surface, GRAY, self.rect)
        pygame.draw.rect(self.parent_surface, WHITE, (self.rect.x+1, self.rect.y+1, self.rect.w-2, self.rect.h-2))

# プルダウン機能
class PullDown(UIElement, ResizableMixin):
    def __init__(self, screen, font_data: Tuple[str, int], rect: pygame.Rect, item_list: List[str], 
                 label_text: str="", pd_h: int=285, 
                 parent: Optional[Any]=None, sound_type: str="click", row: int=0, col: int=0, focusable: bool=False, **kwargs):
        super().__init__(screen=screen, parent=parent, sound_type=sound_type, row=row, col=col, focusable=focusable, **kwargs)

        self.font_data = font_data
        self.font = pygame.font.Font(self.font_data[0], self.font_data[1])

        # 基準位置
        self.rect = rect
        self.set_base_rect(self.rect)

        # プルダウンに表示するリスト
        self.item_list = item_list
        # ボックスに表示される文字
        self.label_text = label_text

        # キャッシュ
        self.cache = SurfaceCache()

        # 見た目用パラメータ
        self.padding = 10
        self.pd_h = pd_h            # プルダウンボックスの最大高さ

        # プルダウンする前のボックス
        self.create_box()
        
        # ボックスに表示される ▼ と ラベル(1回だけ作成する)
        self.triangle = Label(self.screen, self.font_data, "▼", parent=parent)
        self.label = Label(self.screen, self.font_data, self.label_text, parent=parent) if self.label_text else None
        self._place_triangle_and_label()

        # プルダウンのリスト（描画用キャッシュ）
        self.entries = []       # entries:[(text, surface, text_rect, hit_rect), ...]
        self.list_box = None
        self._layout_dirty = True   # レイアウト再計算が必要か
        self._hovered_item = None   # 前回 hoverを覚えておく(サウンド用)

        # hover状態
        self.box_hovered = False
        self.list_hovered = False

    # ボックスのrectを計算
    def _calc_box_rect(self) -> pygame.Rect:
        # ラベル候補 + ▼ を含めた最大幅
        texts = self.item_list + ([self.label_text] if self.label_text else [])
        if texts:
            max_text_w = max(self.font.size(text)[0] for text in texts)
        else:
            max_text_w = 0

        tri_w = self.font.size("▼")[0]
        box_w = max((max_text_w + tri_w + self.padding * 3), self.rect.w)
        box_h = max((self.font.get_height() + self.padding * 2), self.rect.h)
        return Rect(self.rect.x, self.rect.y, box_w, box_h)

    # プルダウンする前のボックスを作成する
    def create_box(self):
        self.box_rect = self._calc_box_rect()           # ボックスのrectを算出
        self.box = Box(self.screen, self.box_rect, self.parent)

    # ラベルの位置を調整する
    def _place_triangle_and_label(self):
        # ▼は右寄せ
        self.triangle.update_text_surface()
        tri_rect = self.triangle.text_surfaces[0].get_rect()
        tri_rect.midright = (self.box.rect.right - self.padding, self.box.rect.centery)
        self.triangle.rect = tri_rect
        self.triangle.x, self.triangle.y = tri_rect.x, tri_rect.y

        # labelは左寄せ
        if self.label:
            self.label.set_text(self.label_text)
            self.label.update_text_surface()
            lbl_w, lbl_h = self.label.max_width, self.label.max_height
            r = pygame.Rect(0, 0, lbl_w, lbl_h)
            r.midleft = (self.box.rect.left + self.padding, self.box.rect.centery)
            self.label.rect = r
            self.label.x, self.label.y = r.x, r.y

    # プルダウンのレイアウト
    def _ensure_layout(self):
        # item_list、位置変更、高さ変更などがあった時だけ再計算
        if not self._layout_dirty:
            return
        
        # 以前のアイテムをクリア        
        self.entries.clear()

        # 一列の幅（ボックス幅に合わせる）
        w = self.box.rect.w
        y0 = self.box.rect.bottom   # ボックスの下から展開
        cur_x, cur_y = self.box.rect.x + self.padding, y0 + self.padding   # 現在の位置
        max_w = w       # 横に広がった際の幅

        for text in self.item_list:
            surf = self.cache.get_surface(self.font, text, BLACK) # キャッシュ利用
            text_rect = surf.get_rect(topleft=(cur_x, cur_y))
            # クリック判定はボックス幅いっぱいに
            hit_rect = Rect(cur_x, cur_y, w, text_rect.h)

            # 項目名とそのsurface, rect、クリック判定用rectを辞書に登録していく
            self.entries.append((text, surf, text_rect, hit_rect))

            # 表示位置を下にずらす
            cur_y += text_rect.h + 1
            
            # プルダウンボックスより下は隣に表示する
            if cur_y >= (y0 + self.pd_h - (self.padding * 2)):
                cur_x += w
                max_w += w
                cur_y = y0 + self.padding

        # ボックスのサイズよりリストの量が少なければボックスサイズをリストのサイズに合わせる
        if max_w == self.box.rect.w:        # 一列しかない場合
            box_heigth = cur_y - y0
            if box_heigth and box_heigth < self.pd_h:   # アイテム全体の高さよりボックス最大値の高さが多い場合
                self.pd_h = box_heigth + self.padding
        else:
            # ボックスサイズが拡大していれば幅をpadding分広げる
            max_w += self.padding * 2

        # 外枠を作る
        self.list_box = Box(self.screen, Rect(self.box.rect.x, y0, max_w, self.pd_h), self.parent)
        self._layout_dirty = False

    # 表示位置を変更する
    def update_position(self, x: Optional[int]=None, y: Optional[int]=None, centerx: Optional[int]=None, centery: Optional[int]=None, 
                        anchor: Tuple[str, str]=("left", "top")):
        if x is not None:
            if anchor[0] == "right":
                self.rect.right = x
            else:
                self.rect.x = x

        if y is not None:
            if anchor[1] == "bottom":
                self.rect.bottom = y
            else:
                self.rect.y = y

        if centerx is not None:
            self.rect.centerx = centerx
        if centery is not None:
            self.rect.centery = centery

        # ボックス再計算⇒ラベル再配置⇒レイアウト無効化
        self.create_box()
        self._place_triangle_and_label()
        self._layout_dirty = True

    # ラベルの更新
    def update_label(self, new_text: str):
        self.label_text = new_text
        if self.label is None:
            self.label = Label(self.screen, self.font_data, new_text, parent=self.parent)
        else:
            self.label.set_text(new_text)
        self._place_triangle_and_label()

    # ボックスの表示
    def draw(self, is_dropped: bool):
        # ボックスと▼
        self.box.draw()
        self.triangle.draw()

        # テキストがあればテキスト
        if self.label:
            self.label.draw()

        # ドロップしている時だけリストを描画
        if is_dropped:
            self._ensure_layout()
            self.list_box.draw()

            for text, surf, text_rect, hit_rect in self.entries:
                # hoverされてる時は背景色を変える
                if self._hovered_item == text:
                    pygame.draw.rect(self.parent_surface, BLUE, hit_rect)
                else:
                    pygame.draw.rect(self.parent_surface, WHITE, hit_rect)

                # テキストを描画
                self.parent_surface.blit(surf, text_rect)

    def collidepoint(self, pos):
        return self.box.collidepoint(pos)

    # クリック時の動作
    def handle_click(self, pos: Tuple[int, int], is_dropped: bool) -> Optional[str]:
        if is_dropped and self.list_box and self.list_box.collidepoint(pos):
            hit_pos = pos_to_local(pos, self.parent)
            for text, surf, text_rect, hit_rect in self.entries:
                if hit_rect.collidepoint(hit_pos):
                    sound_manager.play("クリック")
                    return text
        return None
    
    # マウスオーバー時の動作
    def handle_mouse_hover(self, pos: Tuple[int, int], is_dropped: bool):
        if is_dropped:
            self._ensure_layout()
            hovered = None
            hit_pos = pos_to_local(pos, self.parent)
            for text, surf, text_rect, hit_rect in self.entries:
                if hit_rect.collidepoint(hit_pos):
                    hovered = text
                    break

            if hovered != self._hovered_item:
                # 初回 or 切り替えだけでサウンド
                if hovered is not None:
                    sound_manager.play("カーソル移動")
                self._hovered_item = hovered
                
        # ボックスhover（縁取り）
        is_box_hover = self.box.collidepoint(pos)
        if is_box_hover and not self.box_hovered:  # 初めてホバーした時
            sound_manager.play("カーソル移動")
        self.box_hovered = is_box_hover
        if is_box_hover:
            pygame.draw.rect(self.parent_surface, BLACK, self.box.rect, 2)

    # フォントサイズ変更
    def resize_font(self, screen_size: Tuple[int, int]):
        self.font = setting_font(self.font_data[0], self.font_data[1], screen_size)
        for label in (self.label, self.triangle):
            label.resize_font(screen_size)
        self._place_triangle_and_label()
        self._layout_dirty = True

    # スクリーンサイズ変更によるアップデート
    def relayout(self, screen, parent=None):
        super().relayout(screen, parent)
        self.rect = self.resize(self.screen_size)
        self.resize_font(self.screen_size)

# 主人公の名前・HP・MPを左上、現在地を右上に表示する
class PlayerDataView:
    def __init__(self, screen, room_surface_rect, player, girl, game_state, flags):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.room_surface_rect = room_surface_rect

        self.font_data = (FONT_PATH, SMALL_SIZ)
        self.font = setting_font(FONT_PATH, SMALL_SIZ, self.screen_size)

        self.player = player
        self.room_flag = game_state.room
        self.time = str(game_state.time)     # デバッグ用

        self.girl = girl
        self.girl_fellow = flags.get_flag("girl", "fellow")
        self.girl_alive = flags.get_flag("girl", "girl_alive")

        self.create_surface()

        self.create_image()

        self.status_labels = None
        self.setting_labels()

    # surfaceを作成する
    def create_surface(self):
        #self.size = (300, 100)
        if self.girl_fellow and not self.girl_alive:
            width = 400
        else:
            width = 200
        height = 150
        self.size = (width, height)

        self.size = get_new_size(self.screen_size, self.size)
        self.bg_surface = pygame.Surface(self.size)
        self.rect = self.bg_surface.get_rect()

        self.bg_surface.fill(BLACK)
        self.bg_surface.set_alpha(100)

    # imageを作成する
    def create_image(self):
        _, _, aspect_scale = get_scales(self.screen_size)
        size = 0.4 * aspect_scale

        self.player_img = Image(screen=self.screen, path=self.player.image, scale=size, x=self.rect.x+10, y=self.rect.y+10, line_flag=True, bg_flag=True)
        self.player_img.cat_image(pygame.Rect(100, 50, 200, 300))

        if not self.girl_alive:
            girl_img = "Girl_pale_downcast_eyes_dark.png"
        else:
            girl_img = self.girl.image
        self.girl_img = Image(screen=self.screen, path=girl_img, scale=size, x=0, y=0, line_flag=True, bg_flag=True)
        self.girl_img.cat_image(pygame.Rect(50, 0, 200, 300))

        #self.girl_img.set_rect(x=self.player_img.rect.x+self.player_img.rect.w+100, y=self.player_img.rect.y, centerx=None, centery=None)

    def setting_labels(self):
        player_labels = self.create_label(self.player, self.player_img)
        girl_labels = self.create_label(self.girl, self.girl_img)

        current_room_label = Label(self.screen, font_data=self.font_data, text=ROOM_NAME[self.room_flag], x=self.room_surface_rect.right, y=self.room_surface_rect.y - 30, anchor=("right", "top"), text_color=WHITE)
        current_time_label = Label(self.screen, font_data=self.font_data, text=self.time, x=current_room_label.rect.x - 10, y=current_room_label.rect.y, anchor=("right", "top"), text_color=WHITE)   # デバッグ用

        self.status_labels = player_labels
        if self.girl_fellow or not self.girl_alive:
            self.status_labels += girl_labels
        self.status_labels += [current_room_label, current_time_label]

    def create_label(self, character, character_img):
        margin = 5
        name_label = Label(self.screen, font_data=self.font_data, text=character.name, x=character_img.rect.x + character_img.rect.w + 10, y=character_img.rect.y + margin, text_color=WHITE)
        hp_label = Label(self.screen, font_data=self.font_data, text=f"HP/{character.HP}", x=name_label.rect.x, y=name_label.rect.y + name_label.rect.h + margin, text_color=WHITE)
        mp_label = Label(self.screen, font_data=self.font_data, text=f"MP/{character.MP}", x=name_label.rect.x, y=hp_label.rect.y + hp_label.rect.h + margin, text_color=WHITE)
        return [name_label, hp_label, mp_label]

    def draw(self):
        self.screen.blit(self.bg_surface, self.rect.topleft)

        if self.player_img:
            self.player_img.draw()
        if self.girl_img and self.girl_fellow:
            self.girl_img.draw()

        for label in self.status_labels:
            label.draw()

    def update(self, player, girl, game_state, flags):
        self.player = player
        self.girl = girl
        self.room_flag = game_state.room
        self.time = str(game_state.time)     # 時間表示：デバッグ用

        # 少女の生死によって表示を変更する
        new_girl_alive = flags.get_flag("girl", "alive")
        if self.girl_alive != new_girl_alive:
            self.create_image()
        self.girl_alive = new_girl_alive

        # 少女のフォローの可否によって表示を変更する
        new_girl_fellow = flags.get_flag("girl", "fellow")
        if self.girl_fellow != new_girl_fellow:
            self.create_surface()
        self.girl_fellow = new_girl_fellow

        
        self.status_labels = None
        self.setting_labels()
        self.draw()

# simpledialogの代わり(モーダルはうまくいかないがエラーメッセージの日本語化はできた)
class CustomDialog(simpledialog.Dialog):
    def __init__(self, parent, title="title", text="文字列を入力してください", input_value="", input_type=None, min_value=0, max_value=99, num=None):
        
        self.text = text    # ダイアログに表示するテキスト
        self.input_type = input_type
        self.min_value = min_value      # 入力できる最小値
        self.max_value = max_value      # 入力できる最大値
        self.num = num                  # 入力可能文字数
        self.value = tk.StringVar()
        self.value.set(input_value)
        
        super().__init__(parent, title)

    def body(self, frame):
        # ラベル作成
        label = ttk.Label(frame, text=self.text).pack(pady=10)

        # エントリー作成
        vcmd = (self.register(validate_input), "\%d", "%P", self.input_type, self.num)
        func = ime_on if self.input_type == str else ime_off
        self.entry = ttk.Entry(frame, textvariable=self.value, validate="key", validatecommand=vcmd)
        self.entry.pack(pady=10)
        self.entry.bind(sequence="ForcusIn", func=func)

        return self.entry

    # OKボタンを押したとき
    def apply(self):
        if self.validate():
            try:
                self.result = int(self.value.get())
            except ValueError:
                self.result = self.value.get()

    # 入力を検証する
    def validate(self):
        if self.input_type == int:
            if not validate_int(self.value.get()):
                with TopmostManager(self):
                    messagebox.showerror("入力エラー", f"数字を入力してください")
                return False
            
            value = int(self.value.get())
            # 値がmin-maxの間かどうかをチェックする
            if not (self.min_value <= value <= self.max_value):
                with TopmostManager(self):
                    messagebox.showerror("入力エラー", f"入力値は{self.min_value}から{self.max_value}の間で入力してください")
                return False
            
        if not validate_num(self.value.get(), self.num):
            with TopmostManager(self):
                messagebox.showerror("入力エラー", f"文字数制限を超えています")
            return False

        return True
