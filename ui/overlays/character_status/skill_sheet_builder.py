
from typing import Tuple, Dict, List
import pygame

from constans import SKILL_DATA_PATH, JSON_FOLDER
from utils import load_json
from ui.ui_elements import Label
from models.characters import Player, Human

class SkillSheetBuilder:
    def __init__(self, screen, font_data):
        self.screen = screen
        self.font_data = font_data

    def create_skill_labels(self, character: Player|Human, image_rect: pygame.Rect, parent: pygame.Surface=None, ofset: Tuple[int, int]=None) -> List[Label]:
        skill_items = []
        character_skill_dict = character.skill.copy()
        x, y = image_rect.right + 20 - ofset[0], image_rect.top + 5 - ofset[1]
        margenx, margeny = 30, 6
        max_width = parent.get_rect().width - x - margenx
        startx = x
        starty = y
        i = 1   # カウント用
        for skill, value in character_skill_dict.items():
            lbl_skill = self.create_label(text=f"{skill}: {value}", x=x, y=y, parent=parent)
            skill_items.append(lbl_skill)
            x += lbl_skill.max_width + margenx
            # 3つ表示したら次の行へ
            if i % 3 == 0:
                x = startx
                y += lbl_skill.max_height + margeny
            else:
                # もし技能の幅が文字を置ける最大幅より広く、それが2列目であれば次の行へ
                if lbl_skill.max_width * 3 > max_width and i % 3 == 2:
                    x = startx
                    y += lbl_skill.max_height + margeny
                    # カウントをゼロに戻す
                    i = 0
            i += 1
                
        x = startx
        y += lbl_skill.max_height+ margeny
        under_text = self.create_label("（※ 他技能は初期値）", x=x, y=y, parent=parent)
        skill_items.append(under_text)
        return skill_items

    def create_label(self, text: str, x: int, y: int, parent: pygame.Surface) -> Label:
        label = Label(self.screen, font_data=self.font_data, text=text, x=x, y=y, parent=parent)
        return label
