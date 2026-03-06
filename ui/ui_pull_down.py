from typing import Any, List, Optional, Tuple

import pygame
from pygame import Rect
from pygame.locals import *

from constans import BLACK, BLUE, WHITE
from utils import pos_to_local, setting_font
from ui.ui_base import UIElement, ResizableMixin
from ui.ui_cache import SurfaceCache
from ui.ui_elements import Box, Label
from manager.sound_manager import sound_manager


# プルダウン機能
class PullDown(UIElement, ResizableMixin):
    def __init__(self, screen, font_data: Tuple[str, int], rect: pygame.Rect, item_list: List[str], 
                 label_text: str="", pd_h: int=285, 
                 parent: Optional[Any]=None, sound_type: str="click", row: int=0, col: int=0, focusable: bool=False, 
                 hover_text: Optional[str]=None, **kwargs):
        super().__init__(screen=screen, parent=parent, sound_type=sound_type, row=row, col=col, focusable=focusable, hover_text=hover_text, **kwargs)

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

        self.is_dropped = False   # プルダウンが開いているかどうか
        self.focused_index = -1   # ドロップ内の内部フォーカス
        self.selected_item = None    # 選択されたアイテム

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

    def collidepoint(self, pos):
        return self.box.collidepoint(pos)

    # クリック時の動作
    def handle_click(self, pos: Tuple[int, int]) -> bool:
        if self.collidepoint(pos):
            self.on_decide()
            self.is_dropped = not self.is_dropped
            if self.is_dropped and self.focused_index < 0 and self.item_list:
                self.focused_index = 0
            return True

        if self.is_dropped and self.list_box and self.list_box.collidepoint(pos):
            hit_pos = pos_to_local(pos, self.parent)
            for text, surf, text_rect, hit_rect in self.entries:
                if hit_rect.collidepoint(hit_pos):
                    self.on_decide()
                    self.selected_item = text
                    self.update_label(self.selected_item)
                    self.is_dropped = False
                    return True
        return False
    
    # マウスオーバー時の動作
    def handle_mouse_hover(self, pos: Tuple[int, int]):
        if self.is_dropped:
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

        return self.hover_text if self.hover_text and self.collidepoint(pos) else None

    # キーボード操作時の動作
    def handle_keydown(self, event: pygame.event.Event) -> bool:
        # 閉じている時
        if not self.is_dropped:
            if event.key in (K_RETURN, K_SPACE):
                self.on_decide()
                self.is_dropped = True
                self.focused_index = 0
                return True
            return False
        
        # 開いている時
        if event.key == K_UP:
            self.focused_index = max(0, self.focused_index - 1)
            self._hovered_item = self.get_focused_item()
            sound_manager.play("カーソル移動")
            return True
        elif event.key == K_DOWN:
            self.focused_index = min(len(self.item_list)-1, self.focused_index + 1)
            self._hovered_item = self.get_focused_item()
            sound_manager.play("カーソル移動")
            return True
        elif event.key in (K_RETURN, K_SPACE):
            self.on_decide()
            self.selected_item = self.get_focused_item()
            self.update_label(self.selected_item)
            self.is_dropped = False
            return True
        elif event.key == K_ESCAPE:
            self.on_decide()
            self.is_dropped = False
            return True

        return False

    def get_focused_item(self):
        return self.item_list[self.focused_index] if self.item_list else None

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

    # ボックスの表示
    def draw(self):
        # ボックスと▼
        self.box.draw()
        # ボックスhover時 縁取り
        if self.box_hovered:
            pygame.draw.rect(self.parent_surface, BLACK, self.box.rect, 2)

        self.triangle.draw()

        # テキストがあればテキスト
        if self.label:
            self.label.draw()

        # ドロップしている時だけリストを描画
        if self.is_dropped:
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

