import os, json
import pygame
from pygame.locals import *

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

# フレーム
FRAME_RECT = Rect(30,420,580,150)
DICE_FRAME_RECT = Rect(620,420,150,150)

FILL_RECT = Rect(20,20,800,410)

# パスの指定
PATH = os.path.dirname(__file__)
SCENARIO = "/Scenario/"
PICTURE ="/Picture/"
MUSIC = "/Music/"
SAVE_FOLDER = "/Save/"
JSON_FOLDER = "/Json/"

STATUS_DATA_PATH = "CharaStatus.json"
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
CENTER,NORTH,EAST,WEST,SOUTH = (0,1,2,3,4)


# 基本データ --------------------------------------------

# キャラクターのステータスデータ
with open(f"{PATH}{JSON_FOLDER}{STATUS_DATA_PATH}", "r", encoding="utf-8_sig")as f:
    STATUS = json.load(f)
    
CharaStatus = STATUS["Hero"]    # 主人公
GirlStatus = STATUS["Girl"]     # 少女


# ロード画面（セーブ画面） -------------------------------------

# セーブファイルリスト
SavePath = PATH + SAVE_FOLDER
SaveFiles = os.listdir(SavePath)

# シナリオファイルリスト
ScenarioPath = PATH + SCENARIO
ScenarioFiles = os.listdir(ScenarioPath)

# 選択されたデータ
SelectSaveData = ""

# オープニング画面 --------------------------------------------
OpeningFlag = 0     # オープニングの進行フラグ

# キャラクターシート画面 ---------------------------------------
CharaPage = True    # ページ変更用フラグ

PullDownFlag = False    # プルダウン用フラグ
PullDownItem = ""       # プルダウンアイテム記憶用

# 職業リスト
with open(f"{PATH}{JSON_FOLDER}{PROF_DATA_PATH}","r",encoding="utf-8_sig") as f:
    ProfessionList = json.load(f)

# 技能リスト
with open(f"{PATH}{JSON_FOLDER}{SKILL_DATA_PATH}","r",encoding="utf-8_sig") as f:
    SkillList = json.load(f)

# 趣味リスト
with open(f"{PATH}{JSON_FOLDER}{HOBBY_DATA_PATH}","r",encoding="utf-8_sig") as f:
    HobbyList = json.load(f)

# 本編 -------------------------------------------------------
CenterRoomFlag = 0      # 中央の部屋のシーンフラグ
MemoFlag = 0            # メモの進行フラグ
EastRoomFlag = 0        # 東の部屋のシーンフラグ
RoomFlag = CENTER       # どの部屋にいるかフラグ
DirectionFlag = NORTH   # どの方角を向いてるかフラグ
DiscoveryFlag = False   # 東の部屋奥が見えるかフラグ
KeyOpenFlag = False     # 東の部屋カギが開いてるかフラグ
BookFlag = False        # 本を見つけてるかフラグ
BookHaveFlag = False    # 本を持ってるかフラグ
CandleHaveFlag = False  # キャンドルを持ってるかフラグ
LightFlag = True        # 電気が点いてるかフラグ
PoisonFlag = False      # 毒を入手してるかフラグ
SoupFlag = 0            # スープの状態フラグ 0=通常 1=毒入り 2=空
SoupIdeaFlag = False    # スープの知識があるかフラグ
GirlFlag = False        # 少女がいるかフラグ
# -----------------------------------------------------------
