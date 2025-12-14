import pygame
from pygame import Rect
from typing import Optional, Sequence, Tuple

from ui.ui_elements import *
from ui.ui_command import CommandMenu, Command
from ui.ui_panels import TextFramePanel
from ui.log_view import LogView

class RenderManager:
    def __init__(self, screen, image_cache=None, room_manager=None, text_frame_panel=None, log_view=None):
        self.screen = screen
        self.screen_size = screen.get_size()

        # 外部からのセット
        self.room_manager = room_manager

        # テキスト表示関連
        self.text_frame_panel = text_frame_panel if text_frame_panel else TextFramePanel(self.screen)
        self.log_view = log_view if log_view else LogView(self.screen)

        # 画像表示用cache
        self.image_cache = image_cache if image_cache else ImageCache()

        # 画像要素
        self.girl_image = None
        self.item_image = None

        # コマンドメニュー
        self.command_menu = None
        self.command_menu_rect = None

        self.blackout_images = []
        self.blackout_index = 6         # ブラックアウト画像のインデックス
        self.blackout_phase = None      # ブラックアウトのフェーズ
        self.blackout_timer = None      # ブラックアウトのタイマー
        self.blackout_wait = None       # ブラックアウトの待ち時間
        self.blackout_done = False      # ブラックアウトの完了フラグ
        self.next_after_black_out = {}    # ブラックアウトの後のステップ

    # 少女の立ち絵を表示する
    def show_girl_image(self, state=None, position="right"):
        if state:
            file_name = f"Girl_{state}.png"
        else:
            file_name = "Girl.png"
        scale_x, _, aspect_scale = get_scales(self.screen_size)
        scale = 0.6 * aspect_scale
        frame_rect = self.text_frame_panel.rect
        x = 200 if position == "right" else (-200 if position == "left" else "center")
        if x != "center":
            x = x * scale_x
        self.girl_image = Image(screen=self.screen, path=file_name, cache=self.image_cache, scale=scale, x=x, y=frame_rect.top, anchor=("center", "bottom"))

    def hidden_girl_image(self):
        self.girl_image = None

    # 画像イメージを表示する
    def show_item_image(self, file_name):
        scale = 0.6 if "Memo" in file_name or file_name == "Book1" else (0.5 if "center-room_Light" in file_name else 0.35)
        self.item_image = Image(screen=self.screen, path=file_name, cache=self.image_cache, scale=scale, x="center", centery=200, line_flag=True, bg_flag=True)

    # 画像イメージを消す
    def hidden_item_image(self):
        self.item_image = None

    # コマンドメニューの生成
    def set_command_menu(self, commands:Sequence[Command], target:Optional[str]):
        if not commands:
            self.command_menu = None
            self.command_menu_rect = None
            return
        
        if target == "item":
            target_rect = self.item_image.rect
        elif target == "girl":
            target_rect = self.girl_image.rect

        font = setting_font(FONT_PATH, SMALL_SIZ)
        max_width = 120
        for cmd in commands:
            w = font.size(cmd.text)[0] + 10
            if w > max_width:
                max_width = w
        btn_h = 30
        menu_w = max_width
        menu_h = btn_h * len(commands)

        frame_rect = self.text_frame_panel.rect if self.text_frame_panel else Rect(0, 0, 0, 0)
        menu_rect = self.text_frame_panel.menu_bar.rect
        pos = self._choose_menu_position(target_rect, menu_w, menu_h, frame_rect, menu_rect)
        start_position = self.get_position()
        self.command_menu = CommandMenu(self.screen, commands, start_position)

    # コマンドメニューの表示位置を取得
    def _choose_menu_position(self, target_rect, menu_w: int, menu_h: int, frame_rect, menu_rect):
        """
        menu_wとmenu_hをtargetの周りに配置(右・左・下・上)して、screen内かつframe_rectと被らない位置を返す
        """
        screen_rect = self.screen.get_rect()
        margin = 8

        # right
        x = target_rect.right + margin
        y = target_rect.centery - menu_h // 2
        rect = Rect(x, y, menu_w, menu_h)
        if self._is_rect_valid_for_menu(rect, screen_rect, frame_rect, menu_rect):
            return (max(screen_rect.left+margin, x), max(screen_rect.top+margin, y))
        
        # left
        x = target_rect.left - menu_w - margin
        y = target_rect.centery - menu_h // 2
        rect = Rect(x, y, menu_w, menu_h)
        if self._is_rect_valid_for_menu(rect, screen_rect, frame_rect, menu_rect):
            return (max(screen_rect.left+margin, x), max(screen_rect.top+margin, y))
        
        # below
        x = target_rect.centerx - menu_w // 2
        y = target_rect.bottom + margin
        rect = Rect(x, y, menu_w, menu_h)
        if self._is_rect_valid_for_menu(rect, screen_rect, frame_rect, menu_rect):
            return (max(screen_rect.left+margin, x), max(screen_rect.top+margin, y))
        
        # above
        x = target_rect.centerx - menu_w // 2
        y = target_rect.top - menu_h - margin
        rect = Rect(x, y, menu_w, menu_h)
        if self._is_rect_valid_for_menu(rect, screen_rect, frame_rect, menu_rect):
            return (max(screen_rect.left+margin, x), max(screen_rect.top+margin, y))
        
        # 最終手段：画面右下の安全領域（そんなとこあったっけ？？？）
        safe_x = min(screen_rect.right - menu_w - margin, frame_rect.right - menu_w - margin if frame_rect else screen_rect.right - menu_w - margin)
        safe_y = max(margin, frame_rect.top - menu_h - margin if frame_rect else screen_rect.bottom - menu_h - margin)
        return (max(margin, safe_x), max(margin, safe_y))

    # 画面内に収まっていてテキストフレームに重ならないか判定
    def _is_rect_valid_for_menu(self, rect, screen_rect, frame_rect, menu_rect) -> bool:
        if not screen_rect.contains(rect):
            # 部分的にでも画面からはみ出ていたら不可
            return False
        
        # メニューがテキストフレームに重なるのは不可
        if frame_rect and rect.colliderect(frame_rect):
            return False
        
        # テキストフレーム上部のメニューボタンに重なるのも不可
        if menu_rect and rect.colliderect(menu_rect):
            return False        
        
        return True

    def get_position(self):
        max_x, max_y = self.screen_size[0] // 4 * 3, self.screen_size[1] // 2      # これ以上端に配置すると見えなくなる

        # コマンド表示の指標となる画像位置。クリック時画像があればそこを起点とする。
        if self.item_image:
            image_rect = self.item_image.rect

            # 画像の右側にコマンドボタンを表示する。最大値以上になる場合は左側に配置する。
            x = image_rect.right + 30 if (image_rect.right + 30) <= max_x else image_rect.x - 130
            y = image_rect.y if image_rect.y <= max_y else image_rect.y - 50
        else:
            x, y = self.screen_size[0]//2 + 120, 100

        return (x, y)

    # テキスト描画領域にテキストをセットする
    def set_text(self, text):
        if "{" in text:
            text = self.process_text_template(text)
        self.text_frame_panel.set_text(text)
        self.log_view.append(text)

    # ブラックアウト処理
    def handle_black_out(self, wait_duration):
        # 画像の拡大率を計算する
        _, _, aspect = get_scales(self.screen_size)
        scale = 0.2 * aspect
        # 画像の表示位置を得る
        room_rect = get_room_rect(self.screen)

        # 徐々に黒になる画像0～5を用意する
        image_paths = [f"to_black{i}.png" for i in range(6)]
        self.blackout_images = []
        for path in image_paths:
            self.blackout_images.append(Image(self.screen, path, scale, centerx=room_rect.centerx, centery=room_rect.centery))
        self.blackout_index = 5

        # タイマー
        self.blackout_timer = pygame.time.get_ticks()

        # フェーズ
        self.blackout_phase = "fade_out"

        # 待ち時間
        self.blackout_wait = wait_duration

        # ブラックアウト完了フラグ
        self.blackout_done = False

        # UI表示のための状態フラグ
        self.is_blackout_active = True

        # 次ステップ遷移を予約しておく
        return {"type":"text", "text":f"しばらく経ったあとあなたは目を覚ました。", "progression":"click"}

    # 少女がクリックされた際に実行
    def handle_girl_click(self, pos):
        if self.girl_image:
            if self.girl_image.collidepoint(pos):
                pass
        pass

    # 表示する
    def draw(self, step):
        # ブラックアウトの処理
        if self.is_blackout_active:
            now = pygame.time.get_ticks()

            if self.blackout_phase == "fade_out":
                if now - self.blackout_timer > 100:
                    self.blackout_index -= 1
                    self.blackout_timer = now

                    # 画像が最後の1枚になったら
                    if self.blackout_index <= 0:
                        self.blackout_phase == "black"
                        self.blackout_timer = now

                self.blackout_images[self.blackout_index].draw()
            
            elif self.blackout_phase == "black":
                if now - self.blackout_timer > self.blackout_wait:
                    self.blackout_phase = "fade_in"
                    self.blackout_index = 0
                    self.blackout_timer = now
            
            elif self.blackout_phase == "fade_in":
                if now - self.blackout_timer > 100:
                    self.blackout_index += 1
                    self.blackout_timer = now
                    if self.blackout_index >= len(self.blackout_images):
                        self.is_blackout_active = False
                        # ブラックアウトが終了したら目覚めのシナリオへ
                        self.to_callback_next_scenario("Wake_up")
                        return
                self.blackout_images[self.blackout_index].draw()
            return

        if step["type"] == "text":
            self.text_frame_panel.set_text(step["text"])
            self.log_view.append(step["text"])

        # 結果を表示する
        elif step["type"] == "result_text" and self.result_text:
            self.text_frame_panel.set_text(self.result_text)
            self.log_view.append(self.result_text)
    
        # コマンドメニューを表示する
        if step["type"] == "interaction" and self.command_menu:
            self.command_menu.draw()

        # テキストを表示する
        self.text_frame_panel.draw()

        # アイテムイメージを表示する
        if self.item_image:
            self.item_image.draw()

        # 少女立ち絵を表示する
        if self.girl_image:
            self.girl_image.draw()
