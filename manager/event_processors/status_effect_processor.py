from typing import Callable, Dict, List, Any, Optional

class StatusEffectProcessor:
    STATE_MAP = {"Shock":"ショックロール",
                 "Faint":"気絶",
                 "Dying":"死んでしまった",
                 "Temporary_madness":"一時的狂気",
                 "Indeterminate_madness":"不定の狂気"}
    def __init__(self, dice_service, take_damage, callbacks):
        self.dice_service = dice_service
        self.take_damage = take_damage
        self.callbacks = callbacks

    def process_status_effects(self, state_record: Dict[Any, str], characters, game_state):
        for character, state in state_record.items():
            if state == "Dying":
                self.handle_dying(character, characters)
            elif state == "Faint":
                self.handle_faint(character, game_state, characters)
            elif state == "Shock":
                self.handle_shock(character)
            elif state == "Temporary_madness":
                self.handle_temporary_madness(character)
            elif state == "Indeterminate_madness":
                self.handle_indeterminate_madness(character)

    def handle_dying(self, character, characters):
        """キャラクターが死亡した場合の処理"""
        name = "あなた" if character == characters["player"] else character.name
        text = f"{name}は死んでしまった。"
        self.callbacks["set_result_display"](text)
        if character == characters["player"]:
            # 主人公が死んだらエンディングへ
            self.callbacks["next_scenario"]("Ending_1")
            return
        else:
            set_flag = self.callbacks["set_flag"]
            set_flag("girl", "alive", False)
            set_flag("girl", "fellow", False)
            set_flag("girl", "dice_check", False)
            set_flag("girl", "carry", False)

    def handle_faint(self, character, game_state, characters):
        """キャラクターが気絶した場合の処理"""
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
            self.set_flag("girl", "faint", recovery_time)
            self.set_flag("girl", "dice_check", False)
            # 主人公が気絶していない場合
            if not self.is_blackout_active:
            # 次のシナリオへ移行する
                self.callbacks["next_scenario"]("Faint_ver_girl")

    def handle_shock(self, character, characters):            
        """キャラクターがショック状態の場合の処理"""
        name = "あなた" if character == characters["player"] else character.name
        
        # 判定を行う
        target = "player" if character == characters["player"] else "girl"
        next_step = {"type":"dice_check", "check_type":"shock_roll", "target":target}
        self.handle_dice_check(next_step)

                # 結果表示
                #self.to_callback_next_scenario("result_text")
                #next_step = {"type":"result_text", "progression":"click"}
                #self.handle_scenario_event(next_step)
                
                # ショックロールを失敗した場合
                if character == self.player and not self.player_roll_result:
                    self.state_record[self.player] = "Faint"
                elif character == self.girl and not self.girl_roll_result:
                    self.state_record[self.girl] = "Faint"

                # 失敗してレコードが書き換えられている場合はもう一度状態異常のシナリオへ
                if self.state_record[character] != state:
                    self.to_callback_next_scenario("Status_effect")
                    return
                
                text = f"{name}はなんとか耐えた。"
                self.pending_result_display = True
                self.current_display_text = text

        
            name = "あなた" if character == characters["player"] else character.name

            # 死んだ場合
            if state == "Dying":
            # 気絶した場合
            elif state == "Faint":
            # ショックロール判定を行う
            elif state == "Shock":
                # 判定を行う
                target = "player" if character == self.player else "girl"
                next_step = {"type":"dice_check", "check_type":"shock_roll", "target":target}
                self.handle_dice_check(next_step)

                # 結果表示
                #self.to_callback_next_scenario("result_text")
                #next_step = {"type":"result_text", "progression":"click"}
                #self.handle_scenario_event(next_step)
                
                # ショックロールを失敗した場合
                if character == self.player and not self.player_roll_result:
                    self.state_record[self.player] = "Faint"
                elif character == self.girl and not self.girl_roll_result:
                    self.state_record[self.girl] = "Faint"

                # 失敗してレコードが書き換えられている場合はもう一度状態異常のシナリオへ
                if self.state_record[character] != state:
                    self.to_callback_next_scenario("Status_effect")
                    return
                
                text = f"{name}はなんとか耐えた。"
                self.pending_result_display = True
                self.current_display_text = text
                    
        self.state_record = {}        