import pygame
import pygame.draw
from pygame.locals import *

from constans import *
from utils import *
from ui_elements import *
from game_state import *
from characters import *

from menu import MenuController
from navigation import Navigation
from manager.room_manager import RoomManager
from manager.scenario_manager import ScenarioManager
from manager.event_manager import EventManager

# プレイ画面
class MainPlay:
    def __init__(self, screen, root, save_data=None):
        self.screen = screen
        self.root = root
        self.save_data = save_data
        
        # セーブデータから各データをセットする
        self.set_data(save_data)

        # メニューコントローラー
        self.menu_controller = MenuController(self.screen, self.root, self.set_state)
    
        #self.game_state.room = "east"
    
        # ナビゲーションバー
        self.navigation = Navigation(self.screen)
        self.setup_navigetion()

        # 主人公のステータス表示
        self.player_label = PlayerDataView(self.screen, self.player_status, self.game_state)

        # 管理用
        self.event_manager = EventManager(self.screen, self.player_status, self.game_state, self.flags,
                                          self.handle_next_scenario, self.handle_move_room, self.handle_room_view)
        room_id = f"{self.game_state.room}-room"
        self.scenario_manager = ScenarioManager(self.screen, self.event_manager, room_id)
 
        # 部屋の管理
        self.room_manager = RoomManager(self.screen, self.event_manager, self.flags, self.game_state)

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
    
    # アイテムクリック時のイベント
    def handle_item_click_event(self, event):
        for item in self.room_manager.room.items_select_list:
            if item.handle_click(event.pos):
                self.selected_item = item
                print(item.name)                # デバッグ用
                self.scenario_manager.start_scenario(item.name)
                return True
        self.selected_item = None
        return False

    # コマンドメニューイベント
    def handle_command_menu_event(self, pos):
        self.event_manager.handle_command_click(pos)

    # ナビゲーションバーをクリックした場合のイベント
    def handle_navigation(self, clicked_position):
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

    # イベントマネージャーから次のシナリオを受け取るためのコールバック関数
    def handle_next_scenario(self, next_scenario):
        self.scenario_manager.start_scenario(next_scenario)

    # イベントマネージャーから次の部屋に移るためのコールバック関数
    def handle_move_room(self, room_id):
        next_room = room_id.split("-")[0]
        self.handle_room_view(next_room)
        self.scenario_manager.start_scenario(room_id)
        
    # 部屋の再作成をする（コールバック関数としても使う)
    def handle_room_view(self, room_id):
        next_room = room_id.split("-")[0] if "-room" in room_id else room_id
        self.room_manager.move_to_room(next_room=next_room)
        self.setup_navigetion()

    # マウスオーバー
    def handle_mouse_hover(self):
        key = pygame.mouse.get_pos()
        self.menu_controller.handle_mouse_hover(key)
        self.event_manager.handle_mouse_hover(key)

    # イベントハンドラ
    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                Close(self.root)

            # マウスクリック時
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event)

    # クリックイベント
    def handle_click(self, event):
        # シナリオ進行
        self.scenario_manager.on_click()

        # シナリオ進行中ではない場合
        if not self.scenario_manager.is_active:

            # コマンドメニュー表示中はそれを優先
            if self.event_manager.command_menu:
                self.handle_command_menu_event(event.pos)
            
            # メニューボタン
            elif self.menu_controller.handle_click(event.pos):
                return

            # ナビゲーションバーによる移動
            elif self.handle_navigation(self.navigation.handle_click(event.pos)):
                return
                
            # アイテムクリックイベント
            elif self.handle_item_click_event(event):
                return

    def draw(self):
        create_frame(self.screen)       # テキストフレームの表示

        self.menu_controller.draw()     # メニューの表示

        self.room_manager.draw()        # 部屋の表示

        self.navigation.draw()          # ナビゲーションバーの表示

        # 主人公のステータスの表示
        self.player_label.update(self.player_status, self.game_state)

        # コマンドメニューの表示
        #if self.event_manager.command_menu:
        #    self.event_manager.draw()
            
        # シナリオマネージャーの表示
        self.scenario_manager.draw()

    def update(self):
        if self.scenario_manager.is_active:
            self.scenario_manager.update()

        self.draw()
        self.handle_mouse_hover()
        self.handle_events()
        return self.next_state()

    # メニューボタン用のコールバック関数
    def set_state(self, state=State.NONE):
        self.create_save_data()
        self.state = state

    def next_state(self):
        if self.state == State.SAVE:
            self.state = State.NONE
            return "save", self.save_data
        elif self.state == State.LOAD:
            self.state = State.NONE
            return "load", self.save_data
        return "play", self.save_data
