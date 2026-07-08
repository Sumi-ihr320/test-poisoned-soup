
from typing import Tuple, Dict, List
import pygame

from constans import SKILL_DATA_PATH, JSON_FOLDER
from utils import load_json
from ui.ui_elements import Label
from models.characters import Player, Human

class SkillSheetBuilder:
    def __init__(self):
        self.all_skill_dict = load_json(SKILL_DATA_PATH, JSON_FOLDER)

    def set_skills_data(self, character: Player|Human) -> Dict[str, int]:
        character_skills = character.skills.copy()
        character_all_skill_dict = {}
        for skill in self.all_skill_dict:
            if skill in character_skills:
                character_all_skill_dict[skill] = character_skills[skill]
            else:
                character_all_skill_dict[skill] = self.all_skill_dict[skill]
        return character_all_skill_dict

    def create_skill_labels(self, character: Player|Human, image_rect: pygame.Rect, parent: pygame.Surface=None, ofset: Tuple[int, int]=None) -> List[Label]:
        skill_items = []
        character_all_skill_dict = self.set_skills_data(character)
        x, y = image_rect.right + 20 - ofset[0], image_rect.top + 5 - ofset[1]
        max_x = parent.get_rect().right - margenx
        margenx, margeny = 30, 6
        startx = x
        starty = y
        for skill, value in character_all_skill_dict.items():
            lbl_skill = self.create_label(text=f"{skill}: {value}", x=x, y=y, parent=parent)
            skill_items.append(lbl_skill)
            x += lbl_skill.max_width + margenx
            if x > max_x:
                x = startx
                y += lbl_skill.max_height + margeny
        return skill_items

    def create_label(self, text: str, x: int, y: int, parent: pygame.Surface) -> Label:
        label = Label(self.screen, font_data=self.font_data, text=text, x=x, y=y, parent=parent)
        return label
