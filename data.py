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
TITLE,SAVE,LOAD,SETTING,OPENING,CHARASE,PLAY,ENDING,ENDCREDITS = (0,1,2,3,4,5,6,7,8)

# ナビゲーション表示用
RIGHT,LEFT,UNDER = (0,1,2)

# 方角
CENTER,NORTH,EAST,WEST,SOUTH = (0,1,2,3,4)


# 基本データ --------------------------------------------

# pygame初期化
pygame.init()
# 画面サイズ
screen = pygame.display.set_mode(DISPLAY_SIZE)
# キーリピート設定
pygame.key.set_repeat(100, 100)
# タイトルバーキャプション
pygame.display.set_caption(TITLE_TEXT)

clock = pygame.time.Clock()

# フォントの設定
font = pygame.font.Font(FONT_PATH, FONT_SIZ)
small_font = pygame.font.Font(FONT_PATH, SMALL_SIZ)
big_font = pygame.font.Font(FONT_PATH, BIG_SIZ)
# タイトル用のフォント
title_font = pygame.font.Font(TITLE_FONT_PATH,TITLE_SIZ)
# メニュー用フォント
contents_font = pygame.font.Font(FONT_PATH,CONTENTS_SIZ)

# キャラクターのステータスデータ
with open(STATUS_JSON_PATH,"r",encoding="utf-8_sig")as f:
    STATUS = json.load(f)
    
CharaStatus = STATUS["Hero"]    # 主人公
GirlStatus = STATUS["Girl"]     # 少女

maxAlpha = 255      # alpha値 不透明
minAlpha = 0        # alpha値 透明
AlphaFlag = 0   # ブラックインアウトフラグ  0=無し 1=In 2=Out


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
with open(PROF_JSON_PATH,"r",encoding="utf-8_sig") as f:
    ProfessionList = json.load(f)

# 技能リスト
with open(SKILL_JSOM_PATH,"r",encoding="utf-8_sig") as f:
    SkillList = json.load(f)

# 趣味リスト
with open(HOBBY_JSON_PATH,"r",encoding="utf-8_sig") as f:
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
