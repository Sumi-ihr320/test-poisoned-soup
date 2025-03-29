import pygame
from pygame.locals import *

from constans import *
from utils import *
from ui_elements import Image

# 部屋の型を作るよ
class Room:
    # 部屋画像の縮小パーセンテージ
    SIZE = 0.19
    def __init__(self, screen, room, direction="", room_change_flag=None):
        self.screen = screen
        self.room = room
        self.direction = direction
        self.room_change_flag = room_change_flag if room_change_flag else {}    # どの部屋画像を表示するかのフラグ

        # 部屋画像を表示するエリア
        self.area_rect = ROOM_AREA
        
        # ファイル名一覧
        self.room_path = create_file_path("room", room, direction, self.room_change_flag)
        #self.room2_path = create_file_path("room2", room, direction)

        # 部屋画像の作成
        self.img = Image(self.screen, self.room_path, size=self.SIZE, x="center", y=30, area=self.area_rect)
        #self.img2 = Image(self.screen, self.room2_path, size=self.SIZE, x="center", y=30, area=self.area_rect) if self.room2_path else None

        # 部屋にあるアイテムの作成
        self.items = []
        self.items_draw_list = []
        self.items_select_list= []
        self.create_room_item()

    # 画像表示するよ
    def draw(self):

        # 部屋表示
        self.img.draw()
        # アイテム表示
        if self.items_draw_list:
            for item in self.items_draw_list:
                item.draw()

    # 部屋のアイテムを作成する
    def create_room_item(self):
        room_items = {
            "center":{
                "draw_order":[
                    (f"{self.direction}Door", "center", self.direction, "center", 82),
                    (f"{self.get_abjacent_direction(-1)}Door", "center", self.direction, 86, 63),
                    (f"{self.get_abjacent_direction(1)}Door", "center", self.direction, 568, 64),
                    ("Table", "center", self.direction, *self.get_table_pos()),
                    ("Light", "center", "", "center", 24),
                    ("Soup", "center", "", "center", 224),
                    ("centerMemo", "center", self.direction, *self.get_center_memo_pos())],
                "select_order":["Light", "Soup", "centerMemo", "Table", f"{self.direction}Door",
                                f"{self.get_abjacent_direction(-1)}Door", f"{self.get_abjacent_direction(1)}Door"]
            },
            "north":{
                "draw_order":[
                    ("UnderSinkStorage", "north", "", 289, 220),
                    ("Cooktop", "north", "", 189, 196),
                    ("Sink", "north", "", 432, 186),
                    ("TopSinkStorage", "north", "", 289, 70),
                    ("Pot", "north", "", 254, 173),
                    ("Storage", "north", "", 524, 195),
                    ("CupBoard", "north", "", 0, 0),
                    ("Fridge", "north", "", 592, 9)],
                "select_order":["Pot", "Sink", "Cooktop", "UnderSinkStorage", "TopSinkStorage", "Storage", 
                                "Cupboard", "Fridge"]
            },
            "east":{
                "draw_order":[
                    ("Corpse", "east", "", 401, 188),
                    ("eastMemo", "east", "", 241, 229)],
                "select_order":["eastMemo", "Corpse"]
            } if self.room_change_flag.get("east_room_visible") else {
                "draw_order":[],
                "select_order":[]
            },
            "south":{
                "draw_order":[
                    ("StoneStatue", "south", "", 287, 69),
                    ("Slate1", "south", "", 213, 156),
                    ("Slate2", "south", "", 479, 156)],
                "select_order":["StoneStatue", "Slate1", "Slate2"]
            },
            "west":{
                "draw_order":[
                    ("BookShelf", "west", "", 0, 0),
                    ("Book", "west", "", 262, 216)],
                "select_order":["Book", "BookShelf"]
            } if self.room_change_flag.get("book_found") and self.room_change_flag.get("candle_get") else ({
                "draw_order":[
                    ("BookShelf", "west", "", 0, 0),
                    ("Candle", "west", "", 314, 193),
                    ("Book", "west", "", 262, 216),
                ],
                "select_order":["Book", "Candle", "BookShelf"]
            } if self.room_change_flag.get("book_found") else ({
                "draw_order":[("BookShelf", "west", "", 0, 0)],
                "select_order":["BookShelf"]
            } if self.room_change_flag.get("candle_get") else {
                "draw_order":[
                    ("BookShelf", "west", "", 0, 0),
                    ("Candle", "west", "", 314, 193)],
                "select_order":["Candle", "BookShelf"]
            }))
        }

        # 該当する部屋のアイテムを作成
        if self.room in room_items:
            # 表示順でアイテムを作成
            for item in room_items[self.room]["draw_order"]:
                self.items_draw_list.append(RoomItem(self.img.img, self.room_change_flag, *item))

            # 選択順にアイテムを格納
            item_dict = {obj.name: obj for obj in self.items_draw_list}     # 作成済みオブジェクトを辞書に
            for item_name in room_items[self.room]["select_order"]:
                if item_name in item_dict:
                    self.items_select_list.append(item_dict[item_name])

    # 現在の方角から左右の方角を求める
    def get_abjacent_direction(self, ofset):
        directions = ["north","east","south","west"]
        index = directions.index(self.direction)
        return directions[(index + ofset) % len(directions)]
    
    # 方向に応じたテーブルの座標
    def get_table_pos(self):
        table_positions = {
            "north": ("center", 189),
            "east": (229, 212),
            "south": ("center", 223),
            "west":(260, 213)
        }
        return table_positions.get(self.direction, ("center", 189))

    def get_center_memo_pos(self):
        memo_positions = {
            "north": (306, 237),
            "east": ("center", 253),
            "south": (392, 237),
            "west": ("center", 223)
        }
        return memo_positions.get(self.direction, (306, 237))

# アイテムの型を作るよ
class RoomItem:
    # アイテム画像の縮小パーセンテージ
    SIZE = 0.19
    def __init__(self, screen, room_change_flag, name, room, direction, x, y):
        self.screen = screen
        self.name = name    # アイテム名

        # アイテムの基本情報
        self.path = create_file_path(name, room, direction, room_change_flag)   # ファイルパス
        self.img = Image(self.screen, self.path, self.SIZE, x, y)       # 画像

    def draw(self):
        self.img.draw()
        pygame.draw.rect(self.screen, BLACK, self.img.rect, 1)  # デバッグ用

    def handle_click(self, pos):
        return self.img.rect.collidepoint(pos)