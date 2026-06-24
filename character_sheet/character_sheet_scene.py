from typing import Tuple, List
from dataclasses import dataclass

import pygame
from pygame.locals import *

from constans import ITEM_LIST, JSON_FOLDER, State
from utils import load_json, Close
from models.characters import Player
from input.focus_manager import FocusManager

from ui.ui_panels import TextFramePanel
from ui.navigation import CharasheetNavigation
from ui.sheet_slide_system import SheetSlideSystem
from character_sheet.status_page import StatusPage
from character_sheet.profession_page import ProfessionPage
from character_sheet.confirm_page import ConfirmPage
from base_scene import BaseScene
    
# キャラクターシート作成画面をクラス化してみる
class CharacterSheetScene(BaseScene):
    def __init__(self, screen, root):
        super().__init__(screen, root)


        self.selected_profession = None     # 選択中の職業
        self.is_pulldown_open = False       # プルダウン用のフラグ
        self.selected_hobby = ""            # 選択中の趣味

        # 設定する主人公のステータス
        self.player = Player()
        self.player.add_item(ITEM_LIST["white_robe"])

        # 初期セーブデータ
        self.save_data = load_json("SaveData.json", JSON_FOLDER)
        
        # テキストフレーム
        enabled_flags = {"セーブ": False, "ロード": True, "ログ": False}
        self.text_frame_panel = TextFramePanel(self.screen, self.root, enabled_flags=enabled_flags, on_scene_state_change_callback=self.on_scene_state_change_requested)
        frame_rect = self.text_frame_panel.rect

        # ページ管理
        self.pages = []
        self.create_pages(frame_rect)

        self.sheet_slide_system = SheetSlideSystem(self.screen, self.pages)

        # 現在のページ
        #self.current_page = 0
        # 次のページ
        #self.target_page = 1

        # スライド関係
        #self.is_sliding = False
        #self.slide_offset = 0
        #self.slide_speed = 40

        # ナビゲーション
        surface_rect = self.status_page.rect
        self.navigation = CharasheetNavigation(self.screen, surface_rect)

        # フォーカスマネージャー
        self.focus_manager = FocusManager(self.screen)
        self.register_all()

        # 状態フラグ
        self.state = State.NONE
    
    # ページの作成
    def create_pages(self, frame_rect: pygame.Rect):
        self.status_page = StatusPage(self.screen, self.root, frame_rect, self.player)
        self.status_page.load_status_items()
        self.profession_page = ProfessionPage(self.screen, self.root, frame_rect, self.player)
        self.profession_page.load_selector()
        self.confirm_page = ConfirmPage(self.screen, self.root, frame_rect, self.player, self.save_data, on_scene_state_change_callback=self.on_scene_state_change_requested)

        self.pages.append(self.status_page)
        self.pages.append(self.profession_page)
        self.pages.append(self.confirm_page)

    # 指定したページのフォーカスを登録する
    def register_page(self, page: int):
        self.pages[page].register_all(self.focus_manager)

    # 指定したページのフォーカスを削除する
    def unregister_page(self, page: int):
        self.pages[page].unregister_all(self.focus_manager)

    # ページごとにフォーカスを登録・削除する
    def change_register_page(self, target_page: int):
        # target_page以外のページのフォーカスを先に削除しておく
        for page in range(len(self.pages)):
            if page != target_page:
                self.unregister_page(page)
                self.navigation.unregister_focus(page, self.focus_manager)

        # target_pageのフォーカスを登録する
        self.register_page(target_page)
        self.navigation.register_focus(target_page, self.focus_manager)
        
    # すべての要素をフォーカスマネージャーに登録する
    def register_all(self):
        self.change_register_page(self.sheet_slide_system.get_current_page())
        self.text_frame_panel.register_all(self.focus_manager)

    # ページを表示する
    def draw_page(self):
        """
        current, current_rect = self.draw_page_get_surface_and_rect(self.current_page)
        current_x = current_rect.x - self.slide_offset
        self.screen.blit(current, (current_x, current_rect.y))

        if self.is_sliding:
            target, target_rect = self.draw_page_get_surface_and_rect(self.target_page)
            target_x = self.screen_size[0] - self.slide_offset if self.target_page > self.current_page else - self.screen_size[0] - self.slide_offset
            self.screen.blit(target, (target_x, target_rect.y))
        """
        current_surface_and_rect = self.draw_page_get_surface_and_rect(self.sheet_slide_system.get_current_page())
        target_surface_and_rect = self.draw_page_get_surface_and_rect(self.sheet_slide_system.get_target_page())
        self.sheet_slide_system.draw(current_surface_and_rect, target_surface_and_rect)
        self.navigation.draw(self.sheet_slide_system.current_page)
        self.text_frame_panel.draw()
        self.focus_manager.draw()

    # ページを表示してSurfaceとRectを返す
    def draw_page_get_surface_and_rect(self, page: int) -> Tuple[pygame.Surface, pygame.Rect]:
        return self.pages[page].draw()

    """
    # 次のページを表示
    def next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.target_page = self.current_page + 1
            self.is_sliding = True
            self.change_register_page(self.target_page)
    
    # 前のページを表示
    def prev_page(self):
        if self.current_page > 0:
            self.target_page = self.current_page - 1
            self.is_sliding = True
            self.change_register_page(self.target_page)
    """
            
    # イベントハンドラ
    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンかESCキーで終了
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                Close(self.root)

            result = self.focus_manager.handle_event(event)

            if result:
                # ホバーイベント
                if result["action"] == "hover":
                    self.text_frame_panel.set_text(result["text"])
                else:
                    self.text_frame_panel.set_text("")
                    
                    # テキストフレームパネルのメニューの場合
                    if result["action"] == "menu":
                        return
                    
                    # ナビゲーションの場合
                    elif result["action"] == "navigation":
                        result_text = result["result"]
                        if result_text in ["next", "prev"]:
                            if result_text == "next":
                                self.sheet_slide_system.next_page()
                            elif result_text == "prev":
                                self.sheet_slide_system.prev_page()
                            self.change_register_page(self.sheet_slide_system.get_target_page())
                        elif result_text == "finalize":
                            if self.sheet_slide_system.get_current_page() == 1 and self.is_pulldown_open:
                                self.is_pulldown_open = False
                            self.confirm_page.handle_click(result_text)

                    # その他の場合
                    if result["action"] == "decide":                        
                        # ステータスページの場合
                        current_page = self.sheet_slide_system.get_current_page()
                        if current_page == 0:
                            self.status_page.handle_click(result["target"], result["result"])

                        # 職業ページの場合
                        elif current_page == 1:
                            self.profession_page.handle_click(result["target"], result["result"])
            else:
                self.text_frame_panel.set_text("")                
                            
    def on_scene_state_change_requested(self, state=State.NONE, save_data=None):
        if save_data:
            self.save_data = save_data
        super().on_scene_state_change_requested(state)

    # 画面サイズ更新時にポジションを変更する
    def relayout(self, screen: pygame.Surface):
        super().relayout(screen)
        self.text_frame_panel.relayout(screen)
        # ステータスページをupdate
        self.status_page.relayout(screen)
        # 職業ページをupdate
        self.profession_page.relayout(screen)
        # 確認ページをupdate
        self.confirm_page.relayout(screen)
        # ナビゲーションをupdate
        self.navigation.relayout(screen, self.status_page.rect)

    def update(self):
        # スライドアニメーションの進行
        self.sheet_slide_system.update()
        """
        if self.is_sliding:
            direction = 1 if self.target_page > self.current_page else -1
            self.slide_offset += self.slide_speed * direction

            # 1ページ分スライドしきったら
            if abs(self.slide_offset) >= self.screen_size[0]:
                self.current_page = self.target_page
                self.slide_offset = 0
                self.is_sliding = False
        """
        self.draw_page()    # ページに応じた描画
        self.handle_events()
        return self.next_state()

    def next_state(self):
        if self.state == State.SAVE:
            self.state = State.NONE
            return "save", self.save_data
        elif self.state == State.LOAD:
            self.state = State.NONE
            return "load"
        elif self.state == State.SETTING:
            self.state = State.NONE
            return "setting"
        elif self.state == State.CLOSE:
            self.state = State.NONE
            Close()
        return "charasheet"

