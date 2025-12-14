import os, json

from constans import PATH, SAVE_FOLDER
from utils import *

class SettingManager:
    FILE_PATH = f"{PATH}{SAVE_FOLDER}setting.json"
    def __init__(self, root):
        self.root = root
        self.settings = {
            "fullscreen":False,
            "resolution":[800, 600],
            "str_resolution":"800x600",
            "music_volume":1,
            "se_volume":1,
            "input_mode":InputMode.MOUSE
        }
        self.load_settings()

    # 設定ファイルを読み込む
    def load_settings(self):
        if os.path.exists(self.FILE_PATH):
            try:
                with open(self.FILE_PATH, "r") as f:
                    self.settings = json.load(f)
            except FileNotFoundError:
                with TopmostManager(self.root):
                    messagebox.showerror("ロードエラー", "設定ファイルが見つかりません")
            except json.JSONDecodeError(self.root):
                with TopmostManager(self.root):
                    messagebox.showerror("ロードエラー", "設定データのファイル形式が正しくありません")
            except Exception as e:
                print(f"ロードエラー: {e}")
                with TopmostManager(self.root):
                    messagebox.showerror("ロードエラー", f"設定データのロードに失敗しました: {str(e)}")

    # 設定をjsonファイルに保存する
    def save_settings(self):
        try:
            with open(self.FILE_PATH, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"セーブエラー: {e}")
            with TopmostManager(self.root):
                messagebox.showerror("セーブエラー", "設定データのセーブに失敗しました")

    # 設定値を取得
    def get(self, key):
        return self.settings.get(key)
    
    # 設定値を変更し、即時保存
    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

