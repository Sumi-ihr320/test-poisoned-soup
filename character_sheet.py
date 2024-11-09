import pygame
import pygame.draw
from pygame.locals import *

from constans import *
from utils import *
from ui_elements import *

from status_calculator import *
from pages.status_page import StatusPage
from pages.profession_page import ProfessionPage

# キャラクターシート作成画面をクラス化してみる
class CharacterSheet:
    def __init__(self, screen, root):
        self.screen = screen
        self.root = root

        self.menu = None        # メニューボタン
        self.create_menu()

        self.page_navi = None   # ナビゲーションバー
        self.now_page = 0       # 現在のページ


        self.end_flag = False   # キャラシ作成を終わるフラグ

        self.selected_profession = None     # 選択中の職業
        self.is_pulldown_open = False      # プルダウン用のフラグ
        self.selected_hobby = ""            # 選択中の趣味

        # 設定する主人公のステータス
        chara_data = load_json(CHARA_DATA_PATH)
        self.hero_data = chara_data["Hero"]
        # セーブデータ
        self.save_data = load_json("SaveData.json")

        # ページ管理
        self.status_page = StatusPage(self.screen, self.root, self.hero_data)
        self.status_page.load_status_items(load_json(STATUS_DATA_PATH))
        self.profession_page = ProfessionPage(self.screen, self.root, self.hero_data, self.save_data)
        self.profession_page.load_selecter(self.is_pulldown_open, self.selected_hobby)

        # 状態フラグ
        self.state = State.NONE

    # シートの描画
    def draw_sheet(self):
        pygame.draw.rect(self.screen, SHEET_COLOR, SHEET_RECT)
    
    # メニューボタンの作成
    def create_menu(self):
        self.menu = Menu(self.screen, self.root, self.set_state, save_enabled=False)

    # ページを表示する
    def draw_page(self):
        self.menu.draw()
        self.create_navigation(self.now_page)
        self.page_navi.draw()
        if self.now_page == 0:
            self.status_page.draw()
        else:
            self.profession_page.draw(self.selected_profession)
                
    # ナビゲーションバーを作る
    def create_navigation(self, page):
        position = RIGHT if page == 0 else LEFT
        self.page_navi = PageNavigation(self.screen, position)

    # マウスオーバーイベント
    def handle_mouse_hover(self):
        # マウスオーバーでテキスト表示するよ
        key = pygame.mouse.get_pos()
        horver_text = None

        if self.menu:
            for button in self.menu.buttons:
                button.update(key)

        # ページによって変わる
        if self.now_page == 0:
            horver_text = self.status_page.handle_mouse_hover(key)
        else:
            horver_text = self.profession_page.handle_mouse_hover(key, self.is_pulldown_open)

        if horver_text:
            TextDraw(self.screen, horver_text)

    # イベントハンドラ
    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンかESCキーで終了
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                Close(self.root)
            # マウス左クリック時
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.handle_mouse_click(event.pos)

    # マウスクリック時
    def handle_mouse_click(self, pos):
        if self.menu:
            for button in self.menu.buttons:
                if button.update(pos, True):
                    return
        # １ページ目だったら
        if self.now_page == 0:
            # ページ移動
            if self.page_navi.handle_click(pos):
                self.now_page = 1
            else:
                item = self.status_page.handle_click(pos)
                if item:
                    self.insart_data(item)
        else:
        # 2ページ目だったら
            # ページ移動
            if self.page_navi.handle_click(pos):
                self.now_page = 0
                # もし趣味のプルダウンが開いていたら閉じる
                if self.is_pulldown_open:
                    self.is_pulldown_open = False
            else:
                self.is_pulldown_open, self.selected_profession, self.selected_hobby = self.profession_page.handle_click(pos, self.is_pulldown_open)

    # 更新されたデータをステータスに入力＋自動計算する
    def insart_data(self, status):
        self.hero_data[status.status_name] = status.input.get_value()
        self.auto_calculation(status.status_name)

    # ステータスの自動計算
    def auto_calculation(self, name):
        # 各ステータスに対応する計算
        calculations = {"STR": [calculation_damege_bonus],
                        "SIZ": [calculation_damege_bonus, calculation_health_point],
                        "CON": [calculation_health_point],

                        "POW": [calculation_power_related],
                        "INT": [calculation_idea],
                        "EDU": [calculation_educated_point],
                        "DEX": [calculation_avoid_point]}

        # 計算結果により変化するステータス
        response_status = {calculation_damege_bonus: ["DB"],
                          calculation_health_point: ["HP"],
                          calculation_power_related: ["MP","Luck","SAN"],
                          calculation_idea: ["Idea"],
                          calculation_educated_point: ["Know"],
                          calculation_avoid_point: ["Avo"]}

        if name in calculations:
            for calculation in calculations[name]:
                # 計算結果を取得する
                val = calculation(self.hero_data)
                if name == "EDU":
                    val = val if val < 99 else 99
                # 計算結果をステータスに入力 & ラベルの更新
                if name == "POW":
                    self.hero_data.update(val)
                for status in response_status[calculation]:
                    if name != "POW":
                        self.hero_data[status] = val
                    self.update_status_label(status, self.hero_data[status])
    
    # ステータスラベルの更新
    def update_status_label(self, name, val):
        for item in self.status_page.status_items:
            if item.status_name == name:
                item.input.update_label(f"{val}")

    def update(self):
        create_frame(self.screen)
        self.draw_sheet()
        self.draw_page()    # ページに応じた描画
        self.handle_mouse_hover()
        self.handle_events()
        return self.next_state()

    # メニューボタン用のコールバック関数
    def set_state(self, state=State.NONE):
        self.state = state

    def next_state(self):
        if self.end_flag:
            return "save"
        elif self.state == State.LOAD:
            self.state = State.NONE
            return "load"
        elif self.state == State.CLOSE:
            self.state = State.NONE
            Close()
        return "charasheet"
