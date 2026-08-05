from typing import Tuple

from ui.sheet_slide import SlideSheet
from ui.overlays.character_status.character_status_sheet_builder import CharacterStatusSheetBuilder
from models.characters import Player, Human
from core.game_state import Flags

class CharacterStatusSheet:
    def __init__(self, screen, character: Player|Human, pos: Tuple[int, int], row: int, flags: Flags=None):
        self.screen = screen
        self.screen_size = self.screen.get_size()

        self.character = character
        self.row = row
        self.pos = pos

        self.flags = flags

        self.character_status_sheet_builder = CharacterStatusSheetBuilder(screen)

        self.build()

    # 各キャラクターのキャラシを作成する
    def build(self):
        self.status_surface, self.status_rect = self.character_status_sheet_builder.create_sheet_surface(self.pos)
        self.status_background_image = self.character_status_sheet_builder.create_sheet_background_image(self.status_surface)
        
        self.character_image = self.character_status_sheet_builder.create_character_image(self.character, self.status_rect, self.flags)
        
        status_labels = self.character_status_sheet_builder.status_sheet_builder.create_status_labels(self.character, self.character_image.rect, self.status_surface, ofset=self.status_rect.topleft)

        self.status_sheet = SlideSheet(self.status_surface, self.status_rect)

        self.current_hp_label = status_labels["currentHP"]
        self.current_san_label = status_labels["currentSAN"]
        self.status_labels = status_labels["labels"]

        self.skill_surface, self.skill_rect = self.character_status_sheet_builder.create_sheet_surface(self.pos)
        self.skill_background_image = self.character_status_sheet_builder.create_sheet_background_image(self.skill_surface)
        self.skill_labels = self.character_status_sheet_builder.skill_sheet_builder.create_skill_labels(self.character, self.character_image.rect, self.skill_surface, ofset=self.skill_rect.topleft)

        self.skill_sheet = SlideSheet(self.skill_surface, self.skill_rect)

        self.sheets = [self.status_sheet, self.skill_sheet]

        sheet_buttons = self.character_status_sheet_builder.create_transition_buttons(self.status_rect, self.row)
        self.next_skill_button = sheet_buttons["next"]
        self.prev_status_button = sheet_buttons["prev"]

        self.buttons = [self.next_skill_button, self.prev_status_button]        

    def relayout(self, screen):
        self.screen = screen
        self.character_status_sheet_builder.relayout(screen)
        self.build()

    def update(self, character:Player|Human, flags: Flags=None):
        self.current_hp_label.set_text(str(character.currentHP))
        self.current_san_label.set_text(str(character.currentSAN))

        self.flags = flags
        if isinstance(character, Human):
            self.character_image = self.character_status_sheet_builder.create_character_image(character, self.status_rect, flags)

    def draw(self):
        self.status_background_image.draw()
        self.current_hp_label.draw()
        self.current_san_label.draw()
        for label in self.status_labels:
            label.draw()

        self.skill_background_image.draw()
        for label in self.skill_labels:
            label.draw()