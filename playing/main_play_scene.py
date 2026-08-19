from typing import Optional, Dict, Any

import pygame
from pygame.locals import *

from constans import State, Position
from utils import Close
from ui.player_data_view import PlayerDataView
from core.game_state import GameStatus, Flags
from models.characters import Player, Human

from base_scene import BaseScene
from ui.ui_panels import TextFramePanel
from ui.navigation import MainNavigation
from ui.overlays.log_view import LogView
from ui.overlays.overlay_view import OverlayView, OverlayViews
from ui.overlays.pause_menu import PauseMenu
from ui.overlays.character_status.character_status_view import CharacterStatusView
from ui.overlays.inventory_view import InventoryView
from ui.ui_command import CommandButton
from input.focus_manager import FocusManager
from playing.room_manager import RoomManager
from playing.play_scene_controller import PlaySceneController
from manager.scenario_manager import ScenarioManager
from manager.event_manager import EventManager
from manager.event_callbacks import EventCallbacks

# プレイ画面
class MainPlayScene(BaseScene):
    def __init__(self, screen, root, save_data=None):
        super().__init__(screen, root)

        self.save_data = save_data
        
        # セーブデータから各データをセットする
        self.set_data(save_data)

        # フォーカスマネージャー
        self.focus_manager = FocusManager(self.screen)

        # ログ表示機能
        self.log_view = LogView(self.screen)

        # テキストフレーム
        self.text_frame_panel = TextFramePanel(self.screen, self.root, on_scene_state_change_callback=self.on_scene_state_change_requested)

       # 部屋の管理
        room_id = f"{self.game_state.room}-room"
        self.room_manager = RoomManager(self.screen, frame_rect=self.text_frame_panel.rect, flags=self.flags, game_state=self.game_state)

        # コントローラー
        self.controller = PlaySceneController(self.room_manager, self.setup_navigetion)

        # イベントマネージャー
        callbacks = EventCallbacks(
            on_scenario_start=self.controller.on_scenario_start_requested,
            on_room_transition=self.controller.on_room_transition_requested,
            on_room_refresh=self.controller.on_room_refresh_requested,
            on_scene_state_change=self.on_scene_state_change_requested
        )
        self.event_manager = EventManager(self.screen, root=self.root, player=self.player_status, girl=self.girl_status, game_state=self.game_state, flags=self.flags,
                                          text_frame_panel=self.text_frame_panel, log_view=self.log_view, focus_manager=self.focus_manager,
                                          callbacks=callbacks)
        
        # シナリオマネージャー
        self.scenario_manager = ScenarioManager(self.screen, event_manager=self.event_manager, scenario_id=room_id, auto_start=False)
        self.controller.set_scenario_manager(self.scenario_manager)
 
        # ステータス表示
        self.status_view = PlayerDataView(self.screen, room_surface_rect=self.room_manager.room.surface_rect, player=self.player_status, girl=self.girl_status, game_state=self.game_state, flags=self.flags)

        # ナビゲーションバー
        self.navigation = MainNavigation(self.screen, surface_rect=self.room_manager.room.surface_rect)
        self.setup_navigetion()

        # 右クリックメニュー
        self.current_overlay = None
        self.pause_menu = PauseMenu(self.screen)
        self.character_status_view = CharacterStatusView(self.screen)
        self.inventory_view = InventoryView(self.screen)

        self.overlay_views = OverlayViews(self.pause_menu, self.character_status_view, self.inventory_view, None)

        self.register_all()

        self.scenario_manager.start_scenario(room_id)

    # データをセットする
    def set_data(self, save_data):
        # 主人公データ
        self.player_status = Player().from_dict(save_data["player_status"])

        # 少女のデータ
        self.girl_status = Human().from_dict(save_data["girl_status"])

        # フラグ一覧
        self.state = State.NONE     # saveやload等の状態管理フラグ
        self.game_state = GameStatus().from_dict(save_data["game_state"])
        self.flags = Flags().from_dict(save_data["flags"])

    # セーブデータを作る
    def create_save_data(self):
        self.save_data = {
            "player_status": self.player_status.to_dict(),
            "girl_status": self.girl_status.to_dict(),
            "game_state": self.game_state.to_dict(),
            "flags": self.flags.to_dict()
        }

    # ナビゲーションバーのセット
    def setup_navigetion(self):
        if self.game_state.room == "center":
            position_list = [Position.RIGHT, Position.LEFT]
        else:
            position_list = [Position.UNDER]
        self.navigation.setup_navigation(position_list)
        self.navigation.update_register(self.focus_manager)

    # オーバーレイのページ変更処理
    def switch_overlay(self, prev_page: Optional[OverlayView], next_page: Optional[OverlayView]):
        if prev_page is None and next_page is None:
            return

        if prev_page:
            if next_page is None:
                self.current_overlay = None
                self.register_focus_with_close_overlay(prev_page)
            else:
                prev_page.close()
                prev_page.unregister_all(self.focus_manager)
                    
        if next_page:
            self.current_overlay = next_page
            if next_page is self.overlay_views.menu:
                next_page.open(self.flags)

            elif next_page is self.overlay_views.status:
                next_page.open(self.player_status, self.girl_status, 
                               self.flags, self.focus_manager)
                
            else:
                next_page.open()
            
            if prev_page is None:
                self.register_focus_with_display_overlay(next_page)
            else:
                next_page.register_all(self.focus_manager)

    # アイテムクリック時のイベント
    def handle_item_click_event(self, pos):
        for item in self.room_manager.room.items_select_list:
            result = item.handle_click(pos)
            if result:
                print(result)                # デバッグ用
                self.scenario_manager.start_scenario(result)
                return True
        return False

    # ナビゲーションバーをクリックした場合のイベント
    def handle_navigation(self, clicked_position: Position):
        if self.game_state.room == "center":
            if clicked_position == Position.RIGHT:
                self.room_manager.move_to_room("right")
                return True
            elif clicked_position == Position.LEFT:
                self.room_manager.move_to_room("left")
                return True
        else:
            if clicked_position == Position.UNDER:
                self.game_state.time -= 2
                self.room_manager.move_to_room("under")
                self.setup_navigetion()
                room_id = f"{self.game_state.room}-room"
                self.scenario_manager.start_scenario(room_id)
                return True        
        return False

    # 右クリックイベント
    def handle_right_click(self):
        # シナリオ進行中は反応しない
        if self.scenario_manager.is_active:
            return
        
        # コマンドメニュー表示中は反応しない
        if self.event_manager.render_manager.command_menu:
            return
        
        self.switch_overlay(None, self.overlay_views.menu)

    # クリックイベント
    def handle_click(self, pos):
        # シナリオ進行
        self.scenario_manager.on_click()

        # シナリオ進行中は反応しない
        if self.scenario_manager.is_active:
            return
        
        # 右クリックメニュー中は反応しない
        if self.current_overlay is not None:
            return
        
        # アイテムクリックイベント
        self.handle_item_click_event(pos)

    # マウスオーバー(デバッグ用)
    def handle_mouse_hover(self):
        # 右クリックメニュー表示中は反応しない
        if self.current_overlay is not None:
            return
        
        if self.focus_manager.virtual_cursor.visible:
            key = self.focus_manager.virtual_cursor.get_pos()
        else:
            key = pygame.mouse.get_pos()

        self.room_manager.handle_mouse_hover(key)

    # フォーカスから帰ってきたアクションの処理
    def on_action(self, result):
        action = result["action"]
        # ナビゲーションの場合
        if action == "navigation":
            self.handle_navigation(result["result"])

        # テキストフレームパネルのメニューの場合
        elif action == "menu":
            pass

        # テキストフレームパネルのネクストボタンの場合
        elif action == "next":
            self.scenario_manager.on_click()
 
        elif action == "next_scenario":
            self.event_manager.render_manager.close_command_menu()
            # 何故かコマンドメニューがfocus_managerに残ってしまうことがあるため、コマンドボタンを全て削除するようにする。
            for element in self.focus_manager.elements:
                if isinstance(element, CommandButton):
                    self.focus_manager.elements.remove(element)
            self.scenario_manager.start_scenario(result["next"])

        elif action == "decide":
            # ログ表示画面のボタンの場合
            if self.log_view.is_open:
                selected_action = self.log_view.handle_click(result["result"])
                if selected_action == "close":
                    self.register_focus_with_close_overlay(self.log_view)
            
            # 右クリックメニュー関連の場合
            elif self.current_overlay is not None:
                self.on_action_from_pause_menu(self.current_overlay, result)

            """
            elif self.pause_menu.is_open:
                selected_action = self.pause_menu.handle_click(result["result"])
                if selected_action == "status":
                    self.switch_overlay(self.overlay_views.menu, self.overlay_views.status)
                    
                elif selected_action == "inventory":
                    self.switch_overlay(self.overlay_views.menu, self.overlay_views.inventory)

                elif selected_action == "close":
                    self.switch_overlay(self.overlay_views.menu, None)

            elif self.character_status_view.is_open:
                selected_action = self.character_status_view.handle_click(result["target"], result["result"])
                if selected_action == "close":
                    self.switch_overlay(self.overlay_views.status, self.overlay_views.menu)
            elif self.inventory_view.is_open:
                selected_action = self.inventory_view.handle_click(result["result"])
                if selected_action == "close":
                    self.switch_overlay(self.overlay_views.inventory, self.overlay_views.menu)
            """

        # VirtualCursorのクリックイベント
        elif action == "cursor_click":
            pos = result["pos"]
            self.handle_click(pos)

        # 右クリックだった場合
        elif action == "right_click":
            if self.current_overlay is None:
                self.handle_right_click()

    def on_action_from_pause_menu(self, page: OverlayView, result: Dict[str, Any]):
        if not page.is_open:
            return

        if page is self.overlay_views.status:
            selected_action = page.handle_click(result["target"], result["result"])
        else:
            selected_action = page.handle_click(result=result["result"])

        if selected_action == "close":
            if page is self.overlay_views.menu:
                self.switch_overlay(page, None)
            else:
                self.switch_overlay(page, self.overlay_views.menu)

        elif selected_action == "status":
            self.switch_overlay(page, self.overlay_views.status)
        
        elif selected_action == "inventory":
            self.switch_overlay(page, self.overlay_views.inventory)

    # イベントハンドラ
    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                Close(self.root)

            result = self.focus_manager.handle_event(event)

            if result:
                self.on_action(result)
            else:
                # マウスクリック時
                if event.type == MOUSEBUTTONDOWN:
                    # 左クリック
                    if event.button == 1:
                        self.handle_click(event.pos)
                    
                    # 右クリック
                    #elif event.button == 3:
                    #    self.handle_right_click()                    

    # オーバーレイ関連を開いた時のフォーカス登録
    def register_focus_with_display_overlay(self, page: OverlayView):
        # 全てのフォーカス削除
        self.unregister_all()

        # 各ページのフォーカス登録
        page.register_all(self.focus_manager)

    # オーバーレイ関連を閉じた時のフォーカス登録
    def register_focus_with_close_overlay(self, page: OverlayView):
        # 各ページのフォーカス削除
        page.unregister_all(self.focus_manager)

        # 全てのフォーカス登録
        self.register_all()

    # フォーカス全登録
    def register_all(self):
        # 1. TextFramePanel
        self.scenario_manager.register_all(self.focus_manager)

        # 2. Navigation
        self.navigation.update_register(self.focus_manager)

    # フォーカス全削除
    def unregister_all(self):
        self.log_view.unregister_all(self.focus_manager)
        self.pause_menu.unregister_all(self.focus_manager)
        self.character_status_view.unregister_all(self.focus_manager)
        self.inventory_view.unregister_all(self.focus_manager)
        self.scenario_manager.unregister_all(self.focus_manager)
        self.navigation.unregister_all(self.focus_manager) 

    def relayout(self, screen):
        super().relayout(screen)
        self.text_frame_panel.relayout(screen)
        self.scenario_manager.relayout(screen)
        frame_rect = self.text_frame_panel.rect
        self.room_manager.relayout(screen, frame_rect)
        self.navigation.relayout(screen, self.room_manager.room.surface_rect)
        self.log_view.relayout(screen)
        self.unregister_all()
        self.register_all()

    # 表示
    def draw(self):
        # 部屋の表示
        self.room_manager.draw()

        # ナビゲーションバーの表示
        self.navigation.draw()

        # ステータスの表示
        self.status_view.draw()
        
        # シナリオマネージャーの表示
        self.scenario_manager.draw()

        # 右クリックメニューの表示
        self.pause_menu.draw()

        # キャラクター情報確認ページの表示
        self.character_status_view.draw()

        # インベントリページの表示
        self.inventory_view.draw()

        # ログ表示
        self.log_view.draw()

        # フォーカスマネージャーの表示
        self.focus_manager.draw()

    # 更新
    def update(self):
        # シナリオマネージャーの更新
        if self.scenario_manager.is_active:
            self.scenario_manager.update()

        # ステータス表示の更新
        self.status_view.update(self.player_status, self.girl_status, self.game_state, self.flags)

        if self.current_overlay is self.character_status_view:
            self.character_status_view.update()

        self.draw()

        self.handle_mouse_hover()
        self.handle_events()
        return self.next_state()

    def next_state(self):
        if self.state == State.SAVE:
            self.state = State.NONE
            return "save", self.save_data
        elif self.state == State.LOAD:
            self.state = State.NONE
            return "load", self.save_data
        elif self.state == State.SETTING:
            self.state = State.NONE
            return "setting", self.save_data
        elif self.state == State.LOG:
            self.state = State.NONE
            self.log_view.open()
            self.register_focus_with_display_overlay(self.log_view)
        elif self.state == State.CLOSE:
            self.state = State.NONE
            return "ending", self.save_data
        return "play", self.save_data
