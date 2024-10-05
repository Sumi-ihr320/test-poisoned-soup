import random, os, json, glob
from enum import Enum

import pygame
import pygame.draw
from pygame.locals import *
from tkinter import messagebox

from data import *
from fanction_summary import *
from class_summary import *

# プレイヤーの場所と向きの情報
player = {}
player["room"] = "center"
player["direction"] = "north"
player["flag"] = True
player["center_room_flag"] = 0

# 部屋画像の縮小パーセンテージ
SIZE = 0.19

class PlayState(Enum):
    NONE = 0
    SAVE = 1
    LOAD = 2
    SETTING = 3

# プレイ画面
class MainPlay:
    def __init__(self, screen, save_data=None):
        self.screen = screen
        self.save_data = save_data
        self.hero_status = save_data["hero_status"]  # 主人公のステータス
        play_flags = save_data["flag"]               # フラグリスト

        # フラグ一覧
        self.state = PlayState.NONE     # saveやload等の状態管理フラグ
        self.time = play_flags.get("time", 60)  # 残り時間フラグ（分）
        self.room_flag = play_flags.get("room_flag", "center")              # どの部屋にいるかフラグ
        self.direction_flag = play_flags.get("direction_flag", "north")     # どの方角を向いているかフラグ
        self.girl_flag = play_flags.get("girl_flag", False)                 # 少女を見つけてるかフラグ
        self.light_flag = play_flags.get("light_flag", False)               # 電球が取られていないかフラグ
        self.west_room_book_found_flag = play_flags.get("book_found_flag", False)       # 本を見つけているかフラグ
        self.east_room_visible_flag = play_flags.get("east_room_visible_flag", False)    # 東の部屋が見えるようになっているかフラグ
        self.poison_get_flag = play_flags.get("poison_get_flag", False)     # 毒を見つけているかフラグ
        self.poison_input_flag = play_flags.get("poison_input_flag", False) # 毒をスープに入れているかフラグ

        self.west_room_book_have_flag = False    # 本を持っているかフラグ

        # ナビゲーションバー
        self.right_navi = None
        self.left_navi = None
        self.under_navi = None
        self.create_navigetion()

        # 部屋の作成
        room2_flag = self.room2_flag_check(self.room_flag)
        self.room = Room(self.screen, self.room_flag, self.direction_flag, room2_flag)

    # 二つ目の部屋表示チェック
    def room2_flag_check(self, room):
        if room == "center":
            return self.light_flag
        elif room == "east":
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
        # ナビゲーションバーによる移動
        if self.right_navi and self.right_navi.handle_click(event.pos):
            self.direction_flag = self.direction_move_get("rigth", self.direction_flag)
        elif self.left_navi and self.left_navi.handle_click(event.pos):
            self.direction_flag = self.direction_move_get("left", self.direction_flag)
        elif self.under_navi and self.under_navi.handle_click(event.pos):
            self.room_flag, self.direction_flag = self.room_move_direction_get(self.room_flag)

    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT:
                Close()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                Close()
            # マウスクリック時
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event)

    def draw(self):
        create_frame(self.screen)   # テキストフレームの表示
        self.room.draw()            # 部屋の表示

    def update(self):
        self.draw()
        self.handle_events()
        return self.next_state()
    
    def next_state(self):
        return "play", self.save_data

