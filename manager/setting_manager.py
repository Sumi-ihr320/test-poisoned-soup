import os, json

from constans import PATH, SAVE_FOLDER

class SettingManager:
    FILE_PATH = f"{PATH}{SAVE_FOLDER}setting.json"
    def __init__(self):
        self.settings = {
            "fullscreen":False,
            "resolution":[800, 600],
            "str_resolution":"800x600",
            "music_volume":1,
            "se_volume":1
        }
        self.load_settings()

    # 設定ファイルを読み込む
    def load_settings(self):
        if os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, "r") as f:
                self.settings = json.load(f)

    # 設定をjsonファイルに保存する
    def save_settings(self):
        with open(self.FILE_PATH, "w") as f:
            json.dump(self.settings, f, indent=4)

    # 設定値を取得
    def get(self, key):
        return self.settings.get(key)
    
    # 設定値を変更し、即時保存
    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

