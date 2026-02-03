import os, json
from typing import List, Dict, Any

from constans import PATH, SAVE_FOLDER, ROOM_NAME
from utils import load_json, save_json

class SaveDataManager:
    """
    役割：セーブデータのファイル操作を一元管理
    責務：
    - データの保存・読込・削除
    - ファイル管理
    - データ検証

    依存性：OS、JSON、ファイルシステムのみ
    UI には依存しない
    """
    def __init__(self):
        self.save_folder = f"{PATH}{SAVE_FOLDER}"   # セーブフォルダ
        self._ensure_folder_exists()

    # セーブフォルダが存在していなければ作成
    def _ensure_folder_exists(self):
        if not os.path.isdir(self.save_folder):
            os.makedirs(self.save_folder)

    # セーブファイル一覧を取得
    def get_save_files(self) -> List[str]:
        # フォルダ内にあるデータ一覧を持ってくる
        files = os.listdir(self.save_folder)

        # 設定データはリストに含まない
        return {f for f in files if f != "setting.json"}

    # データをファイルに保存
    def save_file(self, file_name: str, data: Dict) -> Dict[str, bool|str]:
        try:
            full_path = os.path.join(self.save_folder, file_name)
            save_json(full_path, data)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ファイルからデータを読込
    def load_file(self, file_name: str) -> Dict[str, bool|str|Dict[str, Any]]:
        try:
            load_data = load_json(file_name, SAVE_FOLDER)
            return {"success": True, "data": load_data}
        except FileNotFoundError:
            return {"success": False, "error": "ファイルが見つかりません"}
        except json.JSONDecodeError:
            return {"success": False, "error": "ファイル形式が正しくありません"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ファイルを削除する
    def remove_file(self, file_name: str) -> Dict[str, bool|str]:
        try:
            full_path = os.path.join(self.save_folder, file_name)
            os.remove(full_path)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # セーブデータを初期化（ファイルの中身を空にする）
    def delete_file(self, file_name: str) -> Dict[str, bool|str]:
        try:
            full_path = os.path.join(self.save_folder, file_name)
            # ファイルの中身を空にする
            with open(full_path, "w", encoding="utf-8_sig") as f:
                pass

            # 新しいファイル名に変更する
            file_no = self.extract_file_number(file_name)
            new_file_name = f"{file_no}.json"            
            new_path = os.path.join(self.save_folder, new_file_name)
            os.rename(full_path, new_path)

            return {"success": True}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ファイルNoを取得する
    def extract_file_number(self, file_name: str) -> str:
        file_name = file_name.replace(".json", "")
        return file_name.split(" ")[0]

