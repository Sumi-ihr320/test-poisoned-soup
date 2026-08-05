from typing import Optional

from ui.overlays.overlay_view import OverlayView, OverlayCloseButton
from ui.overlays.character_status.character_status_sheet_builder import CharacterStatusSheetBuilder
from ui.overlays.character_status.character_status_sheet import CharacterStatusSheet
from ui.sheet_slide import SheetSlideState, SheetSlideRenderer
from input.focus_manager import FocusManager
from models.characters import Player, Human
from core.game_state import Flags

class SheetSlideController:
    def __init__(self, screen, focus_manager: FocusManager, character_sheet: Optional[CharacterStatusSheet]=None):
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
            # まずはシートに記述してる内容を表示する
            self.character_sheet.draw()

            # シートのsurfaceを表示する
            self.sheet_slide_renderer.draw(self.sheet_slide_state, self.character_sheet.sheets[self.sheet_slide_state.get_current_page()], self.character_sheet.sheets[self.sheet_slide_state.get_target_page()])

            # surfaceより上に表示されているイメージを表示する            
            self.character_sheet.character_image.draw()
            
            # 1ページ目なら次へのボタンを表示
            if self.sheet_slide_state.get_current_page() == 0:
                self.character_sheet.next_skill_button.draw()
            
            # 2ページ目なら戻るのボタンを表示
            elif self.sheet_slide_state.get_current_page() == 1:
                self.character_sheet.prev_status_button.draw()

    def update(self):
        self.sheet_slide_state.update()


class CharacterStatusView(OverlayView):
    def __init__(self, screen, parent=None):
        super().__init__(screen, parent)

        self.player = None
        self.girl = None
        self.flags = None
        self.focus_manager = None

        self.character_status_sheet_builder = CharacterStatusSheetBuilder(self.screen)
        
    # キャラクターシートたちを構成する
    def build_character_sheets(self):
        sheet_width = self.character_status_sheet_builder.sheet_size[0]
        x = self.screen_size[0] // 2 - sheet_width // 2
        self.player_sheet = CharacterStatusSheet(self.screen, self.player, pos=(x, 15), row=1)

        self.player_slide_controller = SheetSlideController(screen=self.screen, focus_manager=self.focus_manager, character_sheet=self.player_sheet)

        player_rect_height = self.player_sheet.status_rect.height
        girl_y = 15 + player_rect_height + 15
        self.girl_sheet = CharacterStatusSheet(self.screen, self.girl, pos=(x, girl_y), row=2, flags=self.flags)

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
        
    def update(self):
        self.player_sheet.update(self.player)
        self.girl_sheet.update(self.girl, self.flags)
        self.player_slide_controller.update()
        self.girl_slide_controller.update()
    
    def draw(self):
        if not self.is_open:
            return
        
        self.screen.blit(self.surface, (0, 0))

        self.player_slide_controller.draw()
        #if self.flags.get_flag("girl", "fellow"):
        self.girl_slide_controller.draw()

        for c in self.children:
            c.draw()
