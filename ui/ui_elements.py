from typing import Tuple, Any, Optional, Callable

import pygame
from pygame.locals import *

from constans import BLACK, WHITE, GRAY, BLUE, PATH, PICTURE, FONT_PATH, FONT_SIZ
from utils import setting_font, get_new_size, get_scales
from ui.ui_base import UIElement, TextBase, ResizableMixin, RectSettingBase, RichTextRenderer
from ui.ui_cache import ImageCache, SurfaceCache
from manager.sound_manager import sound_manager

# ラベル
class Label(UIElement, RectSettingBase, TextBase):
    def __init__(self, screen, font_data: Tuple[str, int], text: str, 
                 x: int=0, y: int=0, centerx: Optional[int]=None, centery: Optional[int]=None, anchor: Tuple[str, str]=("left", "top"), 
                 text_color: Tuple[int, int, int]=BLACK, background_color: Optional[Tuple[int, int, int]]=None, 
                 hover_type: str="box", hover_line_bold: int=1, hover_text_color: Optional[Tuple[int, int, int]]=None, 
                 hover_back_color: Optional[Tuple[int, int, int]]=WHITE, hover_text: Optional[str]=None,
                 sound_type: str="click", row: int=0, col: int=0, focusable: bool=False, parent: Optional[Any]=None, **kwargs):
        super().__init__(screen=screen, parent=parent, sound_type=sound_type, row=row, col=col, focusable=focusable, 
                         font_data=font_data, text=text, x=x, y=y, centerx=centerx, centery=centery, anchor=anchor, 
                         text_color=text_color, background_color=background_color, hover_text=hover_text, **kwargs)
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
            if self.hover_back_color:
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

# テキストフレームに表示する用のラベル
class TextFrameLabel(UIElement):
    def __init__(self, screen, frame_rect: pygame.Rect, parent: Optional[Any]=None, font_data: Tuple[str, int]=(FONT_PATH, FONT_SIZ), 
                 padding: int=10, row: int=0, col: int=0, focusable: bool=False, hover_text: Optional[str]=None, **kwargs):
        super().__init__(screen=screen, parent=parent, row=row, col=col, focusable=focusable, hover_text=hover_text, **kwargs)
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
                 parent: Optional[Any]=None, sound_type: str="click", row: int=0, col: int=0, focusable: bool=False, 
                 hover_text: Optional[str]=None, **kwargs):
        super().__init__(screen=screen, parent=parent, sound_type=sound_type, row=row, col=col, focusable=focusable, font_data=font_data, text=text, text_color=text_color, hover_text=hover_text, **kwargs)

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

# 画像表示
class Image(UIElement, RectSettingBase):
    def __init__(self, screen, path: str, cache: ImageCache=None, scale: float=None, 
                 x: int=0, y: int=0, centerx: Optional[int]=None, centery: Optional[int]=None, 
                 line_flag: bool=False, line_width: int=1, bg_flag: bool=False, size_wh: Optional[Tuple[int, int]]=None, 
                 anchor: Tuple[str, str]=("left", "top"), parent: Optional[Any]=None, sound_type: str="click", 
                 row: int=0, col: int=0, focusable: bool=False, hover_text: Optional[str]=None, **kwargs):
        super().__init__(screen=screen, parent=parent, sound_type=sound_type, row=row, col=col, focusable=focusable, x=x, y=y, centerx=centerx, centery=centery, anchor=anchor, hover_text=hover_text, **kwargs)

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

# 箱をクラスにするよ (主にプルダウンで使ってるよ)
class Box(UIElement):
    def __init__(self, screen, rect: pygame.Rect, parent: Optional[Any]=None, row: int=0, col: int=0, focusable: bool=False, hover_text: Optional[str]=None, **kwargs):
        super().__init__(screen, parent, row, col, focusable, hover_text=hover_text, **kwargs)
        self.rect = rect

    def draw(self):
        pygame.draw.rect(self.parent_surface, GRAY, self.rect)
        pygame.draw.rect(self.parent_surface, WHITE, (self.rect.x+1, self.rect.y+1, self.rect.w-2, self.rect.h-2))

