from dataclasses import dataclass
from typing import List, Optional, Tuple
import pygame

from constans import FONT_PATH, SMALL_SIZ, BLACK, RED
from utils import get_new_size, get_scales
from ui.ui_cache import ImageCache
from ui.ui_elements import Image, Label
from ui.sheet_slide import SlideSheet
from ui.overlays.character_status.status_sheet_builder import StatusSheetBuilder
from ui.overlays.character_status.skill_sheet_builder import SkillSheetBuilder
from models.characters import Player, Human

@dataclass
class CharacterStatusElements:
    status_surface: pygame.Surface
    status_rect: pygame.Rect
    status_background_image: Image

    status_sheet: SlideSheet

    skill_surface: Optional[pygame.Surface]
    skill_rect: Optional[pygame.Rect]
    skill_background_image: Optional[Image]

    skill_sheet: Optional[SlideSheet]

    sheets: List[SlideSheet]

    character_image: Image

    current_hp_label: Label
    current_san_label: Label
    status_labels: List[Label]

    skill_labels: List[Label]

    next_skill_button: Label
    prev_status_button: Label

    buttons: List[Label]

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

class CharacterSheetBuilder:
    def __init__(self, screen):
        self.screen = screen
        self.screen_size = self.screen.get_size()

        self.font_data = (FONT_PATH, self.calculate_font_size())
        self.cache = ImageCache()

        # キャラクターシートのサイズ
        self.sheet_size = self.calculate_sheet_size()

        self.status_sheet_builder = StatusSheetBuilder()
        self.skill_sheet_builder = SkillSheetBuilder()

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
        #self.add(next_skill_button)
        prev_status_button = self.create_button("＜＜ ステータス一覧へ", "prev", sheet_rect, row)
        return {"next": next_skill_button, "prev": prev_status_button}

    # 各キャラクターのキャラシを作成する
    def build(self, character: Player|Human, pos: Tuple[int, int], row: int) -> CharacterStatusElements:
        status_sheet_surface, status_sheet_rect, status_sheet_bg = self.create_sheet_surface(pos)
        status_sheet = SlideSheet(status_sheet_surface, status_sheet_rect)
        character_image = self.create_character_image(character, status_sheet_rect)
        status_labels = self.status_sheet_builder.create_status_labels(character, character_image.rect, status_sheet_surface, ofset=status_sheet_rect.topleft)
        skill_sheet_surface, skill_rect, skill_bg = self.create_sheet_surface(pos)
        skill_labels = self.skill_sheet_builder.create_skill_labels(character, character_image.rect, skill_sheet_surface, ofset=skill_rect.topleft)
        skill_sheet = SlideSheet(skill_sheet_surface, skill_rect)
        sheet_buttons = self.create_transition_buttons(status_sheet_rect, row)

        sheet = CharacterStatusElements(status_surface=status_sheet_surface, status_rect=status_sheet_rect, 
                                        status_background_image=status_sheet_bg, status_sheet=status_sheet,
                                        skill_surface=skill_sheet_surface, skill_rect=skill_rect, 
                                        skill_background_image=skill_bg, skill_sheet=skill_sheet,
                                        character_image=character_image,
                                        current_hp_label=status_labels["currentHP"], current_san_label=status_labels["currentSAN"], 
                                        status_labels=status_labels["labels"], skill_labels=skill_labels,
                                        next_skill_button=sheet_buttons["next"], prev_status_button=sheet_buttons["prev"],
                                        sheets=[status_sheet, skill_sheet], buttons=list(sheet_buttons.values()))
        return sheet

    def create_button(self, text: str, action: str, sheet_rect: pygame.Rect, row: int) -> SheetTransitionButton:
        button = SheetTransitionButton(self.screen, font_data=self.font_data, text=text, action=action, sheet_rect=sheet_rect, row=row)
        return button

    def create_image(self, path: str, x: int, y: int, parent: pygame.Surface=None) -> Image:
        image = Image(self.screen, path=path, cache=self.cache, scale=0.56, x=x, y=y, parent=parent,
                      bg_flag=True, line_flag=True)
        return image

    def relayout(self, screen, parent: pygame.Surface=None):
        self.screen = screen
        self.screen_size = screen.get_size()
        
    