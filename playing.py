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
player["flag"] = True
player["center_room_flag"] = 0

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
    create_frame(screen)

    # 文章の表示
    #Scenario(screen)

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
                        
                        # 真ん中のドア
                        elif room.now_room.room_item.center_door.rect.collidepoint(event.pos):
                            player["direction"] = ""
                            if direction_flag == "north":
                                player["room"] = "north"
                            elif direction_flag == "east":
                                player["room"] = "east"
                            elif direction_flag == "south":
                                player["room"] = "south"
                            else:
                                player["room"] = "west"
                        # 左のドア
                        elif room.now_room.room_item.left_door.rect.collidepoint(event.pos):
                            player["direction"] = ""
                            if direction_flag == "north":
                                player["room"] = "west"
                            elif direction_flag == "east":
                                player["room"] = "north"
                            elif direction_flag == "south":
                                player["room"] = "east"
                            else:
                                player["room"] = "south"
                        # 右のドア
                        elif room.now_room.room_item.right_door.rect.collidepoint(event.pos):
                            player["direction"] = ""
                            if direction_flag == "north":
                                player["room"] = "east"
                            elif direction_flag == "east":
                                player["room"] = "south"
                            elif direction_flag == "south":
                                player["room"] = "west"
                            else:
                                player["room"] = "north"
                        
                else:
                    if under_nave.navi_rect.collidepoint(event.pos):
                        # 真ん中の部屋に戻る
                        player["room"] = "center"
                        if room_flag == "north":
                            player["direction"] = "south"
                        elif room_flag == "east":
                            player["direction"] = "west"
                        elif room_flag == "south":
                            player["direction"] = "north"
                        else:
                            player["direction"] = "east"

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
        self.player_data = player
        self.room_flag = self.player_data["room"]
        self.direction_flag = self.player_data["direction"]
        self.flag = self.player_data["flag"]

        # 各部屋を作ります
        self.now_room = Room(screen, self.room_flag, direction=self.direction_flag, flag=self.flag)

# 部屋の型を作るよ
class Room:
    def __init__(self, screen, room, direction="", flag=False):
        self.screen = screen

        # 部屋画像を表示するエリア
        self.area_rect = Rect(0,0,820,375)
        
        # ファイル名一覧
        self.room_path = create_file_path("room", room, direction)
        self.room2_path = create_file_path("room2", room, direction)
        self.scenario_list = create_scenario_path("", room)

        # 部屋画像の表示
        path = self.room_path
        if self.room2_path != "":
            if flag:
                path = self.room2_path
        self.room_view(path, area=self.area_rect)

        # 部屋にあるアイテムの作成
        self.create_item(self.img, room, direction)

        # 部屋のシナリオが存在する場合
        if self.scenario_list != []:
            Scenario(self.screen, self.scenario_list)
        
        # 部屋の説明

    # 画像表示するよ
    def room_view(self, path, size=SIZE, area=None):
        # 画像の読み込みと位置取得
        self.img, rect = CreateImage(path, size)

        # 画像の位置を変更する
        self.rect = SetRect(self.screen, rect, y=30, x_center=True)

        # area内に表示
        self.screen.blit(self.img, self.rect, area=self.area_rect)

    def create_item(self, screen, room, direction):
        self.room_item = CreateItem(screen, room, direction)

# 実際にアイテムを作っていくよ
class CreateItem:
    def __init__(self, screen, room, direction):

        self.create_item(screen, room, direction)
    
    def create_item(self, screen, room, direction):
        if room == "center":
            self.light = Item(screen, "Light", room, "", "center", 54)
            self.soup = Item(screen, "Soup", room, "", "center", 254)
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
            center_door_name = direction + "Door"
            index = directions.index(direction)
            left_index = index - 1
            left_direct = directions[left_index]
            left_door_name = left_direct + "Door"
            right_index = index + 1
            if right_index > len(directions) - 1:
                right_index = 0
            right_direct = directions[right_index]
            rigth_door_name = right_direct + "Door"
            
            self.center_door = Item(screen, center_door_name, room, direction, "center", 112)
            self.left_door = Item(screen, left_door_name, room, direction, 121, 93)
            self.right_door = Item(screen, rigth_door_name, room, direction, 603, 94)
            self.table = Item(screen, "Table", "center", direction, position[direction]["tablex"], position[direction]["tabley"])
            self.center_memo = Item(screen, "Memo", "center", direction, position[direction]["memox"], position[direction]["memoy"])
        elif room == "north":
            self.under_storage = Item(screen, "UnderSinkStorage", "north", "", 325, 250)
            self.cooktop = Item(screen, "Cooktop", "north", "", 225, 226)
            self.sink = Item(screen, "Sink", "north", "", 468, 216)
            self.top_storage = Item(screen, "TopSinkStorage", "north", "", 325, 100)
            self.pot = Item(screen, "Pot", "north", "", 290, 203)
            self.storage = Item(screen, "Storage", "north", "", 560, 225)
            self.cupboard = Item(screen, "CupBoard", "north", "", 36, 30)
            self.fridge = Item(screen, "Fridge", "north", "", 628, 39)
        elif room == "east":
            self.corpse = Item(screen, "Corpse", "east", "", 437, 218)
            self.east_memo = Item(screen, "Memo", "east", "", 277, 259)
        elif room == "south":
            self.statue = Item(screen, "StoneStatue", "south", "",287, 69)
            self.slate1 = Item(screen, "Slate1", "south", "", 213, 156)
            self.slate2 = Item(screen, "Slate2", "south", "", 479, 156)
        else:
            self.bookshelf = Item(screen, "BookShelf", "west", "", 36, 30)
            self.chandle = Item(screen, "Candle", "west", "", 350, 223)
            self.book = Item(screen, "Book", "west", "", 298, 246)

# アイテムの型を作るよ
class Item:
    def __init__(self, screen, name, room, direction, x, y):
        self.screen = screen
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

        self.item_view(self.screen, self.path, self.x, self.y)
    
    def item_view(self, screen, path, x, y):
        # 座標
        x_flag, y_flag = False, False
        if x == "center":
            x == 0
            x_flag = True
        if y == "center":
            y = 0
            y_flag = True
        self.rect = Image(screen, path, SIZE, x, y, x_center=x_flag, y_center=y_flag)

        # 表示するテキスト
    
        # 起こるイベント
    
# シナリオのパスを作って返す
def create_scenario_path(item, room):
    path = "." + SCENARIO
    room_path = path + room + "-room"
    item_path = room_path
    if item != "":
        item_path = room_path + "_" + item
        search_text = item_path + "*.txt"
    else:
        search_text = item_path + "?.txt"
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
        if direction != "":
            room_path += "_" + direction

    if item == "room":
        return room_path + ".jpg"

    if item == "room2":
        if room == "east":
            return path + "black-room.jpg"
        elif room == "west":
            return room_path + "_PicupBook.jpg"
        else:
            return ""

    # アイテムのパスを作っていく
    img_path = room_path + "_" + item + ".png"

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

