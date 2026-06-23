from typing import Dict, Any, Tuple, List, Optional
from dataclasses import dataclass

import pygame

from constans import FONT_PATH, SMALL_SIZ, BLACK, RED
from utils import get_new_size, get_scales
from ui.overlays.overlay_view import OverlayView, OverlayCloseButton
from ui.ui_elements import Image, Label
from ui.ui_cache import ImageCache
from models.characters import Player, Human
from core.game_state import Flags

@dataclass
class CharacterStatusElements:
    surface_1: pygame.Surface
    rect_1: pygame.Rect
    background_image_1: Image

    surface_2: Optional[pygame.Surface]
    rect_2: Optional[pygame.Rect]
    background_image_2: Optional[Image]

    character_image: Image

    current_hp_label: Label
    current_san_label: Label
    status_labels: List[Label]
    next_skill_button: Label
    prev_status_button: Label

class SheetTransitionButton(Label):
    def __init__(self, screen, font_data, text, sheet_rect, x = 0, y = 0, centerx = None, centery = None, anchor = ("right", "bottom"), 
                 text_color = BLACK, background_color = None, 
                 hover_type = "line", hover_line_bold = 1, hover_text_color = RED, hover_back_color = None, hover_text = None, 
                 result_type = None, action=None, sound_type = "click", row = 0, col = 0, focusable = True, parent = None, **kwargs):
        x = sheet_rect.right - 10
        y = sheet_rect.bottom - 10
        super().__init__(screen, font_data, text, x, y, centerx, centery, anchor, text_color, background_color, hover_type, hover_line_bold, hover_text_color, hover_back_color, hover_text, result_type, sound_type, row, col, focusable, parent, **kwargs)
        self.action = action

    def handle_click(self, pos) -> bool:
        if self.collidepoint(pos):
            self.on_decide()
            return self.action
        return None    

