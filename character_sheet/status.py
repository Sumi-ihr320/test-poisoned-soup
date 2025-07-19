from pygame.locals import *

from constans import *
from utils import *
from ui.ui_elements import *

# ステータス作るよ
class Status:
    MAX_STATUS_VALUE = 99

    def __init__(self, screen, root, percentage, font, name, status_name, label_name, status, x, y, w, h, text="", button_flag=True, input_flag=True, box_flag=True, dice_text=""):
        self.screen = screen
        self.root = root

        self.font = font
        self.percentage = percentage

        self.name = name                # ステータスの名前
        self.status_name = status_name  # CharaStatusでの名前
        self.label_name = label_name if label_name != "" else self.name     # 実際に表示する名前（スペースなどで位置調整する場合があるため）
        self.text = text                # 説明文
        self.dice_text = dice_text      # ダイスボタンに表示するテキスト

        self.create_label(x, y)

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

    # ラベル作成
    def create_label(self, x, y):
        self.status_label = Label(self.screen, self.font, self.label_name, x, y)    # ラベル作成

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
    def __init__(self, screen, sheet_rect, percentage, font, title_text, x, y, flag):
        self.screen = screen
        self.sheet_rect = sheet_rect
        self.font = font

        self.percentage = percentage

        self.title_text = title_text
        self.title_x, self.title_y = x, y
        self.flag = flag

        # 性別ボタン配置
        self.button_placement()

        # 画像を作成
        self.man_image = self.create_image("man")
        self.woman_image = self.create_image("woman")
        self.neuter_image = self.create_image("neuter")

    # 性別ボタンの配置
    def button_placement(self):
        # フラグをman, woman, neuterにする
        man_flag, woman_flag, neuter_flag = self.flag_check(self.flag)

        # 性別欄のテキストの位置
        text_width = self.font.size(self.title_text)[0]
        start_width = self.font.size(self.title_text[:3])[0]
        end_width = self.font.size(self.title_text[-1])[0]

        # 配置したいスペースの幅
        text_max_size = text_width - (start_width + end_width)

        # 各ラベルの幅
        man_width = self.font.size("男")[0]
        woman_width = self.font.size("女")[0]
        neuter_width = self.font.size("その他")[0]

        # ボタンの全幅
        total_button_width = man_width + woman_width + neuter_width

        # ボタン間空間の計算
        spacing = (text_max_size - total_button_width) // 4

        # 最初のボタンの表示位置
        text_x = self.title_x + start_width + spacing
        self.man = self.create_button("男", text_x, self.title_y, man_flag)

        text_x += man_width + spacing
        self.woman = self.create_button("女", text_x, self.title_y, woman_flag)

        text_x += woman_width + spacing
        self.neuter = self.create_button("その他", text_x, self.title_y, neuter_flag)

    # ボタン作るよ
    def create_button(self, text, x, y, flag):
        push_color = (106,93,33)
        no_push_color = None
        
        # 背景色と文字色をフラグによって変える
        background = push_color if flag else no_push_color
        color = WHITE if flag else BLACK
        return Label(self.screen, self.font, text, x, y, color=color, background=background)

    # 画像作るよ
    def create_image(self, flag):
        w_percent, h_percent = self.percentage
        image_x = (self.sheet_rect.x + 10) * w_percent
        image_y = (self.sheet_rect.y + 10) * h_percent
        img_siz = 0.5 * h_percent

        img_path = f"silhouette_{flag}.png"
        
        return Image(self.screen, img_path, img_siz, image_x, image_y, line_flag=True, bg_flag=True, line_width=2)

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
        self.flag = flag
        self.button_placement()

    # 描画するよ
    def draw(self):
        self.man.draw()
        self.woman.draw()
        self.neuter.draw()
        if self.flag == "man":
            self.man_image.draw()
        elif self.flag == "woman":
            self.woman_image.draw()
        else:
            self.neuter_image.draw()
