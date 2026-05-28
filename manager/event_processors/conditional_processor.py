from typing import Callable, Dict, List, Any

from core.game_state import GameStatus, Flags

class ConditionalProcessor:
    """
    条件分岐を処理するクラス。
    flags: Flags オブジェクト
    next_scenario_cb: 次シナリオへ遷移するコールバック
    """
    def __init__(self, flags: Flags, game_state: GameStatus, next_scenario_cb: Callable[[str], None]):
        self.flags = flags
        self.game_state = game_state
        self.next_scenario_cb = next_scenario_cb

    # 条件分岐を処理する
    def process_conditional(self, conditions: List[Dict[str, Any]], conditional_type: str=None):
        for condition in conditions:
            cond = condition["if"]
            # 他のconditionに当てはまらなかった場合
            if cond == "else":
                return {"next": condition["next"]}

            # 全部のフラグがOKだったら
            if all(self.check_flag(key, value) for key, value in cond.items()):

                # タイプが無い場合(普通の場合)
                if conditional_type is None:
                    return {"next": condition["next"]}

                # 複数のタイプが組み合わさってる場合
                elif "and" in conditional_type:
                    types = conditional_type.split("_and_")
                    result = {}
                    for key in types:
                        res = self.resolve_condition_result(condition, key)
                        if res["next"] is not None:
                            result.update(res)
                        else:
                            if result is None:
                                result = res
                            else:
                                result[key] = res[key]
                    return result

                # 少女画像の表示の場合
                elif conditional_type == "girl_image":
                    return {"girl_image": True, "state": condition.get("state", None), "position": condition.get("position", "right"), "next": condition.get("next", None)}

                # 単一のタイプの場合
                else:
                    return self.resolve_condition_result(condition, conditional_type)
                
        return None

    def resolve_condition_result(self, condition: Dict[str, Any], key: str):
        plural = key + "s"
        if plural in condition:
            result = self.get_item_by_time(condition[plural], key)
            if result is not None:
                if result[1] is not None:
                    return {key: result[0], "next": result[1]}
                else:
                    return {key: result[0], "next": condition.get("next", None)}
            else:
                return None
        else:
            return {key: condition[key], "next": condition.get("next", None)}

    # 時間によって変わるテキストや画像などを取得する
    def get_item_by_time(self, item_list: List[Dict[str, Any]], key: str):
        for item in item_list:
            if self.check_flag("time", {">": item["min_time"]}):
                return item[key], item.get("next", None)
        return None

    # フラグをチェックする
    def check_flag(self, key: str, value: Any) -> bool:
        """
        cond: {flag : {operator : value}}
        operator: "=="(等価比較), "!="(不等価比較), ">(大なり比較)", "<"(小なり比較)
        """
        if isinstance(value, dict):
            operator, val = list(value.items())[0]
        else:
            operator = "=="
            val = value

        if key in ["time", "hp_damaged"]:
            current = getattr(self.game_state, key)
        else:
            current = self.flags.get_flag_key_only(key)

        ok = False
        if operator == "==":
            ok = current == val
        elif operator == "!=":
            ok = current != val
        elif operator == ">":
            ok = current > val
        elif operator == "<":
            ok = current < val
        else:
            raise ValueError(f"不明なoperatorです: {operator}")

        return ok
    
