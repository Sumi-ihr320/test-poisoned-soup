from typing import Tuple
import pygame

from constans import FONT_PATH, SMALL_SIZ, BLACK, RED
from utils import get_new_size, get_scales
from ui.ui_cache import ImageCache
from ui.ui_elements import Image, Label
from ui.overlays.character_status.status_sheet_builder import StatusSheetBuilder
from ui.overlays.character_status.skill_sheet_builder import SkillSheetBuilder
from models.characters import Player, Human
from core.game_state import Flags

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

class CharacterStatusSheetBuilder:
    def __init__(self, screen):
        self.screen = screen
        self.screen_size = self.screen.get_size()

        self.font_data = (FONT_PATH, self.calculate_font_size())
        self.cache = ImageCache()

        # キャラクターシートのサイズ
        self.sheet_size = self.calculate_sheet_size()

        self.status_sheet_builder = StatusSheetBuilder(self.screen, self.font_data)
        self.skill_sheet_builder = SkillSheetBuilder(self.screen, self.font_data)

    # シートサイズの計算
    def calculate_sheet_size(self) -> Tuple[int, int]:
        sheet_size = (700, 250)
        return get_new_size(self.screen_size, sheet_size)

    # フォントサイズの計算    
    def calculate_font_size(self) -> int:
        _, _, aspect = get_scales(self.screen_size)
        font_size = int(SMALL_SIZ * aspect)
        return font_size

    # キャラクターシートのsurfaceとrectを作成する
    def create_sheet_surface(self, pos: Tuple[int, int]) -> Tuple[pygame.Surface, pygame.Rect, Image]:
        sheet_surface = pygame.Surface(self.sheet_size)
        sheet_rect = sheet_surface.get_rect(topleft=pos)
        return sheet_surface, sheet_rect
    
    # キャラクターシートの背景画像を作成する
    def create_sheet_background_image(self, sheet_surface):
        sheet_bg_img = Image(self.screen, path="old_paper.jpg", cache=self.cache, x="center", y="center", size_wh=self.sheet_size, parent=sheet_surface)
        return sheet_bg_img

    # キャラクターイメージを作成する
    def create_character_image(self, character: Player|Human, sheet_rect: pygame.Rect, flags: Flags=None) -> Image:
        if isinstance(character, Player):
            path = f"silhouette_{character.sex}_face.png"
        elif isinstance(character, Human):
            if not flags.get_flag("girl", "alive"):
                expression = "_pale_downcast_eyes_dark"
            elif flags.get_flag("girl", "faint") > 0:
                expression = "_pale_downcast_eyes"
            elif flags.get_flag("girl", "hp_damaged_g"):
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
        prev_status_button = self.create_button("＜＜ ステータス一覧へ", "prev", sheet_rect, row)
        return {"next": next_skill_button, "prev": prev_status_button}

    def create_button(self, text: str, action: str, sheet_rect: pygame.Rect, row: int) -> SheetTransitionButton:
        button = SheetTransitionButton(self.screen, font_data=self.font_data, text=text, action=action, sheet_rect=sheet_rect, row=row)
        return button

    def create_image(self, path: str, x: int, y: int, parent: pygame.Surface=None) -> Image:
        _, _, aspect = get_scales(self.screen_size)
        scale = 0.56 * aspect 
        image = Image(self.screen, path=path, cache=self.cache, scale=scale, x=x, y=y, parent=parent,
                      bg_flag=True, line_flag=True)
        return image

    def relayout(self, screen):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.font_data = (FONT_PATH, self.calculate_font_size())
        self.sheet_size = self.calculate_sheet_size()
