import os, sys, re, json
import ctypes, platform, subprocess
from typing import Any, Dict, List, Tuple
from tkinter import messagebox

import pygame
from pygame.locals import *
from pygame.font import Font

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

# 部屋画像のrectを算出する
def get_room_rect(screen, frame_rect):
    screen_size = screen.get_size()
    room_size = get_new_size(screen_size, SHEET_SIZE, True)
    surface = pygame.Surface(room_size)

    screen_rect = screen.get_rect()
    surface_rect = surface.get_rect(centerx=screen_rect.centerx, bottom=frame_rect.top - 20)
    return surface_rect

def get_scales(screen_size):
    """
    screen_size を元に BASE_SIZE との比率を割り出す
    scale_x, scale_y, aspect_scale を返す
    """
    base_w, base_h = BASE_SIZE
    cur_w, cur_h = screen_size
    scale_x = cur_w / base_w
    scale_y = cur_h / base_h
    aspect_scale = min(scale_x, scale_y)
    return scale_x, scale_y, aspect_scale

# 現在のサイズから新しいサイズを割り出す
def get_new_size(screen_size:Tuple[int, int], item_size:Tuple[int, int], not_change_ratio:bool=False) -> Tuple[int, int]:
    """
    現在のサイズから比率に応じた新しいサイズを割り出す。
    not_change_ratio: 現在のアスペクト比を保ったままにするか
    """
    scale_x, scale_y, aspect_scale = get_scales(screen_size)
    if not_change_ratio:
        new_size = (int(item_size[0] * aspect_scale), int(item_size[1] * aspect_scale))
    else:
        new_size = (int(item_size[0] * scale_x), int(item_size[1] * scale_y))
    return new_size

# font_pathとfont_sizeから現在のscreen_sizeに合わせてサイズを設定したフォントを返す
def setting_font(font_path: str, font_size: int, screen_size: Tuple[int, int]) -> Font:
    _, scale_y, _ = get_scales(screen_size)
    new_size = int(font_size * scale_y)
    return pygame.font.Font(font_path, new_size)

# タグで色を解析してsegmentを返す
def parse_color_tags(text: str, default_color: Tuple[int, int, int]=WHITE) -> List[Tuple[str, Tuple[int, int, int]]]:
    """
    text 内の <color="red"></color> などのタグを解析して
    segment: [(text, color), (...)] の形式にして返す
    default_color: タグ指定部分以外の色
    """
    pattern = re.compile(r"(.*?)<color=([\w]+)>(.*?)<color/>(.*)")
    segments = []

    while text:
        match = pattern.match(text)
        if match:
            befor, new_color, colored_text, after = match.groups()

            # タグの前の部分
            if befor:
                segments.append((befor, default_color))

            # タグの中の部分
            new_color = COLOR_MAP.get(new_color, default_color)    # 色を変更
            
            segments.append((colored_text, new_color))

            # タグの後の部分 次のループで描画
            text = after

        else:
            # タグが無い場合そのまま描画
            segments.append((text, default_color))
            break
    return segments

# parentを確認してオフセットを取得する
def parent_check(parent):
    if parent is not None and hasattr(parent, "get_global_offset"):
        ox, oy = parent.get_global_offset()
        return ox, oy
    return 0, 0

# posをオフセットを確認してローカル座標に変換する
def pos_to_local(pos, parent):
    ox, oy = parent_check(parent)
    return (pos[0] - ox, pos[1] - oy)

# posをオフセットを確認してグローバル座標に変換する
def pos_to_global(pos, parent):
    ox, oy = parent_check(parent)
    return (pos[0] + ox, pos[1] + oy)

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
def load_json(file_name: str, forder: str=None):
    file_path = os.path.join(f"{PATH}{forder}", file_name) if forder else file_name
    if os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8_sig") as f:
            return json.load(f)
    else:
        print(f"{file_path} が見つかりません")

def load_and_normalize_json(file_name: str, full_path: bool=True):
    """
    ファイルを読み、トップレベルが map (id -> steps) でも
    list of {scenario_id, steps} でも受け取り、
    { scenario_id: steps_list } を返す
    """
    if full_path:
        data = load_json(file_name)
    else:
        data = load_json(file_name, SCENARIO)
    
    scenarios: Dict[str, List[Any]] = {}

    # 既存のトップレベルマップ形式の場合
    if isinstance(data, dict) and all(isinstance(v, list) for v in data.values()):
        scenarios = dict(data)

    # [{'scenario_id':name, 'steps':[...]}] の形式の場合
    elif isinstance(data, list):
        for item in data:
            sid = item.get("scenario_id", item.get("name", ""))
            steps = item.get("steps", [])
            if sid:
                scenarios[sid] = steps
    else:
        scenarios["unnamed"] = data if isinstance(data, list) else [data]

    return scenarios

# jsonファイルの書き込み
def save_json(file_name: str, data: Dict, forder: str=None):
    file_path = os.path.join(f"{PATH}{forder}", file_name) if forder else file_name
    with open(file_path, "w", encoding="utf-8_sig") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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

def dice_confirmation(text):
    """
    "1D6" などのテキストを分析して pieces, dice_faces, modifier の形にして返す
    pieces: 何個のダイスか
    dice_faces: 何面ダイスか
    modifier: +や-で付属が付いているか
    """
    # テキストに+か-が入っているか確認
    modifier = re.search(r"\+|\-", text)
    cut_index = modifier.start() if modifier else 0
    pieces = text[0]
    dice_faces = text[2:] if cut_index == 0 else text[2:cut_index]
    return int(pieces), int(dice_faces), modifier

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
