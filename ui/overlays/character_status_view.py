from typing import Dict, Any, Tuple, List
from dataclasses import dataclass

import pygame

from constans import FONT_PATH, SMALL_SIZ
from utils import get_new_size, get_scales
from ui.overlays.overlay_view import OverlayView, OverlayCloseButton
from ui.ui_elements import Image, Label
from models.characters import Player, Human
from core.game_state import Flags

@dataclass
class CharacterStatusElements:
    surface: pygame.Surface
    background_image: Image
    character_image: Image

    current_hp_label: Label
    current_san_label: Label
    status_labels: List[Label]

class CharacterStatusView(OverlayView):
    def __init__(self, screen, parent=None):
        super().__init__(screen, parent)

        self.player = None
        self.girl = None
        self.flags = None

        self.font_data = (FONT_PATH, self.calculate_font_size())

        # キャラクターシートのサイズ
        self.sheet_size = self.calculate_sheet_size()

    # シートサイズの計算
    def calculate_sheet_size(self) -> Tuple[int, int]:
        sheet_size = (770, 250)
        return get_new_size(self.screen_size, sheet_size)

    # フォントサイズの計算    
    def calculate_font_size(self) -> int:
        _, _, aspect = get_scales(self.screen_size)
        font_size = int(SMALL_SIZ * aspect)
        return font_size

    # キャラクターシートのsurfaceを作成する
    def create_sheet_surface(self) -> Tuple[pygame.Surface, Image]:
        sheet_surface = pygame.Surface(self.sheet_size)
        sheet_bg_img = Image(self.screen, path="old_paper.jpg", x="center", y="center", size_wh=self.sheet_size, parent=sheet_surface)
        return sheet_surface, sheet_bg_img
    
    # ステータスラベルを作成する
    def create_status_labels(self, character: Player|Human, image_rect: pygame.Rect, parent: pygame.Surface=None) -> Dict[str, List[Label]|Label]:
        status_items = {}
        x, y = image_rect.right + 20, image_rect.y + 5
        margenx, margeny = 30, 6
        startx = x
        title_y = y
        character_status_dict = self.build_status_data(character)
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
                status_items["label"].append(lbl_status)
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

    # キャラクターイメージを作成する
    def create_character_image(self, character: Player|Human, parent: pygame.Surface=None) -> Image:
        if character is self.player:
            path = f"silhouette_{self.player.sex}_face.png"
        elif character is self.girl:
            if not self.flags.get_flag("girl", "alive"):
                expression = "_pale_downcast_eyes_dark"
            elif self.flags.get_flag("girl", "faint") > 0:
                expression = "_pale_downcast_eyes"
            elif self.flags.get_flag("girl", "hp_damaged_g"):
                expression = "_pale"
            else:
                expression = ""
            path = f"Girl_face{expression}.png"

        character_image = self.create_image(path=path, x=10, y=10, parent=parent)
        return character_image

    def create_label_button(self, text: str, parent: pygame.Surface) -> Label:
        parent_rect = parent.get_rect()
        label = Label(self.screen, font_data=self.font_data, text=text, x=parent_rect.right - 10, y=parent_rect.bottom - 10, anchor=("right", "bottom"), 
                      parent=parent, focusable=True)
        return label

    def create_image(self, path: str, x: int, y: int, parent: pygame.Surface) -> Image:
        image = Image(self.screen, path=path, scale=0.56, x=x, y=y, parent=parent,
                      bg_flag=True, line_flag=True)
        return image

    def create_label(self, text: str, x: int, y: int, parent: pygame.Surface) -> Label:
        label = Label(self.screen, font_data=self.font_data, text=text, x=x, y=y, parent=parent)
        return label

    def build_status_data(self, character: Player|Human) -> Dict[str, Dict[str, Any]]:
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

    # 各キャラクターのキャラシを作成する
    def build_character_sheet(self, character: Player|Human) -> CharacterStatusElements:
        character_sheet_surface, character_sheet_bg = self.create_sheet_surface()
        character_image = self.create_character_image(character, character_sheet_surface)
        character_status_labels = self.create_status_labels(character, character_image.rect, character_sheet_surface)
        sheet = CharacterStatusElements(character_sheet_surface, character_sheet_bg, character_image, 
                                        character_status_labels["currentHP"], character_status_labels["currentSAN"], 
                                        character_status_labels["labels"])
        return sheet

    # キャラクターシートたちを構成する
    def build_character_sheets(self):
        self.player_sheet = self.build_character_sheet(self.player)
        self.girl_sheet = self.build_character_sheet(self.girl)

    def create_close_button(self):
        screen_rect = self.screen.get_rect()
        self.close_button = OverlayCloseButton(self.screen, x=screen_rect.right-20, y=20)
        self.add(self.close_button)        

    def open(self, player: Player, girl: Human, flags: Flags):
        super().open()
        self.player = player
        self.girl = girl
        self.flags = flags
        self.clear()
        self.create_close_button()
        self.build_character_sheets()

    def relayout(self, screen):
        super().relayout(screen, parent=None)

        self.sheet_size = self.calculate_sheet_size()

        for c in self.children:
            c.relayout(screen, parent=None)

    def draw_player(self):
        self.screen.blit(self.player_sheet.surface, (15, 15))
        self.player_sheet.bg.draw()

        self.player_sheet.image.draw()
        self.player_sheet.currentHP_label.draw()
        self.player_sheet.currentSAN_label.draw()
        for label in self.player_sheet.status_label:
            label.draw()

    def draw_girl(self):
        player_sheet_rect = self.player_sheet.surface.get_rect()
        self.screen.blit(self.girl_sheet.surface, (15, 15 + player_sheet_rect.height))

        self.girl_sheet.image.draw()
        self.girl_sheet.currentHP_label.draw()
        self.girl_sheet.currentSAN_label.draw()
        for label in self.girl_sheet.status_label:
            label.draw()
        
    def draw(self):
        if not self.is_open:
            return
        
        self.screen.blit(self.surface, (0, 0))

        self.draw_player()

        for c in self.children:
            c.draw()
