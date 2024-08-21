import random, os, json, glob
import pygame
import pygame.draw
from pygame.locals import *
import tkinter as tk
from tkinter import messagebox

from data import *
from fanction_summary import *
from class_summary import *

# プレイヤーの場所と向きの情報
player = {}
player["room"] = "center"
player["direction"] = "north"

# 部屋画像の縮小パーセンテージ
SIZE = 0.19

# プレイ画面
def MainPlay(screen):
    global CenterRoomFlag
    global EastRoomFlag
    global DiscoveryFlag
    global player

    room_flag = player["room"]
    direction_flag = player["direction"]

    # 部屋の表示
    room = create_room(screen, player)

    # テキストフレームの表示
    Frame(screen)

    # 文章の表示
    Scenario(screen)

    # ナビゲーションバーの表示
    if room_flag == "center":
        right_navi = PageNavigation(screen, RIGHT)
        left_navi = PageNavigation(screen,LEFT)
    else:
        under_nave = PageNavigation(screen,UNDER)

    for event in pygame.event.get():
        # マウスクリック時
        if event.type == MOUSEBUTTONDOWN:
            # 左ボタン
            if event.button == 1:
                if room_flag == "center":
                    if CenterRoomFlag < 5:
                        CenterRoomFlag += 1
                    else:
                        # 部屋の向き移動
                        if right_navi.navi_rect.collidepoint(event.pos):
                            if direction_flag == "north":
                                player["direction"] = "east"
                            elif direction_flag == "east":
                                player["direction"] = "south"
                            elif direction_flag == "south":
                                player["direction"] = "west"
                            else:
                                player["direction"] = "north"
                        elif left_navi.navi_rect.collidepoint(event.pos):
                            if direction_flag == "north":
                                player["direction"] = "west"
                            elif direction_flag == "east":
                                player["direction"] = "north"
                            elif direction_flag == "south":
                                player["direction"] = "east"
                            else:
                                player["direction"] = "south"
                        """
                        # 真ん中のドア
                        elif room.center_door_rect.collidepoint(event.pos):
                            if DirectionFlag == NORTH:
                                RoomFlag = NORTH
                            elif DirectionFlag == WEST:
                                RoomFlag = WEST
                            elif DirectionFlag == EAST:
                                RoomFlag = EAST
                            else:
                                RoomFlag = SOUTH
                        # 左のドア
                        elif room.left_door_rect.collidepoint(event.pos):
                            if DirectionFlag == NORTH:
                                RoomFlag = WEST
                            elif DirectionFlag == WEST:
                                RoomFlag = SOUTH
                            elif DirectionFlag == EAST:
                                RoomFlag = NORTH
                            else:
                                RoomFlag = EAST
                        # 右のドア
                        elif room.right_door_rect.collidepoint(event.pos):
                            if DirectionFlag == NORTH:
                                RoomFlag = EAST
                            elif DirectionFlag == WEST:
                                RoomFlag = NORTH
                            elif DirectionFlag == EAST:
                                RoomFlag = SOUTH
                            else:
                                RoomFlag = WEST
                        """
                else:
                    if under_nave.navi_rect.collidepoint(event.pos):
                        # 真ん中の部屋に戻る
                        player["room"] = "center"

        # 閉じるボタンで終了
        if event.type == QUIT:
            Close()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                Close()

    return "play", "" 

# 部屋を作るよ
class create_room:
    def __init__(self, screen, player):
        # 部屋に置いてあるアイテムリスト
        file_path = PATH + "/room_item.json"
        with open(file_path, "r", encoding="utf-8_sig") as f:
            self.data = json.load(f)
        self.player_data = player
        self.room_flag = self.player_data["room"]
        self.direction_flag = self.player_data["direction"]

        # 各部屋を作ります
        self.now_room = Room(screen,self.room_flag, self.data[self.room_flag], self.direction_flag)

# 部屋の型を作るよ
class Room:
    def __init__(self, screen, room_flag, data, direction_flag=""):
        self.screen = screen
        # 部屋画像を表示するエリア
        self.area_rect = Rect(0,0,820,375)
        # 部屋にあるアイテム一覧
        self.data = data
        
        self.room_flag = room_flag
        self.direction_flag = direction_flag
        # ファイル名一覧
        self.img_paths = create_file_path(self.room_flag, self.data, direction_flag)

        # 部屋画像の表示
        self.room_view(self.img_paths["room"], area=self.area_rect)

        # 部屋にあるアイテムの作成
        self.create_item(self.room_flag, self.data)
        
        # 部屋の説明

    # 画像表示するよ
    def room_view(self, path, size=SIZE, area=None):
        # 画像の読み込みと位置取得
        self.img, rect = CreateImage(path, size)

        # 画像の位置を変更する
        self.rect = SetRect(self.screen, rect, y=30, x_center=True)

        # 表示
        self.screen.blit(self.img, self.rect, area=self.area_rect)

    def create_item(self, room, data):
        self.items = {}
        if type(data) is "directry":
            self.items = data["all"] + data[self.direction_flag]
        else:
            self.items = data

        for item in data:
            self.items[item] = Item(self.screen, item, path=self.img_paths[item])

        if self.room_flag == "center":
            pass

