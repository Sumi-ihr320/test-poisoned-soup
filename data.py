import os
from pygame.locals import *

DISPLAY_SIZE = (800, 600)
BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (73,74,65)
RED = (183,40,46)

SHEET_COLOR = (189,183,107)
# SHEET_COLOR = (237,228,205)
SHEET_RECT = Rect(30,30,740,375)

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

FONT_PATH = os.path.join(PATH,"HGRKK.TTC")
TITLE_FONT_PATH = os.path.join(PATH,"genkai-mincho.ttf")
FONT_SIZ = 22
SMALL_SIZ = 18
BIG_SIZ = 25
TITLE_SIZ = 60
OPENING_SIZ = 30
TITLE_TEXT = "毒入りスープ"

# シーン切り替えフラグ
TITLE,SETTING,OPENING,CHARASE,PLAY,ENDING,ENDCREDITS = (0,1,2,3,4,5,6)
