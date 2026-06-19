from typing import Dict
from models.characters import Player

# ダメージボーナスの計算
def calculation_damage_bonus(player: Player) -> str:
    st = player.STR + player.SIZ
    if 2 <= st <= 12:
        return "-1D6"
    elif 13 <= st <= 16:
        return "-1D4"
    elif 25 <= st <= 32:
        return "+1D4"
    elif 33 <= st <= 40:
        return "+1D6"
    return "0"

# HPの計算
def calculation_health_point(player: Player) -> int:
    return (player.CON + player.SIZ) // 2

# POW 関連の計算
def calculation_power_related(player: Player) -> Dict[str, int]:
    # MP、幸運、SAN値の計算
    pow_val = player.POW
    return {"maxMP":pow_val, "Luck":pow_val * 5, "maxSAN":pow_val * 5}

# アイデアの計算
def calculation_idea(player: Player) -> int:
    return player.INT * 5

# 知識の計算
def calculation_educated_point(player: Player) -> int:
    return player.EDU * 5
        
# 回避の計算
def calculation_avoid_point(player: Player) -> int:
    return player.DEX * 2
