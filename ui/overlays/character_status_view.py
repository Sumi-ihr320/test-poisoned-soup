from typing import Dict, Any, Tuple, List, Optional
from dataclasses import dataclass

import pygame

from constans import FONT_PATH, SMALL_SIZ, BLACK, RED
from utils import get_new_size, get_scales
from ui.overlays.overlay_view import OverlayView, OverlayCloseButton
from ui.ui_elements import Image, Label
from ui.ui_cache import ImageCache
from ui.sheet_slide import SlideSheet, SheetSlideState, SheetSlideRenderer
from input.focus_manager import FocusManager
from models.characters import Player, Human
from core.game_state import Flags

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
    next_skill_button: Label
    prev_status_button: Label

    buttons: List[Label]

class SheetSlideController:
    def __init__(self, screen, focus_manager: FocusManager, character_sheet: Optional[CharacterStatusElements]=None):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.focus_manager = focus_manager

        self.character_sheet = character_sheet

        self.sheet_slide_state = SheetSlideState(self.screen_width, len(self.character_sheet.sheets))
        self.sheet_slide_renderer = SheetSlideRenderer(self.screen)

    def handle_slide(self, action: str):
        if action == "next":
            self.sheet_slide_state.next_page()
        elif action == "prev":
            self.sheet_slide_state.prev_page()

    def draw(self):
        if self.character_sheet:
            self.sheet_slide_renderer.draw(self.sheet_slide_state, self.character_sheet.sheets[self.sheet_slide_state.get_current_page()], self.character_sheet.sheets[self.sheet_slide_state.get_target_page()])

    def update(self):
        self.sheet_slide_state.update()

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
        self.focus_manager = None

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
        #self.add(next_skill_button)
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
        status_sheet_surface, status_sheet_rect, status_sheet_bg = self.create_sheet_surface(pos)
        status_sheet = SlideSheet(status_sheet_surface, status_sheet_rect)
        character_image = self.create_character_image(character, status_sheet_rect)
        status_labels = self.create_status_labels(character, character_image.rect, status_sheet_surface, ofset=status_sheet_rect.topleft)
        skill_surface, skill_rect, skill_bg = self.create_sheet_surface(pos)
        skill_sheet = SlideSheet(skill_surface, skill_rect)
        sheet_buttons = self.create_transition_buttons(status_sheet_rect, row)

        sheet = CharacterStatusElements(status_surface=status_sheet_surface, status_rect=status_sheet_rect, 
                                        status_background_image=status_sheet_bg, status_sheet=status_sheet,
                                        skill_surface=skill_surface, skill_rect=skill_rect, 
                                        skill_background_image=skill_bg, skill_sheet=skill_sheet,
                                        character_image=character_image,
                                        current_hp_label=status_labels["currentHP"], current_san_label=status_labels["currentSAN"], 
                                        status_labels=status_labels["labels"], 
                                        next_skill_button=sheet_buttons["next"], prev_status_button=sheet_buttons["prev"],
                                        sheets=[status_sheet, skill_sheet], buttons=list(sheet_buttons.values()))
        return sheet

    # キャラクターシートたちを構成する
    def build_character_sheets(self):
        x = self.screen_size[0] // 2 - self.sheet_size[0] // 2
        self.player_sheet = self.build_character_sheet(self.player, (x, 15), row=1)

        self.player_slide_controller = SheetSlideController(screen=self.screen, focus_manager=self.focus_manager, character_sheet=self.player_sheet)

        player_rect_height = self.player_sheet.status_rect.height
        girl_y = 15 + player_rect_height + 15
        self.girl_sheet = self.build_character_sheet(self.girl, (x, girl_y), row=2)

        self.girl_slide_controller = SheetSlideController(screen=self.screen, focus_manager=self.focus_manager, character_sheet=self.girl_sheet)

    def create_close_button(self):
        player_sheet_rect = self.player_sheet.status_rect

        self.close_button = OverlayCloseButton(self.screen, x=player_sheet_rect.right-10, y=player_sheet_rect.y+10)
        self.add(self.close_button)        

    def open(self, player: Player, girl: Human, flags: Flags, focus_manager: FocusManager):
        super().open()
        self.player = player
        self.girl = girl
        self.flags = flags
        self.focus_manager = focus_manager
        self.clear()
        self.build_character_sheets()
        self.create_close_button()

    def handle_click(self, element, result):
        selected_action = result

        if selected_action == "close":
            self.close()

        if element in self.player_sheet.buttons:
            self.player_slide_controller.handle_slide(selected_action)
            self.register_sheet_changes(self.focus_manager)
        
        elif element in self.girl_sheet.buttons:
            self.girl_slide_controller.handle_slide(selected_action)
            self.register_sheet_changes(self.focus_manager)

        return selected_action

    # シート切り替え時のフォーカス登録変更
    def register_sheet_changes(self, focus_manager: FocusManager):
        player_current_page = self.player_slide_controller.sheet_slide_state.get_current_page()
        if player_current_page == 0:
            self.register_transition(focus_manager, self.player_sheet.prev_status_button, self.player_sheet.next_skill_button)
        elif player_current_page == 1:
            self.register_transition(focus_manager, self.player_sheet.next_skill_button, self.player_sheet.prev_status_button)

        girl_current_page = self.girl_slide_controller.sheet_slide_state.get_current_page()
        if girl_current_page == 0:
            self.register_transition(focus_manager, self.girl_sheet.prev_status_button, self.girl_sheet.next_skill_button)
        elif girl_current_page == 1:
            self.register_transition(focus_manager, self.girl_sheet.next_skill_button, self.girl_sheet.prev_status_button)

    # ページ切り替え時のフォーカス登録変更
    def register_transition(self, focus_manager: FocusManager, old_button, new_button):
        if old_button in focus_manager.elements:
            focus_manager.elements.remove(old_button)
        if new_button not in focus_manager.elements:
            focus_manager.register(new_button)
                
    def relayout(self, screen):
        super().relayout(screen, parent=None)

        self.sheet_size = self.calculate_sheet_size()

        for c in self.children:
            c.relayout(screen, parent=None)

    def draw_sheet(self, elements: CharacterStatusElements, slide_controller: SheetSlideController):
        current_page = slide_controller.sheet_slide_state.get_current_page()
        if current_page == 0:
            elements.status_background_image.draw()
            elements.current_hp_label.draw()
            elements.current_san_label.draw()
            for label in elements.status_labels:
                label.draw()
        else:
            elements.skill_background_image.draw()
        
        slide_controller.draw()
        
        elements.character_image.draw()

        if current_page == 0: 
            elements.next_skill_button.draw()
        elif current_page == 1:
            elements.prev_status_button.draw()
        
    def draw(self):
        if not self.is_open:
            return
        
        self.screen.blit(self.surface, (0, 0))

        self.draw_sheet(self.player_sheet, self.player_slide_controller)
        #if self.flags.get_flag("girl", "fellow"):
        self.draw_sheet(self.girl_sheet, self.girl_slide_controller)

        for c in self.children:
            c.draw()
