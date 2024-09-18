import sys, re, random
import pygame
from pygame.locals import *
from tkinter import simpledialog
from tkinter import messagebox

from data import *


# 終了処理をまとめるよ
def Close():
    if messagebox.askokcancel("確認","本当に終了しますか？"):
        pygame.quit()
        sys.exit()
    else:
        pass

# フレームの作成
def create_frame(screen):
    # テキストフレーム
    pygame.draw.rect(screen, WHITE, FRAME_RECT,3)
    # ダイスフレーム
    pygame.draw.rect(screen, WHITE, DICE_FRAME_RECT,3)

# テキストフレームに文字を表示するよ
def TextDraw(screen, text):
    # フォントの設定
    font = pygame.font.Font(FONT_PATH, FONT_SIZ)

    texts = []
    y = 435
    texts = text.splitlines()
    for txt in texts:
        surface = font.render(txt,True,WHITE)
        rect = surface.get_rect(left=45,top=y)
        screen.blit(surface,rect)
        y += 25

# テキストファイルのロード
def load_texts(file_path):
    with open(file_path, "r", encoding="utf-8_sig") as f:
        return f.readlines()
    
# jsonファイルのロード
def load_json(file):
    file_path = os.path.join(f"{PATH}{JSON_FOLDER}", file)
    with open(file_path, "r", encoding="utf-8_sig") as f:
        return json.load(f)

# 選択した職業から主人公のステータスにデータを入れるよ
def ProfDataIn():
    global CharaStatus

    # 入力されている技能をリセット
    CharaStatus["skill"] = {}
    CharaStatus["Avo"] = CharaStatus["DEX"] * 2
    # 職業から設定されている技能一覧を取得
    prof = CharaStatus["Profession"]
    skills = ProfessionList[prof]["skill"]
    # 加算できる技能ポイントを算出する
    max = CharaStatus["EDU"] * 20
    if max > 0:
        i = max
        for skill in skills:
            # 各技能に割り振られているパーセンテージを出す
            percent = skills[skill]
            # 技能ポイントをパーセンテージ分算出
            bonus = int(max * (percent / 100))
            # 基本技能ポイント
            if skill == "回避":
                data = CharaStatus["Avo"]
            else:
                data = SkillList[skill]
            # 計算する
            result, surplus = Calculation(data, bonus, 90)
            # 主人公のステータスにポイントを入力
            if skill == "回避":
                CharaStatus["Avo"] = result
            else:
                CharaStatus["skill"][skill] = result
            # 技能ポイント - 使用した技能ポイント + 余りの技能ポイント
            i = i - bonus + surplus

            # 技能ポイントが足りなかった場合
            if i < 0:
                print("技能ポイントが足りません")
                break

        # 全ての技能ポイント割り振り後にポイントが余った場合
        if i > 0:
            # ポイントが0になるまで繰り返す
            while i > 0:
                lists = {}
                # スキルリストから90以下のスキルをリスト化する
                for skill in CharaStatus["skill"]:
                    point = CharaStatus["skill"][skill]
                    if point < 90:
                        lists[skill] = point
                if len(lists) > 0:
                    # リストの数よりポイントが多い場合
                    if len(lists) < i:
                        # リストの数でポイントを割る
                        quotient = int(i / len(lists))
                        
                        # 計算していく
                        for skill in lists:
                            point = lists[skill]
                            result, surplus = Calculation(point, quotient, 90)
                            CharaStatus["skill"][skill] = result
                            i = i - quotient + surplus
                    else:
                        select = random.choice(list(lists))
                        CharaStatus["skill"][select]  += i
                        i -= i
                   
# 選択した趣味から主人公のステータスにデータを入れるよ
def HobyDataIn():
    global CharaStatus

    hobby = PullDownItem
    my_skills = CharaStatus["skill"]
    skills = HobbyList[hobby]
    max = CharaStatus["INT"] * 10
    percent = [70,30]
    if max > 0:
        point = max
        for i in range(len(skills)):
            skill = skills[i]
            # 基本技能ポイント
            if skill in my_skills:
                data = my_skills[skill]
            else:
                data = SkillList[skill]
            # 技能ポイントをパーセンテージ分算出
            bonus = int(max * (percent[i] / 100))
            # 計算する
            result, surplus = Calculation(data,bonus,90)
            # スキルに値を入れる
            CharaStatus["skill"][skill] = result
            # 残りのポイントを算出
            point = point - bonus + surplus

        if point > 0:
            for i in range(len(skills)):
                skill = skills[i]
                data = my_skills[skill]
                result,surplus = Calculation(data,point,90)
                CharaStatus["skill"][skills[i]] = result
                point = surplus

# "〇D〇" のテキストから何個のダイスか、何面ダイスか、+〇、-〇が付いてるかを抽出する
def dice_confirmation(text):
    # テキストに+か-が入っているか確認
    plus_item = re.search(r"\+|\-", text)
    cut_index = plus_item.start() if plus_item else 0
    pieces = text[0]
    dice = text[2:] if cut_index == 0 else text[2:cut_index]
    return int(pieces), int(dice), plus_item

# 答えと余りを算出する計算式を関数にしてみた
def Calculation(a, b, max=None):
    surplus = 0
    result = a + b
    if max is not None:
        if result > max:
            surplus = result - max
            result = max
    return result, surplus
