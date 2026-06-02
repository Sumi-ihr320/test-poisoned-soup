import pygame

from constans import FONT_PATH, SMALL_SIZ, BLACK, WHITE, ROOM_NAME
from utils import get_new_size, get_scales
from ui.ui_cache import ImageCache
from ui.ui_elements import Image, Label
from models.characters import Player, Human
from core.game_state import GameStatus, Flags

# 主人公の名前・HP・MPを左上、現在地を右上に表示する
class PlayerDataView:
    def __init__(self, screen, room_surface_rect, player: Player, girl: Human, game_state: GameStatus, flags: Flags):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.room_surface_rect = room_surface_rect

        self.font_data = (FONT_PATH, SMALL_SIZ)

        self.player = player
        self.room_flag = game_state.room
        self.time = str(game_state.time)     # デバッグ用

        self.girl = girl
        self.girl_fellow = flags.get_flag("girl", "fellow")
        self.girl_alive = flags.get_flag("girl", "alive")

        self.cache = ImageCache()

        self.lbl_player_currenthp = None
        self.lbl_girl_currenthp = None
        self.lbl_current_room = None
        self.lbl_current_time = None    # デバッグ用

        self.calculate_surface_size()
        self.create_surface()

        self.build_images()

        self.build_labels()

    # surfaceのサイズを割り出す
    def calculate_surface_size(self):
        #self.size = (300, 100)
        if self.girl_fellow or not self.girl_alive:
            width = 500
        else:
            width = 250
        height = 150
        self.size = (width, height)

        self.size = get_new_size(self.screen_size, self.size)

    # surfaceを作成する
    def create_surface(self):
        self.bg_surface = pygame.Surface(self.size)
        self.rect = self.bg_surface.get_rect()

        self.bg_surface.fill(BLACK)
        self.bg_surface.set_alpha(100)

    # imageを作成する
    def build_images(self):
        self.player_img = self.create_image(path=self.player.image, x=self.rect.x+10, y=self.rect.y+10)
        self.player_img.cat_image(pygame.Rect(100, 50, 200, 300))

        self.build_girl_image()

    def build_girl_image(self):
        if not self.girl_alive:
            girl_img = "Girl_pale_downcast_eyes_dark.png"
        else:
            girl_img = self.girl.image
        self.girl_img = self.create_image(path=girl_img, x=0, y=0)
        self.girl_img.cat_image(pygame.Rect(50, 0, 200, 300))

        #self.girl_img.set_rect(x=self.player_img.rect.x+self.player_img.rect.w+100, y=self.player_img.rect.y, centerx=None, centery=None)

    def create_image(self, path, x, y):
        _, _, aspect_scale = get_scales(self.screen_size)
        size = 0.4 * aspect_scale
        image = Image(screen=self.screen, path=path, cache=self.cache, scale=size, x=x, y=y, line_flag=True, bg_flag=True)
        return image

    def build_labels(self):
        self.status_labels = []
        
        self.lbl_player_currenthp, player_labels = self.create_character_labels(self.player, self.player_img)
        self.lbl_girl_currenthp, girl_labels = self.create_character_labels(self.girl, self.girl_img)

        self.lbl_current_room = self.create_label(ROOM_NAME[self.room_flag], x=self.room_surface_rect.right, y=self.room_surface_rect.y - 30, anchor=("right", "top"))
        self.lbl_current_time = self.create_label(self.time, x=self.lbl_current_room.rect.x - 10, y=self.lbl_current_room.rect.y, anchor=("right", "top"))

        self.status_labels = player_labels
        if self.girl_fellow or not self.girl_alive:
            self.status_labels += girl_labels
        self.status_labels += [self.lbl_current_room, self.lbl_current_time]

    def create_character_labels(self, character: Player|Human, character_img):
        margin = 5

        lbl_name = self.create_label(character.name, x=character_img.rect.x + character_img.rect.w + 10, y=character_img.rect.y + margin)

        lbl_hp = self.create_label("HP： ", x=lbl_name.rect.x, y=lbl_name.rect.y + lbl_name.rect.h + margin)
        lbl_currenthp = self.create_label(f"{character.currentHP}", x=lbl_hp.rect.right, y=lbl_hp.rect.y)
        lbl_slash = self.create_label(" / ", x=lbl_currenthp.rect.right, y=lbl_hp.rect.y)
        lbl_maxhp = self.create_label(f"{character.maxHP}", x=lbl_slash.rect.right, y=lbl_hp.rect.y)

        # もし表示の方がsurfaceのrect.widthより幅が広かった場合、rect.widthを調整する
        width = max(lbl_name.rect.right + 10 - self.rect.left, lbl_maxhp.rect.right + 10 - self.rect.left, self.size[0])
        if width > self.size[0]:
            self.size = (width, self.size[1])
            self.create_surface()

        lbl_list = [lbl_name, lbl_hp, lbl_currenthp, lbl_slash, lbl_maxhp]
        return lbl_currenthp, lbl_list
    
    def create_label(self, text, x, y, anchor=("left", "top")):
        label = Label(self.screen, font_data=self.font_data, text=text, x=x, y=y, text_color=WHITE, anchor=anchor)
        return label

    # ゲームの状態が変わった時にラベルの表示を更新する
    def update_texts(self):
        self.lbl_player_currenthp.set_text(f"{self.player.currentHP}")
        self.lbl_girl_currenthp.set_text(f"{self.girl.currentHP}")
        self.lbl_current_room.set_text(ROOM_NAME[self.room_flag])
        self.lbl_current_time.set_text(self.time)

    def update(self, player: Player, girl: Human, game_state: GameStatus, flags: Flags):
        self.player = player
        self.girl = girl
        self.room_flag = game_state.room
        self.time = str(game_state.time)     # 時間表示：デバッグ用

        # 少女の生死によって表示を変更する
        new_girl_alive = flags.get_flag("girl", "alive")
        if self.girl_alive != new_girl_alive:
            self.build_girl_image()
        self.girl_alive = new_girl_alive

        # 少女のフォローの可否によって表示を変更する
        new_girl_fellow = flags.get_flag("girl", "fellow")
        if self.girl_fellow != new_girl_fellow:
            self.calculate_surface_size()
            self.create_surface()
            self.build_labels()
        self.girl_fellow = new_girl_fellow
        
        self.update_texts()

    def draw(self):
        self.screen.blit(self.bg_surface, self.rect.topleft)

        if self.player_img:
            self.player_img.draw()
        if self.girl_img and (self.girl_fellow or not self.girl_alive):
            self.girl_img.draw()

        for label in self.status_labels:
            label.draw()

