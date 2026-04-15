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
from ui.log_view import LogView
from input.focus_manager import FocusManager
from playing.room_manager import RoomManager
from manager.scenario_manager import ScenarioManager
from manager.event_manager import EventManager
from manager.sound_manager import sound_manager

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
        self.text_frame_panel = TextFramePanel(self.screen, self.root, next_callback=self.set_state)

        # 管理用
        self.event_manager = EventManager(self.screen, root=self.root, player=self.player_status, girl=self.girl_status, game_state=self.game_state, flags=self.flags,
                                          text_frame_panel=self.text_frame_panel, log_view=self.log_view, focus_manager=self.focus_manager,
                                          next_scenario_call_back=self.handle_next_scenario, move_to_room_call_back=self.handle_move_room, room_new_view=self.handle_room_view, set_state=self.set_state)
        room_id = f"{self.game_state.room}-room"
        self.scenario_manager = ScenarioManager(self.screen, event_manager=self.event_manager, scenario_id=room_id, auto_start=False)
        self.scenario_manager.start_scenario(room_id)
 
        # 部屋の管理
        self.room_manager = RoomManager(self.screen, frame_rect=self.text_frame_panel.rect, event_manager=self.event_manager, flags=self.flags, game_state=self.game_state)

        # ステータス表示
        self.status_label = PlayerDataView(self.screen, room_surface_rect=self.room_manager.room.surface_rect, player=self.player_status, girl=self.girl_status, game_state=self.game_state, flags=self.flags)

        # ナビゲーションバー
        self.navigation = MainNavigation(self.screen, surface_rect=self.room_manager.room.surface_rect)
        self.setup_navigetion()

        # 選択されたアイテム
        self.selected_item = None

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
    
    # イベントマネージャーから次のシナリオを受け取るためのコールバック関数
    def handle_next_scenario(self, next_scenario: str):
        self.scenario_manager.start_scenario(next_scenario)

    # イベントマネージャーから次の部屋に移るためのコールバック関数
    def handle_move_room(self, room_id: str):
        next_room = room_id.split("-")[0]
        self.handle_room_view(next_room)
        self.scenario_manager.start_scenario(room_id)
        
    # 部屋の再作成をする（コールバック関数としても使う)
    def handle_room_view(self, room_id: str):
        next_room = room_id.split("-")[0] if "-room" in room_id else room_id
        self.room_manager.move_to_room(next_room=next_room)
        self.setup_navigetion()

    # アイテムクリック時のイベント
    def handle_item_click_event(self, pos):
        for item in self.room_manager.room.items_select_list:
            surface_rect = self.room_manager.room.surface_rect
            pos_x, pos_y = pos

            new_pos = (pos_x - surface_rect.x, pos_y - surface_rect.y)
            if item.handle_click(new_pos):
                sound_manager.play("選択")
                self.selected_item = item
                print(item.name)                # デバッグ用
                self.scenario_manager.start_scenario(item.name)
                return True
        self.selected_item = None
        return False

    # ナビゲーションバーをクリックした場合のイベント
    def handle_navigation(self, clicked_position: Position):
        state = False
        if self.game_state.room == "center":
            if clicked_position == Position.RIGHT:
                self.room_manager.move_to_room("right")
                state = True
            elif clicked_position == Position.LEFT:
                self.room_manager.move_to_room("left")
                state = True
        else:
            if clicked_position == Position.UNDER:
                self.game_state.time -= 2
                self.room_manager.move_to_room("under")
                self.setup_navigetion()
                room_id = f"{self.game_state.room}-room"
                self.scenario_manager.start_scenario(room_id)
                state = True
        
        if state:
            self.selected_item = None

        return state

    # 右クリックイベント
    def handle_click_right(self, event):
        # シナリオ進行中は反応しない
        if not self.scenario_manager.is_active:
            # コマンドメニュー表示中は反応しない
            if not self.event_manager.render_manager.command_menu:
                pass

    # クリックイベント
    def handle_click(self, pos):
        # シナリオ進行
        self.scenario_manager.on_click()

        # シナリオ進行中ではない場合
        if not self.scenario_manager.is_active:
            # アイテムクリックイベント
            if self.handle_item_click_event(pos):
                return

    # マウスオーバー
    def handle_mouse_hover(self):
        #if self.use_virtual_cursor:
        #    key = self.cursor.get_pos()
        #else:
        key = pygame.mouse.get_pos()
        #self.menu_controller.handle_mouse_hover(key)
        self.event_manager.render_manager.handle_mouse_hover(key)
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
            self.scenario_manager.start_scenario(result["next"])

        elif action == "decide":
            # ログ表示画面のボタンの場合
            if result["target"] == self.log_view.close_image:
                self.log_view.is_open = False
                self.register_focus_with_close_log()

        # VirtualCursorのクリックイベント
        elif action == "cursor_click":
            pos = result["pos"]
            self.handle_click(pos)

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
                    
                    """
                    # 右クリック
                    elif event.button == 3:
                        self.handle_click_right(event)
                    """

    # ログ表示開始時にセットするフォーカス登録
    def register_focus_with_display_log(self):
        # ログ表示のフォーカス登録
        self.log_view.register_all(self.focus_manager)

        # ナビゲーションのフォーカス削除
        self.navigation.unregister_all(self.focus_manager)

    # ログ表示終了時にセットするフォーカス登録
    def register_focus_with_close_log(self):
        # ログ表示のフォーカス削除
        self.log_view.unregister_all(self.focus_manager)

        # ナビゲーションのフォーカス登録
        self.navigation.update_register(self.focus_manager)

    # フォーカス全登録
    def register_all(self):
        # 1. LogView
        if self.log_view.is_open:
            self.log_view.register_all(self.focus_manager)
        else:
            self.log_view.unregister_all(self.focus_manager)
        
        # 2. TextFramePanel
        self.scenario_manager.register_all(self.focus_manager)

        # 3.Navigation
        self.navigation.update_register(self.focus_manager)

    # フォーカス全削除
    def unregister_all(self):
        self.log_view.unregister_all(self.focus_manager)
        self.scenario_manager.unregister_all(self.focus_manager)
        self.navigation.unregister_all(self.focus_manager) 

    # 表示
    def draw(self):
        self.room_manager.draw()        # 部屋の表示

        self.navigation.draw()          # ナビゲーションバーの表示

        # ステータスの表示
        self.status_label.update(self.player_status, self.girl_status, self.game_state, self.flags)
        self.status_label.draw()
        
        # シナリオマネージャーの表示
        self.scenario_manager.draw()

        # ログ表示
        self.log_view.draw()

        # フォーカスマネージャーの表示
        self.focus_manager.draw()

    # 更新
    def update(self):

        if self.scenario_manager.is_active:
            self.scenario_manager.update()

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
            self.log_view.is_open = True
            self.register_focus_with_display_log()
        elif self.state == State.CLOSE:
            self.state = State.NONE
            return "ending", self.save_data
        return "play", self.save_data
