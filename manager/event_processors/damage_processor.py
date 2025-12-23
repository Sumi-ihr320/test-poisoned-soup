from typing import Dict, Any


class DamageProcessor:
    def __init__(self, dice_service, damage_applier):
        """
        dice_service: DiceService
        damage_applier: callback(character, status, damage) -> state: str or None
        """
        self.dice_service = dice_service
        self.damage_applier = damage_applier

    def process_damage(self, step: Dict[str, Any], characters: Dict[Any, bool]):
        """
        step: シナリオのステップ {"status": str, "value": int or str, "target": str, "text": str}
        characters: {character_obj: roll_result=bool}
        戻り値: {"texts":[...], "state_record":{char:state}, "damage_points":{char:int}}
        """
        texts = []
        state_record = {}
        damage_points = {}

        value = step.get("value", None)
        status = step.get("status", None)
        failure_text = step.get("text", "")

        # ダメージを受ける人数分繰り返す
        for character, roll_result in characters.items():

            # 半分のダメージを受ける場合
            if value == "1/2" and status:
                status_point = getattr(character, status)
                damage_point = status_point // 2

            # value が success/failure 表記の場合
            elif isinstance(value, str) and "/" in str(value):
                success_s, failure_s = value.split("/")
                # dが入っていればダイスロールで値を出す
                if "d" in failure_s:
                    damage_point = self.dice_service.roll(failure_s)
                else:
                    damage_point = int(failure_s)
                success = int(success_s)

            else:
                # 固定値またはダイス表記の場合
                if isinstance(value, int):
                    damage_point = int(value)
                elif isinstance(value, str) and "d" in value:
                    damage_point = self.dice_service.roll(value)
                else:
                    damage_point = int(value)

            # どのステータスが減るか
            if status:
                # SANチェック後の正気度ダメージの場合
                if status == "SAN":
                    if roll_result:
                        if "success" in locals() and success == 0:
                            text = f"{character.name}は正気度が減らずに済んだ"
                        else:
                            state = self.damage_applier(character, status, success)
                            text = f"{character.name}は{success}ポイントの正気度を失った"
                    else:
                        state = self.damage_applier(character, status, damage_point)
                        text = f"{character.name}は{damage_point}ポイントの正気度を失った"

                else:
                    state = self.damage_applier(character, status, damage_point)
                    text = f"{character.name}は{damage_point}ポイントのダメージを受けた"

                # ダメージの量によって何らかの特殊状態になった場合(狂気、ショック、気絶、死亡)
                if state:
                    state_record[character] = state

            damage_points[character] = damage_point
            texts.append(text)

        if failure_text:
            texts.insert(0, failure_text)

        return {"texts": texts, "state_record": state_record, "damage_points":damage_points}

