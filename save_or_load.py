import os, json
import datetime as dt

import pygame
from pygame.locals import *

from constans import *
from utils import *
from ui.ui_elements import Label
from input.focus_manager import *
from input.input_mode_manager import InputMode, input_mode_manager
from base_scene import BaseScene

# データロード
class Save_or_Load(BaseScene):
    def __init__(self, screen, root, save_load_flag, befor_event, save_data, setting_manager=None):
        super().__init__(screen, root)

        # フォントの設定
        self.set_font_data()

        self.save_load_flag = save_load_flag    # save か load か
        self.befor_event = befor_event          # 来る前にしてたイベント

        self.save_data = save_data              # 保存するデータ
        self.load_data = None                   # ロードするデータ
        self.setting_manager = setting_manager  # 保存するための設定ファイル

        self.forder_name = f"{PATH}{SAVE_FOLDER}"   # セーブフォルダ

        # セーブロード用ウィンドウサイズ
        self.setting_rect()

        # 選択したデータ
        self.select_file_name = None

        # セーブデータリスト
        self.save_data_list = []    # フォルダから持ってきたセーブデータファイル一覧
        self.load_save_data()
        self.data_label_list = []   # セーブデータファイルのラベルリスト
        self.create_save_data_list()
        self.set_save_data_rect()

        # 画面作成
        self.top = None     # セーブ or ロード
        self.enter = None   # 決定
        self.delete = None  # 削除
        self.close = None   # 閉じる
        self.button_list = []
        self.label_list = []
        self.create_label()
        
        # フォーカスの設定
        #self.create_grid_list()
        #self.focus = FocusManager(self.screen, self.focus_grid_list)

        #self.hovered = False

        # マウスが何かアイテムを選択しているかどうか
        #self.mouse_focus = None

        # キーボードモードかマウスモードか
        #self.mouse_focus, self.focus = swich_keybord_or_mouse(self.mouse_focus, self.focus, self.focus_grid_list)


    # フォントの設定
    def set_font_data(self):
        self.font_data = (FONT_PATH, FONT_SIZ)
        self.contents_font_data = (FONT_PATH, CONTENTS_SIZ)

    # ウィンドウサイズを作成する
    def setting_rect(self):
        self_size = (600, 500)
        w, h = get_new_size(self.screen_size, self_size)
        x = (self.screen.get_width() // 2) - (w // 2)
        y = (self.screen.get_height() // 2) - (h // 2)
        self.window_rect = Rect(x,y,w,h)

    # データ表示ボックスを表示
    def create_window(self):
        pygame.draw.rect(self.screen, SHEET_COLOR, self.window_rect)
        pygame.draw.rect(self.screen, GRAY, self.window_rect, 2)

   # ラベルの作成
    def create_label(self):
        if self.save_load_flag == "save":
            top_text = "セーブ"
            enter_text = "セーブ"
        else:
            top_text = "ロード"
            enter_text = "ロード"

        self.top = Label(self.screen, self.contents_font_data, top_text, y=self.window_rect.top+30, centerx=self.window_rect.centerx)
        self.enter = Label(self.screen, self.contents_font_data, enter_text, y=self.window_rect.bottom-50, centerx=self.window_rect.centerx-150)
        self.delete = Label(self.screen, self.contents_font_data, "削除", y=self.window_rect.bottom-50, centerx=self.window_rect.centerx)
        self.close = Label(self.screen, self.contents_font_data, "閉じる", y=self.window_rect.bottom-50, centerx=self.window_rect.centerx+150)
        self.button_list = [self.enter, self.delete, self.close]
        self.label_list = [self.top] + self.button_list

    # セーブデータ一覧を探してくる
    def load_save_data(self):
        # セーブフォルダが無ければ作る
        if not os.path.isdir(self.forder_name):
            os.makedirs(self.forder_name)

        # フォルダ内にあるデータ一覧を持ってくる
        self.save_data_list = os.listdir(self.forder_name)

        # 設定データはリストに含まない
        self.save_data_list.remove("setting.json")

    # セーブデータ一覧ラベルを作成する
    def create_save_data_list(self):
        if self.save_data_list:
            for data in self.save_data_list:
                data_name = data.replace(".json", "")
                label = Label(self.screen, self.font_data, data_name)
                item = {"file":data, "label":label}
                self.data_label_list.append(item)

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
                y += 30

    # フォーカス移動用のグリッドリストを作成する
    def create_grid_list(self):
        self.focus_grid_list = []

        # データリスト
        for data in self.data_label_list:
            self.focus_grid_list.append([data["label"]])

        # ボタンリスト
        self.focus_grid_list.append(self.button_list)

    # データ削除
    def data_delete(self):
        # データが選択されているかをチェック
        if not self.check_select_file():
            return
        
        # データが存在しているかをチェック
        if not self.check_save_data():
            with TopmostManager(self.root):
                messagebox.showerror("削除エラー", "データがありません")
                return
        
        # 本当に削除するかを確認
        with TopmostManager(self.root):
            if not messagebox.askokcancel("削除", f"{self.select_file_name}\n本当に削除してよろしいですか？"):
                return
                    
        file_name = f"{self.forder_name}{self.select_file_name}"
        try:
            # ファイルの中身を空にする
            with open(file_name, "w", encoding="utf-8_sig") as f:
                pass
        except Exception as e:
            print(f"データエラー: {e}")

        # 新しいファイル名に変更する
        file_no = self.get_file_no(self.select_file_name)
        new_file_name = f"{self.forder_name}{file_no}.json"
        os.rename(file_name, new_file_name)
        with TopmostManager(self.root):
            messagebox.showinfo("削除", "削除が完了しました")
        
        # リストを更新
        self.reload()
        self.draw()

    # 設定データのセーブ
    def setting_save(self):
        self.setting_manager.set("input_mode", input_mode_manager.get_mode())

    # データセーブ
    def save(self):
        # 設定データをセーブしておく
        self.setting_save()

        # セーブする場所が選択されているかチェック
        if not self.check_select_file():
            return
        
        # すでにデータがあった場合は上書き確認
        if self.check_save_data():
            with TopmostManager(self.root):
                if not messagebox.askokcancel("セーブ", f"{self.select_file_name}\nセーブデータを上書きしますか？"):
                    return

        # 新しいファイル名に変更する
        old_file_name = f"{self.forder_name}{self.select_file_name}"
        new_file_name = self.create_file_name()
        os.rename(old_file_name, new_file_name)

        # データを書き込む
        try:
            with open(new_file_name, "w", encoding="utf-8_sig") as f:
                json.dump(self.save_data, f, indent=2, ensure_ascii=False)
            with TopmostManager(self.root):
                messagebox.showinfo("セーブ", "セーブが完了しました")
            self.state = State.SAVE
        except Exception as e:
            print(f"セーブエラー: {e}")
            with TopmostManager(self.root):
                messagebox.showerror("セーブエラー", "セーブに失敗しました")

    # データロード
    def load(self):
        # データが選択されているかをチェック
        if not self.check_select_file():
            return
        
        # データが存在するかをチェック
        if not self.check_save_data():
            with TopmostManager(self.root):
                messagebox.showerror("ロードエラー", "データがありません")
        else:
            file_name = f"{self.forder_name}{self.select_file_name}"
            try:
                self.load_data = load_json(SAVE_FOLDER, self.select_file_name)
                with TopmostManager(self.root):
                    messagebox.showinfo("ロード", "ロードに成功しました")
                self.state = State.LOAD
            except FileNotFoundError:
                with TopmostManager(self.root):
                    messagebox.showerror("ロードエラー", "ファイルが見つかりません")
            except json.JSONDecodeError:
                with TopmostManager(self.root):
                    messagebox.showerror("ロードエラー", "ファイル形式が正しくありません")
            except Exception as e:
                print(f"ロードエラー: {e}")
                with TopmostManager(self.root):
                    messagebox.showerror("ロードエラー", f"ロードに失敗しました: {str(e)}")

    # 選択された箇所にデータがあるかないかを確認する
    def check_save_data(self):
        if len(self.select_file_name.replace(".json", "")) == 2:
            return False
        return True

    # データが選択されているかのチェックとエラーメッセージ
    def check_select_file(self):
        if self.select_file_name is None:
            with TopmostManager(self.root):
                messagebox.showerror("エラー", "データが選択されていません")
            return False
        return True

    # ファイルNoを取得する
    def get_file_no(self, file_name):
        file_name = file_name.replace(".json", "")
        return file_name.split(" ")[0]

    # リスト更新
    def reload(self):
        self.save_data_list = []
        self.load_save_data()
        if not self.data_label_list:
            self.create_save_data_list()
        else:
            for data, save_data in zip(self.data_label_list, self.save_data_list):
                data["file"] = save_data
                data_name = save_data.replace(".json", "")
                data["label"].set_text(data_name)
        self.set_save_data_rect()

    # 画面サイズ変更時のアイテム表示位置の変更
    def update_item_position(self, screen):
        super().update_item_position(screen)
        label_list = []
        for data in self.data_label_list:
            label_list.append(data["label"])
        self.label_list += label_list
        for label in self.label_list:
            label.update_item_position(screen)
    
    # ファイル名を作る
    def create_file_name(self):
        # 今日の日付と時間を取得
        now = dt.datetime.now()
        str_now = now.strftime("%Y-%m-%d_%H-%M-%S")

        # 選択された場所に保存する
        # セーブデータのインデックスを切り出す
        if self.select_file_name:
            try:
                data_no = self.get_file_no(self.select_file_name)
            except IndexError:
                data_no = "00"
        else:
            # 新規セーブの場合
            data_no = str(len(self.save_data_list)).zfill(2)

        # キャラクター名と場所
        name = self.save_data.get("player_status", {}).get("name", "Unknown")
        room_direction = self.save_data.get("game_state", {}).get("room", None)
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
                item.draw(type="line", back_color=BLACK)
        if self.data_label_list:
            for data in self.data_label_list:
                if data["file"] == self.select_file_name:
                    data["label"].draw(forcused=True)
                else:
                    data["label"].draw()

    # マウスオーバーで枠を表示するよ
    def handle_mouse_hover(self):
        pos = pygame.mouse.get_pos()

        for item in self.button_list:
            item.handle_mouse_hover(pos)

    def handle_event(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT:
                Close(self.root)

            # キーボード押下時
            elif event.type == KEYDOWN:
                if input_mode_manager.get_mode() == InputMode.MOUSE:
                    self.focus = swich_to_keybord(self.mouse_focus, self.focus, self.focus_grid_list)

                if event.key == K_ESCAPE:
                    Close(self.root)

                elif event.key == K_UP:
                    self.focus.move_up()

                elif event.key in (K_DOWN, K_TAB):
                    self.focus.move_down()

                elif event.key == K_LEFT:
                    self.focus.move_left()

                elif event.key == K_RIGHT:
                    self.focus.move_right()

                elif event.key in (K_RETURN, K_KP_ENTER):
                    pos = self.focus.get_selected().get_center()
                    self.handle_ckick(pos)

            # マウス移動時
            if event.type == MOUSEMOTION:
                if input_mode_manager.get_mode() == InputMode.KEYBOARD:
                    self.mouse_focus = swich_to_mouse(self.mouse_focus, self.focus)

            # マウスクリック時
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if input_mode_manager.get_mode() == InputMode.KEYBOARD:
                    self.mouse_focus = swich_to_mouse(self.mouse_focus, self.focus)

                self.handle_ckick(event.pos)

    def handle_ckick(self, pos):
        # 閉じるボタン
        if self.close.handle_click(pos, "select"):
            self.state = State.CLOSE

        # 決定ボタン
        elif self.enter.handle_click(pos, "select"):
            if self.save_load_flag == "save":
                self.save()                
            else:
                self.load()

        # 削除ボタン
        elif self.delete.handle_click(pos, "select"):
            self.data_delete()

        # データ一覧の選択
        for data in self.data_label_list:
            if data["label"].handle_click(pos):
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
                    with TopmostManager(self.root):
                        if messagebox.askokcancel("閉じる", "セーブせずに本編に進みますか？"):
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

