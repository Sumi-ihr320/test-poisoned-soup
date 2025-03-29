import os
from enum import Enum
from pygame.locals import Rect
from character_item import *


#DISPLAY_SIZE = (800, 600)
TITLE_TEXT = "毒入りスープ"
SIZE_MAP = {
    "800x600":  (800, 600),
    "1024x768": (1024, 768),
    "1280x720": (1280, 720),
    "1280x960": (1280, 960),
    "1920x1080":(1920, 1080),
    "フルスクリーン":()
}
RATIO = {
    (800,600):(1,1),
    (1024,768):(1.28, 1.28),
    (1280,720):(1.6, 1.2),
    (1280,960):(1.6, 1.6),
    (1920,1080):(2.4, 1.8)
}

# 色
BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (73,74,65)
RED = (183,40,46)
BLUE = (71,131,132)
COLOR_MAP = {"black": (0, 0, 0),
             "white": (255, 255, 255),
             "gray":  (73, 74, 65),
             "red":   (255, 0, 0),
             "blue":  (0, 0, 255),
             "yellow":(255, 217, 0),
             "green": (0, 128, 0)}

# 設定
SETTING_COLOR = (0,82,67)

# キャラクターシート
SHEET_COLOR = (189,183,107)
SHEET_SIZE = (740, 375)
SHEET_RECT = Rect(30,30,740,375)

# Rect
FRAME_W, FRAME_H = 740, 150
#FRAME_SIZE = (740, 150)
#FRAME_RECT = Rect(30,420,580,150)
FRAME_RECT = Rect(30,420,730,150)
MENU_FRAME_RECT = Rect(620,420,150,150)


FILL_RECT = Rect(20,20,800,410)
ROOM_AREA = Rect(0,0,820,375)

# 画面中央の座標
#WINDOW_CENTER_X = DISPLAY_SIZE[0] // 2
#WINDOW_CENTER_Y = DISPLAY_SIZE[1] // 2
 
# パスの指定
PATH = os.path.dirname(__file__)
SCENARIO = "/Scenario/"
PICTURE ="/Picture/"
SOUND = "/Sound/"
SAVE_FOLDER = "/Save/"
JSON_FOLDER = "/Json/"

CHARA_DATA_PATH = "CharaStatus.json"
STATUS_DATA_PATH = "Status.json"
PROF_DATA_PATH = "Profession.json"
SKILL_DATA_PATH = "SkillList.json"
HOBBY_DATA_PATH = "Hobby.json"

SCENARIO_FILES = [
    "Opening.json",
    "CenterRoom.json",
    "Door.json",
    "Light.json",
    "Soup.json",
    "CenterMemo.json",
    "EastRoom.json",
    "SouthRoom.json",
    "WestRoom.json",
    "Candle.json",
    "Other.json",
    "Ending.json"
]

# フォント
FONT_PATH = os.path.join(PATH,"HGRKK.TTC")
TITLE_FONT_PATH = os.path.join(PATH,"genkai-mincho.ttf")
FONT_SIZ = 22   # 基本サイズ
SMALL_SIZ = 18  # 小さいサイズ
BIG_SIZ = 25    # 大きいサイズ
TITLE_SIZ = 60      # タイトル用
CONTENTS_SIZ = 30    # メニュー用

# シーン切り替えフラグ
TITLE,SAVE,LOAD,SETTING,OPENING,CHARASE,PLAY,ENDING,ENDCREDITS = (0,1,2,3,4,5,6,7,8)

# 部屋の名前
ROOM_NAME = {"center":"中央の部屋",
            "north":"北の部屋",
            "east":"東の部屋",
            "west":"西の部屋",
            "south":"南の部屋"}

# ナビゲーション表示用のポジションフラグ
class Position(Enum):
    RIGHT = 0
    LEFT = 1
    UNDER = 2

# 状態フラグ
class State(Enum):
    NONE = 0
    SAVE = 1
    LOAD = 2
    SETTING = 3
    CLOSE = 4


ITEM_LIST = {
    "white_robe": Armor("白いローブ"),
    "bloody_robe": Armor("血まみれの白いローブ"),
    "gun": Weapon("22口径ショート・オートマチック", img_name="Pistol.png", skill="拳銃", damage_dice="1d6",
                  attack_range="10m", one_round=3, bullets=6, durability=6),
    "light_bulb": CharacterItem("電球", img_name="Light_bulb.png"),
    "bottle": CharacterItem("瓶", img_name="Bottle.png"),
    "book": CharacterItem("黒い本", img_name="Book.png"),
    "candle1": CharacterItem("ろうそく", img_name="Candle_0.png"),
    "candle2": CharacterItem("ろうそく", img_name="Candle_1.png"),
    "candle_goes_out1": CharacterItem("消えたろうそく", img_name="Candle_0_goes_out.png"),
    "candle_goes_out2": CharacterItem("消えたろうそく", img_name="Candle_1_goes_out.png"),
    "kitchen_knife": Weapon("包丁", img_name="", skill="こぶし", damage_dice="1D4+DB",attack_range="近接", one_round=1,durability=8),
    "knife": Weapon("ナイフ", img_name="Knife.png", skill="こぶし", damage_dice="1D3+DB",attack_range="近接",durability=5),
    "fork": Weapon("フォーク", img_name="Fork.png", skill="こぶし", damage_dice="1D3",attack_range="近接",durability=4),
    "spoon": Weapon("スプーン", img_name="Spoon.png", skill="こぶし", damage_dice="1D2",attack_range="近接",durability=3)
}