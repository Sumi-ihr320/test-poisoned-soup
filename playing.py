import pygame
import pygame.draw
from pygame.locals import *

from constans import *
from utils import *
from ui_elements import *

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
        self.hero_status = save_data["hero_status"]  # 主人公のステータス
        
        # フラグをセットする
        self.set_flag(save_data["flag"])

        # メニューコントローラー
        self.menu_controller = MenuController(self.screen, self.root, self.set_state)
    
        # ナビゲーションバー
        self.navigation = Navigation(self.screen)
        self.setup_navigetion()

        # 部屋の管理
        self.room_manager = RoomManager(self.screen, self.room_flag, self.direction_flag, self.east_room_flag, self.items_flag["book"])

        # 主人公のステータス表示
        self.status_label = None
        self.create_hero_label()

        self.scenario_manager = ScenarioManager(self.screen, "center-room")
        self.event_manager = EventManager(self.screen, self.scenario_manager)

        # 選択されたアイテム
        self.selected_item = None

    # 主人公の名前・HP・MP・現在地を右上に表示する
    def create_hero_label(self):
        font = pygame.font.Font(FONT_PATH, SMALL_SIZ)
        name_label = Label(self.screen, font, self.hero_status["name"], 500, 10, position="right", color=WHITE)
        hp_label = Label(self.screen, font, f"HP/{self.hero_status["HP"]}", 590, 10, position="right", color=WHITE)
        mp_label = Label(self.screen, font, f"MP/{self.hero_status["MP"]}", 650, 10, position="right", color=WHITE)
        current_room_label = Label(self.screen, font, ROOM_NAME[self.room_flag], 770, 10, position="right", color=WHITE)
        self.status_label = [name_label, hp_label, mp_label, current_room_label]

    # フラグをセットする
    def set_flag(self, play_flags):
        # フラグ一覧
        self.state = State.NONE     # saveやload等の状態管理フラグ
        self.time = play_flags.get("time", 60)  # 残り時間フラグ（分）
        self.room_flag = play_flags.get("room_flag", "center")              # どの部屋にいるかフラグ
        self.direction_flag = play_flags.get("direction_flag", "north")     # どの方角を向いているかフラグ
        self.girl_flag = play_flags.get("girl_flag", False)                 # 少女を見つけてるかフラグ

        # 各部屋のシナリオフラグ
        self.room_scenario_flag = play_flags.get(
            "room_scenario_flag", {"center":0, "north":0, "south":0, "east":0, "west":0}
        )
        self.max_room_scenario_flag = 0             # シナリオフラグの最大値
        self.light_flag = play_flags.get("light_flag", False)               # 電球が取られていないかフラグ
        self.east_room_flag = play_flags.get("east_room_flag", {"open":False, "visivle":False})     # 東の部屋のフラグ
        self.poison_get_flag = play_flags.get("poison_get_flag", False)     # 毒を見つけているかフラグ

        # アイテムの状態フラグ
        self.items_flag = play_flags.get(
            "items_flag", {
                    "soup", {"poison":False, "know":False, "drink":False, "temperature":0},    # スープに関するフラグ
                    "center_memo", {"scenario":0, "objective":False},                          # 真ん中の部屋のメモに関するフラグ
                    "book", {"found":False, "get":False}                                       # 西の部屋の本に関するフラグ
            }
        )

    # セーブデータを作る
    def create_save_data(self):
        save_data = {}
        save_data["hero_status"] = self.hero_status
        flag = {"time":self.time,
                "room_flag":self.room_flag,
                "direction_flag":self.direction_flag,
                "girl_flag":self.girl_flag,
                "room_scenario_flag":self.room_scenario_flag,
                "light_flag":self.light_flag,
                "east_room_flag":self.east_room_flag,
                "poison_get_flag":self.poison_get_flag,
                "items_flag":self.items_flag,
                }
        save_data["flag"] = flag
        self.save_data = save_data

    # ナビゲーションバーのセット
    def setup_navigetion(self):
        if self.room_flag == "center":
            self.navigation.setup_navigation([Position.RIGHT, Position.LEFT])
        else:
            self.navigation.setup_navigation([Position.UNDER])

    # 部屋に最初に入った時に起こるイベント   ※イベント中は他のクリックイベントは作動しない
    def first_room_scenario_count(self, room):
        if self.room_scenario_flag[room] < self.max_room_scenario_flag:
            self.room_scenario_flag[room] += 1
            return True
        return False
    
    # アイテムが選択された時のシナリオフラグカウント（うまくいってない）
    def selected_item_scenario_count(self, item):
        if item == "centerMemo":
            if self.items_flag["center_memo"]["scenario"] < self.item_max_flag:
                self.items_flag["center_memo"]["scenario"] += 1
                return True
        return False

    # アイテムクリック時のイベントをまとめる
    def handle_item_click_event(self, event):
        for item in self.room_manager.room.items_select_list:
            if item.handle_click(event.pos):
                self.selected_item = item
                print(item.name)                # デバッグ用
                self.event_manager.tregger_item_event(item)
                return True
        self.selected_item = None
        return False

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
        if not self.first_room_scenario_count(self.room_flag):
            if not self.selected_item_scenario_count(self.selected_item):
                # メニューボタン
                if self.menu_controller.handle_click(event.pos):
                    return

                if self.room_flag == "center":
                    # ナビゲーションバーによる移動
                    clicked_position = self.navigation.handle_click(event.pos)
                    if clicked_position == Position.RIGHT:
                        self.room_manager.move_room("right")
                        self.selected_item = None
                    elif clicked_position == Position.LEFT:
                        self.room_manager.move_room("left")
                        self.selected_item = None
                    else:
                        if self.handle_item_click_event(event):
                            return
                        self.handle_command_menu_event(event)
                else:
                    # ナビゲーションバーによる移動
                    if self.navigation.handle_click(event.pos) is not None:
                        self.room_manager.move_room("under")
                    else:
                        if self.handle_item_click_event(event):
                            return
                        self.handle_command_menu_event(event)

    def draw(self):
        create_frame(self.screen)       # テキストフレームの表示
        self.menu_controller.draw()     # メニューの表示
        self.room_manager.draw(self.selected_item, self.items_flag["soup"])  # 部屋の表示
        self.navigation.draw()          # ナビゲーションバーの表示

        # 主人公のステータスの表示
        for status in self.status_label:
            status.draw()

        if self.event_manager.command_menu:
            self.event_manager.command_menu.draw()
            
        self.scenario_manager.draw()

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
        # 悩み中　item_managerかevent_managerを使う
        # menuを表示

        # doorのイベント
        # ドア画像表示
        # メニュー表示 → 入るで移動
        # 東の部屋は鍵開けイベント有り
        # 南の部屋は窓を覗く、聞き耳、入る（静かに・普通に・勢いよく）
    

        # centerMemoの時のイベントまとめ
        # memo1～3のシナリオ表示
        # memo1の時は1枚目の画像、memo3の時に２枚目の画像、memo4の時に３枚目の画像を表示
        # memoに目星コマンドでmemo_objectiveシナリオ表示 → 目星ダイスロール
        # 目星成功でmemo_objectiveシナリオ進行 → objectiveフラグtrue
        # memo1～4でシナリオが表示されるように

        # soupは医学成功で情報開示
        # あとは時間等で表示が変わる

        pass
    
    # シナリオ表示用

    def update(self):
        self.draw()
        self.handle_mouse_hover()
        self.handle_events()
        self.draw_scenario()
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
