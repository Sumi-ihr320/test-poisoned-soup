# ダメージボーナスの計算
def calculation_damege_bonus(hero_data):
    st = hero_data["STR"] + hero_data["SIZ"]
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
def calculation_health_point(hero_data):
    return (hero_data["CON"] + hero_data["SIZ"]) // 2

# POW 関連の計算
def calculation_power_related(hero_data):
    # MP、幸運、SAN値の計算
    pow_val = hero_data["POW"]
    return {"MP":pow_val, "Luck":pow_val * 5, "SAN":pow_val * 5}

# アイデアの計算
def calculation_idea(hero_data):
    return hero_data["INT"] * 5

# 知識の計算
def calculation_educated_point(hero_data):
    return hero_data["EDU"] * 5
        
# 回避の計算
def calculation_avoid_point(hero_data):
    return hero_data["DEX"] * 2
