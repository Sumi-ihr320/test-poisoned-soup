import pygame
from pygame.locals import *

from constans import *
from utils import *
from ui_elements import *

# ステータス作るよ
class Status:
    MAX_STATUS_VALUE = 99

    def __init__(self, screen, root, name, status_name, label_name, status, x, y, w, h, text="", button_flag=True, input_flag=True, box_flag=True, dice_text=""):
        self.screen = screen
        self.root = root
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)

        self.name = name                # ステータスの名前
        self.status_name = status_name  # CharaStatusでの名前
        self.label_name = label_name if label_name != "" else self.name     # 実際に表示する名前（スペースなどで位置調整する場合があるため）
        self.text = text                # 説明文
        self.dice_text = dice_text      # ダイスボタンに表示するテキスト
        self.status_label = Label(self.screen, self.font, self.label_name, x, y)    # ラベル作成

        # ステータスの値
        self.status = status

        # 入力可能かのフラグ
        self.input_flag = input_flag
        self.input = None   # 初期化
        if box_flag:    # インプットボックスを作るかのフラグ
            self.create_input(x, y, w, h)

        self.button = None  # 初期化
        if button_flag: # ダイスボタンを作るかのフラグ
            self.create_dice_button()

    # インプットボックスを作成
    def create_input(self, x, y, w, h):
        # ステータスラベルの隣
        input_x = x + self.status_label.rect.w + 5
        input_y = y - 4     # ラベルより大きいので少し上に
        self.input = InputBox(self.screen, self.font, Rect(input_x, input_y, w, h), str(self.status), self.input_flag)

    # ダイスボタンを作成
    def create_dice_button(self):
        # インプットボックスがあればその位置、なければラベルの位置
        rect = self.input.rect.copy() if self.input else self.status_label.rect.copy()
        # その幅分隣
        rect.x = rect.x + rect.w + 5
        self.button = Button(self.screen, self.font, self.dice_text, rect, self.dice_process)

    def draw(self):
        self.status_label.draw()
        if self.input:
            self.input.draw_box()
        if self.button:
            self.button.draw()

    # 入力ボックスの最大値最小値を決めるよ
    def determine_input_range(self, edu):
        min, max = 0, self.MAX_STATUS_VALUE

        # 最大値最小値を決めるよ
        if self.status_name == "age":
            min = edu + 6

        elif self.dice_text:
            pieces, dice, plus_item = dice_confirmation(self.dice_text)
            min, max = pieces, dice * pieces
            if plus_item:
                num = int(self.dice_text[-1])
                if plus_item.group() == "+":
                    min += num
                    max += num
                else:
                    min -= num
                    max -= num
        return min, max
    
    # 入力ボックスの処理まとめるよ
    def input_process(self, edu):
        min, max = self.determine_input_range(edu)
        value_type = type(self.status)
        num = 2 if value_type == int else None

        # カスタムダイアログに入力された値を取得してラベルを更新する
        with TopmostManager(self.root):
            dialog = CustomDialog(self.root, self.name, f"あなたの{self.name}を入力してください", self.input.label_text, value_type, min, max, num)
            value = dialog.result

        if value is not None:
            if self.input:
                self.input.update_label(f"{value}")

    # ダイス処理まとめるよ
    def dice_process(self):
        dice = DiceRoll(self.dice_text)
        self.input.update_label(f"{dice.result}")

    def handle_mouse_hover(self, pos):
        if self.status_label.rect.collidepoint(pos):
            return self.text
        elif self.input and self.input.rect.collidepoint(pos):
            return self.text
        elif self.button and self.button.rect.collidepoint(pos):
            return "ダイスでランダムに値を決めることができます"
        return None

# 選んだ性別によって画像が変わるようにするよ
class SexChange:
    def __init__(self, screen, x, y, flag, image_x=40, image_y=40):
        self.screen = screen
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)

        # フラグをman, woman, neuterにする
        man_flag, woman_flag, neuter_flag = self.flag_check(flag)

        self.man = self.create_button("男", x, y, man_flag)
        self.woman = self.create_button("女", x+40, y, woman_flag)
        self.neuter = self.create_button("その他", x+80, y, neuter_flag)

        # 画像を作成
        self.image_x = image_x
        self.image_y = image_y
        self.man_image = self.create_image("man")
        self.woman_image = self.create_image("woman")
        self.neuter_image = self.create_image("neuter")

    # ボタン作るよ
    def create_button(self, text, x, y, flag):
        push_color = (106,93,33)
        no_push_color = SHEET_COLOR
        
        # 背景色と文字色をフラグによって変える
        background = push_color if flag else no_push_color
        color = WHITE if flag else BLACK
        return Label(self.screen, self.font, text, x, y, color=color, background=background)

    # 画像作るよ
    def create_image(self, flag):
        img_path = f"{PATH}{PICTURE}silhouette_{flag}.png"
        return Image(self.screen, img_path, 0.5, self.image_x, self.image_y, line_flag=True, line_width=2)

    # どれが選択されているかのフラグチェック
    def flag_check(self, flag):
        if flag == "man":
            man_flag = True
            woman_flag = False
            neuter_flag = False
        elif flag == "woman":
            man_flag = False
            woman_flag = True
            neuter_flag = False
        else:
            man_flag = False
            woman_flag = False
            neuter_flag = True
        
        return man_flag, woman_flag, neuter_flag

    # 性別が変わった時にボタンの状態を更新する
    def update_sex(self, flag):
        man_flag, woman_flag, neuter_flag = self.flag_check(flag)
        self.man = self.create_button("男", self.man.rect.x, self.man.rect.y, man_flag)
        self.woman = self.create_button("女", self.woman.rect.x, self.woman.rect.y, woman_flag)
        self.neuter = self.create_button("その他", self.neuter.rect.x, self.neuter.rect.y, neuter_flag)

    # 描画するよ
    def draw(self, flag):
        self.man.draw()
        self.woman.draw()
        self.neuter.draw()
        if flag == "man":
            self.man_image.draw()
        elif flag == "woman":
            self.woman_image.draw()
        else:
            self.neuter_image.draw()
