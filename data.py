import os
from pygame.locals import *

DISPLAY_SIZE = (800, 600)
TITLE_TEXT = "毒入りスープ"

# 色
BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (73,74,65)
RED = (183,40,46)

# キャラクターシート
SHEET_COLOR = (189,183,107)
SHEET_RECT = Rect(30,30,740,375)

# フレーム
FRAME_RECT = Rect(30,420,580,150)
DICE_FRAME_RECT = Rect(620,420,150,150)

FILL_RECT = Rect(20,20,800,410)

# パスの指定
PATH = os.path.dirname(__file__)
SCENARIO = "/Scenario/"
PICTURE ="/Picture/"
MUSIC = "/Music/"
SAVE = "/Save/"

STATUS_JSON_PATH = os.path.join(PATH,"CharaStatus.json")
PROF_JSON_PATH = os.path.join(PATH,"Profession.json")
SKILL_JSOM_PATH = os.path.join(PATH,"SkillList.json")
HOBBY_JSON_PATH = os.path.join(PATH,"Hobby.json")

# フォント
FONT_PATH = os.path.join(PATH,"HGRKK.TTC")
TITLE_FONT_PATH = os.path.join(PATH,"genkai-mincho.ttf")
FONT_SIZ = 22   # 基本サイズ
SMALL_SIZ = 18  # 小さいサイズ
BIG_SIZ = 25    # 大きいサイズ
TITLE_SIZ = 60      # タイトル用
CONTENTS_SIZ = 30    # メニュー用

# シーン切り替えフラグ
TITLE,LOAD,SETTING,OPENING,CHARASE,PLAY,ENDING,ENDCREDITS = (0,1,2,3,4,5,6,7)

# ナビゲーション表示用
RIGHT,LEFT,UNDER = (0,1,2)

# 方角
CENTER,NORTH,EAST,WEST,SOUTH = (0,1,2,3,4)