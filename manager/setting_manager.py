import os, json
from tkinter import messagebox

from constans import PATH, SAVE_FOLDER, InputMode
from utils import TopmostManager

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

    # エラーメッセージを表示する
    def show_error(self, flag: str, message: str):
        with TopmostManager(self.root):
            messagebox.showerror(title=f"{flag}エラー", message=message)

    # InputModeを文字列に変換
    def enum_to_str(self, input_mode: InputMode) -> str:
        return input_mode.value
    
    # 文字列をInputModeに変換
    def str_to_enum(self, input_mode_str: str) -> InputMode:
        return InputMode(input_mode_str)    

    # 設定ファイルを読み込む
    def load_settings(self):
        if os.path.exists(self.FILE_PATH):
            try:
                with open(self.FILE_PATH, "r") as f:
                    self.settings = json.load(f)
                    self.settings["input_mode"] = self.str_to_enum(self.settings["input_mode"])
            except FileNotFoundError:
                self.show_error("ロード", "設定ファイルが見つかりません")
            except json.JSONDecodeError:
                self.show_error("ロード", "設定データのファイル形式が正しくありません")
            except Exception as e:
                print(f"ロードエラー: {e}")
                self.show_error("ロード", f"設定データのロードに失敗しました: {str(e)}")
 
    # 設定をjsonファイルに保存する
    def save_settings(self):
        settings = self.settings.copy()
        settings["input_mode"] = self.enum_to_str(settings["input_mode"])
        try:
            with open(self.FILE_PATH, "w") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"セーブエラー: {e}")
            self.show_error("セーブ", "設定データのセーブに失敗しました")

    # 設定値を取得
    def get(self, key):
        return self.settings.get(key)
    
    # 設定値を変更し、即時保存
    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

