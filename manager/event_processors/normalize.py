from typing import Any, Dict, List
import re

def _to_piece(val) -> Dict[str, Any]:
    """値を canonical piece にする。数値->fixed、'1d6'->dice、dictはそのまま"""
    if isinstance(val, dict):
        return val
    if val is None:
        return {"type": "fixed", "value": 0}
    s = str(val).strip()
    # 整数文字列なら fixed
    if re.fullmatch(r'-?\d+', s):
        return {"type": "fixed", "value": int(s)}
    
    # fraction 文字列 (例： 1/2) は fraction として扱うがsouceは不明なのでえっ、どうすべき？
    if "/" in s:
        raise ValueError(f"pieceに/が含まれています: {s}")

    # ダイス表記ならdice
    if re.search(r'[dD]\d+', s):
        return {"type": "dice", "spec": s}
    
    return {"type": "fixed", "value": 0}

def _wrap_next_step(name: str) -> Dict[str, Any]:
    """文字列の次のステップ指定を canonical な next_step ステップに変換する"""
    return {"type": "next_step", "next": name}

def normalize_damage_spec(step: Dict[str, Any]) -> Dict[str, Any]:
    """
    step の 'damage' または 'value' を見て canonical dict を返す
    - 優先順: fraction('1/2') -> branch('A/B') -> dice/fixed
    - 古い表現  value:'0/1d4' や  value: '1/2' に対応
    """
    d = step.get("damage", None)
    if d is None and "value" in step:
        d = step["value"]

    if d is None:
        return {}
    
    # まず fraction (例 '1/2') をチェック
    if isinstance(d, str) and re.fullmatch(r'\s*\d+\s*/\s*\d+\s*', d):
        # fraction は  source が必要　(例 status フィールド)
        src = step.get("status") or step.get("source")
        parts = [int(x.strip()) for x in d.split("/", 1)]
        return {"type": "fraction", "source": src, "num": parts[0], "den": parts[1]}
    
    # branch (A/B)　例 '0/1d6' の場合
    if isinstance(d, str) and "/" in d:
        a, b = d.split("/", 1)
        return {
            "type": "branch",
            "target": step.get("status"),
            "success": _to_piece(a.strip()),
            "failure": _to_piece(b.strip())
        }
    
    # dict のままならそのまま返す
    if isinstance(d, dict):
        return d
    
    # 単一の値 (数値やダイス)
    return _to_piece(d)

def nomalize_dice_check(step: Dict[str, Any]) -> Dict[str, Any]:
    """
    dice_check の古いフィールドを変換
    - success/failure (文字列で次のシナリオ名) があれば on_success/ on_failure に変換
    - 他はそのまま返す
    """
    out = dict(step)    # shallow copy
    if "success" in step and "on_success" not in step:
        # success が次のシナリオ名なら next_step にする
        if isinstance(step["success"], str):
            out["on_success"] = [_wrap_next_step(step["success"])]
    if "failure" in step and "on_failure" not in step:
        if isinstance(step["failure"], str):
            out["on_failure"] = [_wrap_next_step(step["failure"])]
    return out

def normalize_step(step: Dict[str, Any]) -> Dict[str, Any]:
    """1ステップを正規化する (damage, dice_check 等)"""
    t = step.get("type")
    out = dict(step)
    if t == "damage":
        out["damage"] = normalize_damage_spec(step)
    if t == "dice_check":
        out = nomalize_dice_check(step)
    # 必要なら他の type の正規化ルールをここに追加
    return out

