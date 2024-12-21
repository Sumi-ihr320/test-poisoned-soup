import pygame
from pygame.locals import *

from constans import *
from utils import *
from ui_elements import Image

# 部屋の型を作るよ
class Room:
    # 部屋画像の縮小パーセンテージ
    SIZE = 0.19
    def __init__(self, screen, room, direction="", room2_flag=False):
        self.screen = screen
        self.room2_flag = room2_flag    # 二つ目の部屋画像を表示するかのフラグ

        # 部屋画像を表示するエリア
        self.area_rect = ROOM_AREA
        
        # ファイル名一覧
        self.room_path = create_file_path("room", room, direction)
        self.room2_path = create_file_path("room2", room, direction)
        #self.scenario_list = create_scenario_path(room=room)

        # 部屋画像の作成
        self.img = Image(self.screen, self.room_path, size=self.SIZE, x="center", y=30, area=self.area_rect)
        self.img2 = Image(self.screen, self.room2_path, size=self.SIZE, x="center", y=30, area=self.area_rect) if self.room2_path else None

        # 部屋にあるアイテムの作成
        self.items = []
        self.items_draw_list = []
        self.items_select_list= []
        self.create_room_item(self.img.img, room, direction)

    # 画像表示するよ
    def draw(self, selected_item, flags):
        # フラグが立っていればroom_img2を表示する
        if self.room2_flag and self.img2:
            self.img2.draw()
        else:
            self.img.draw()

        if self.items_draw_list:
            for item in self.items_draw_list:
                if item == selected_item:
                    img_number = 0
                    if item == "Soup":
                        if flags.get_flag("items", "soup_drink") == True:
                            img_number = 1
                        elif flags.get_flag("items", "soup_in_poison") == True:
                            img_number = 2
                    item.draw(is_selected=True, img_number=img_number)
                else:
                    item.draw()

    # 部屋のアイテムを作成する
    def create_room_item(self, surface, room, direction):
        if room == "center":
            self.light = RoomItem(surface, "Light", room, "", "center", 24)
            self.soup = RoomItem(surface, "Soup", room, "", "center", 224)
            directions = ["north","east","south","west"]
            position = {"north":{"tablex":"center","tabley":189,
                                 "memox":306,"memoy":237},
                        "east":{"tablex":229,"tabley":212,
                                "memox":"center","memoy":253},
                        "south":{"tablex":"center","tabley":223,
                                 "memox":392,"memoy":237},
                        "west":{"tablex":260,"tabley":213,
                                "memox":"center","memoy":223}
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
            self.center_door = RoomItem(surface, center_door_name, room, direction, "center", 82)
            self.left_door = RoomItem(surface, left_door_name, room, direction, 86, 63)
            self.right_door = RoomItem(surface, rigth_door_name, room, direction, 568, 64)
            self.table = RoomItem(surface, "Table", "center", direction, position[direction]["tablex"], position[direction]["tabley"])
            self.center_memo = RoomItem(surface, "centerMemo", "center", direction, position[direction]["memox"], position[direction]["memoy"])
            self.items_draw_list = [self.center_door, self.left_door, self.right_door, self.table, self.light, self.soup, self.center_memo]
            self.items_select_list = [self.light, self.soup, self.center_memo, self.table, self.center_door, self.left_door, self.right_door]
        elif room == "north":
            self.under_storage = RoomItem(surface, "UnderSinkStorage", "north", "", 325, 250)
            self.cooktop = RoomItem(surface, "Cooktop", "north", "", 225, 226)
            self.sink = RoomItem(surface, "Sink", "north", "", 468, 216)
            self.top_storage = RoomItem(surface, "TopSinkStorage", "north", "", 325, 100)
            self.pot = RoomItem(surface, "Pot", "north", "", 290, 203)
            self.storage = RoomItem(surface, "Storage", "north", "", 560, 225)
            self.cupboard = RoomItem(surface, "CupBoard", "north", "", 36, 30)
            self.fridge = RoomItem(surface, "Fridge", "north", "", 628, 39)
            self.items_draw_list = [self.under_storage, self.cooktop, self.sink, self.top_storage, self.pot, self.storage, self.cupboard, self.fridge]
            self.items_select_list = [self.pot, self.sink, self.cooktop, self.under_storage, self.top_storage, self.storage, self.cupboard, self.fridge]
        elif room == "east":
            self.corpse = RoomItem(surface, "Corpse", "east", "", 437, 218)
            self.east_memo = RoomItem(surface, "eastMemo", "east", "", 277, 259)
            self.items_draw_list = [self.corpse, self.east_memo]
            self.items_select_list = [self.east_memo, self.corpse]
        elif room == "south":
            self.statue = RoomItem(surface, "StoneStatue", "south", "",287, 69)
            self.slate1 = RoomItem(surface, "Slate1", "south", "", 213, 156)
            self.slate2 = RoomItem(surface, "Slate2", "south", "", 479, 156)
            self.items_draw_list = [self.statue, self.slate1, self.slate2]
            self.items_select_list = [self.statue, self.slate1, self.slate2]
        else:
            self.bookshelf = RoomItem(surface, "BookShelf", "west", "", 36, 30)
            self.chandle = RoomItem(surface, "Candle", "west", "", 350, 223)
            self.book = RoomItem(surface, "Book", "west", "", 298, 246)
            self.items_draw_list = [self.bookshelf, self.chandle, self.book]
            self.items_select_list = [self.book, self.chandle, self.bookshelf]

# アイテムの型を作るよ
class RoomItem:
    # アイテム画像の縮小パーセンテージ
    SIZE = 0.19
    def __init__(self, screen, name, room, direction, x, y):
        self.screen = screen
        self.name = name    # アイテム名

        # アイテムの基本情報
        self.path = create_file_path(name, room, direction)             # ファイルパス
        self.img = Image(self.screen, self.path, self.SIZE, x, y)       # 画像

        # クリック時画像パス
        self.big_img_path_list = create_item_path(name)
        self.big_imgs = []
        self.create_images()

        # イベントトリガーやコマンドに必要なデータを保持
        #self.scenario_key = name.lower()    # json内での対応するキー
        self.command_list = None

    # クリック時の画像リストを作る
    def create_images(self):
        size = 0.6 if "Memo" in self.name else 0.35
        if self.big_img_path_list:
            for path in self.big_img_path_list:
                self.big_imgs.append(Image(self.screen, path, size, x="center", centery=200, line_flag=True, bg_flag=True))
        elif self.name == "Light":
            self.big_imgs.append(Image(self.screen, self.path, 0.5, x="center", centery=200, line_flag=True, bg_flag=True))

    def draw(self, is_selected=None, img_number=0):
        self.img.draw()
        if is_selected:
            if self.big_imgs:
                self.big_imgs[img_number].draw()
        pygame.draw.rect(self.screen, BLACK, self.img.rect, 1)  # デバッグ用

    # コマンドメニューの表示位置を取得
    def get_position(self):
        max_x, max_y = 620, 220     # これ以上端に配置すると見えなくなる
        # コマンド表示の指標となる画像位置。クリック時画像があればそこを起点とする。なければ元の画像。
        image_rect = self.big_imgs[0].rect if self.big_imgs else self.img.rect

        # 画像の右側にコマンドボタンを表示する。最大値以上になる場合は左側に配置する。
        x = image_rect.right + 30 if (image_rect.right + 30) <= max_x else image_rect.x - 130
        y = image_rect.y if image_rect.y <= max_y else image_rect.y - 50

        return (x, y)

    def handle_click(self, pos):
        return self.img.rect.collidepoint(pos)