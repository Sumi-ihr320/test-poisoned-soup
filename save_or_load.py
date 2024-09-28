import pygame
import pygame.draw
from pygame.locals import *

from data import *
from fanction_summary import *
from class_summary import *

# データロード
class Save_or_Load:
    def __init__(self, screen, save_load_flag, return_flag):
        self.screen = screen
        # フォントの設定
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)                    # 基本フォント
        self.contents_font = pygame.font.Font(FONT_PATH,CONTENTS_SIZ)        # メニュー用フォント

        self.save_load_flag = save_load_flag    # save か load か
        self.return_flag = return_flag          # どこに戻るかのフラグ
        self.close_flag = False                 # 画面終了フラグ
        self.enter_flag = False                 # 完了フラグ

        # セーブデータリスト
        self.save_data_list = []
        self.load_data()

        # 選択したデータ
        self.select_data = None

        # 画面作成
        self.top = None     # セーブ or ロード
        self.enter = None   # 決定
        self.close = None   # 閉じる
        self.button_list = []
        self.create_label()

    # データ表示ボックスを表示
    def create_window(self):
        w = 400
        h = 500
        x = (self.screen.get_width() / 2) - (w / 2)
        y = (self.screen.get_height() / 2) - (h / 2)
        self.window_rect = Rect(x,y,w,h)
        pygame.draw.rect(self.screen, SHEET_COLOR, self.window_rect)
        pygame.draw.rect(self.screen, BLACK,self. window_rect,2)

   # ラベルの作成
    def create_label(self):
        if self.save_load_flag == "save":
            top_text = "セーブ"
            enter_text = "保存"
        else:
            top_text = "ロード"
            enter_text = "開始"

        self.top = Label(self.screen, self.contents_font, top_text, y=80, centerx=WINDOW_CENTER_X)
        self.enter = Label(self.screen, self.contents_font, enter_text, 250, 500)
        self.close = Label(self.screen, self.contents_font, "CLOSE", 480, 500)
        self.button_list = [self.enter,self.close]

    # セーブデータ一覧を探してくる
    def load_data(self):
        # セーブフォルダが無ければ作る
        dir_name = f"{PATH}{SAVE_FOLDER}"
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)

        # フォルダ内にあるデータ一覧を持ってくる
        self.save_data_list = os.listdir(dir_name)

    # セーブデータ一覧を表示する
    def create_save_data_list(self):
        x = (self.screen.get_width() // 2) - 150
        start_y = 150
        y = start_y
        self.data_lbl_list = []
        for data in self.save_data_list:
            if self.select_data == data:
                color = WHITE
            else:
                color = None
            data_name = data.replace(".json", "")
            self.data_lbl_list.append(Label(self.screen, self.font, data_name, x, y, background=color))
            y += 30

    # 画面を描画
    def draw(self):
        self.create_window()
        if self.top:
            self.top.draw()
        if self.button_list:
            for item in self.button_list:
                item.draw()

    # マウスオーバーで枠を表示するよ
    def handle_mouse_hover(self):
        pos = pygame.mouse.get_pos()
        for item in self.button_list:
            if item.rect.collidepoint(pos):
                pygame.draw.rect(self.screen, BLACK, item.rect, 1)

    def handle_ckick(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT:
                Close()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                Close()
            # マウスクリック時
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.window.close.rect.collidepoint(event.pos):
                    self.close_flag = True
                elif self.window.enter.rect.collidepoint(event.pos):
                    pass

                for i in range(len(self.window.data_rect_list)):
                    if self.window.data_rect_list[i].collidepoint(event.pos):
                        SelectSaveData = self.save_files[i]
                        print(SelectSaveData)

    def update(self):
        if self.window:
            self.draw()
            self.handle_mouse_hover()
            self.handle_ckick()
        return self.next_state()
                            
    def next_state(self):
        if self.close_flag:
            if self.return_flag == "title":
                return "title"
            elif self.return_flag == "play":
                return "play"
        if self.enter_flag:
            return "play"
        return "load"

