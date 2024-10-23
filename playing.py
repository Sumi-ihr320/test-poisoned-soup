from enum import Enum

import pygame
import pygame.draw
from pygame.locals import *

from data import *
from fanction_summary import *
from class_summary import *

class PlayState(Enum):
    NONE = 0
    SAVE = 1
    LOAD = 2
    SETTING = 3

# プレイ画面
class MainPlay:
    def __init__(self, screen, root, save_data=None):
        self.screen = screen
        self.root = root
        self.save_data = save_data
        self.hero_status = save_data["hero_status"]  # 主人公のステータス
        
        # フラグをセットする
        self.set_flag(save_data["flag"])

        # メニューを作る
        self.menu = None
        self.create_menu()
    
        # ナビゲーションバー
        self.right_navi = None
        self.left_navi = None
        self.under_navi = None
        self.create_navigetion()

        # 部屋を作る
        self.room = None
        self.create_room()

        # 表示するシナリオのリスト
        self.scenario_list = []
        # テキストフレームに表示するテキスト
        self.text = ""

        # 選択されたアイテム
        self.selected_item = None

    # メニューの作成
    def create_menu(self):
        self.menu = Menu(self.screen, self.root)

    # 部屋の作成
    def create_room(self):
        room2_flag = self.room2_flag_check(self.room_flag)
        self.room = Room(self.screen, self.room_flag, self.direction_flag, room2_flag)
        self.max_room_scenario_flag = len(self.room.scenario_list)
        print(self.room.scenario_list)  # デバッグ用

    # フラグをセットする
    def set_flag(self, play_flags):
        # フラグ一覧
        self.state = PlayState.NONE     # saveやload等の状態管理フラグ
        self.time = play_flags.get("time", 60)  # 残り時間フラグ（分）
        self.room_flag = play_flags.get("room_flag", "center")              # どの部屋にいるかフラグ
        self.direction_flag = play_flags.get("direction_flag", "north")     # どの方角を向いているかフラグ
        self.girl_flag = play_flags.get("girl_flag", False)                 # 少女を見つけてるかフラグ

        self.room_scenario_flag = play_flags.get("room_scenario_flag", {"center":0, "north":0, "south":0, "east":0, "west":0})    # 各部屋のシナリオフラグ
        self.max_room_scenario_flag = 0             # シナリオフラグの最大値
        self.light_flag = play_flags.get("light_flag", False)               # 電球が取られていないかフラグ
        self.east_room_flag = play_flags.get("east_room_flag", {"open":False, "visivle":False})     # 東の部屋のフラグ
        self.poison_get_flag = play_flags.get("poison_get_flag", False)     # 毒を見つけているかフラグ

        # アイテムの状態フラグ
        self.soup_flag = play_flags.get("soup_flag", {"poison":False, "know":False, "drink":False, "temperature":0}) # スープに関するフラグ
        self.center_memo_flag = play_flags.get("center_memo_flag", {"scenario":0, "objective":False})       # 真ん中の部屋のメモに関するフラグ
        self.book_flag = play_flags.get("book_flag", {"found":False, "get":False})  # 西の部屋の本に関するフラグ

    # 二つ目の部屋表示チェック
    def room2_flag_check(self, room):
        if room == "east":
            return self.east_room_flag["visivle"]
        elif room == "west":
            return self.book_flag["found"]
        else:
            return False

    # ナビゲーションバーを作成
    def create_navigetion(self):
        # ナビゲーションバーの表示
        if self.room_flag == "center":
            self.right_navi = PageNavigation(self.screen, RIGHT)
            self.left_navi = PageNavigation(self.screen, LEFT)
        else:
            self.under_navi = PageNavigation(self.screen, UNDER)

    # 向き移動先を取得
    def direction_move_get(self, position, direction):
        if position == "right":
            if direction == "north":
                return "east"
            elif direction == "east":
                return "south"
            elif direction == "south":
                return "west"
            else:
                return "north"
        elif position == "left":
            if direction == "north":
                return "west"
            elif direction == "west":
                return "south"
            elif direction == "south":
                return "east"
            else:
                return "north"
            
        # 扉からの移動先
        elif position == "center":
            return direction
                
        else:
            return direction

    # 部屋の戻り先を取得
    def room_move_direction_get(self, room):
        if room == "north":
            direction = "south"
        elif room == "south":
            direction = "north"
        elif room == "east":
            direction = "west"
        else:
            direction = "east"
        return "center", direction

    # 部屋移動をまとめる
    def move_room(self, position):
        if position == "under":
            if self.book_flag["get"]:
                # 本を持って出ようとしたらイベント
                pass
                # 戦闘終了後は部屋のほうを向いている
                self.room_flag, self.direction_flag = "center", self.room_flag
                # 扉が元に戻ったことを説明
            else:
                self.room_flag, self.direction_flag = self.room_move_direction_get(self.room_flag)
        else:
            self.direction_flag = self.direction_move_get(position, self.direction_flag)
        self.create_room()

    # 部屋に最初に入った時に起こるイベント   ※イベント中は他のクリックイベントは作動しない
    def first_room_scenario_count(self, room):
        if self.room_scenario_flag[room] < self.max_room_scenario_flag:
            self.room_scenario_flag[room] += 1
            return True
        return False

    def handle_mouse_hover(self):
        key = pygame.mouse.get_pos()
        for button in self.menu.buttons:
            button.update(key)
            
    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT:
                Close(self.root)
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                Close(self.root)
            # マウスクリック時
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event)

    def handle_click(self, event):
        if not self.first_room_scenario_count(self.room_flag):
            if self.room_flag == "center":
                # ナビゲーションバーによる移動
                if self.right_navi and self.right_navi.handle_click(event.pos):
                    self.move_room("right")
                elif self.left_navi and self.left_navi.handle_click(event.pos):
                    self.move_room("left")
                else:
                    for button in self.menu.buttons:
                        if button.update(event.pos, True):
                            break

                    for item in self.room.items_select_list:
                        if item.handle_click(event.pos):
                            self.selected_item = item
                            print(item.name)                # デバッグ用
                            print(item.scenario_path_list)  # デバッグ用
                            break
            else:
                # ナビゲーションバーによる移動
                if self.under_navi and self.under_navi.handle_click(event.pos):
                    self.move_room("under")

    def draw(self):
        create_frame(self.screen)   # テキストフレームの表示
        self.menu.draw()            # メニューの表示
        self.room.draw()            # 部屋の表示
        if self.left_navi:
            self.left_navi.draw()
        if self.right_navi:
            self.right_navi.draw()
        if self.under_navi:
            self.under_navi.draw()
        if self.selected_item:
            img_number = 0
            if self.selected_item == "Soup":
                if self.soup_flag["drink"]:
                    img_number = 1
                elif self.soup_flag["poison"]:
                    img_number = 2
            self.selected_item.draw(is_selected=True, img_number=img_number)

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
                    pass
                elif self.selected_item.scenario_path_list:
                    file_name = self.selected_item.scenario_path_list[0]
        if file_name:
            self.text = load_text(file_name)

    # シナリオ表示用
    def draw_scenario(self):
        self.create_scenario()
        TextDraw(self.screen, self.text)

    def update(self):
        self.draw()
        self.handle_mouse_hover()
        self.handle_events()
        self.draw_scenario()
        return self.next_state()
    
    def next_state(self):
        return "play", self.save_data
