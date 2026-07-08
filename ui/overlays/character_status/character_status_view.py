from typing import Optional

from ui.overlays.overlay_view import OverlayView, OverlayCloseButton
from ui.overlays.character_status.character_sheet_builder import CharacterSheetBuilder, CharacterStatusElements
from ui.sheet_slide import SheetSlideState, SheetSlideRenderer
from input.focus_manager import FocusManager
from models.characters import Player, Human
from core.game_state import Flags

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


class CharacterStatusView(OverlayView):
    def __init__(self, screen, parent=None):
        super().__init__(screen, parent)

        self.player = None
        self.girl = None
        self.flags = None
        self.focus_manager = None

        self.character_sheet_builder = CharacterSheetBuilder(self.screen)
        

    # キャラクターシートたちを構成する
    def build_character_sheets(self):
        sheet_width = self.character_sheet_builder.sheet_size[0]
        x = self.screen_size[0] // 2 - sheet_width // 2
        self.player_sheet = self.character_sheet_builder.build_character_sheet(self.player, (x, 15), row=1)

        self.player_slide_controller = SheetSlideController(screen=self.screen, focus_manager=self.focus_manager, character_sheet=self.player_sheet)

        player_rect_height = self.player_sheet.status_rect.height
        girl_y = 15 + player_rect_height + 15
        self.girl_sheet = self.character_sheet_builder.build_character_sheet(self.girl, (x, girl_y), row=2)

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
        self.register_sheet_changes(focus_manager)

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
        elif current_page == 1:
            elements.skill_background_image.draw()
            for label in elements.skill_labels:
                label.draw()
        
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
