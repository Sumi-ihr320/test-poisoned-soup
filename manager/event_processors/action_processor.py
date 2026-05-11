from typing import Dict, Any, Callable
import re

from constans import ITEM_LIST
from models.characters import Player, Human
from core.game_state import GameStatus, Flags

class ActionProcessor:
    def __init__(self, player: Player, girl: Human, flags: Flags, 
                 on_room_refresh_callback: Callable, on_move_to_room_callback: Callable):
        self.player = player
        self.girl = girl
        self.flags = flags

        self.on_room_refresh_cb = on_room_refresh_callback
        self.on_move_to_room_cb = on_move_to_room_callback

        # 部屋の表示に変更を与えるフラグのリスト
        self.room_flag_list = ["light_remove",        # 電気が消える
                               "soup_in_poison",      # スープの色が変わる
                               "soup_drink",          # 器が空になる
                               "soup_destruction",    # 器が空になる
                               "soup_bowl_get",       # 器が無くなる
                               "east_room_visivle",   # 東の部屋が見えるようになる
                               "book_found",          # 本が追加される
                               "book_get",            # 本が無くなる
                               "candle_get",          # ロウソクが無くなる
                               "candle_goes_out"]     # ロウソクが消える


    # アクションを実行する
    def process_action(self, step: Dict[str, Any]):
        action = step["action"]

        # 部屋移動
        if action == "move_to_room":
            room_id = step.get("room_id", None)
            self.on_move_to_room_cb(room_id)

        # フラグセット
        elif action == "set_flag":
            # フラグをセットする            
            category = step.get("category", None)
            value = step.get("value", None)
            flag = step["flag"]
            if category and value is not None:
                self.set_flag(category, flag, value)
            else:
                if isinstance(flag, dict):
                    for key, val in flag.items():
                        self.set_flag_key_only(key, val)
                else:
                    self.set_flag_key_only(flag, value)

            # もしroom_flag_listのフラグに該当していたら部屋情報を更新する
            for key_flag in self.room_flag_list:
                if flag == key_flag:
                    self.on_room_refresh_cb()
                    break

        # アイテムを取得する
        elif action == "get_item":
            target = step.get("target", None)
            item = ITEM_LIST[step["item"]]
            character = self.girl if target == "girl" else self.player
            character.add_item(item)

        # アイテムを手放す
        elif action == "lost_item":
            target = step.get("target", None)
            item = ITEM_LIST[step["item"]]
            character = self.girl if target == "girl" else self.player
            character.remove_item(item)

    # フラグをセットする
    def set_flag(self, category: str, flag: str, value: Any):
        if type(value) == str:
            obj = re.match(r"\+|-", value)
            if obj:
                int_value = int(value[1:])
                flag_value = self.flags.get_flag(category, flag)
                if value[0] == "+":
                    value = flag_value + int_value
                else:
                    value = flag_value - int_value

        self.flags.update_flag(category, flag, value)

    # キーのみでフラグをセットする
    def set_flag_key_only(self, key: str, value: Any):
        if isinstance(value, dict):
            sign, val = list(value.items())[0]
            if sign in ["+", "-"]:
                int_value = int(val)
                current_value = self.flags.get_flag_key_only(key)
                if sign == "+":
                    value = current_value + int_value
                else:
                    value = current_value - int_value
        
        self.flags.update_flag_key_only(key, value)
