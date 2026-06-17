import pygame

from constans import FONT_PATH, SMALL_SIZ
from utils import get_new_size, get_scales
from ui.overlays.overlay_view import OverlayView, OverlayCloseButton
from ui.ui_elements import Image, Label
from models.characters import Player, Human
from core.game_state import Flags

class CharacterStatusView(OverlayView):
    def __init__(self, screen):
        super().__init__(screen)

        self.player = None
        self.girl = None
        self.flags = None

        self.create_close_button()

        self.font_data = (FONT_PATH, self.calculate_font_size())

        # キャラクターシートのサイズ
        self.sheet_size = self.calculate_sheet_size()

    # シートサイズの計算
    def calculate_sheet_size(self):
        sheet_size = (400, 300)
        return get_new_size(self.screen_size, sheet_size)

    # フォントサイズの計算    
    def calculate_font_size(self):
        _, _, aspect = get_scales(self.screen_size)
        font_size = int(SMALL_SIZ * aspect)
        return font_size

    # キャラクターシートのsurfaceを作成する
    def create_sheet_surface(self):
        sheet_surface = pygame.Surface(self.sheet_size)
        sheet_bg_img = Image(self.screen, path="old_paper.jpg", x="center", y="center", size_wh=self.sheet_size, parent=sheet_surface)
        return sheet_surface, sheet_bg_img
    
    def create_character_status(self, character: Player|Human):
        status_items = {}
        x, y = 10, 10
        margenx, margeny = 10, 10 
        startx = x
        title_y = y
        character_status_dict = self.set_status(character)
        for key, status in character_status_dict.items():
            lbl_title = self.create_label(text=status["text"], x=x, y=y)
            x += lbl_title.max_width
            title_y = y
            lbl_status = self.create_label(text=str(status["status"]), x=x, y=y)
            status_items[key] = {"title": lbl_title, "status": lbl_status}
            if status in ["name", "currentHP", "currentSAN", "STR", "DEX", "INT", "Idea", "DB"]:
                x = startx
                y += lbl_status.max_height + margeny
            else:
                x += lbl_status.max_width + margenx
                y = title_y
        return status_items

    def create_label(self, text, x, y):
        label = Label(self.screen, font_data=self.font_data, text=text, x=x, y=y)
        return label

    def set_status(self, character: Player|Human):
        sex_map = {"man": "男", "woman": "女", "neuter": "その他"}
        status_map = {
            "name":{"text": "名前： ", "status": character.name},
            "age": {"text": "年齢： ", "status": character.age},
            "sex": {"text": "性別： ", "status": sex_map[character.sex]},
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

    # キャラクターシートたちを構成する
    def build_character_sheets(self):
        pass

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

    def relayout(self, screen):
        super().relayout(screen, parent=None)

        self.sheet_size = self.calculate_sheet_size()

        for c in self.children:
            c.relayout(screen, parent=None)