# 実際にアイテムを作っていくよ
class CreateItem:
    def __init__(self):
        pass
    
    def create_item(self):
        self.light = Item("light", "center", "", "center", 54)
        self.soup = Item("soup", "center", "", "center", 254)
        directions = ["north","east","south","west"]
        self.center_door = []
        self.left_door = []
        self.right_door = []
        i = 0
        for direction in directions:
            door_name = direction + "Door"
            self.center_door.append(Item(door_name, "center", direction, "center", 112))
            left_num = i + 1
            if left_num > len(directions):
                left_num = 0
            self.left_door.append(Item(door_name, "center", directions[left_num], 121, 93))
            right_num = i - 1
            self.north_door_right = Item("NorthDoor", "center", directions[right_num], 603, 94)
            i += 1
        self.north_door_center = Item("NorthDoor", "center", "north", "center", 112)
        self.north_door_left = Item("NorthDoor", "center", "east", 121, 93)
        self.north_door_right = Item("NorthDoor", "center", "north", 603, 94)
        self.east_door_center = item("EastDoor", "center", "east", "center", 112)
        

            self.left_door_rect = self.image(paths["Door1"],93,121)
            self.center_door_rect = self.image(paths["Door2"],112,center_flag=True)
            self.right_door_rect = self.image(paths["Door3"],94,603)
            tablex,memox = 0,0
            table_flag,memo_flag = False,False
            if DirectionFlag == NORTH:
                tabley, table_flag = 219, True
                memoy, memox = 267, 341
            elif DirectionFlag == EAST:
                tabley, tablex = 242, 264
                memoy, memo_flag = 283, True
            elif DirectionFlag == SOUTH:
                tabley, table_flag = 253, True
                memoy, memox = 267, 427
            elif DirectionFlag == WEST:
                tabley, tablex = 243, 295
                memoy, memo_flag = 253, True
            self.table_rect = self.image(paths["Table"],tabley,tablex,center_flag=table_flag)
            self.memo_rect = self.image(paths["Memo"],memoy,memox,center_flag=memo_flag)

# アイテムの型を作るよ
class Item:
    def __init__(self, name, room, direction, x, y):
        # 名前
        self.name = name
        # ファイルパス
        self.path = create_file_path(name, room, direction)
        # 座標
        self.x, self.y = x, y
        # シナリオファイルパス
        self.scenario_path_list = create_scenario_path(name, room)
        # クリック時画像パス
        self.big_img_path_list = create_item_path(name)

    """
    def item_view(self, path, x, y, x_flag, y_flag):
        # 座標
        self.rect = Image(self.screen, path, SIZE, x, y, x_center=x_flag, y_center=y_flag)

        # 表示するテキスト
    
        # 起こるイベント
    """

# シナリオのパスを作って返す
def create_scenario_path(item, room):
    path = "." + SCENARIO
    room_path = path + room + "-room"
    item_path = room_path + "_" + item
    search_text = item_path + "*.txt"
    return glob.glob(search_text)

# アイテムファイルのパス名を作って返す
def create_item_path(item):
    path = "." + PICTURE
    search_text = path + item + "*.png"
    return glob.glob(search_text)

# 画像のファイル名を作って返す
def create_file_path(item, room, direction):
    path = PATH + PICTURE
    room_path = path + room + "-room"
    if room == "center":
        room_path += "_" + direction

    if item == "room":
        return room_path + ".jpg"

    if item == "room2":
        if room == "east":
            return "black_room.jpg"
        elif room == "west":
            return "west-room_PicupBook.jpg"

    # アイテムのパスを作っていく
    img_path = room_path + "_" + item + ".png"

    return img_path

