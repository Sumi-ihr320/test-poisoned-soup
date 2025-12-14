import pygame

from ui.ui_elements import Image

class VirtualCursor:
    def __init__(self, screen, img_path="cursor.png", spead=6):
        self.screen = screen
        self.pos = pygame.Vector2(screen.get_width() // 2, screen.get_height() // 2)

        self.spead = spead      # キー連打での移動量(ピクセル) or スナップ先移動
        self.snap_on_move = False    # 移動時に最寄り要素にスナップするか

        self.cursor_image = Image(self.screen, img_path, scale=0.1, x=self.pos.x, y=self.pos.y)

        self.hovered_element = None

        self.visible = False

    def update(self, event):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_UP]:
            move.y -= 1
        if keys[pygame.K_DOWN]:
            move.y += 1
        if keys[pygame.K_LEFT]:
            move.x -= 1
        if keys[pygame.K_RIGHT]:
            move.x += 1

        if move.length_squared() > 0:
            move = move.normalize() * self.spead
            self.pos += move
            self.cursor_image.set_position(self.pos.x, self.pos.y)

    # カーソル下にある要素を判定
    def check_hover(self, elements):
        hovered = None
        for el in elements:
            if el.collidepoint(self.pos):
                hovered = el
                break
        self.hovered_element = hovered
        return hovered

    # カーソル位置をセットする
    def set_pos(self, pos):
        self.pos = pygame.Vector2(pos[0], pos[1])
        self.cursor_image.set_position(self.pos.x, self.pos.y)

    # カーソル位置を取得する
    def get_pos(self):
        return self.cursor_image.rect.topleft()

    def draw(self):        
        if self.visible:
            self.cursor_image.draw()
