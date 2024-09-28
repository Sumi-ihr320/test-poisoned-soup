import os, json
#import pygame
#import pygame.draw
from pygame.locals import *
import datetime as dt

from data import *
from fanction_summary import *
from class_summary import *

# データセーブ
def Save(screen, flag, list):

    # 今日の日付と時間を取得
    now = dt.datetime.now()
    str_now = now.strftime("%Y-%m-%d_%H-%M-%S")

    # セーブフォルダが無ければ作る
    dir_name = f"{PATH}{SAVE_FOLDER}"
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    # 10個程度の保存領域からどのデータにセーブするか選択できるようにしたい
    #window = DataWindow(screen, "save", save_files)

    # キャラクター名、日時でセーブデータを作る
    file_name = dir_name + CharaStatus["name"] + " " + str_now + ".json"
    data = {}
    data["CharaStatus"] = CharaStatus
    data["flag"] = {"CenterRoomFlag":CenterRoomFlag,
                    "MemoFlag":MemoFlag,
                    "EastRoomFlag":EastRoomFlag,
                    "RoomFlag":RoomFlag,
                    "DirectionFlag":DirectionFlag,
                    "DiscoveryFlag":DiscoveryFlag,
                    "KeyOpenFlag":KeyOpenFlag,
                    "BookFlag":BookFlag,
                    "PoisonFlag":PoisonFlag,
                    "SoupFlag":SoupFlag,
                    "SoupIdeaFlag":SoupIdeaFlag,
                    "GirlFlag":GirlFlag}
    
    with open(file_name,"w",encoding="utf-8_sig") as f:
        json.dump(data,f,indent=2,ensure_ascii=False)

    # キャラシ画面からセーブした際は本編に進む
    if flag == "charasheet":
        return "play"
