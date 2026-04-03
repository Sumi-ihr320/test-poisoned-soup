import pygame

from constans import FONT_PATH, FONT_SIZ, WHITE, BLACK_ALPHA
from utils import setting_font
from ui.ui_elements import Image
from ui.ui_cache import SurfaceCache
from ui.ui_base import RichTextRenderer

class LogView:
    def __init__(self, screen, parent=None, font_data=(FONT_PATH, FONT_SIZ), padding=12, text_color=WHITE,
                 max_entries=500, block_spacing=8):
        self.screen = screen
        self.screen_size = screen.get_size()

        self.parent = parent
        self.parent_surface = parent.surface if parent is not None else screen

        self.frame_rect = None
        self._setting_rect()
        self.padding = padding
        
        self.font_data = font_data
        self.font = self._entry_font()
        self.text_color = text_color

        self.max_entries = max_entries
        self.block_spacing = block_spacing

        # 共有キャッシュ/レンダラー
        self.cache = SurfaceCache()
        self.renderer = RichTextRenderer(self.cache)

        # entries: list of dict {'text':str, 'rendered':[(surf, x, y), ...], 'w':int, 'h':int}
        self.entries = []

        # virtual layout (computed)
        self.total_h = 0

        # scroll (pixcel)
        self.scroll_y = 0

        # ×ボタン
        self.close_image = Image(self.screen, "close_button.png", scale=0.5, 
                                 x=self.frame_rect.right - 10, y=self.frame_rect.y + 10, anchor=("right", "top"),
                                 focusable=True)

        # 表示フラグ
        self.is_open = False

        # options
        self.show_background = True
        self.background_color = BLACK_ALPHA

    # 描画領域ののrectを設定する
    def _setting_rect(self):
        screen_rect = self.screen.get_rect()
        x, y, w, h = screen_rect.x + 10, screen_rect.y + 10, screen_rect.w - 20, screen_rect.h - 20
        self.frame_rect = pygame.Rect(x, y, w, h)

    # --- 補助: 一つのテキストをレンダリングしてブロックを作る ---
    def _render_entry(self, text):
        # 段落リストを準備
        paragraphs = text.splitlines() if text else [""]

        # 使用できる幅はログ枠内部の幅 (padding差し引き)
        inner_w = max(1, self.frame_rect.width - self.padding * 2)

        # layout_paragraphsで行単位のリストを作る
        lines = self.renderer.layout_paragraphs(paragraphs, self.font, inner_w, self.text_color)

        # buird_surfaceで(surf, x, y)リスト・width・heightを得る
        rendered, max_w, total_h = self.renderer.build_surface(lines, self.font)

        # 注意：rendered yは0..total_h-行高さの範囲(行高さはfont.get_height())
        return {'text':text, 'rendered':rendered, 'w':max_w, 'h':total_h}

    # entry用のフォント(Logの見た目を変えたいならここで微調整可能)
    def _entry_font(self):
        return setting_font(self.font_data[0], self.font_data[1], self.screen_size)
    
    # --- 追加 / 削除系 ---
    def append(self, text):
        # 新規エントリをレンダリングしてリストに追加
        entry = self._render_entry(text)
        self.entries.append(entry)

        # 上限管理
        if len(self.entries) > self.max_entries:
            # POP oldest
            to_remove = len(self.entries) - self.max_entries
            del self.entries[:to_remove]

        # レイアウト管理（縦積み）
        self._recompute_layout()
        
        # 自動で一番下へスクロール
        self.scroll_to_bottom()

    def clear(self):
        self.entries.clear()
        self.total_h = 0
        self.scroll_y = 0

    # --- レイアウトの再計算 (各ブロックの縦位置を決める) ---
    def _recompute_layout(self):
        y = 0
        for e in self.entries:
            e['y_top'] = y  # ブロックの描画起点 (frame内のローカル座標、paddingを足すのは描画時)
            y += e['h'] + self.block_spacing
        self.total_h = max(0, y - self.block_spacing)  # 最後はspacingが余分なので調整

    # --- スクロール制御 ---
    def scroll(self, dy):
        visible_h = max(0, self.frame_rect.height - self.padding * 2)
        max_scroll = max(0, self.total_h - visible_h)
        self.scroll_y = max(0, min(max_scroll, self.scroll_y + dy))

    # スクロール一番下へ移動
    def scroll_to_bottom(self):
        visible_h = max(0, self.frame_rect.height - self.padding * 2)
        max_scroll = max(0, self.total_h - visible_h)
        self.scroll_y = max_scroll

    # フォントやサイズが変わったら全エントリーを再構築
    def rebuild_all(self):
        # 再レンダリング
        new_entries = []
        for e in self.entries:
            new_entries.append(self._render_entry(e['text']))
        self.entries = new_entries
        self._recompute_layout()
        self.scroll_to_bottom()

    # フォーカスマネージャーに登録
    def register_all(self, focus_manager):
        focus_manager.register(self.close_image)

    # フォーカスマネージャーから削除
    def unregister_all(self, focus_manager):
        if self.close_image in focus_manager.elements:
            focus_manager.elements.remove(self.close_image)

    # ログ表示を終了
    def close(self):
        self.is_open = False

    def handle_click(self, pos):
        if self.close_image.handle_click(pos):
            self.close()

    # 画面サイズ変更時の全アイテム更新
    def relayout(self, screen, parent=None):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.parent = parent
        self.parent_surface = parent.surface if parent is not None else screen
        self._setting_rect()
        self._entry_font()
        self.cache.clear()
        self.rebuild_all()
        self.close_image.relayout()

    def draw(self):
        if not self.is_open:
            return
        
        # 背景
        if self.show_background:
            s = pygame.Surface((self.frame_rect.w, self.frame_rect.h), pygame.SRCALPHA)
            s.fill(self.background_color)
            self.parent_surface.blit(s, (self.frame_rect.x, self.frame_rect.y))

        ox = self.frame_rect.x + self.padding
        oy = self.frame_rect.y + self.padding
        visible_h = self.frame_rect.height - self.padding * 2

        # entries は上から下に縦並び
        for e in self.entries:
            block_top = e['y_top'] - self.scroll_y

            # 早期除外 (ブロック全部が画面外)
            if block_top + e['h'] < 0:
                continue
            if block_top > visible_h:
                continue

            # ブロック内部のrendered listを描画
            for surf, x, y in e['rendered']:
                vy = block_top + y
                # 再度可視チェック(部分的に見えるだけなら描く)
                if vy + surf.get_height() < 0:
                    continue
                if vy > visible_h:
                    continue
                self.parent_surface.blit(surf, (ox + x, oy + vy))

        # 閉じるボタン
        self.close_image.draw()
