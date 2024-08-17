import random, os, json
import pygame
import pygame.draw
from pygame.locals import *
import tkinter as tk
from tkinter import messagebox

from data import *
from fanction_summary import *
from class_summary import *

from title import Title
from load import Load
from save import Save
from opening import Opening
from character_sheet import CharacterSheet

# プレイヤーの場所と向きの情報
player = {}
player["room"] = "center"
player["direction"] = "north"

# プレイ画面
def MainPlay(screen):
    global CenterRoomFlag
    global EastRoomFlag
    global DiscoveryFlag
    global AlphaFlag

    #if PlaySceneFlag == 0:
    #    pygame.time.wait(500)

    # 部屋の表示
    room = create_room(screen, player)

    # 文章の表示
    Scenario()

    # ナビゲーションバーの表示
    if RoomFlag == CENTER:
        right_navi = PageNavigation(screen, RIGHT)
        left_navi = PageNavigation(screen,LEFT)
    else:
        under_nave = PageNavigation(screen,UNDER)

    for event in pygame.event.get():
        # マウスクリック時
        if event.type == MOUSEBUTTONDOWN:
            # 左ボタン
            if event.button == 1:
                if RoomFlag == CENTER:
                    if CenterRoomFlag < 5:
                        CenterRoomFlag += 1
                    else:
                        # 部屋の向き移動
                        if right_navi.navi_rect.collidepoint(event.pos):
                            if DirectionFlag == NORTH:
                                DirectionFlag = EAST
                            elif DirectionFlag == EAST:
                                DirectionFlag = SOUTH
                            elif DirectionFlag == SOUTH:
                                DirectionFlag = WEST
                            else:
                                DirectionFlag = NORTH
                        elif left_navi.navi_rect.collidepoint(event.pos):
                            if DirectionFlag == NORTH:
                                DirectionFlag = WEST
                            elif DirectionFlag == EAST:
                                DirectionFlag = NORTH
                            elif DirectionFlag == SOUTH:
                                DirectionFlag = EAST
                            else:
                                DirectionFlag = SOUTH
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
                else:
                    if under_nave.navi_rect.collidepoint(event.pos):
                        # 真ん中の部屋に戻る
                        RoomFlag = CENTER

        # 閉じるボタンで終了
        if event.type == QUIT:
            Close()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                Close()


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
        self.room_view(self.img_paths["room"])
        
        # 部屋の説明

    # 画像表示するよ
    def room_view(self, path, x=0, y=0, size=0.19, area=None):
 
        # 画像の読み込み＆アルファ化(透明化)
        self.img = pygame.image.load(path).convert_alpha()
        # 画像の縮小
        self.img = pygame.transform.rotozoom(self.img, 0, size)

        # 画像の位置取得
        self.rect = self.img.get_rect()

        # 画像の位置を変更する
        self.rect.centerx = self.screen.get_width() / 2  # 画面中央に置く
        self.rect.centery += y

        # 表示
        self.screen.blit(self.img, self.rect, area=self.area_rect)

    def create_item(self):
        if type(self.data) is "directry":
            for item in self.data["all"]:
                self.img_paths[item]
            for item in self.data[self.direction_flag]:
                self.img_paths[item]
        else:
            # アイテムの表示
            for item in self.data:
                self.img_paths[item]

        if self.room_flag == "center":              
            self.soup = Item(self.screen,"soup", "center", 254, self.img_paths["soup"])



# アイテムの型を作るよ
class Item:
    def __init__(self, screen, name, x, y, path):
        self.screen = screen
        # 名前
        self.name = name
        # 座標
        self.x = x
        self.y = y
        # 画像ファイルパス
        self.path = path
        # 画像

        # 表示するテキスト
        # 起こるイベント

class create_room:
    def __init__(self, screen, player):
        # 部屋に置いてあるアイテムリスト
        file_path = PATH + "room_item.json"
        with open(file_path, "r", encoding="utf-8_sig") as f:
            self.data = json.load(f)
        self.player_data = player
        self.room_flag = self.player_data["room"]
        self.direction_flag = self.player_data["direction"]

        # 各部屋を作ります
        self.center_room_north = Room(screen,"center", self.data["center"],"north")
        self.center_room_south = Room(screen,"center", self.data["center"],"south")
        self.center_room_east = Room(screen, "center", self.data["center"], "east")
        self.center_room_west = Room(screen, "center", self.data["center"], "west")
        self.north_room = Room(screen, "north", self.data["north"])
        self.east_room = Room(screen, "east", self.data["east"])
        self.south_room = Room(screen, "south", self.data["south"])
        self.west_room = Room(screen, "west", self.data["west"])
        

