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

        # ナビゲーションバー
        self.right_navi = None
        self.left_navi = None
        self.under_navi = None
        self.create_navigetion()

        # 部屋を作る
        self.create_room()

    # 部屋の作成
    def create_room(self):
        room2_flag = self.room2_flag_check(self.room_flag)
        self.room = Room(self.screen, self.room_flag, self.direction_flag, room2_flag)
        self.max_room_scenario_flag = len(self.room.scenario_list)
        print(self.room.scenario_list)

    # フラグをセットする
    def set_flag(self, play_flags):
        # フラグ一覧
        self.state = PlayState.NONE     # saveやload等の状態管理フラグ
        self.time = play_flags.get("time", 60)  # 残り時間フラグ（分）
        self.room_flag = play_flags.get("room_flag", "center")              # どの部屋にいるかフラグ
        self.direction_flag = play_flags.get("direction_flag", "north")     # どの方角を向いているかフラグ
        self.girl_flag = play_flags.get("girl_flag", False)                 # 少女を見つけてるかフラグ

        self.center_room_scenario_flag = play_flags.get("center_room_scenario_flag", 0) # 中央の部屋のシナリオフラグ
        self.north_room_scenario_flag = play_flags.get("north_room_scenario_flag", 0) # 北の部屋のシナリオフラグ
        self.south_room_scenario_flag = play_flags.get("south_room_scenario_flag", 0) # 南の部屋のシナリオフラグ
        self.east_room_scenario_flag = play_flags.get("east_room_scenario_flag", 0) # 東の部屋のシナリオフラグ
        self.west_room_scenario_flag = play_flags.get("west_room_scenario_flag", 0) # 西の部屋のシナリオフラグ
        self.max_room_scenario_flag = 0             # シナリオフラグの最大値
        self.light_flag = play_flags.get("light_flag", False)               # 電球が取られていないかフラグ
        self.west_room_book_found_flag = play_flags.get("book_found_flag", False)       # 本を見つけているかフラグ
        self.east_room_visible_flag = play_flags.get("east_room_visible_flag", False)    # 東の部屋が見えるようになっているかフラグ
        self.poison_get_flag = play_flags.get("poison_get_flag", False)     # 毒を見つけているかフラグ
        self.poison_input_flag = play_flags.get("poison_input_flag", False) # 毒をスープに入れているかフラグ
        self.west_room_book_have_flag = False    # 本を持っているかフラグ

    # 二つ目の部屋表示チェック
    def room2_flag_check(self, room):
        if room == "east":
            return self.east_room_visible_flag
        elif room == "west":
            return self.west_room_book_found_flag
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

    def handle_click(self, event):
        if not self.first_room_scenario(self.room_flag):
            if self.room_flag == "center":
                # ナビゲーションバーによる移動
                if self.right_navi and self.right_navi.handle_click(event.pos):
                    self.move_room("right")
                elif self.left_navi and self.left_navi.handle_click(event.pos):
                    self.move_room("left")
                else:
                    for item in self.room.items_select_list:
                        if item.handle_click(event.pos):
                            print(item.name)
                        pass
            else:
                # ナビゲーションバーによる移動
                if self.under_navi and self.under_navi.handle_click(event.pos):
                    self.move_room("under")

    def first_room_scenario(self, room):
        # 部屋に最初に入った時に起こるイベント
        # イベント中は他のクリックイベントは作動しない
        if room == "center":
            if self.center_room_scenario_flag < self.max_room_scenario_flag:
                self.center_room_scenario_flag += 1
                return True
        if room == "north":
            if self.north_room_scenario_flag < self.max_room_scenario_flag:
                self.north_room_scenario_flag += 1
                return True
        if room == "east":
            if self.east_room_scenario_flag < self.max_room_scenario_flag:
                self.east_room_scenario_flag += 1
                return True
        if room == "west":
            if self.west_room_scenario_flag < self.max_room_scenario_flag:
                self.west_room_scenario_flag += 1
                return True
        return False

    # 部屋移動をまとめる
    def move_room(self, position):
        if position == "under":
            self.room_flag, self.direction_flag = self.room_move_direction_get(self.room_flag)
        else:
            self.direction_flag = self.direction_move_get(position, self.direction_flag)
        self.create_room()

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

    def draw(self):
        create_frame(self.screen)   # テキストフレームの表示
        self.room.draw()            # 部屋の表示
        if self.left_navi:
            self.left_navi.draw()
        if self.right_navi:
            self.right_navi.draw()
        if self.under_navi:
            self.under_navi.draw()

    # シナリオ表示用
    def draw_scenario(self):
        text = ""
        file_name = ""
        room_scenario_flag = {"center": self.center_room_scenario_flag,
                              "north": self.north_room_scenario_flag,
                              "east": self.east_room_scenario_flag,
                              "west": self.west_room_scenario_flag}
        if room_scenario_flag[self.room_flag] < self.max_room_scenario_flag:
            if self.room.scenario_list:
                file_name = self.room.scenario_list[room_scenario_flag[self.room_flag]]
        if file_name:
            if os.path.isfile(file_name):
                with open(file_name,"r",encoding="utf-8_sig") as f:
                    text = f.read()
        TextDraw(self.screen, text)


    def update(self):
        self.draw()
        self.handle_events()
        self.draw_scenario()
        return self.next_state()
    
    def next_state(self):
        return "play", self.save_data

    

"""
# シナリオ表示用
def Scenario(screen, room):
    text = ""
    room_name = room + "_room"
    item_name = ""
    flag_name = ""
    if RoomFlag == CENTER:
        room_name = "_Center_room_"
        if CenterRoomFlag < 5:
            flag_name = str(CenterRoomFlag)
        else:
            pass

    file_name = ScenarioPath + room_name + item_name + flag_name + ".txt"
    if os.path.isfile(file_name):
        with open(file_name,"r",encoding="utf-8_sig") as f:
            text = f.read()
    TextDraw(screen, text)
"""