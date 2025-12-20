from utils import opposition_percent
from ..dice_service import DiceService
from core.game_state import Flags


class DiceProcessor:
    def __init__(self, dice_service: DiceService, skill_list: dict, flags: Flags):
        self.dice_service = dice_service
        self.skill_list = skill_list
        self.flags = flags

    # ダイスロールを処理
    def process_dice_roll(self, step, character):
        dice_text = step.get("dice", "1d100")
        check_type = step["check_type"]
        half = step.get("half", False)      # 半分の値でチェックする
        status = step.get("status", step.get("skill", None))

        if check_type == "VS_active":
            active = getattr(character, status)
            passive = step["enemy_status"]
            threshold = opposition_percent(active, passive)

        elif check_type == "VS_passive":
            active = step["enemy_status"]
            passive = getattr(character, status)
            threshold = opposition_percent(active, passive)

        elif check_type == "毒対抗ロール":
            active = step["POT"]
            status = "CON"
            passive = getattr(character, status)
            threshold = opposition_percent(active, passive)

        elif check_type == "shock_roll":
            status = "CON"
            threshold = getattr(character, status) * 5

        elif check_type == "SANチェック":
            status = "SAN"
            threshold = getattr(character, status)

        elif check_type == "skill":
            #skill = step["skill"]
            threshold = character.skill.get(status, self.skill_list[status])

        elif check_type == "status":
            check_list = {"回避":"Dodge",
                          "幸運":"Luck"}
            status = check_list.get(status, status)
            threshold = getattr(character, status)
        
        if half:
            threshold = threshold // 2

        check_result, dice_result = self.dice_service.check_threshold(dice_text, threshold)

        result_text = f"{character.name}：成功！ <color=blue>{dice_result}<color/>/{threshold}" if check_result == True else f"{character.name}：失敗！ <color=red>{dice_result}<color/>/{threshold}"

        return {"status": status, "ok": check_result, "value": dice_result, "text": result_text}
