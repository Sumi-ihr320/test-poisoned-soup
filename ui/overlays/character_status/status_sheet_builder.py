from typing import Any, Dict, List, Tuple
import pygame

from models.characters import Player, Human
from ui.ui_elements import Label

class StatusSheetBuilder:
    def __init__(self):
        pass

    def set_status_data(self, character: Player|Human) -> Dict[str, Dict[str, Any]]:
        sex_map = {"man": "男", "woman": "女", "neuter": "その他"}
        status_map = {
            "name":{"text": "名前： ", "status": character.name},
            "age": {"text": "年齢： ", "status": character.age},
            "sex": {"text": "性別： ", "status": sex_map[character.sex]},
            "Profession": {"text": "職業： ", "status": character.Profession},
            "Hobby": {"text": "趣味： ", "status": getattr(character, "Hobby", "なし")},
            "currentHP": {"text": "耐久力： ", "status": character.currentHP},
            "maxHP": {"text": " / ", "status": character.maxHP},
            "currentSAN": {"text": "正気度： ", "status": character.currentSAN},
            "maxSAN": {"text": " / ", "status": character.maxSAN},
            "STR": {"text": "STR： ", "status": character.STR},
            "CON": {"text": "CON： ", "status": character.CON},
            "SIZ": {"text": "SIZ： ", "status": character.SIZ},
            "DEX": {"text": "DEX： ", "status": character.DEX},
            "APP": {"text": "APP： ", "status": character.APP},
            "EDU": {"text": "EDU： ", "status": character.EDU},
            "INT": {"text": "INT： ", "status": character.INT},
            "POW": {"text": "POW： ", "status": character.POW},
            "Luck": {"text": "幸運： ", "status": character.Luck},
            "Idea": {"text": "アイデア： ", "status": character.Idea},
            "Know": {"text": "知識： ", "status": character.Know},
            "Dodge": {"text": "回避： ", "status": character.Dodge},
            "DB": {"text": "ﾀﾞﾒｰｼﾞ･ﾎﾞｰﾅｽ： ", "status": character.DB}
        }
        return status_map
    
    # ステータスラベルを作成する
    def create_status_labels(self, character: Player|Human, image_rect: pygame.Rect, parent: pygame.Surface=None, ofset: Tuple[int, int]=None) -> Dict[str, List[Label]|Label]:
        status_items = {}
        x, y = image_rect.right + 20 - ofset[0], image_rect.top + 5 - ofset[1]
        margenx, margeny = 30, 6
        startx = x
        title_y = y
        character_status_dict = self.set_status_data(character)
        status_items["labels"] = []
        for key, status in character_status_dict.items():
            lbl_title = self.create_label(text=status["text"], x=x, y=y, parent=parent)
            status_items["labels"].append(lbl_title)
            x += lbl_title.max_width
            title_y = y
            lbl_status = self.create_label(text=str(status["status"]), x=x, y=y, parent=parent)
            if key == "currentHP":
                status_items["currentHP"] = lbl_status
            elif key == "currentSAN":
                status_items["currentSAN"] = lbl_status
            else:
                status_items["labels"].append(lbl_status)
            if key in ["name", "sex", "Hobby", "maxSAN", "SIZ", "EDU", "Luck", "Dodge"]:
                x = startx
                y += lbl_status.max_height + margeny
            else:
                if key in ["currentHP", "currentSAN"]: 
                    x += lbl_status.max_width
                else:
                    x += lbl_status.max_width + margenx
                y = title_y
        return status_items
    
    def create_label(self, text: str, x: int, y: int, parent: pygame.Surface) -> Label:
        label = Label(self.screen, font_data=self.font_data, text=text, x=x, y=y, parent=parent)
        return label

