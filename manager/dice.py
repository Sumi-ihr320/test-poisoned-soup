from typing import Optional, Tuple
import random
from utils import dice_confirmation

class DiceEngine:
    def __init__(self, rng: Optional[random.Random]=None):
        self.rng = rng if rng else random.Random()

    # ダイスロールを計算してtotal: int を返す
    def roll(self, dice_text: str) -> int:
        pieces, dice_faces, modifier = dice_confirmation(dice_text)

        # ランダムで数字を出して個数分＋する
        total = sum(self.rng.randint(1, dice_faces) for _ in range(pieces))

        # プラスα文字列があった場合は計算する
        if modifier:
            sign = modifier.group()
            index = modifier.end()
            value = int(dice_text[index])

            total += value if sign == "+" else - value

        return total

    # ロール結果の成否判定を行い、成否の bool とロール結果の int を返す
    def check_threshold(self, dice_text: str, threshold: int, op: str = "<=") -> Tuple[bool, int]:
        """
        threshold: 判定の基準値
        return: 成否と結果 Tuple[bool, int]
        """
        value = self.roll(dice_text)
        if op == "<=":
            return (value <= threshold, value)
        if op == ">":
            return (value > threshold, value)
        raise ValueError("Unsupported op")


