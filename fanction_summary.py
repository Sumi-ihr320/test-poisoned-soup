import sys, re, glob
from tkinter import messagebox

import pygame
from pygame.locals import *

from data import *

# messagebox や sinpledialog を最前面に表示し続ける
class TopmostManager:
    def __init__(self, root):
        self.root = root

    def __enter__(self):
        self.root.attributes("-topmost", True)

    def __exit__(self, exc_type, exc_value, trackback):
        self.root.attributes("-topmost", False)

# 終了処理をまとめるよ
def Close(root):
    with TopmostManager(root):
        if messagebox.askokcancel("確認","本当に終了しますか？"):
            pygame.quit()
            sys.exit()
        else:
            pass

# tkinterを画面中央に配置するためのサイズ作成
def create_size_tkinter(root):
    root.update_idletasks()     # ウィンドウサイズを更新
    sw, sh = root.winfo_screenmmwidth(), root.winfo_screenmmheight()    # 画面の解像度を取得
    w, h = root.winfo_width(), root.winfo_height()                      # ウィンドウサイズを取得
    x = (sw - w) // 2
    y = (sh - h) // 2
    return f"+{x}+{y}"

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

# 入力時のvalidate
def validate_input(value, value_type, num=None):
    if value_type == int:
        if validate_int(value):
            return validate_num(value, num)
    else:
        return validate_num(value, num)
    return False

# 数字のみ
def validate_int(value):
    return value.isdigit()

# 文字数制限
def validate_num(value, num):
    if num:
        if len(value) <= num:
            return True
        return False
    else:
        return True

# シナリオのパスを作って返す
def create_scenario_path(item, room):
    path = f".{SCENARIO}"
    room_path = f"{path}{room}-room"
    item_path = room_path
    if item != "":
        item_path = f"{room_path}_{item}"
        search_text = f"{item_path}*.txt"
    else:
        search_text = f"{item_path}?.txt"
    return glob.glob(search_text)

# アイテムファイルのパス名を作って返す
def create_item_path(item):
    path = f".{PICTURE}"
    search_text = f"{path}{item}*.png"
    return glob.glob(search_text)

# 画像のファイル名を作って返す
def create_file_path(item, room, direction):
    path = f"{PATH}{PICTURE}"
    room_path = f"{path}{room}-room"
    if room == "center":
        if direction != "":
            room_path += f"_{direction}"

    if item == "room":
        return f"{room_path}.jpg"

    if item == "room2":
        if room == "east":
            return f"{path}black-room.jpg"
        elif room == "west":
            return f"{room_path}_PicupBook.jpg"
        else:
            return ""

    # アイテムのパスを作っていく
    img_path = f"{room_path}_{item}.png"

    return img_path
