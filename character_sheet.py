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

        self.page_navi = None   # 初期化
        self.now_page = 0       # 現在のページ
        self.sex_button = None
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
        self.create_navigation(self.page_navi)
        if self.now_page == 0:
            self.create_status_page()
        else:
            self.create_chara_profession()

    # キャラステータス作成画面を作る
    def create_status_page(self):
        status_json = self.load_data()
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
        self.end_button = Button(self.screen, self.font, (530,330,100,100), "キャラ作成\n終了", self.end_button)

    # ナビゲーションバーを作る
    def create_navigation(self, page):
        position = RIGHT if page == 0 else LEFT
        self.page_navi = PageNavigation(self.screen, position)

    # 終了ボタンを押した時のイベント
    def end_button(self):
        texts = []
        for status in CharaStatus:
            if CharaStatus[status] == "" or CharaStatus[status] == 0:
                if status == "name":
                    texts.append("名前が入力されていません")
                elif status == "age":
                    texts.append("年齢が入力されていません")
                elif status == "STR" or status == "CON" or status == "SIZ" or status == "DEX" or status == "APP" or status == "EDU" or status == "INT" or status == "POW":
                    texts.append(status + "が入力されていません")
                elif status == "Profession":
                    texts.append("職業が選択されていません")
        if self.hoby_selecter.pull.selected_item == "":
            texts.append("趣味が選択されていません")
        else:
            HobyDataIn()
        if texts != []:
            text = "\n".join(texts)
            messagebox.showerror("未入力", text)
        else:
            self.end_flag = True

    # マウスオーバーイベント
    def handle_mouse_hover(self):
        # マウスオーバーでテキスト表示するよ
        key = pygame.mouse.get_pos()

        # ページによって変わる
        if self.now_page == 0:
            for stat in self.status_items:
                stat.handle_mouse_hover(key)
        else:
            if not self.hoby_selecter.pull.is_open:
                for prof in self.prof_selecter.prof_items:
                    prof.handle_mousu_hover(key)
                if self.end_button.rect.collidepoint(key):
                    TextDraw(self.screen, "キャラクター作成を終了します")
            self.hoby_selecter.handle_mousu_hover(key)

    # イベントハンドラ
    def handle_events(self):
        for event in pygame.event.get():
            # マウスクリック時
            if event.type == MOUSEBUTTONDOWN:
                # 左ボタン
                if event.button == 1:
                    # １ページ目だったら
                    if self.now_page == 0:
                        # ページ移動
                        if self.page_navi.navi_rect.collidepoint(event.pos):
                            self.now_page == 1
                        # 男ボタン
                        elif self.sex_button.man_rect.collidepoint(event.pos):
                            CharaStatus["sex"] = True
                        # 女ボタン
                        elif self.sex_button.woman_rect.collidepoint(event.pos):
                            CharaStatus["sex"] = False                                        
                        else:
                            # 他のステータスをリストでまとめた
                            for status in self.status_items:
                                # インプットボックス
                                if status.input:
                                    if status.input.rect.collidepoint(event.pos):
                                        if status.input_flag:
                                            status.InputProcess()
                                # ダイスボタン
                                elif status.button:
                                    if status.button.rect.collidepoint(event.pos):
                                        status.DiceProcess()                        
                    else:
                    # 2ページ目だったら
                        # ページ移動
                        if self.page_navi.navi_rect.collidepoint(event.pos):
                            self.now_page == 0
                            if self.hoby_selecter.pull.is_dropped:
                                self.hoby_selecter.pull.toggle_pulldown_list()

                        # プルダウンのクリック処理
                        if self.hoby_selecter.pull.box_rect.collidepoint(event.pos):
                            self.hoby_selecter.pull.toggle_pulldown_list()

                        self.hoby_selecter.pull.handle_click(event.pos)

                        if not self.hoby_selecter.pull.is_open:
                            if self.end_button.is_clicked(event.pos):
                                self.end_button.update(event.pos)
                            else:
                                for prof in self.prof_selecter.prof_items:
                                    prof.handle_click(event.pos)

    def update(self):
        self.draw_sheet()        
        self.draw_frame()
        self.draw_page()
        self.handle_mouse_hover()
        self.handle_events()
        return self.next_state()

    def next_state(self):
        if self.end_flag:
            return "save", "play"
        return "charasheet", ""        
