import pygame

from constans import FONT_PATH, SMALL_SIZ, BLACK, WHITE, ROOM_NAME
from utils import setting_font, get_new_size, get_scales
from ui.ui_elements import Image, Label

# 主人公の名前・HP・MPを左上、現在地を右上に表示する
class PlayerDataView:
    def __init__(self, screen, room_surface_rect, player, girl, game_state, flags):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.room_surface_rect = room_surface_rect

        self.font_data = (FONT_PATH, SMALL_SIZ)
        self.font = setting_font(FONT_PATH, SMALL_SIZ, self.screen_size)

        self.player = player
        self.room_flag = game_state.room
        self.time = str(game_state.time)     # デバッグ用

        self.girl = girl
        self.girl_fellow = flags.get_flag("girl", "fellow")
        self.girl_alive = flags.get_flag("girl", "girl_alive")

        self.create_surface()

        self.create_image()

        self.status_labels = None
        self.setting_labels()

    # surfaceを作成する
    def create_surface(self):
        #self.size = (300, 100)
        if self.girl_fellow and not self.girl_alive:
            width = 400
        else:
            width = 200
        height = 150
        self.size = (width, height)

        self.size = get_new_size(self.screen_size, self.size)
        self.bg_surface = pygame.Surface(self.size)
        self.rect = self.bg_surface.get_rect()

        self.bg_surface.fill(BLACK)
        self.bg_surface.set_alpha(100)

    # imageを作成する
    def create_image(self):
        _, _, aspect_scale = get_scales(self.screen_size)
        size = 0.4 * aspect_scale

        self.player_img = Image(screen=self.screen, path=self.player.image, scale=size, x=self.rect.x+10, y=self.rect.y+10, line_flag=True, bg_flag=True)
        self.player_img.cat_image(pygame.Rect(100, 50, 200, 300))

        if not self.girl_alive:
            girl_img = "Girl_pale_downcast_eyes_dark.png"
        else:
            girl_img = self.girl.image
        self.girl_img = Image(screen=self.screen, path=girl_img, scale=size, x=0, y=0, line_flag=True, bg_flag=True)
        self.girl_img.cat_image(pygame.Rect(50, 0, 200, 300))

        #self.girl_img.set_rect(x=self.player_img.rect.x+self.player_img.rect.w+100, y=self.player_img.rect.y, centerx=None, centery=None)

    def setting_labels(self):
        player_labels = self.create_label(self.player, self.player_img)
        girl_labels = self.create_label(self.girl, self.girl_img)

        current_room_label = Label(self.screen, font_data=self.font_data, text=ROOM_NAME[self.room_flag], x=self.room_surface_rect.right, y=self.room_surface_rect.y - 30, anchor=("right", "top"), text_color=WHITE)
        current_time_label = Label(self.screen, font_data=self.font_data, text=self.time, x=current_room_label.rect.x - 10, y=current_room_label.rect.y, anchor=("right", "top"), text_color=WHITE)   # デバッグ用

        self.status_labels = player_labels
        if self.girl_fellow or not self.girl_alive:
            self.status_labels += girl_labels
        self.status_labels += [current_room_label, current_time_label]

    def create_label(self, character, character_img):
        margin = 5
        name_label = Label(self.screen, font_data=self.font_data, text=character.name, x=character_img.rect.x + character_img.rect.w + 10, y=character_img.rect.y + margin, text_color=WHITE)
        hp_label = Label(self.screen, font_data=self.font_data, text=f"HP/{character.HP}", x=name_label.rect.x, y=name_label.rect.y + name_label.rect.h + margin, text_color=WHITE)
        mp_label = Label(self.screen, font_data=self.font_data, text=f"MP/{character.MP}", x=name_label.rect.x, y=hp_label.rect.y + hp_label.rect.h + margin, text_color=WHITE)
        return [name_label, hp_label, mp_label]

    def draw(self):
        self.screen.blit(self.bg_surface, self.rect.topleft)

        if self.player_img:
            self.player_img.draw()
        if self.girl_img and self.girl_fellow:
            self.girl_img.draw()

        for label in self.status_labels:
            label.draw()

    def update(self, player, girl, game_state, flags):
        self.player = player
        self.girl = girl
        self.room_flag = game_state.room
        self.time = str(game_state.time)     # 時間表示：デバッグ用

        # 少女の生死によって表示を変更する
        new_girl_alive = flags.get_flag("girl", "alive")
        if self.girl_alive != new_girl_alive:
            self.create_image()
        self.girl_alive = new_girl_alive

        # 少女のフォローの可否によって表示を変更する
        new_girl_fellow = flags.get_flag("girl", "fellow")
        if self.girl_fellow != new_girl_fellow:
            self.create_surface()
        self.girl_fellow = new_girl_fellow

        
        self.status_labels = None
        self.setting_labels()
        self.draw()
