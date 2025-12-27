from typing import Optional, Tuple, Dict, Any
from normalize import normalize_step

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

        new_step = normalize_step(step)

        value = new_step.get("value", None)
        status = new_step.get("status", None)
        failure_text = new_step.get("text", "")

        damage_info = new_step.get("damage", None)
    
        # ダメージを受ける人数分繰り返す
        for character, roll_result in characters.items():
            status, damage_point = self.resolve_damage(value, status, damage_info, character, roll_result)

            # どのステータスが減るか
            text = ""
            if status:
                # SANチェック後の正気度ダメージの場合
                if status == "SAN":
                    if roll_result and damage_point == 0:
                        state = None
                        text = f"{character.name}は正気度が減らずに済んだ"
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

    def resolve_damage(self, value: Optional[int], status: Optional[str], damage_info: Optional[Dict], character, roll_result: bool) -> Tuple[Optional[str], int]:
        """
        ダメージ情報に応じてダメージポイントを計算し、ステータスと一緒に返す
        戻り値: (status: str or None, damage_point: int)
        """
        if damage_info:
            damage_type = damage_info.get("type", None)
            
            if damage_type == "fixed":
                return (status, damage_info.get("value", 0))
            
            # "1/2" などの分数表記の場合
            if damage_type == "fraction":
                source = damage_info.get("source", None)
                if not source:
                    raise ValueError("fractionのsourceが指定されていません")
                num = damage_info.get("num", 0)
                den = damage_info.get("den", 1)
                status_point = getattr(character, source) if source else 0
                return (source, int((status_point / den) * num))

            # 成/否表記の場合
            if damage_type == "branch":
                target = damage_info.get("target", None)
                success_piece = damage_info.get("success", 0)
                success_point = self.check_piece(success_piece)
                failure_piece = damage_info.get("failure", 0)
                failure_point = self.check_piece(failure_piece)

                if roll_result:
                    return (target, success_point)
                else:
                    return (target, failure_point)

        else:
            if not value:
                return (status, 0)
            
            # 半分のダメージを受ける場合
            if value == "1/2" and status:
                status_point = getattr(character, status)
                return (status, status_point // 2)

            # value が success/failure 表記の場合
            if isinstance(value, str) and "/" in str(value):
                success_s, failure_s = value.split("/")
                # dが入っていればダイスロールで値を出す
                if "d" in failure_s.lower():
                    failure_point = self.dice_service.roll(failure_s)
                else:
                    failure_point = int(failure_s)
                success_point = int(success_s)

                if roll_result:
                    return (status, success_point)
                else:
                    return (status, failure_point)
            
            # 固定値またはダイス表記の場合
            if isinstance(value, int):
                return (status, int(value))
            elif isinstance(value, str) and "d" in value:
                return (status, self.dice_service.roll(value))
            else:
                return (status, int(value))

        return (status, 0)

    def check_piece(self, piece: Any) -> int:
        """damage の piece (int, dict) を評価してダメージポイントを返す"""
        if isinstance(piece, int):
            return piece
        
        elif isinstance(piece, dict):
            piece_type = piece.get("type", "")
            if piece_type == "fixed":
                return piece.get("value", 0)
            elif piece_type == "dice":
                spec = piece.get("spec", None)
                return self.dice_service.roll(spec)
        
        return 0
        
        
    