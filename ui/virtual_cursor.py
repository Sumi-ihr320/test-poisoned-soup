import pygame
from utils import *
from ui.ui_elements import *

class VirtualCursor:
    def __init__(self, screen):
        self.screen = screen
        self.screen_rect = self.screen.get_rect()

        self.image = Image(self.screen, "cursor.png", 0.1)
        self.rect = self.image.rect

        self.rect.center = self.screen_rect.center
        self.speed = 1
        self.visible = True     # モード切替用

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.rect.clamp_ip(self.screen_rect)

    def draw(self):
        if self.visible:
            self.image.draw()

    def get_pos(self):
        return self.rect.topleft
    
    def set_pos(self, pos):
        self.rect.topleft = pos
        

# カーソル移動
def handle_cursor_move(use_cursor, cursor):
    keys = pygame.key.get_pressed()
    if use_cursor:
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        cursor.move(dx, dy)

# キーボードモードオン
def on_keybord(cursor):
    # ボタンを押すことでキーボードモードに変更
    cursor.set_pos(pygame.mouse.get_pos())
    pygame.mouse.set_visible(False)
    return True

# キーボードモードオフ
def off_keybord(cursor):
    # マウスを動かしたらキーボードモード終了
    pygame.mouse.set_pos(cursor.get_pos())
    pygame.mouse.set_visible(True)
    return False
