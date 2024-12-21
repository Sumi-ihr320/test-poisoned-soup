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
    
        # ナビゲーションバー
        self.navigation = Navigation(self.screen)
        self.setup_navigetion()

        # 主人公のステータス表示
        self.player_label = PlayerDataView(self.screen, self.player_status, self.game_state.room)

        # 管理用
        self.scenario_manager = ScenarioManager(self.screen, "center-room", self.flags, self.handle_action)
        self.event_manager = EventManager(self.screen, self.scenario_manager, self.flags)

        # 部屋の管理
        self.room_manager = RoomManager(self.screen, self.event_manager, self.flags)

        # 選択されたアイテム
        self.selected_item = None

    # データをセットする
    def set_data(self, save_data):
        # 主人公データ
        self.player_status = Player().from_dict(save_data["player_status"])

        # フラグ一覧
        self.state = State.NONE     # saveやload等の状態管理フラグ
        self.game_state = GameStatus().from_dict(save_data["game_state"])
        self.flags = Flags().from_dict(save_data["flags"])

    # セーブデータを作る
    def create_save_data(self):
        self.save_data = {
            "player_status": self.player_status.to_dict(),
            "game_state": self.game_state.to_dict(),
            "flags": self.flags.to_dict()
        }

    # ナビゲーションバーのセット
    def setup_navigetion(self):
        if self.game_state.room == "center":
            self.navigation.setup_navigation([Position.RIGHT, Position.LEFT])
        else:
            self.navigation.setup_navigation([Position.UNDER])
    
    # アイテムクリック時のイベントをまとめる
    def handle_item_click_event(self, event):
        for item in self.room_manager.room.items_select_list:
            if item.handle_click(event.pos):
                self.selected_item = item
                print(item.name)                # デバッグ用
                self.scenario_manager.start_scenario(item.name)
                return True
        self.selected_item = None
        return False

    # イベントマネージャーにシナリオマネージャーからデータを移す為のコールバック関数
    def handle_action(self, action, step):
        self.event_manager.handle_action(action, step)

    # コマンドメニューイベント
    def handle_command_menu_event(self, event):
        if self.event_manager.command_menu:
            self.event_manager.command_menu.handle_click(event.pos)

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
        self.scenario_manager.update()

        # シナリオ進行中ではない場合
        if not self.scenario_manager.is_active:

            # メニューボタン
            if self.menu_controller.handle_click(event.pos):
                return

            if self.game_state.room == "center":
                # ナビゲーションバーによる移動
                clicked_position = self.navigation.handle_click(event.pos)
                if clicked_position == Position.RIGHT:
                    self.room_manager.move_to_room("right")
                    self.selected_item = None
                elif clicked_position == Position.LEFT:
                    self.room_manager.move_to_room("left")
                    self.selected_item = None
                else:
                    if self.handle_item_click_event(event):
                        return
                    self.handle_command_menu_event(event)
            else:
                # ナビゲーションバーによる移動
                if self.navigation.handle_click(event.pos) is not None:
                    self.room_manager.move_to_room("under")
                else:
                    if self.handle_item_click_event(event):
                        return
                    self.handle_command_menu_event(event)


    def draw(self):
        create_frame(self.screen)       # テキストフレームの表示

        self.menu_controller.draw()     # メニューの表示

        self.room_manager.draw(self.selected_item, self.flags)  # 部屋の表示

        self.navigation.draw()          # ナビゲーションバーの表示

        # 主人公のステータスの表示
        self.player_label.draw()

        # コマンドメニューの表示
        if self.event_manager.command_menu:
            self.event_manager.command_menu.draw()
            
        # シナリオマネージャーの表示
        self.scenario_manager.draw()

    """
    # シナリオを作成する
    def create_scenario(self):
        self.text = ""
        file_name = ""
        if self.room_scenario_flag[self.room_flag] < self.max_room_scenario_flag:
            if self.room.scenario_list:
                file_name = self.room.scenario_list[self.room_scenario_flag[self.room_flag]]
        else:
            if self.selected_item:
                if self.selected_item.name == "Soup":
                    if self.time >= 45:
                        time = 1
                    elif self.time >= 30:
                        time = 2
                    elif self.time >= 15:
                        time = 3
                    else:
                        time = 4
                    event = "know" if self.soup_flag["know"] else ""
                    file_name = create_scenario_path(item="Soup", event=event, time=time)[0]
                elif self.selected_item.name == "centerMemo":
                    self.item_max_flag = 4 if self.items_flag["center_memo"]["objective"] else 3
                    if self.items_flag["center_memo"]["scenario"] < self.item_max_flag:
                        file_name = self.selected_item.scenario_path_list[self.items_flag["center_memo"]["scenario"]]
                elif self.selected_item.scenario_path_list:
                    file_name = self.selected_item.scenario_path_list[0]
        if file_name:
            self.text = load_text(file_name)

    def item_event(self):

        pass
    
    # シナリオ表示用
    """
    def update(self):
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
