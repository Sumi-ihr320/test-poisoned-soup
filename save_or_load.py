import os, json
import datetime as dt
from enum import Enum

import pygame
import pygame.draw
from pygame.locals import *

from data import *
from fanction_summary import *
from class_summary import *

class SaveLoadState(Enum):
    NONE = 0
    SAVE = 1
    LOAD = 2
    CLOSE = 3

# データロード
class Save_or_Load:
    def __init__(self, screen, save_load_flag, return_flag, save_data=None):
        self.screen = screen
        # フォントの設定
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)                    # 基本フォント
        self.contents_font = pygame.font.Font(FONT_PATH,CONTENTS_SIZ)        # メニュー用フォント

        self.save_load_flag = save_load_flag    # save か load か
        self.return_flag = return_flag          # どこに戻るかのフラグ

        self.state = SaveLoadState.NONE         # 閉じるフラグや完了フラグ等の状態管理フラグ

        self.save_data = save_data              # 保存するデータ
        self.load_data = None                   # ロードするデータ

        self.forder_name = f"{PATH}{SAVE_FOLDER}"   # セーブフォルダ

        # 選択したデータ
        self.select_file_name = None

        # セーブデータリスト
        self.save_data_list = []
        self.load_save_data()
        self.data_lbl_list = []
        self.create_save_data_list()

        # 画面作成
        self.top = None     # セーブ or ロード
        self.enter = None   # 決定
        self.delete = None  # 削除
        self.close = None   # 閉じる
        self.button_list = []
        self.create_label()

    # データ表示ボックスを表示
    def create_window(self):
        w = 600
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
        self.enter = Label(self.screen, self.contents_font, enter_text, 200, 500)
        self.delete_label = Label(self.screen, self.contents_font, "削除", y=500, centerx=WINDOW_CENTER_X)
        self.close = Label(self.screen, self.contents_font, "閉じる", 520, 500)
        self.button_list = [self.enter, self.delete_label, self.close]

    # セーブデータ一覧を探してくる
    def load_save_data(self):
        # セーブフォルダが無ければ作る
        if not os.path.isdir(self.forder_name):
            os.makedirs(self.forder_name)

        # フォルダ内にあるデータ一覧を持ってくる
        self.save_data_list = os.listdir(self.forder_name)

    # セーブデータ一覧を表示する
    def create_save_data_list(self):
        x = (self.screen.get_width() // 2) - 200
        start_y = 150
        y = start_y
        if self.save_data_list:
            for data in self.save_data_list:
                data_name = data.replace(".json", "")
                self.data_lbl_list.append(Label(self.screen, self.font, data_name, x, y))
                y += 30

    def data_delete(self):
        if self.select_file_name is None:
            messagebox.showerror("エラー", "データが選択されていません")
        else:
            if messagebox.askokcancel("削除", f"{self.select_file_name}\n本当に削除してよろしいですか？"):
                file_name = f"{self.forder_name}{self.select_file_name}"
                try:
                    # ファイルの中身を空にする
                    with open(file_name, "w", encoding="utf-8_sig") as f:
                        pass
                except Exception as e:
                    print(f"データエラー: {e}")

                # 新しいファイル名に変更する
                file_no = self.select_file_name.split(" ")[0]
                new_file_name = f"{self.forder_name}{file_no}.json"
                os.rename(file_name, new_file_name)
                self.draw()
                messagebox.showinfo("削除", "削除が完了しました")

    # データセーブ
    def save(self):
        file_name = self.create_file_name()
        try:
            with open(file_name, "w", encoding="utf-8_sig") as f:
                json.dump(self.save_data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("セーブ", "セーブが完了しました")
            self.state = SaveLoadState.SAVE            
        except Exception as e:
            print(f"セーブエラー: {e}")
            messagebox.showerror("セーブエラー", "セーブに失敗しました")

    # データロード
    def load(self):
        if len(self.select_file_name.replace(".json", "")) == 2:
            messagebox.showerror("ロードエラー", "データがありません")
        else:
            file_name = f"{self.forder_name}{self.select_file_name}"
            try:
                self.load_data = load_json(file_name)
                messagebox.showinfo("ロード", "ロードに成功しました")
                self.state = SaveLoadState.LOAD
            except FileNotFoundError:
                messagebox.showerror("ロードエラー", "ファイルが見つかりません")
            except json.JSONDecodeError:
                messagebox.showerror("ロードエラー", "ファイル形式が正しくありません")
            except Exception as e:
                print(f"ロードエラー: {e}")
                messagebox.showerror("ロードエラー", f"ロードに失敗しました: {str(e)}")

    # ファイル名を作る
    def create_file_name(self):
        # 今日の日付と時間を取得
        now = dt.datetime.now()
        str_now = now.strftime("%Y-%m-%d_%H-%M-%S")

        # 選択された場所に保存する
        # セーブデータのインデックスを切り出す
        if self.select_file_name:
            try:
                data_no = self.select_file_name.split(" ")[0]
            except IndexError:
                data_no = "00"
        else:
            # 新規セーブの場合
            data_no = str(len(self.save_data_list)).zfill(2)

        # キャラクター名と場所
        name = self.save_data.get("hero_status", {}).get("name", "Unknown")
        room_direction = self.save_data.get("flag", {}).get("room_flag", None)
        if room_direction:
            room_name = ROOM_NAME[room_direction]
        else:
            room_name = ""

        # キャラクター名、プレイ中なら現在地、日時でファイル名を作る
        return f"{self.forder_name}{data_no} {name} {room_name} {str_now}.json"

    # 画面を描画
    def draw(self):
        self.create_window()
        if self.top:
            self.top.draw()
        if self.button_list:
            for item in self.button_list:
                item.draw()
        if self.data_lbl_list:
            for label, save_data in zip(self.data_lbl_list, self.save_data_list):
                if save_data == self.select_file_name:
                    label.set_background_color(WHITE)
                else:
                    label.set_background_color(None)
                label.draw()

    # マウスオーバーで枠を表示するよ
    def handle_mouse_hover(self):
        pos = pygame.mouse.get_pos()
        for item in self.button_list:
            if item.rect.collidepoint(pos):
                pygame.draw.rect(self.screen, BLACK, item.rect, 1)

    def handle_event(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT:
                Close()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                Close()
            # マウスクリック時
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.handle_ckick(event)

    def handle_ckick(self, event):
        # 閉じるボタン
        if self.close.rect.collidepoint(event.pos):
            self.state = SaveLoadState.CLOSE

        # 決定ボタン
        elif self.enter.rect.collidepoint(event.pos):
            if self.save_load_flag == "save":
                self.save()                
            else:
                self.load()

        # 削除ボタン
        elif self.delete_label.rect.collidepoint(event.pos):
            self.data_delete()

        # データ一覧の選択
        for label, save_data in zip(self.data_lbl_list, self.save_data_list):
            if label.rect.collidepoint(event.pos):
                self.select_file_name = save_data
                print(self.select_file_name)

    def update(self):
        self.draw()
        self.handle_mouse_hover()
        self.handle_event()
        return self.next_state()
                            
    def next_state(self):
        if self.state == SaveLoadState.CLOSE:
            if self.return_flag == "title":
                return "title", None
            elif self.return_flag == "play":
                return "play", self.save_data
        elif self.state == SaveLoadState.SAVE:
            return "play", self.save_data
        elif self.state == SaveLoadState.LOAD:
            return "play", self.load_data
        else:
            if self.save_load_flag == "save":
                return "save", self.save_data
            else:
                return "load", self.save_data

