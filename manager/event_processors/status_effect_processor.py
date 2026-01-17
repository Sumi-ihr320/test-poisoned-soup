from typing import Callable, Dict, Any
from core.game_state import GameStatus

class StatusEffectProcessor:
    STATE_MAP = {"Shock":"ショックロール",
                 "Faint":"気絶",
                 "Dying":"死んでしまった",
                 "Temporary_madness":"一時的狂気",
                 "Indeterminate_madness":"不定の狂気"}
    def __init__(self, dice_service, take_damage, callbacks: Dict[str, Callable]):
        """
        役割：状態異常による結果（テキスト、フラグ変更、次のシナリオ）を決定する

        やってはいけないこと：
        - render_manager の状態を参照する（is_blackout_active）
        - dice_check を勝手に実行する（EventManagerへの依存）

        やるべきこと：
        - 状態異常の処理結果を戻り値で返す
        - EventManager に「次の処理」を依頼するだけ
        """
        self.dice_service = dice_service
        self.take_damage = take_damage
        self.callbacks = callbacks

    def process_status_effects(self, state_record: Dict[Any, str], characters, game_state: GameStatus):
        results = []
        for character, state in state_record.items():
            if state == "Dying":    # 死亡
                result = self.handle_dying(character, characters)
            elif state == "Faint":  # 気絶
                result = self.handle_faint(character, characters, game_state)
            elif state == "Shock":  # ショック
                result = self.handle_shock(character, characters)
            elif state == "Temporary_madness":      # 一時的狂気
                result = self.handle_temporary_madness(character, characters)
            elif state == "Indeterminate_madness":  # 不定の狂気
                result = self.handle_indeterminate_madness(character, characters)

            if result:
                results.append(result)

        return results

    def handle_dying(self, character, characters):
        """死亡した場合の処理"""
        name = "あなた" if character == characters["player"] else character.name
        text = f"{name}は死んでしまった。"
        self.callbacks["set_result_display"](text)
        if character == characters["player"]:
            # 主人公が死んだらエンディングへ
            self.callbacks["next_scenario"]("Ending_1")
            return {}
        else:
            set_flag = self.callbacks["set_flag"]
            set_flag("girl", "alive", False)
            set_flag("girl", "fellow", False)
            set_flag("girl", "dice_check", False)
            set_flag("girl", "carry", False)

    def handle_faint(self, character, characters, game_state):
        """気絶した場合の処理"""
        name = "あなた" if character == characters["player"] else character.name
        text = f"{name}は気絶してしまった。"
        self.callbacks["set_result_display"](text)
        
        # 気絶した時間 - 気絶する時間 = 気絶から目覚める時間
        faint_time = game_state.time
        dice_result = self.dice_service.roll("1d10")
        wait_duration = dice_result * 100
        recovery_time = faint_time - dice_result

        if character == characters["player"]:
            # 主人公が気絶したらブラックアウトする
            self.callbacks["black_out"](wait_duration)
            return {"recovery_time": recovery_time}
        else:
            self.callbacks["set_flag"]("girl", "faint", recovery_time)
            self.callbacks["set_flag"]("girl", "dice_check", False)
            # 主人公が気絶していない場合
            if not self.callbacks["get_blackout_state"]():
            # 次のシナリオへ移行する
                self.callbacks["next_scenario"]("Faint_ver_girl")

    def handle_shock(self, character, characters):
        """ショック状態の場合の処理"""

        return {
            "action": "need_dice_check",
            "type": "shock_roll",
            "target": "player" if character == characters["player"] else "girl",
            "character": character
        }
                            
    def handle_temporary_madness(self, character, characters):
        """一時的狂気の処理"""
        pass

    def handle_indeterminate_madness(self, character, characters):
        """不定の狂気の処理"""
        pass