# 部屋の型を作るよ
class Room:
    def __init__(self, screen, room, direction="", room2_flag=False):
        self.screen = screen
        self.room2_flag = room2_flag    # 二つ目の部屋画像を表示するかのフラグ

        # 部屋画像を表示するエリア
        self.area_rect = Rect(0,0,820,375)
        
        # ファイル名一覧
        self.room_path = create_file_path("room", room, direction)
        self.room2_path = create_file_path("room2", room, direction)
        self.scenario_list = create_scenario_path("", room)

        # 部屋画像の作成
        self.img = Image(self.screen, self.room_path, size=SIZE, x="center", y=30, area=self.area_rect)
        self.img2 = Image(self.screen, self.room2_path, size=SIZE, x="center", y=30, area=self.area_rect) if self.room2_path else None

        # 部屋にあるアイテムの作成
        self.items = []
        self.create_item(self.img, room, direction)

        # 部屋のシナリオが存在する場合
        if self.scenario_list != []:
            Scenario(self.screen, self.scenario_list)
        
        # 部屋の説明

    # 画像表示するよ
    def draw(self):
        # フラグが立っていればroom_img2を表示する
        if self.room2_flag:
            if self.img2:
                self.img2.draw()
        else:
            self.img.draw()

    # 部屋のアイテムを作成する
    def create_item(self, screen, room, direction):
        if room == "center":
            self.light = Item(self.screen, "Light", room, "", "center", 54)
            self.soup = Item(self.screen, "Soup", room, "", "center", 254)
            directions = ["north","east","south","west"]
            position = {"north":{"tablex":"center","tabley":219,
                                 "memox":341,"memoy":267},
                        "east":{"tablex":264,"tabley":242,
                                "memox":"center","memoy":283},
                        "south":{"tablex":"center","tabley":253,
                                 "memox":427,"memoy":267},
                        "west":{"tablex":295,"tabley":243,
                                "memox":"center","memoy":253}
            }
            center_door_name = f"{direction}Door"
            index = directions.index(direction)
            left_index = index - 1
            left_direct = directions[left_index]
            left_door_name = f"{left_direct}Door"
            right_index = index + 1
            if right_index > len(directions) - 1:
                right_index = 0
            right_direct = directions[right_index]
            rigth_door_name = f"{right_direct}Door"
            self.center_door = Item(self.screen, center_door_name, room, direction, "center", 112)
            self.left_door = Item(self.screen, left_door_name, room, direction, 121, 93)
            self.right_door = Item(self.screen, rigth_door_name, room, direction, 603, 94)
            self.table = Item(self.screen, "Table", "center", direction, position[direction]["tablex"], position[direction]["tabley"])
            self.center_memo = Item(self.screen, "Memo", "center", direction, position[direction]["memox"], position[direction]["memoy"])
        elif room == "north":
            self.under_storage = Item(self.screen, "UnderSinkStorage", "north", "", 325, 250)
            self.cooktop = Item(self.screen, "Cooktop", "north", "", 225, 226)
            self.sink = Item(self.screen, "Sink", "north", "", 468, 216)
            self.top_storage = Item(self.screen, "TopSinkStorage", "north", "", 325, 100)
            self.pot = Item(self.screen, "Pot", "north", "", 290, 203)
            self.storage = Item(self.screen, "Storage", "north", "", 560, 225)
            self.cupboard = Item(self.screen, "CupBoard", "north", "", 36, 30)
            self.fridge = Item(self.screen, "Fridge", "north", "", 628, 39)
        elif room == "east":
            self.corpse = Item(self.screen, "Corpse", "east", "", 437, 218)
            self.east_memo = Item(self.screen, "Memo", "east", "", 277, 259)
        elif room == "south":
            self.statue = Item(self.screen, "StoneStatue", "south", "",287, 69)
            self.slate1 = Item(self.screen, "Slate1", "south", "", 213, 156)
            self.slate2 = Item(self.screen, "Slate2", "south", "", 479, 156)
        else:
            self.bookshelf = Item(self.screen, "BookShelf", "west", "", 36, 30)
            self.chandle = Item(self.screen, "Candle", "west", "", 350, 223)
            self.book = Item(self.screen, "Book", "west", "", 298, 246)

# アイテムの型を作るよ
class Item:
    def __init__(self, screen, name, room, direction, x, y):
        self.screen = screen
        self.name = name    # アイテム名

        # ファイルパス
        self.path = create_file_path(name, room, direction)

        # 画像
        self.img = Image(self.screen, self.path, SIZE, x, y)

        # シナリオファイルパス
        self.scenario_path_list = create_scenario_path(name, room)

        # クリック時画像パス
        self.big_img_path_list = create_item_path(name)
    
    def draw(self):
        self.img.draw()

    def handle_click(self):
        # 表示するテキスト
    
        # 起こるイベント
        pass
    
# シナリオのパスを作って返す
def create_scenario_path(item, room):
    path = f".{SCENARIO}"
    room_path = f"{path}{room}-room"
    item_path = room_path
    if item != "":
        item_path = f"{room_path}_{item}"
        search_text = f"{item_path}*.txt"
    else:
        search_text = f"{item_path}?.txt"
    return glob.glob(search_text)

# アイテムファイルのパス名を作って返す
def create_item_path(item):
    path = f".{PICTURE}"
    search_text = f"{path}{item}*.png"
    return glob.glob(search_text)

# 画像のファイル名を作って返す
def create_file_path(item, room, direction):
    path = f"{PATH}{PICTURE}"
    room_path = f"{path}{room}-room"
    if room == "center":
        if direction != "":
            room_path += f"_{direction}"

    if item == "room":
        return f"{room_path}.jpg"

    if item == "room2":
        if room == "east":
            return f"{path}black-room.jpg"
        elif room == "west":
            return f"{room_path}_PicupBook.jpg"
        else:
            return ""

    # アイテムのパスを作っていく
    img_path = f"{room_path}_{item}.png"

    return img_path

# シナリオの表示システムを作るよ
class Scenario:
    def __init__(self, screen, scenario_list):

        self.view(screen, scenario_list)

    def view(self, screen, scenario_list):
        for path in scenario_list:
            
            pass
#        if os.path.isfile(path):
#            with open(path,"r",encoding="utf-8_sig") as f:
#                text = f.read()
#        TextDraw(screen, text)


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

# フェードイン試し用
def FadeIn(screen, clock, background, speed=1):
    alpha = 255
    while alpha >= 0:
        background.set_alpha(alpha)
        screen.fill(BLACK)
        screen.blit(background,(20,20))
        pygame.display.flip()
        alpha -= speed
        clock.tick(60)