"""
class Room:
    def __init__(self, screen):
        self.screen = screen
        # 現在地のファイル名一覧
        self.img_paths = self.file_path()
        # 部屋画像を表示するエリア
        self.area_rect = Rect(0,0,820,375)
        # 部屋画像の表示
        self.room_img, self.room_rect = self.image(self.img_paths["Room"],SHEET_RECT.y,area=self.area_rect,center_flag=True,room_flag=True)
        # 電気が消えているときは暗い画像を表示する
        if LightFlag == False:
            black_img, black_rect = self.image(self.img_paths["LightOff"],SHEET_RECT.y,area=self.area_rect,center_flag=True,room_flag=True)
        # 部屋にあるアイテムの配置
        self.item(self.img_paths)
    
        return paths

    # 画像表示するよ
    def image(self, path, y, x=0, size=0.19, area=None, center_flag=False, room_flag=False, line_flag=False):
        # 画像の読み込み＆アルファ化(透明化)
        img = pygame.image.load(path).convert_alpha()
        # 画像の縮小
        img = pygame.transform.rotozoom(img, 0, size)

        # 画像の位置取得
        rect = img.get_rect()
        # 画像の位置を変更する
        if center_flag:
            # 画面中央に置きたい場合
            rect.centerx = self.screen.get_width() / 2
        else:
            rect.centerx += x
        rect.centery += y

        # 部屋のimgの場合はメインsurfaceに、部屋のアイテムは部屋のsurfaceに
        if room_flag:
            self.screen.blit(img, rect, area=area)
            # 枠を描写する場合
            if line_flag:
                if line_flag == True:
                    pygame.draw.rect(self.screen, BLACK, rect, 2)
            return img, rect
        else:
            self.room_img.blit(img, rect, area=area)
            return rect

    # アイテム表示するよ
    def item(self, paths):
        if RoomFlag == CENTER:
            self.left_door_rect = self.image(paths["Door1"],93,121)
            self.center_door_rect = self.image(paths["Door2"],112,center_flag=True)
            self.right_door_rect = self.image(paths["Door3"],94,603)
            self.light_rect = self.image(paths["Light"],54,center_flag=True)
            tablex,memox = 0,0
            table_flag,memo_flag = False,False
            if DirectionFlag == NORTH:
                tabley, table_flag = 219, True
                memoy, memox = 267, 341
            elif DirectionFlag == EAST:
                tabley, tablex = 242, 264
                memoy, memo_flag = 283, True
            elif DirectionFlag == SOUTH:
                tabley, table_flag = 253, True
                memoy, memox = 267, 427
            elif DirectionFlag == WEST:
                tabley, tablex = 243, 295
                memoy, memo_flag = 253, True
            self.table_rect = self.image(paths["Table"],tabley,tablex,center_flag=table_flag)
            self.memo_rect = self.image(paths["Memo"],memoy,memox,center_flag=memo_flag)
            self.soup_rect = self.image(paths["Soup"],254,center_flag=True)
        elif RoomFlag == NORTH:
            self.under_storage_rect = self.image(paths["UnderSinkStorage"],250,325)
            self.cooktop_rect = self.image(paths["Cooktop"],226,225)
            self.sink_rect = self.image(paths["Sink"],216,468)
            self.top_storage_rect = self.image(paths["TopSinkStorage"],100,325)
            self.pot_rect = self.image(paths["Pot"],203,290)
            self.storage_rect = self.image(paths["Storage"],225,560)
            self.cupboard_rect = self.image(paths["CupBoard"],30,36)
            self.fridge_rect = self.image(paths["Fridge"],39,628)
        elif RoomFlag == EAST:
            if DiscoveryFlag:
                self.corpse_rect = self.image(paths["Corpse"],218,437)
                self.memo_rect = self.image(paths["Memo"],259,277)
        elif RoomFlag == WEST:
            self.bookshelf_rect = self.image(paths["BookShelf"],30,36)
            self.chandle_rect = self.image(paths["Candle"],223,350)
            if BookFlag:
                self.book_rect = self.image(paths["Book"],246,298)
        else:
            self.statue_rect = self.image(paths["StoneStatue"],69,287)
            self.slate1_rect = self.image(paths["Slate1"],156,213)
            self.slate2_rect = self.image(paths["Slate2"],156,479)

    # アイテムクリックのイベント決めるよ
    def event(self, rect):
        if rect == self.soup_rect:
            img_path = PATH + PICTURE + "soup_" + SoupFlag + ".png"
            y = self.area_rect.y + (self.area_rect / 2)
            img, img_rect = self.image(img_path, y, size=0.5, center_flag=True, line_flag=True)
"""

# シナリオの型を作るよ
#class Scenario:
#    def __init__(self) -> None:
#        pass    

# シナリオ表示用
def Scenario(screen):
    text = ""
    room_name = ""
    room_number = str(RoomFlag)
    item_name = ""
    flag_name = ""
    if RoomFlag == CENTER:
        room_name = "_Center_room_"
        if CenterRoomFlag < 5:
            flag_name = str(CenterRoomFlag)
        else:
            pass

    file_name = ScenarioPath + room_number + room_name + item_name + flag_name + ".txt"
    if os.path.isfile(file_name):
        with open(file_name,"r",encoding="utf-8_sig") as f:
            text = f.read()
    TextDraw(screen, text)


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

