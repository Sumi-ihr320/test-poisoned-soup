from typing import Callable, Dict, Any
from core.game_state import GameStatus

class StatusEffectProcessor:
    STATE_MAP = {"Shock":"ショックロール",
                 "Faint":"気絶",
                 "Dying":"死んでしまった",
                 "Temporary_madness":"一時的狂気",
                 "Indeterminate_madness":"不定の狂気"}
    def __init__(self, dice_service, take_damage):
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
        return_info = {}
        name = "あなた" if character == characters["player"] else character.name
        return_info["text"] = f"{name}は死んでしまった。"

        if character == characters["player"]:
            # 主人公が死んだらエンディングへ
            return_info["action"] = "next_scenario"
            return_info["next"] = "Ending_1"
        else:
            return_info["action"] = "set_flags"
            return_info["flags"] = [
                {"category": "girl", "flag": "alive", "value": False},
                {"category": "girl", "flag": "fellow", "value": False},
                {"category": "girl", "flag": "dice_check", "value": False},
                {"category": "girl", "flag": "carry", "value": False}
            ]
        return return_info
    
    def handle_faint(self, character, characters, game_state):
        """気絶した場合の処理"""
        return_info = {}
        name = "あなた" if character == characters["player"] else character.name
        return_info["text"] = f"{name}は気絶してしまった。"
        
        # 気絶した時間 - 気絶する時間 = 気絶から目覚める時間
        faint_time = game_state.time
        dice_result = self.dice_service.roll("1d10")
        wait_duration = dice_result * 100
        recovery_time = faint_time - dice_result

        if character == characters["player"]:
            # 主人公が気絶したらブラックアウトする
            return_info["action"] = "black_out"
            return_info["wait_duration"] = wait_duration
            return_info["recovery_time"] = recovery_time
        else:
            return_info["action"] = "set_flags"
            return_info["flags"] = [
                {"category": "girl", "flag": "faint", "value": recovery_time},
                {"category": "girl", "flag": "dice_check", "value": False}
            ]
            return_info["if_question"] = "player_fainted"
            return_info["next"] = "Faint_ver_girl"
        return return_info

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
        return_info = {}
        pass

    def handle_indeterminate_madness(self, character, characters):
        """不定の狂気の処理"""
        return_info = {}
        pass