# 画像のファイル名を作成する
def create_file_path(room, item_list, direction_flag):
    paths = {}
    path = PATH + PICTURE
    room_path = path + room + "-room"
    if room == "center":
        room_path += "_" + direction_flag
    room_img_path = room_path + ".jpg"
    paths["room"] = room_img_path

    if room == "east":
        black_room_img_path = "black_room.jpg"
        paths["room2"] = black_room_img_path
    if room == "west":
        pickupbook_room_img_path = "west-room_PicupBook.jpg"
        paths["room2"] = pickupbook_room_img_path
    else:
        paths["room2"] = ""

    if room == "center":
        item_l = item_list["all"] + item_list[direction_flag]
    else:
        item_l = item_list

    # アイテムリストのパスを作っていく
    for item in item_l:
        img_path = room_path + "_" + item + ".png"
        paths[item] = img_path

    return paths

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
    
    # ファイル名取得するよ
    def file_path(self):
        paths = {}
        path = PATH + PICTURE
        if RoomFlag == CENTER:
            room_path = path + "central-room_"
            paths["LightOff"] = room_path + "LightOff.png"
            paths["Light"] = room_path + "Light.png"
            paths["Soup"] = room_path + "Soup.png"
            if DirectionFlag == NORTH:
                room_direct_path = room_path + "north"
                paths["Door1"] = room_direct_path + "_WestDoor.png"
                paths["Door2"] = room_direct_path + "_NorthDoor.png"
                paths["Door3"] = room_direct_path + "_EastDoor.png"
            elif DirectionFlag == EAST:
                room_direct_path = room_path + "east"
                paths["Door1"] = room_direct_path + "_NorthDoor.png"
                paths["Door2"] = room_direct_path + "_EastDoor.png"
                paths["Door3"] = room_direct_path + "_SouthDoor.png"
            elif DirectionFlag == WEST:
                room_direct_path = room_path + "west"
                paths["Door1"] = room_direct_path + "_SouthDoor.png"
                paths["Door2"] = room_direct_path + "_WestDoor.png"
                paths["Door3"] = room_direct_path + "_NorthDoor.png"
            elif DirectionFlag == SOUTH:
                room_direct_path = room_path + "south"
                paths["Door1"] = room_direct_path + "_EastDoor.png"
                paths["Door2"] = room_direct_path + "_SouthDoor.png"
                paths["Door3"] = room_direct_path + "_WestDoor.png"
            paths["Room"] = room_direct_path + ".jpg"
            paths["Memo"] = room_direct_path + "_Memo.png"
            paths["Table"] = room_direct_path + "_Table.png"
        else:
            if RoomFlag == NORTH:
                room_path = path + "north-room"
                paths["Cooktop"] = room_path + "_Cooktop.png"
                paths["Pot"] = room_path + "_Pot.png"
                paths["CupBoard"] = room_path + "_CupBoard.png"
                paths["Fridge"] = room_path + "_Fridge.png"
                paths["Sink"] = room_path + "_Sink.png"
                paths["Storage"] = room_path + "_Storage.png"
                paths["TopSinkStorage"] = room_path + "_TopSinkStorage.png"
                paths["UnderSinkStorage"] = room_path + "_UnderSinkStorage.png"
                
            elif RoomFlag == EAST:
                if DiscoveryFlag:
                    room_path = path + "east-room"
                    paths["Corpse"] = room_path + "_Corpse.png"
                    paths["Memo"] = room_path + "_Memo.png"
                else:
                    room_path = path + "black-room"
            elif RoomFlag == SOUTH:
                room_path = path + "south-room"
                paths["StoneStatue"] = room_path + "_StoneStatue.png"
                paths["Slate1"] = room_path + "_Slate_01.png"
                paths["Slate2"] = room_path + "_Slate_02.png"
            elif RoomFlag == WEST:
                room_path = path + "west-room"
                paths["BookShelf"] = room_path + "_BookShelf.png"
                paths["Candle"] = room_path + "_Candle.png"
                if BookFlag:
                    paths["Book"] = room_path + "_Book.png"
                    room_path += "_PicupBook"
            paths["Room"] = room_path + ".jpg"


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

