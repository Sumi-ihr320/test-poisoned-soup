import os
from enum import Enum
from pygame.locals import Rect


DISPLAY_SIZE = (800, 600)
TITLE_TEXT = "毒入りスープ"

# 色
BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (73,74,65)
RED = (183,40,46)
BLUE = (71,131,132)

# キャラクターシート
SHEET_COLOR = (189,183,107)
SHEET_RECT = Rect(30,30,740,375)

# Rect
FRAME_RECT = Rect(30,420,580,150)
MENU_FRAME_RECT = Rect(620,420,150,150)

FILL_RECT = Rect(20,20,800,410)
ROOM_AREA = Rect(0,0,820,375)

# 画面中央の座標
WINDOW_CENTER_X = DISPLAY_SIZE[0] // 2
WINDOW_CENTER_Y = DISPLAY_SIZE[1] // 2
 
# パスの指定
PATH = os.path.dirname(__file__)
SCENARIO = "/Scenario/"
PICTURE ="/Picture/"
MUSIC = "/Music/"
SAVE_FOLDER = "/Save/"
JSON_FOLDER = "/Json/"

CHARA_DATA_PATH = "CharaStatus.json"
STATUS_DATA_PATH = "Status.json"
PROF_DATA_PATH = "Profession.json"
SKILL_DATA_PATH = "SkillList.json"
HOBBY_DATA_PATH = "Hobby.json"

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

# ナビゲーション表示用
RIGHT,LEFT,UNDER = (0,1,2)

# 方角
# CENTER,NORTH,EAST,WEST,SOUTH = (0,1,2,3,4)

# 部屋の名前
ROOM_NAME = {"center":"中央の部屋",
            "north":"北の部屋",
            "east":"東の部屋",
            "west":"西の部屋",
            "south":"南の部屋"}

EVENT_NAME = {"入る":"open",
              "目星":"objective",
              "医学":"medicine",
              "アイデア":"idea"}

# play中の状態
class PlayState(Enum):
    NONE = 0
    SAVE = 1
    LOAD = 2
    SETTING = 3
