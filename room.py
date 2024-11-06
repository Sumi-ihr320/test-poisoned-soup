import pygame
from pygame.locals import *

from constans import *
from utils import *
from ui_elements import *


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
        self.scenario_list = create_scenario_path(room=room)

        # 部屋画像の作成
        self.img = Image(self.screen, self.room_path, size=self.SIZE, x="center", y=30, area=self.area_rect)
        self.img2 = Image(self.screen, self.room2_path, size=self.SIZE, x="center", y=30, area=self.area_rect) if self.room2_path else None

        # 部屋にあるアイテムの作成
        self.items = []
        self.items_draw_list = []
        self.items_select_list= []
        self.create_item(self.img.img, room, direction)

    # 画像表示するよ
    def draw(self):
        # フラグが立っていればroom_img2を表示する
        if self.room2_flag and self.img2:
            self.img2.draw()
        else:
            self.img.draw()

        if self.items_draw_list:
            for item in self.items_draw_list:
                item.draw()

    # 部屋のアイテムを作成する
    def create_item(self, surface, room, direction):
        if room == "center":
            self.light = Item(surface, "Light", room, "", "center", 24, ["目星", "外す", "壊す"])
            self.soup = Item(surface, "Soup", room, "", "center", 224, ["目星", "医学", "触る", "飲む", "捨てる"])
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
            self.center_door = Item(surface, center_door_name, room, direction, "center", 82, ["目星", "聞き耳", "叩く", "開ける"])
            self.left_door = Item(surface, left_door_name, room, direction, 86, 63, ["目星", "聞き耳", "叩く", "開ける"])
            self.right_door = Item(surface, rigth_door_name, room, direction, 568, 64, ["目星", "聞き耳", "叩く", "開ける"])
            self.table = Item(surface, "Table", "center", direction, position[direction]["tablex"], position[direction]["tabley"], ["目星"])
            self.center_memo = Item(surface, "centerMemo", "center", direction, position[direction]["memox"], position[direction]["memoy"], ["目星"])
            self.items_draw_list = [self.center_door, self.left_door, self.right_door, self.table, self.light, self.soup, self.center_memo]
            self.items_select_list = [self.light, self.soup, self.center_memo, self.table, self.center_door, self.left_door, self.right_door]
        elif room == "north":
            self.under_storage = Item(surface, "UnderSinkStorage", "north", "", 325, 250)
            self.cooktop = Item(surface, "Cooktop", "north", "", 225, 226)
            self.sink = Item(surface, "Sink", "north", "", 468, 216)
            self.top_storage = Item(surface, "TopSinkStorage", "north", "", 325, 100)
            self.pot = Item(surface, "Pot", "north", "", 290, 203)
            self.storage = Item(surface, "Storage", "north", "", 560, 225)
            self.cupboard = Item(surface, "CupBoard", "north", "", 36, 30)
            self.fridge = Item(surface, "Fridge", "north", "", 628, 39)
            self.items_draw_list = [self.under_storage, self.cooktop, self.sink, self.top_storage, self.pot, self.storage, self.cupboard, self.fridge]
            self.items_select_list = [self.pot, self.sink, self.cooktop, self.under_storage, self.top_storage, self.storage, self.cupboard, self.fridge]
        elif room == "east":
            self.corpse = Item(surface, "Corpse", "east", "", 437, 218)
            self.east_memo = Item(surface, "eastMemo", "east", "", 277, 259)
            self.items_draw_list = [self.corpse, self.east_memo]
            self.items_select_list = [self.east_memo, self.corpse]
        elif room == "south":
            self.statue = Item(surface, "StoneStatue", "south", "",287, 69)
            self.slate1 = Item(surface, "Slate1", "south", "", 213, 156)
            self.slate2 = Item(surface, "Slate2", "south", "", 479, 156)
            self.items_draw_list = [self.statue, self.slate1, self.slate2]
            self.items_select_list = [self.statue, self.slate1, self.slate2]
        else:
            self.bookshelf = Item(surface, "BookShelf", "west", "", 36, 30)
            self.chandle = Item(surface, "Candle", "west", "", 350, 223)
            self.book = Item(surface, "Book", "west", "", 298, 246)
            self.items_draw_list = [self.bookshelf, self.chandle, self.book]
            self.items_select_list = [self.book, self.chandle, self.bookshelf]

# アイテムの型を作るよ
class Item:
    # アイテム画像の縮小パーセンテージ
    SIZE = 0.19
    def __init__(self, screen, name, room, direction, x, y, command_list=None):
        self.screen = screen
        self.name = name    # アイテム名

        # ファイルパス
        self.path = create_file_path(name, room, direction)

        # 画像
        self.img = Image(self.screen, self.path, self.SIZE, x, y)

        # シナリオファイルパス
        self.scenario_path_list = create_scenario_path(item=name)

        # クリック時画像パス
        self.big_img_path_list = create_item_path(name)
        self.big_imgs = []
        self.create_images()

        # メニューに表示するコマンド
        self.command_list = command_list
        self.menu_buttons = []
        self.create_menu()

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
            if self.menu_buttons:
                for button in self.menu_buttons:
                    button.draw()
        pygame.draw.rect(self.screen, BLACK, self.img.rect, 1)  # デバッグ用

    def event(self):
        pass

    # コマンドメニューボタンを作る
    def create_menu(self):
        font = pygame.font.Font(FONT_PATH, SMALL_SIZ)
        w, h = 100, 30
        max_x, max_y = 620, 220     # これ以上端に配置すると見えなくなる
        # コマンド表示の指標となる画像位置。クリック時画像があればそこを起点とする。なければ元の画像。
        image_rect = self.big_imgs[0].rect if self.big_imgs else self.img.rect

        # 画像の右側にコマンドボタンを表示する。最大値以上になる場合は左側に配置する。
        x = image_rect.right + 30 if (image_rect.right + 30) <= max_x else image_rect.x - 130
        y = image_rect.y if image_rect.y <= max_y else image_rect.y - 50

        if self.command_list:
            for command in self.command_list:
                if command in EVENT_NAME:
                    event = EVENT_NAME[command]
                self.menu_buttons.append(Button(self.screen, font, command, (x,y,w,h), out_color=BLACK))
                y += h

    # コマンドボタンのイベント作成
    def open(self):
        pass

    def handle_click(self, pos):
        if self.img.rect.collidepoint(pos):
            return True                
        return False

        # 表示するテキスト
        return self.scenario_path_list
    
        # 起こるイベント
        pass

    