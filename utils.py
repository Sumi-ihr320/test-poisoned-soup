import sys, re, json
import ctypes, platform, subprocess
from tkinter import messagebox

import pygame
from pygame.locals import *

from constans import *

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
        if messagebox.askokcancel("確認","本当に終了しますか？\n※セーブせずに終了するとデータは消えてしまいます"):
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
    frame_rect = get_frame_rect(screen)
    pygame.draw.rect(screen, WHITE, frame_rect, 3)
    # メニューフレーム
    #pygame.draw.rect(screen, WHITE, MENU_FRAME_RECT,3)

# テキストフレームのrectを割り出す
def get_frame_rect(screen):
    window_size = screen.get_size()
    frame_w, frame_h = get_new_size(window_size, (FRAME_SIZE))
    frame_x = (window_size[0] // 2) - (frame_w // 2)
    frame_y = window_size[1] - (frame_h + 30)

    return Rect(frame_x, frame_y, frame_w, frame_h)

# 部屋画像のrectを算出する
def get_room_rect(screen):
    window_size = screen.get_size()
    room_size = get_new_size(window_size, SHEET_SIZE, True)
    surface = pygame.Surface(room_size)

    window_rect = screen.get_rect()
    frame_rect = get_frame_rect(screen)
    surface_rect = surface.get_rect(centerx=window_rect.centerx, bottom=frame_rect.top - 20)
    return surface_rect

# 現在のウィンドウサイズから新しいサイズを割り出す
def get_new_size(window_size, item_size, not_change_ratio=False):
    w_percent, h_percent = RATIO[window_size]
    if not_change_ratio:
        new_size = (int(item_size[0] * h_percent), int(item_size[1] * h_percent))
    else:
        new_size = (int(item_size[0] * w_percent), int(item_size[1] * h_percent))
    return new_size

# フォントサイズを計算して設定する
def setting_font(font_path, font_size, window_size):
    h_percent = RATIO[window_size][1]
    new_size = int(font_size * h_percent)
    return pygame.font.Font(font_path, new_size)

# テキストフレームに文字を表示するよ
def TextDraw(screen, text):
    window_size = screen.get_size()
    # フォントの設定
    font = setting_font(FONT_PATH, FONT_SIZ, window_size)
    # フレームの位置を得る
    frame_rect = get_frame_rect(screen)

    texts = []
    x, y = frame_rect.x + 10, frame_rect.y + 10
    texts = text.splitlines()
    for txt in texts:
        RendarText(screen, txt, font, (x, y))
        y += 25

# タグを使って色を付けられるようにする。
def RendarText(screen, text, font, pos, default_color=WHITE):
    # <color=color_name>～<color/> を解析して部分的に色を変える
    x, y = pos
    color = default_color
    pattern = re.compile(r"(.*?)<color=([\w]+)>(.*?)<color/>(.*)")

    while text:
        match = pattern.match(text)
        if match:
            befor, new_color, colored_text, after = match.groups()

            # タグの前の部分
            if befor:
                rendered = font.render(befor, True, color)
                screen.blit(rendered, (x, y))
                x += rendered.get_width()

            # タグの中の部分
            if new_color in COLOR_MAP:
                new_color = COLOR_MAP[new_color]    # 色を変更
            rendered = font.render(colored_text, True, new_color)
            screen.blit(rendered, (x, y))
            x += rendered.get_width()

            # タグの後の部分 次のループで描画
            text = after

        else:
            # タグが無い場合そのまま描画
            rendered = font.render(text, True, color)
            screen.blit(rendered, (x, y))
            break

# テキストファイルのロード
def load_text(file_path):
    if os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8_sig") as f:
            return f.read()
    else:
        print(f"{file_path} が見つかりません")

def create_filepath(folder, file):
    return os.path.join(f"{PATH}{folder}", file)

# jsonファイルのロード
def load_json(forder, file):
    file_path = os.path.join(f"{PATH}{forder}", file)
    if os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8_sig") as f:
            return json.load(f)
    else:
        print(f"{file_path} が見つかりません")

# 基本のサウンドファイルが入っているかのチェック
def sound_check(sound_manager):
    sounds_to_load = {
        "選択":"Choice.mp3",
        "クリック":"Click.mp3",
        "カーソル移動":"Move.mp3"
    }

    # sound_manager.soundsが空の時はすべてロード
    if not sound_manager.sounds:
        for name, file in sounds_to_load.items():
            sound_manager.load_sound(name, file)

    else:
        # まだロードされていないサウンドのみロード
        for name, file in sounds_to_load.items():
            if name not in sound_manager.sounds:
                sound_manager.load_sound(name, file)

# "〇D〇" のテキストから何個のダイスか、何面ダイスか、+〇、-〇が付いてるかを抽出する
def dice_confirmation(text):
    # テキストに+か-が入っているか確認
    plus_item = re.search(r"\+|\-", text)
    cut_index = plus_item.start() if plus_item else 0
    pieces = text[0]
    dice = text[2:] if cut_index == 0 else text[2:cut_index]
    return int(pieces), int(dice), plus_item

# 対抗ロールの成功値計算(return パーセンテージ)
def opposition_percent(active, passive):
    return 50 + ((active - passive) * 5)

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
def validate_input(action, value, value_type, num=None):
    # 削除の時は確認しない
    if action == '\\0':
        return True

    # タイプが数字の時は数字かどうかのチェックと文字数チェックを行う
    if value_type == "<class 'int'>":
        return validate_int(value) and validate_num(value, num)
    
    # 数字以外（文字列）の時は文字数のチェックのみ行う
    else:
        return validate_num(value, num)

# 数字のみ
def validate_int(value):
    return value.isdigit()

# 文字数制限
def validate_num(value, num):
    if num is None or num == "None":
        return True
    else:
        return len(value) <= int(num)

def ime_on(event):
    pf = platform.system()
    if pf == "Windows":
        user32 = ctypes.WinDLL(name="user32")
        imm32 = ctypes.WinDLL(name="imm32")
        h_wnd = user32.GetForegroundWindow()
        h_imc = imm32.ImmGetContext(h_wnd)
        imm32.ImmSetOpenStatus(h_imc, True)
        imm32.ImmReleaseContext(h_wnd, h_imc)

    elif pf == "Darwin":
        applescript = r'tell application "System Events" to keystroke (key code {104})'
        subprocess.run(["osascript", "-e", applescript])

    elif pf == "Linux":
        try:
            subprocess.run(["ibus", "engine", "mozc-jp"])  # ibusの場合
            subprocess.run(["fcitx-remote", "-o"])  # fcitxの場合
            subprocess.run(["echo", "1", ">", "$UIM_FEP_SETMODE"])  # uimの場合(合っているのか不明)
        except FileNotFoundError:
            pass        

def ime_off(event):
    pf = platform.system()
    if pf == "Windows":
        user32 = ctypes.WinDLL(name="user32")
        imm32 = ctypes.WinDLL(name="imm32")
        h_wnd = user32.GetForegroundWindow()
        h_imc = imm32.ImmGetContext(h_wnd)
        imm32.ImmSetOpenStatus(h_imc, False)
        imm32.ImmReleaseContext(h_wnd, h_imc)

    elif pf == "Darwin":
        applescript = r'tell application "System Events" to keystroke (key code {102})'
        subprocess.run(["osascript", "-e", applescript])

    elif pf == "Linux":
        try:
            subprocess.run(["ibus", "engine", "xkb:jp::jpn"])  # ibusの場合
            subprocess.run(["fcitx-remote", "-c"])  # fcitxの場合
            subprocess.run(["echo", "0", ">", "$UIM_FEP_SETMODE"])  # uimの場合(合っているのか不明)
        except FileNotFoundError:
            pass

# 画像のファイル名を作って返す
def create_file_path(item, room, direction, flag=None):
    if flag is None:
        flag = {}
    
    room_path = f"{room}-room"

    # 中央の部屋には方向情報を追加
    if room == "center" and direction:
        room_path += f"_{direction}"

        # 電球が外されていたら_darkを加える
        if flag.get("light_remove"):
            room_path = f"{room_path}_dark"

    # 西の部屋では
    elif room == "west":
        # キャンドルが消えているか別の部屋に置いてある場合暗くなる
        if flag.get("candle_goes_out") != 0 or flag.get("candle_out"):
            room_path = f"{room_path}_dark"
    
    if item == "room":
        # 器を手に入れている場合
        if room == "center" and flag.get("soup_bowl_get"):
            room_path = f"{room_path}_NoSoup"

        # 東の部屋が見えていない場合
        elif room == "east" and not flag.get("east_room_visible"):
            room_path = "black-room"

        elif room == "west" and (flag.get("book_found") or flag.get("candle_get")):
            # 本を見つけてる場合
            if flag.get("book_found"):
                room_path = f"{room_path}_PickupBook"
            # キャンドルを手に入れている場合
            if flag.get("candle_get"):
                room_path = f"{room_path}_NoCandle"
        
        # 少女を生贄に捧げてる場合
        elif room == "south" and flag.get("hunting_horrors_offered_sacrifice"):
            room_path = f"{room_path}_Blood"

        return f"{room_path}.jpg"
    
    # テーブルの場合
    elif item == "Table":
        # スープが乗っていないテーブル
        if flag.get("soup_bowl_get"):
            item = f"{item}_no_bowl"
    
    # 石像の場合
    elif item == "StoneStatue":
        # 血が点いている石像
        if flag.get("hunting_horrors_offered_sacrifice"):
            item = f"{item}_Blood"

    # アイテムのパスを作っていく
    img_path = f"{room_path}_{item}.png"

    return img_path
