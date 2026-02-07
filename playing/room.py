from typing import Dict, List, Tuple, Any, Optional
import pygame
from pygame.locals import *

from constans import BLACK, SHEET_COLOR, SHEET_SIZE
from utils import get_new_size, get_scales, create_file_path
from ui.ui_elements import Image, ImageCache

# 部屋の型を作るよ
class Room:
    # 部屋画像の縮小パーセンテージ
    SIZE = 0.2
    def __init__(self, screen, frame_rect: pygame.Rect, 
                 room: str, direction: str="", room_change_flag: Optional[Dict[str, Any]]=None, 
                 image_cache: Optional[ImageCache]=None):
        self.screen = screen
        self.screen_size = screen.get_size()

        # フラグ
        self.room = room
        self.direction = direction
        self.room_change_flag = room_change_flag if room_change_flag else {}    # どの部屋画像を表示するかのフラグ

        # イメージ用cache
        self.image_cache = image_cache

        self.frame_rect = frame_rect

        # 部屋画像表示用surface
        self.create_surface()
        
        # ファイル名一覧
        self.room_path = create_file_path("room", room, direction, self.room_change_flag)

        # 部屋画像の作成
        self.shrink_percent = self.get_shrink_percentage()
        self.room_img = Image(self.screen, self.room_path, self.image_cache, scale=self.shrink_percent, x="center", y="center", parent=self)

        # 部屋にあるアイテムの作成
        self.items = []
        self.items_draw_list = []
        self.items_select_list= []
        self.create_room_item()
        
    # 画像表示するよ
    def draw(self):
        self.screen.blit(self.surface, self.surface_rect.topleft)
        # 部屋表示
        self.room_img.draw()
        # アイテム表示
        if self.items_draw_list:
            for item in self.items_draw_list:
                item.draw()

    def relayout(self, screen):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.create_surface()
        self.room_img.relayout(screen, self.surface)

    def handle_mouse_hover(self, pos):
        if self.items_select_list:
            for item in self.items_select_list:
                pos_x, pos_y = pos
                new_pos = (pos_x - self.surface_rect.x, pos_y - self.surface_rect.y)
                item.handle_mouse_hover(new_pos)

    # 部屋用のsurfaceを作成
    def create_surface(self):
        self.room_size = get_new_size(self.screen_size, SHEET_SIZE, True)
        self.surface = pygame.Surface(self.room_size)
        screen_rect = self.screen.get_rect()
        self.surface_rect = self.surface.get_rect(centerx=screen_rect.centerx, bottom=self.frame_rect.top - 20)

        self.surface.fill(SHEET_COLOR)

    # オフセットを返す
    def get_global_offset(self):
        return self.surface_rect.topleft

    # rectを返す
    def get_rect(self):
        return self.surface_rect

    # 画像サイズの縮小パーセンテージを取得する
    def get_shrink_percentage(self):
        _, _, aspect_scale = get_scales(self.screen_size)
        return self.SIZE * aspect_scale

    # 部屋のアイテムを作成する
    def create_room_item(self):
        soup_name = self.check_flag_item_name("Soup")
        light_name = self.check_flag_item_name("Light")
        book_shelf_name = self.check_flag_item_name("BookShelf")

        center_order = self.check_flag_item_order("center")
        west_order = self.check_flag_item_order("west")
        room_items = {
            "center":{
                "items":[
                    [f"{self.direction}Door", "center", self.direction, "center", 58],
                    [f"{self.get_abjacent_direction(-1)}Door", "center", self.direction, 75, 38],
                    [f"{self.get_abjacent_direction(1)}Door", "center", self.direction, 584, 39],
                    ["Table", "center", self.direction, *self.get_table_pos()],
                    [light_name, "center", "", "center", -1],
                    [soup_name, "center", "", "center", 207],
                    ["centerMemo", "center", self.direction, *self.get_center_memo_pos()]
                ],
                "draw_order":center_order.get("draw_order", []),
                "select_order":center_order.get("select_order", [])
            },
            "north":{
                "items":[
                    ["UnderSinkStorage", "north", "", 290, 204],
                    ["Cooktop", "north", "", 186, 179],
                    ["Sink", "north", "", 441, 168],
                    ["TopSinkStorage", "north", "", 291, 47],
                    ["Pot", "north", "", 255, 155],
                    ["Storage", "north", "", 538, 178],
                    ["CupBoard", "north", "", -14, -27],
                    ["Fridge", "north", "", 610, -18]],
                "draw_order":["UnderSinkStorage", "Cooktop", "Sink", "TopSinkStorage", "Pot", "Storage",
                              "CupBoard", "Fridge"],
                "select_order":["Pot", "Sink", "Cooktop", "UnderSinkStorage", "TopSinkStorage", "Storage", 
                                "Cupboard", "Fridge"]
            },
            "east":{
                "items":[
                    ["Corpse", "east", "", 401, 188],
                    ["eastMemo", "east", "", 241, 229]],
                "draw_order":["Corpse", "eastMemo"] if self.room_change_flag.get("east_room_visible") else [],
                "select_order":["eastMemo", "Corpse"] if self.room_change_flag.get("east_room_visible") else []
            },
            "south":{
                "items":[
                    ["StoneStatue", "south", "", 287, 69],
                    ["Slate1", "south", "", 213, 156],
                    ["Slate2", "south", "", 479, 156]],
                "draw_order":["StoneStatue", "Slate1", "Slate2"],
                "select_order":["StoneStatue", "Slate1", "Slate2"]
            },
            "west":{
                "items":[
                    [book_shelf_name, "west", "", "center", -30],
                    ["Candle", "west", "", 315, 173],
                    ["Book", "west", "", 262, 216]
                ],
                "draw_order":west_order.get("draw_order", []),
                "select_order":west_order.get("select_order", [])
            }
        }

        # 該当する部屋のアイテムを作成
        if self.room in room_items:
            scale_x, scale_y, _ = get_scales(self.screen_size)
            
            items_list = []
            # アイテムを作成
            for item in room_items[self.room]["items"]:
                item[3] = int(item[3] * scale_x) if type(item[3]) == int else item[3]
                item[4] = int(item[4] * scale_y) if type(item[4]) == int else item[4]
                items_list.append(RoomItem(self.screen, self, self.room_change_flag, self.shrink_percent, *item, image_cache=self.image_cache))

            # 表示順にアイテムを格納
            item_dict = {obj.name: obj for obj in items_list}     # 作成済みオブジェクトを辞書に
            for item_name in room_items[self.room]["draw_order"]:
                if item_name in item_dict:
                    self.items_draw_list.append(item_dict[item_name])

            # 選択順にアイテムを格納
            for item_name in room_items[self.room]["select_order"]:
                if item_name in item_dict:
                    self.items_select_list.append(item_dict[item_name])

    #　フラグによるアイテム名を取得する
    def check_flag_item_name(self, item: str) -> str:
        item_name = item
        if item == "Soup":
            if self.room_change_flag.get("soup_in_poison"):
                item_name = f"{item_name}_poison"
            elif self.room_change_flag.get("soup_drink") or self.room_change_flag.get("soup_destruction"):
                item_name = f"{item_name}_none"
        elif item == "Light":
            if self.room_change_flag.get("light_remove"):
                item_name = f"{item_name}_nothing"
        elif item == "BookShelf":
            if self.room_change_flag.get("candle_get"):
                item_name = f"{item_name}_no_candle"
        return item_name
    
    # フラグによるアイテム順列を取得する
    def check_flag_item_order(self, room: str) -> Dict[str, Dict[str, List[str]]]:
        if room == "west":
            book_shelf_name = self.check_flag_item_name("BookShelf")
            book_found = self.room_change_flag.get("book_found")
            candle_get = self.room_change_flag.get("candle_get")
            if book_found and candle_get:
                order = {"draw_order":[book_shelf_name, "Book"],
                        "select_order":["Book", book_shelf_name]}
            elif book_found:
                order = {"draw_order":[book_shelf_name, "Candle", "Book"],
                        "select_order":["Book", "Candle", book_shelf_name]}
            elif candle_get:
                order = {"draw_order":[book_shelf_name],
                        "select_order":[book_shelf_name]}
            else:
                order = {"draw_order":[book_shelf_name, "Candle"],
                        "select_order":["Candle", book_shelf_name]}
            return order
        elif room == "center":
            soup_name = self.check_flag_item_name("Soup")
            light_name = self.check_flag_item_name("Light")
            bowl_get = self.room_change_flag.get("soup_bowl_get")
            if bowl_get:
                order = {"draw_order":[f"{self.direction}Door", f"{self.get_abjacent_direction(-1)}Door",
                                       f"{self.get_abjacent_direction(1)}Door", "Table", light_name, "centerMemo"],
                        "select_order":["Light", "centerMemo", "Table", f"{self.direction}Door",
                                        f"{self.get_abjacent_direction(-1)}Door", f"{self.get_abjacent_direction(1)}Door"]}
            else:
                order = {"draw_order":[f"{self.direction}Door", f"{self.get_abjacent_direction(-1)}Door",
                                       f"{self.get_abjacent_direction(1)}Door", "Table", light_name, soup_name, "centerMemo"],
                        "select_order":["Light", soup_name, "centerMemo", "Table", f"{self.direction}Door",
                                        f"{self.get_abjacent_direction(-1)}Door", f"{self.get_abjacent_direction(1)}Door"]}
            return order

    # 現在の方角から左右の方角を求める
    def get_abjacent_direction(self, ofset: int) -> str:
        directions = ["north", "east", "south", "west"]
        index = directions.index(self.direction)
        return directions[(index + ofset) % len(directions)]
    
    # 方向に応じたテーブルの座標
    def get_table_pos(self):
        table_positions = {
            "north": ("center", 171),
            "east": (228, 194),
            "south": ("center", 207),
            "west":(259, 195)
        }
        return table_positions.get(self.direction, ("center", 171))

    def get_center_memo_pos(self):
        memo_positions = {
            "north": (308, 221),
            "east": ("center", 236),
            "south": (397, 219),
            "west": ("center", 205)
        }
        return memo_positions.get(self.direction, (306, 217))
    

# アイテムの型を作るよ
class RoomItem:
    # アイテム画像の縮小パーセンテージ
    SIZE = 0.19
    def __init__(self, screen, parent, room_change_flag: Dict[str, Any], shrink_percent: float, 
                 name: str, room: str, direction: Optional[str], 
                 x: int, y: int, anchor: Tuple[str, str]=("left", "top"), image_cache: ImageCache=None):
        self.screen = screen
        self.parent = parent
        self.name = name    # アイテム名

        # アイテムの基本情報
        self.path = create_file_path(name, room, direction, room_change_flag)   # ファイルパス

        self.img = Image(self.screen, self.path, image_cache, scale=shrink_percent, x=x, y=y, anchor=anchor, parent=self.parent)       # 画像

    def relayout(self, screen, parent=None):
        self.screen = screen
        self.parent = parent
        self.img.relayout(screen, parent)

    def draw(self):
        self.img.draw()

    def handle_mouse_hover(self, pos):
        if self.img.collidepoint(pos):
            pygame.draw.rect(self.screen, BLACK, self.img.rect, 1)  # デバッグ用

    def handle_click(self, pos):
        return self.img.collidepoint(pos)
    