class CharacterStatusView(OverlayView):
    def __init__(self, screen, parent=None):
        super().__init__(screen, parent)

        self.player = None
        self.girl = None
        self.flags = None

        self.font_data = (FONT_PATH, self.calculate_font_size())
        self.cache = ImageCache()

        # キャラクターシートのサイズ
        self.sheet_size = self.calculate_sheet_size()

    # シートサイズの計算
    def calculate_sheet_size(self) -> Tuple[int, int]:
        sheet_size = (700, 250)
        return get_new_size(self.screen_size, sheet_size)

    # フォントサイズの計算    
    def calculate_font_size(self) -> int:
        _, _, aspect = get_scales(self.screen_size)
        font_size = int(SMALL_SIZ * aspect)
        return font_size

    # キャラクターシートのsurfaceを作成する
    def create_sheet_surface(self, pos: Tuple[int, int]) -> Tuple[pygame.Surface, pygame.Rect, Image]:
        sheet_surface = pygame.Surface(self.sheet_size)
        sheet_rect = sheet_surface.get_rect(topleft=pos)
        sheet_bg_img = Image(self.screen, path="old_paper.jpg", cache=self.cache, x="center", y="center", size_wh=self.sheet_size, parent=sheet_surface)
        return sheet_surface, sheet_rect, sheet_bg_img
    
    # ステータスラベルを作成する
    def create_status_labels(self, character: Player|Human, image_rect: pygame.Rect, parent: pygame.Surface=None, ofset: Tuple[int, int]=None) -> Dict[str, List[Label]|Label]:
        status_items = {}
        x, y = image_rect.right + 20 - ofset[0], image_rect.top + 5 - ofset[1]
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

    # キャラクターイメージを作成する
    def create_character_image(self, character: Player|Human, sheet_rect: pygame.Rect) -> Image:
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

        x = sheet_rect.x + 10
        y = sheet_rect.y + 10
        character_image = self.create_image(path=path, x=x, y=y)
        return character_image

    def create_transition_buttons(self, sheet_rect: pygame.Rect, row:int):
        next_skill_button = self.create_button("技能一覧へ ＞＞", "next", sheet_rect, row)
        self.add(next_skill_button)
        prev_status_button = self.create_button("＜＜ ステータス一覧へ", "prev", sheet_rect, row)
        return {"next": next_skill_button, "prev": prev_status_button}

    def create_button(self, text: str, action: str, sheet_rect: pygame.Rect, row: int) -> SheetTransitionButton:
        button = SheetTransitionButton(self.screen, font_data=self.font_data, text=text, action=action, sheet_rect=sheet_rect, row=row)
        return button

    def create_image(self, path: str, x: int, y: int, parent: pygame.Surface=None) -> Image:
        image = Image(self.screen, path=path, cache=self.cache, scale=0.56, x=x, y=y, parent=parent,
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
    def build_character_sheet(self, character: Player|Human, pos: Tuple[int, int], row: int) -> CharacterStatusElements:
        character_sheet_surface, character_sheet_rect, character_sheet_bg = self.create_sheet_surface(pos)
        character_image = self.create_character_image(character, character_sheet_rect)
        character_status_labels = self.create_status_labels(character, character_image.rect, character_sheet_surface, ofset=character_sheet_rect.topleft)
        character_sheet_buttons = self.create_transition_buttons(character_sheet_rect, row)
        sheet = CharacterStatusElements(surface_1=character_sheet_surface, rect_1=character_sheet_rect, 
                                        background_image_1=character_sheet_bg, 
                                        surface_2=None, rect_2=None, background_image_2=None,
                                        character_image=character_image,
                                        current_hp_label=character_status_labels["currentHP"], current_san_label=character_status_labels["currentSAN"], 
                                        status_labels=character_status_labels["labels"], 
                                        next_skill_button=character_sheet_buttons["next"], prev_status_button=character_sheet_buttons["prev"])
        return sheet

    # キャラクターシートたちを構成する
    def build_character_sheets(self):
        x = self.screen_size[0] // 2 - self.sheet_size[0] // 2
        self.player_sheet = self.build_character_sheet(self.player, (x, 15), row=1)
        girl_y = 15 + self.player_sheet.rect_1.height + 15
        self.girl_sheet = self.build_character_sheet(self.girl, (x, girl_y), row=2)

    def create_close_button(self):
        self.close_button = OverlayCloseButton(self.screen, x=self.player_sheet.rect_1.right-10, y=self.player_sheet.rect_1.y+10)
        self.add(self.close_button)        

    def open(self, player: Player, girl: Human, flags: Flags):
        super().open()
        self.player = player
        self.girl = girl
        self.flags = flags
        self.clear()
        self.build_character_sheets()
        self.create_close_button()

    def handle_click(self, element, result):
        selected_action = result

        if selected_action == "close":
            self.close()

        elif selected_action == "next":
            if element == self.player_sheet.next_skill_button:
                pass
            elif element == self.girl_sheet.next_skill_button:
                pass

        elif selected_action == "prev":
            if element == self.player_sheet.prev_status_button:
                pass
            elif element == self.girl_sheet.prev_status_button:
                pass
        
        return selected_action

    def relayout(self, screen):
        super().relayout(screen, parent=None)

        self.sheet_size = self.calculate_sheet_size()

        for c in self.children:
            c.relayout(screen, parent=None)

    def draw_sheet(self, elements: CharacterStatusElements):
        self.screen.blit(elements.surface_1, elements.rect_1)
        elements.background_image_1.draw()

        elements.character_image.draw()
        elements.current_hp_label.draw()
        elements.current_san_label.draw()
        for label in elements.status_labels:
            label.draw()
        elements.next_skill_button.draw()
        
    def draw(self):
        if not self.is_open:
            return
        
        self.screen.blit(self.surface, (0, 0))

        self.draw_sheet(self.player_sheet)
        #if self.flags.get_flag("girl", "fellow"):
        self.draw_sheet(self.girl_sheet)

        for c in self.children:
            c.draw()
