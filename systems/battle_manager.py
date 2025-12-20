from ui.ui_elements import *

class BattleManager:
    def __init__(self, screen, player, enemy, room_background, room_rect, girl=None):
        self.screen = screen
        self.window_size = self.screen.get_size()
        self.player = player
        self.girl = girl
        self.enemy = enemy
        self.background = room_background
        self.room_rect = room_rect

        self.set_font()

        self.result = None

    def set_font(self):
        self.font = setting_font(FONT_PATH, FONT_SIZ, self.window_size)
        self.small_font = setting_font(FONT_PATH, SMALL_SIZ, self.window_size)

    def create_window(self):
        if self.girl:
            width = 400
        else:
            width = 200
        height = 100
        
    def create_image(self):
        #self.background_img = Image()
        self.enemy_img = Image(self.screen, self.enemy.image, 0.5, "center", "center")
        self.player_img = Image(self.screen, self.player.image, 0.3)
        if self.girl:
            self.girl_img = Image(self.screen, self.girl.image, 0.3)

    def create_label(self):
        player_name = Label(self.screen, self.small_font, self.player.name)
        player_hp = Label(self.screen, self.small_font, self.player.HP)
        player_mp = Label(self.screen, self.small_font, self.player.MP)
        self.player_label = [player_name, player_hp, player_mp]
        if self.girl:
            girl_name = Label(self.screen, self.small_font, self.girl.name)
            girl_hp = Label(self.screen, self.small_font, self.girl.HP)
            girl_mp = Label(self.screen, self.small_font, self.girl.MP)
            self.girl_label = [girl_name, girl_hp, girl_mp]

    def create_button(self):
        command_list = ["攻撃", "防御", "技能", "アイテム", "逃げる"]

    def update(self):
        pass

    def draw(self):
        #self.screen.blit(self.background, self.room_rect)
        if self.player_label:
            for label in self.player_label:
                label.draw()
            
        if self.girl_label:
            for label in self.girl_label:
                label.draw()

    def handle_click(self):
        pass

    def is_finished(self):
        return self.result is not None
