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
        self.log_view = LogView(self.screen, callback=self.log_view_end)
        self.log_view_flag = False

        # テキストフレーム
        self.text_frame_panel = TextFramePanel(self.screen, next_callback=self.set_state)

        # 管理用
        self.event_manager = EventManager(self.screen, self.player_status, self.girl_status, self.game_state, self.flags,
                                          self.text_frame_panel, self.log_view,
                                          self.handle_next_scenario, self.handle_move_room, self.handle_room_view, self.set_state)
        room_id = f"{self.game_state.room}-room"
        self.scenario_manager = ScenarioManager(self.screen, self.event_manager, room_id, auto_start=False)
        self.scenario_manager.start_scenario(room_id)
 
        # 部屋の管理
        self.room_manager = RoomManager(self.screen, self.text_frame_panel.rect, self.event_manager, self.flags, self.game_state)

        # ステータス表示
        self.status_label = PlayerDataView(self.screen, self.room_manager.room.surface_rect, self.player_status, self.girl_status, self.game_state, self.flags)

        # ナビゲーションバー
        self.navigation = MainNavigation(self.screen, self.room_manager.room.surface_rect)
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
            self.navigation.setup_navigation([Position.RIGHT, Position.LEFT])
        else:
            self.navigation.setup_navigation([Position.UNDER])
    
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

    # 少女の表示中に少女をクリックで起こるイベント
    def handle_girl_click_event(self, pos):
        self.event_manager.render_manager.handle_girl_click(pos)

    # コマンドメニューイベント
    def handle_command_menu_event(self, pos):
        self.event_manager.render_manager.handle_command_click(pos)

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
            if clicked_position is not None:
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
        # ログ表示
        if self.log_view_flag:
            self.log_view.handle_click(pos)
        else:
            # render_managerのクリックイベント処理
            if self.event_manager.render_manager.handle_click(pos):
                return
            #if self.text_frame_panel.handle_click(pos):
            #    return

            # シナリオ進行
            self.scenario_manager.on_click()

            # シナリオ進行中ではない場合
            if not self.scenario_manager.is_active:

                # コマンドメニュー表示中はそれを優先
                if self.event_manager.render_manager.command_menu:
                    self.handle_command_menu_event(pos)
                
                # ナビゲーションバーによる移動
                elif self.handle_navigation(self.navigation.handle_click(pos)):
                    return
                
                # 少女が表示中は少女のクリックイベントがアイテムより優先される
                elif self.handle_girl_click_event(pos):
                    return

                # アイテムクリックイベント
                elif self.handle_item_click_event(pos):
                    return

            sound_manager.play("クリック")

    # マウスオーバー
    def handle_mouse_hover(self):
        #if self.use_virtual_cursor:
        #    key = self.cursor.get_pos()
        #else:
        key = pygame.mouse.get_pos()
        #self.menu_controller.handle_mouse_hover(key)
        self.event_manager.render_manager.handle_mouse_hover(key)
        self.room_manager.handle_mouse_hover(key)

    # キーダウンイベント
    def handle_keydown(self, key):
        # ESCキーで終了
        if key == K_ESCAPE:
            Close(self.root)

        # エンターキーでクリックイベント
        #elif key == K_RETURN or key == K_KP_ENTER:
            #self.handle_click(self.cursor.get_pos())

    # イベントハンドラ
    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT:
                Close(self.root)

            # キーボード押下時
            if event.type == KEYDOWN:
                #if not self.use_virtual_cursor:
                    # ボタンを押すことでキーボードモードに変更
                    #self.use_virtual_cursor = on_keybord(self.cursor)
                    
                self.handle_keydown(event.key)

            # マウス移動時
            #if event.type == MOUSEMOTION:
                #if self.use_virtual_cursor:
                    # マウスを動かしたらキーボードモード終了
                #    self.use_virtual_cursor = off_keybord(self.cursor)

            # マウスクリック時
            if event.type == MOUSEBUTTONDOWN:
                # 左クリック
                if event.button == 1:
                    self.handle_click(event.pos)

                # 右クリック
                elif event.button == 3:
                    self.handle_click_right(event)
                    
    # 表示
    def draw(self):
        #create_frame(self.screen)       # テキストフレームの表示
        #self.text_frame_panel.draw()

        self.room_manager.draw()        # 部屋の表示

        self.navigation.draw()          # ナビゲーションバーの表示

        # ステータスの表示
        self.status_label.update(self.player_status, self.girl_status, self.game_state, self.flags)

        # イベントマネージャーの表示
        #self.event_manager.draw()
        
        # シナリオマネージャーの表示
        self.scenario_manager.draw()

        # ログ表示
        if self.log_view_flag:
            self.log_view.draw()

        # バーチャルカーソルの表示
        #if self.use_virtual_cursor:
        #    self.cursor.draw()
            
    # 更新
    def update(self):
        #if self.use_virtual_cursor:
            #handle_cursor_move(self.use_virtual_cursor, self.cursor)

        if self.scenario_manager.is_active:
            self.scenario_manager.update()

        self.draw()

        self.handle_mouse_hover()
        self.handle_events()
        return self.next_state()

    # ログ表示を閉じる用のコールバック関数
    def log_view_end(self, flag):
        if flag:
            self.log_view_flag = False


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
            self.log_view_flag = True
        elif self.state == State.CLOSE:
            return "ending", self.save_data
        return "play", self.save_data
