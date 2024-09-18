import pygame
import pygame.draw
from pygame.locals import *

from data import *
from fanction_summary import *
from class_summary import *

# キャラクターシート作成画面をクラス化してみる
class CharacterSheet:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)

        self.page_navi = None   # ナビゲーションバー
        self.now_page = 0       # 現在のページ
        self.sex_button = None  # 男女ボタン
        self.status_items = []  # ステータスのアイテム一覧
        self.end_flag = False   # キャラシ作成を終わるフラグ

    # シートの描画
    def draw_sheet(self):
        pygame.draw.rect(self.screen, SHEET_COLOR, SHEET_RECT)
        
    # テキストフレームの表示
    def draw_frame(self):
        create_frame(self.screen)

    # ページを表示する
    def draw_page(self):
        self.create_navigation(self.now_page)
        if self.now_page == 0:
            self.create_status_page()
            for item in self.status_items:
                item.draw()
            if self.sex_button:
                self.sex_button.draw(CharaStatus["sex"])
        else:
            self.create_chara_profession()
            self.prof_selecter.draw()
            
    # キャラステータス作成画面を作る
    def create_status_page(self):
        status_json = self.load_data()
        if not self.status_items:   # すでにアイテムがあるか確認
            for status in status_json:
                items = status_json[status]
                item = Status(self.screen, items["name"], status, items["view_name"],
                            items["x"], items["y"], items["w"], items["h"], items["text"],
                            items["button_flag"], items["input_flag"], items["box_flag"], items["dice_text"])
                self.status_items.append(item)
                if status == "sex":
                    self.sex_button = SexChange(self.screen, 310, 80, CharaStatus["sex"])

    # jsonファイルを取ってくる
    def load_data(self):
        file_path = f"{PATH}{JSON_FOLDER}Status.json"
        return load_json(file_path)

    def create_chara_profession(self):
        # 職業選択画面
        self.create_profession_selecter()

        # 趣味選択画面
        self.create_hoby_selecter()

        # キャラ作成終了ボタン
        self.create_end_button()
    
    # 職業選択画面を作る
    def create_profession_selecter(self):
        self.prof_selecter = ProfessionSelecter(self.screen)

    # 趣味選択画面を作る
    def create_hoby_selecter(self):
        self.hoby_selecter = HobbySelecter(self.screen)

    # キャラ作成終了ボタンを作る
    def create_end_button(self):
        self.end_button = Button(self.screen, self.font, (600,330,100,50), "キャラ作成\n終了", self.end_button_event)        

    # ナビゲーションバーを作る
    def create_navigation(self, page):
        position = RIGHT if page == 0 else LEFT
        self.page_navi = PageNavigation(self.screen, position)

    # 終了ボタンを押した時のイベント
    def end_button_event(self):
        manual_input_fields = { "name":"名前が入力されていません",
                                "age":"年齢が入力されていません",
                                "STR":"STRが入力されていません",
                                "CON":"CONが入力されていません",
                                "SIZ":"SIZが入力されていません",
                                "DEX":"DEXが入力されていません",
                                "APP":"APPが入力されていません",
                                "EDU":"EDUが入力されていません",
                                "INT":"INTが入力されていません",
                                "POW":"POWが入力されていません",
                                "Profession":"職業が選択されていません"
                                }
        texts = []

        # 手動入力が必要なステータスのみエラーチェックする
        for status, error_msg in manual_input_fields.items():
            if CharaStatus.get(status) == "" or CharaStatus.get(status) == 0:
                texts.append(error_msg)

        # 趣味が選択されていない場合のチェック
        if self.hoby_selecter.select_item == "":
            texts.append("趣味が選択されていません")
        else:
            HobyDataIn()
        if texts:
            text = "\n".join(texts)
            messagebox.showerror("未入力", text)
        else:
            self.end_flag = True

    # マウスオーバーイベント
    def handle_mouse_hover(self):
        # マウスオーバーでテキスト表示するよ
        key = pygame.mouse.get_pos()
        horver_text = None

        # ページによって変わる
        if self.now_page == 0:
            for stat in self.status_items:
                if stat.button:
                    stat.button.update(key)
                text = stat.handle_mouse_hover(key)
                if text is not None:
                    horver_text = text
                    break
        else:
            horver_text = self.hoby_selecter.handle_mouse_hover(key)

            if not self.hoby_selecter.pull.is_open():
                for prof in self.prof_selecter.prof_items:
                    text = prof.handle_mouse_hover(key)
                    if text is not None:
                        horver_text = text
                        break
                if self.end_button.rect.collidepoint(key):
                    self.end_button.update(key)
                    if horver_text is None:
                        horver_text = "キャラクター作成を終了します"

        if horver_text:
            TextDraw(self.screen, horver_text)

    # イベントハンドラ
    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンかESCキーで終了
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                Close()
            # マウス左クリック時
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.handle_mouse_click(event.pos)

    # マウスクリック時
    def handle_mouse_click(self, pos):
        # １ページ目だったら
        if self.now_page == 0:
            self.handle_first_page_click(pos)
        else:
        # 2ページ目だったら
            self.handle_second_page_click(pos)

    # 1ページ目の処理
    def handle_first_page_click(self, pos):
        # ページ移動
        if self.page_navi.handle_click(pos):
            self.now_page = 1
        # 男ボタン
        elif self.sex_button and self.sex_button.man.rect.collidepoint(pos):
            CharaStatus["sex"] = True
            self.sex_button.update_sex(True)
        # 女ボタン
        elif self.sex_button and self.sex_button.woman.rect.collidepoint(pos):
            CharaStatus["sex"] = False
            self.sex_button.update_sex(False)
        else:
            # 他のステータスをリストでまとめた
            for status in self.status_items:
                # インプットボックス
                if status.input and status.input.rect.collidepoint(pos) and status.input_flag:   # かつ入力フラグがonの場合
                    status.input_process()
                    break
                # ダイスボタン
                if status.button:
                    if status.button.update(pos, True):
                        break

    # 2ページ目の処理
    def handle_second_page_click(self, pos):
        # ページ移動
        if self.page_navi.handle_click(pos):
            self.now_page = 0
            # もし趣味のプルダウンが開いていたら閉じる
            if self.hoby_selecter.pull.is_dropped:
                print("Closing dropdown due to page navigation.")                
                self.hoby_selecter.pull.toggle_pulldown_list()

        # プルダウンのクリック処理
        elif self.hoby_selecter.pull.box_rect.collidepoint(pos):
            print("Toggling dropdown.")
            self.hoby_selecter.pull.toggle_pulldown_list()

        # プルダウンが開いているときは
        elif self.hoby_selecter.pull.is_open():
            print("Dropdown is open, handling item click.")
            # 趣味欄のクリック処理
            self.hoby_selecter.pull.handle_click(pos)
            return

        else:
            # もしプルダウンが開いていなかったら
            print("Dropdown is closed, handling other clicks.")
            # ボタンのクリック処理
            if self.end_button.is_clicked(pos):
                self.end_button.update(pos, True)
            else:
                # 職業のクリック処理
                for prof in self.prof_selecter.prof_items:
                    if prof.handle_click(pos):
                        break

    def update(self):
        self.draw_sheet()        
        self.draw_frame()
        self.draw_page()    # ページに応じた描画
        self.handle_mouse_hover()
        self.handle_events()
        return self.next_state()

    def next_state(self):
        if self.end_flag:
            return "save", "play"
        return "charasheet", ""        
