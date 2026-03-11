import datetime as dt
from typing import Any

import pygame
from pygame.locals import *
from tkinter import messagebox

from constans import *
from utils import get_new_size, Close, TopmostManager
from ui.ui_elements import Label
from input.focus_manager import FocusManager
from base_scene import BaseScene
from save_data.save_data_manager import SaveDataManager

# セーブロード
class SaveDataScene(BaseScene):
    def __init__(self, screen, root, save_load_flag, befor_event, save_data, setting_manager=None):
        super().__init__(screen, root)

        # フォントの設定
        self.set_font_data()

        self.save_load_flag = save_load_flag    # save か load か
        self.befor_event = befor_event          # 来る前にしてたイベント

        self.save_data = save_data              # 保存するデータ
        self.load_data = None                   # ロードするデータ
        self.setting_manager = setting_manager  # 保存するための設定ファイル

        # セーブデータマネージャー
        self.save_data_manager = SaveDataManager()

        # フォーカスマネージャー
        self.focus_manager = FocusManager(self.screen)

        # セーブロード用ウィンドウサイズ
        self.window_size = (600, 500)
        self.setting_window_rect()

        # 選択したデータ
        self.select_file_name = None

        # セーブデータリスト
        self.fetch_and_validate_save_data_list()

        # セーブデータのファイルとラベルのリスト
        self.data_label_list = []   # セーブデータファイルとラベルのリスト
        self.refresh_label_list()

        # 画面作成
        self.top = None     # セーブ or ロード
        self.enter = None   # 決定
        self.delete = None  # 削除
        self.close = None   # 閉じる
        self.button_list = []
        self.label_list = []
        self.create_labels()

        # フォーカス登録
        self.all_register_focusable()

    # フォントの設定
    def set_font_data(self):
        self.font_data = (FONT_PATH, FONT_SIZ)
        self.contents_font_data = (FONT_PATH, CONTENTS_SIZ)

    # ウィンドウのrect設定
    def setting_window_rect(self):
        w, h = get_new_size(self.screen_size, self.window_size)
        x = (self.screen.get_width() // 2) - (w // 2)
        y = (self.screen.get_height() // 2) - (h // 2)
        self.window_rect = Rect(x,y,w,h)

   # ラベルの作成
    def create_labels(self):
        if self.save_load_flag == "save":
            top_text = enter_text = "セーブ"
        else:
            top_text = enter_text = "ロード"

        self.top = Label(screen=self.screen, font_data=self.contents_font_data, text=top_text, 
                         y=self.window_rect.top+30, centerx=self.window_rect.centerx)
        self.enter = self.create_button_label(enter_text, centerx=self.window_rect.centerx-150, col=0)
        self.delete = self.create_button_label("削除", centerx=self.window_rect.centerx, col=1)
        self.close = self.create_button_label("閉じる", centerx=self.window_rect.centerx+150, col=2)
        self.label_list = [self.top] + self.button_list

    # ボタン用ラベルを作成しラベルを返す
    def create_button_label(self, text: str, centerx: int, col: int) -> Label:
        label = Label(screen=self.screen, font_data=self.contents_font_data, text=text, 
                      y=self.window_rect.bottom-50, centerx=centerx,
                      hover_type="line", hover_back_color=BLACK,
                      sound_type="select", focusable=True, row=20, col=col)
        self.button_list.append(label)
        return label
    
    # セーブデータ一覧ラベルを作成する
    def create_save_data_label_list(self):
        if self.save_data_list:
            label_list = []
            for i, data in enumerate(self.save_data_list):
                data_number = self.save_data_manager.extract_file_number(data)
                data_name = data.replace(".json", "")
                label = Label(screen=self.screen, font_data=self.font_data, text=data_name,
                              hover_back_color=BLUE,
                              focusable=True, row=i, col=0)
                item = {"number": data_number, "file":data, "label":label}
                label_list.append(item)
        label_list.sort(key=lambda x: x["number"])
        self.data_label_list = label_list

    # セーブデータ一覧のrectを設定する
    def set_save_data_rect(self):
        x = self.window_rect.centerx - 250
        start_y = self.window_rect.top + 100
        y = start_y
        w = 500
        if self.data_label_list:
            for data in self.data_label_list:
                data["label"].x = x
                data["label"].y = y
                data["label"].rect.w = w
                data["label"].click_rect = Rect(x, y, w, data["label"].max_height)
                y += 30

    # データセーブ
    def save(self):
        # 1. セーブする場所が選択されているかチェック
        result = self.validate_selection()
        if not result["success"]:
            self.show_error(result["error"], "セーブ")
            return
        
        # 2. すでにデータがあった場合は上書き確認
        if self.check_existing_file():
            if not self.ask_confirmation(f"{self.select_file_name}\nセーブデータを上書きしますか？"):
                return

        # 3. 設定データをセーブしておく
        self.setting_manager.save_settings()

        # 4. 新しいファイル名に変更する
        new_file_name = self.create_filename()

        # データを書き込む
        result = self.save_data_manager.save_file(new_file_name, self.save_data)
        if result["success"]:
            self.show_info("セーブが完了しました", "セーブ")
            # 古いファイルを削除
            result = self.save_data_manager.remove_file(self.select_file_name)
            if not result["success"]:
                self.show_error(f"古いセーブデータの削除に失敗しました:\n {result['error']}", "セーブ")
            self.state = State.SAVE
        else:
            self.show_error(f"セーブに失敗しました:\n {result['error']}", "セーブ")

    # データロード
    def load(self):
        # データが選択されているかをチェック
        result = self.validate_selection()
        if not result["success"]:
            self.show_error(result["error"], "ロード")
            return
        
        # データが存在するかをチェック
        if not self.check_existing_file():
            self.show_error("データが存在しません", "ロード")
            return
        
        # データを読み込む
        result = self.save_data_manager.load_file(self.select_file_name)
        if result["success"]:
            self.load_data = result["data"]
            self.show_info("ロードに成功しました", "ロード")
            self.state = State.LOAD
        else:
            self.show_error(f"ロードに失敗しました:\n {result['error']}", "ロード")

    # データ削除
    def delete_data(self):
        # データが選択されているかをチェック
        result = self.validate_selection()
        if not result["success"]:
            self.show_error(result["error"], "削除")
            return
        
        # データが存在しているかをチェック
        if not self.check_existing_file():
            self.show_error("データが存在しません", "削除")
            return
        
        # 本当に削除するかを確認
        if not self.ask_confirmation(f"{self.select_file_name}\n本当に削除してよろしいですか？", "削除"):
            return

        # データを削除する        
        result = self.save_data_manager.delete_file(self.select_file_name)
        if result["success"]:
            self.show_info("削除が完了しました", "削除")
            self.fetch_and_validate_save_data_list()
            self.refresh_label_list()
            self.draw()
        else:
            self.show_error(f"削除に失敗しました:\n {result['error']}", "削除")

    # 選択された箇所にデータがあるかないかを確認する
    def check_existing_file(self):
        if len(self.select_file_name.replace(".json", "")) == 2:
            return False
        return True

    # データが選択されているかのチェックとエラーメッセージ
    def validate_selection(self):
        if self.select_file_name is None:
            return {"success": False, "error": "データが選択されていません"}
        return {"success": True}

    # エラーメッセージを表示する
    def show_error(self, message: str, mode: str=""):
        with TopmostManager(self.root):
            messagebox.showerror(f"{mode}エラー", message)

    def show_info(self, message: str, mode: str="セーブ"):
        with TopmostManager(self.root):
            messagebox.showinfo(mode, message)

    # ユーザーにok / cancelの確認をする
    def ask_confirmation(self, message: str, mode: str="セーブ"):
        with TopmostManager(self.root):
            if not messagebox.askokcancel(mode, message):
                return False
        return True
    
    # ファイル名を作る
    def create_filename(self):
        # 今日の日付と時間を取得
        now = dt.datetime.now()
        str_now = now.strftime("%Y-%m-%d_%H-%M-%S")

        # 選択された場所に保存する
        # セーブデータのインデックスを切り出す
        if self.select_file_name:
            try:
                file_number = self.save_data_manager.extract_file_number(self.select_file_name)
            except IndexError:
                file_number = "01"
        else:
            # 新規セーブの場合
            file_number = str(len(self.save_data_list)).zfill(2)

        # キャラクター名と場所
        name = self.save_data.get("player_status", {}).get("name", "Unknown")
        room_direction = self.save_data.get("game_state", {}).get("room", None)
        if room_direction:
            room_name = ROOM_NAME[room_direction]
        else:
            room_name = ""

        # キャラクター名、プレイ中なら現在地、日時でファイル名を作る
        return f"{file_number} {name} {room_name} {str_now}.json"

    # フォーカス登録
    def all_register_focusable(self):
        for button in self.button_list:
            self.focus_manager.register(button)
        for data in self.data_label_list:
            self.focus_manager.register(data["label"])

    # セーブデータのリストを取得し重複チェックする
    def fetch_and_validate_save_data_list(self):
        self.save_data_list = []

        # 一覧を取得
        save_data_list = self.save_data_manager.get_save_files()

        # 重複チェック
        self.save_data_list = self.save_data_manager.clean_duplicate_files(save_data_list)

    # セーブデータリストのラベルを更新する（なければ作る）
    def refresh_label_list(self):
        """セーブデータリストのラベルを更新する

        注：セーブスロットは固定10個で、削除時はファイル内容を空にするだけなのでラベル数は変わらない。
        """
        if not self.save_data_list:
            self.data_label_list = []
            return
        
        if not self.data_label_list:
            self.create_save_data_label_list()
        else:
            # 今のファイル一覧のファイル番号を把握
            existing_numbers = {
                self.save_data_manager.extract_file_number(f)
                for f in self.save_data_list
            }

            # ラベルを更新
            updated_labels = []
            for data in self.data_label_list:
                if data["number"] in existing_numbers:
                    # ファイルが存在するラベルのみ保持
                    for save_data in self.save_data_list:
                        if self.save_data_manager.extract_file_number(save_data) == data["number"]:
                            data["file"] = save_data
                            data_name = save_data.replace(".json", "")
                            data["label"].set_text(data_name)
                updated_labels.append(data)

            self.data_label_list = updated_labels

            """# ファイル一覧の更新内容をラベルに反映
            for save_data in self.save_data_list:
                save_data_number = self.save_data_manager.extract_file_number(save_data)
                for data in self.data_label_list:
                    if data["number"] == save_data_number:
                        data["file"] = save_data
                        data_name = save_data.replace(".json", "")
                        data["label"].set_text(data_name)
            """

        self.set_save_data_rect()

    # 画面サイズ変更時のアイテム表示位置の変更
    def relayout(self, screen):
        super().relayout(screen)
        self.setting_window_rect()
        for label in self.label_list:
            label.relayout(screen)
        for data in self.data_label_list:
            data["label"].relayout(screen)
        self.set_save_data_rect()

    # データ表示ボックスを表示
    def draw_window(self):
        pygame.draw.rect(self.screen, SHEET_COLOR, self.window_rect)
        pygame.draw.rect(self.screen, GRAY, self.window_rect, 2)

    # 画面を描画
    def draw(self):
        self.draw_window()
        if self.top:
            self.top.draw()
        if self.button_list:
            for item in self.button_list:
                item.draw()
        if self.data_label_list:
            for data in self.data_label_list:
                data["label"].draw()

    def handle_event(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT:
                Close(self.root)
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                Close(self.root)

            result = self.focus_manager.handle_event(event)
            if result and result["action"] == "decide":
                self.on_focus_decide(result["target"])

    # focus_managerでdecideが返された時の処理
    def on_focus_decide(self, element: Any):
        # 決定ボタン
        if element is self.enter:
            if self.save_load_flag == "save":
                self.save()
            else:
                self.load()

        # 削除ボタン
        elif element is self.delete:
            self.delete_data()

        # 閉じるボタン
        elif element is self.close:
            self.state = State.CLOSE

        else:
            # データ一覧の選択
            for data in self.data_label_list:
                if data["label"] == element:
                    self.select_file_name = data["file"]
                    print(self.select_file_name)

    def update(self):
        self.draw()
        self.handle_mouse_hover()
        self.handle_event()
        return self.next_state()
                            
    def next_state(self):
        # 閉じるボタン
        if self.state == State.CLOSE:
            if self.befor_event in ["title", "opening"]:
                return self.befor_event, None
            
            elif self.befor_event == "charasheet":
                if self.save_load_flag == "save":
                    if self.ask_confirmation("セーブせずに本編に進みますか？", "閉じる"):
                        return "play", self.save_data
                    else:
                        self.state = State.NONE
                        return "save", self.save_data
                else:
                    return "charasheet", None

            elif self.befor_event == "play":
                return "play", self.save_data
        
        # セーブボタン
        elif self.state == State.SAVE:
            return "play", self.save_data

        # ロードボタン
        elif self.state == State.LOAD:
            return "play", self.load_data
        else:
            if self.save_load_flag == "save":
                return "save", self.save_data
            else:
                return "load", self.save_data

