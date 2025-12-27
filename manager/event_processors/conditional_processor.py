from typing import Callable, Dict, List, Any
from core.game_state import GameStatus, Flags

class ConditionalProcessor:
    """
    条件分岐を処理するクラス。
    flags: Flags オブジェクト
    next_scenario_cb: 次シナリオへ遷移するコールバック
    """
    def __init__(self, flags: Flags, game_state: GameStatus, next_scenario_cb: callable[[str], None]):
        self.flags = flags
        self.game_state = game_state
        self.next_scenario_cb = next_scenario_cb

    # フラグをチェックする
    def flag_check(self, cond: Dict[str, Any]) -> bool:
        """
        cond: {"category": str, "flag": str, "value": Any, operator: str}
        operator: "equal"(等価比較), "not_equal"(不等価比較), "greater_than(大なり比較)"
        """
        category = cond["category"]
        flag = cond["flag"]
        val = cond["value"]
        operator = cond.get("operator", "equal")

        if category == "game_state":
            current = getattr(self.game_state, flag)
        else:
            current = self.flags.get_flag(category, flag)

        ok = False
        if operator == "equal":
            ok = current == val
        elif operator == "not_equal":
            ok = current != val
        elif operator == "grater_than":
            ok = current > val
        else:
            raise ValueError(f"不明なoperatorです: {operator}")

        return ok
    
