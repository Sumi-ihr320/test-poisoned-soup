import pygame
import pygame.draw
from pygame.locals import *

from constans import *
from utils import *
from ui_elements import *
from characters import Player
from character_item import *

from menu import MenuController, update_menu
from navigation import Navigation
from status_calculator import *
from pages.status_page import StatusPage
from pages.profession_page import ProfessionPage

# キャラクターシート作成画面をクラス化してみる
class CharacterSheet:
    def __init__(self, screen, root):
        self.screen = screen
        self.root = root

        # メニューボタン
        self.menu_controller = MenuController(self.screen, self.root, self.set_state, save_enabled=False)

        # surfaceを作成
        self.create_surface()

        self.now_page = 0       # 現在のページ

        # ナビゲーション
        self.navigetion = Navigation(self.screen, self.sheet_rect)
        self.setup_navigation()

        self.selected_profession = None     # 選択中の職業
        self.is_pulldown_open = False       # プルダウン用のフラグ
        self.selected_hobby = ""            # 選択中の趣味

        # 設定する主人公のステータス
        self.player = Player()
        self.player.add_item(ITEM_LIST["white_robe"])

        # セーブデータ
        self.save_data = load_json("SaveData.json")

        # ページ管理
        self.status_page = StatusPage(self.screen, self.root, self.player)
        self.status_page.load_status_items(load_json(STATUS_DATA_PATH))
        self.profession_page = ProfessionPage(self.screen, self.root, self.player, self.save_data, self.set_state)
        self.profession_page.load_selecter(self.selected_hobby)

        # 状態フラグ
        self.state = State.NONE

    # シート用のsurfaceを作る
    def create_surface(self):
        self.window_size = self.screen.get_size()
        w_percent, h_percent = RATIO[self.window_size]
        sheet_w, sheet_h = SHEET_SIZE
        self.sheet_surface = pygame.Surface((int(sheet_w * w_percent), int(sheet_h * h_percent)))

        # テキストフレームの位置からシート位置を算出
        frame_rect = get_frame(self.screen)
        self.sheet_rect = self.sheet_surface.get_rect(centerx=(self.screen.get_width()//2),bottom=frame_rect.top - 20)

        self.sheet_surface.fill(SHEET_COLOR)

    # シートの描画
    def draw_sheet(self):
        self.screen.blit(self.sheet_surface, self.sheet_rect.topleft)
        #pygame.draw.rect(self.screen, SHEET_COLOR, SHEET_RECT)
    
    # ページを表示する
    def draw_page(self):
        self.menu_controller = update_menu(self.screen, self.menu_controller)
        self.menu_controller.draw()
        self.navigetion.draw()
        if self.now_page == 0:
            self.status_page.draw()
        else:
            self.profession_page.draw(self.selected_profession, self.is_pulldown_open)
    
    # ナビゲーションバーを作る
    def setup_navigation(self):
        position = Position.RIGHT if self.now_page == 0 else Position.LEFT
        self.navigetion.setup_navigation([position])

    # マウスオーバーイベント
    def handle_mouse_hover(self):
        # マウスオーバーでテキスト表示するよ
        key = pygame.mouse.get_pos()
        horver_text = None

        self.menu_controller.handle_mouse_hover(key)
        
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
        if self.menu_controller.handle_click(pos):
            return
        
        # １ページ目だったら
        if self.now_page == 0:
            # ページ移動
            if self.navigetion.handle_click(pos) is not None:
                self.now_page = 1
                self.setup_navigation()
            else:
                item = self.status_page.handle_click(pos)
                if item:
                    self.insart_data(item)
        else:
        # 2ページ目だったら
            # ページ移動
            if self.navigetion.handle_click(pos):
                self.now_page = 0
                self.setup_navigation()
                # もし趣味のプルダウンが開いていたら閉じる
                if self.is_pulldown_open:
                    self.is_pulldown_open = False
            else:
                self.is_pulldown_open, self.selected_profession, self.selected_hobby = self.profession_page.handle_click(pos, self.is_pulldown_open, self.selected_profession, self.selected_hobby)

    # 更新されたデータをステータスに入力＋自動計算する
    def insart_data(self, status):
        setattr(self.player, status.status_name, status.input.get_value())
        #self.player_data[status.status_name] = status.input.get_value()
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
                          calculation_avoid_point: ["Dodge"]}

        if name in calculations:
            for calculation in calculations[name]:
                # 計算結果を取得する
                val = calculation(self.player)
                if name == "EDU":
                    val = val if val < 99 else 99
                # 計算結果をステータスに入力 & ラベルの更新
                if name == "POW":
                    for status, value in val.items():
                        setattr(self.player, status, value)
                for status in response_status[calculation]:
                    if name != "POW":
                        setattr(self.player, status, val)
                    self.update_status_label(status, getattr(self.player, status))
    
    # ステータスラベルの更新
    def update_status_label(self, name, val):
        for item in self.status_page.status_items:
            if item.status_name == name:
                item.input.update_label(f"{val}")

    # 画面サイズ更新時にポジションを変更する
    def update_item_position(self):
        # シートを作り直す
        self.create_surface()
        # ナビゲーションを作り直す
        self.navigetion.screen = self.screen
        self.navigetion.surface_rect = self.sheet_rect
        self.setup_navigation()


    def update(self):
        create_frame(self.screen)
        self.draw_sheet()
        self.draw_page()    # ページに応じた描画
        self.handle_mouse_hover()
        self.handle_events()
        return self.next_state()

    # メニューボタン用のコールバック関数
    def set_state(self, state=State.NONE, save_data=None):
        self.state = state
        if save_data:
            self.save_data = save_data

    def next_state(self):
        if self.state == State.SAVE:
            return "save", self.save_data
        elif self.state == State.LOAD:
            self.state = State.NONE
            return "load"
        elif self.state == State.SETTING:
            self.state = State.NONE
            return "setting"
        elif self.state == State.CLOSE:
            self.state = State.NONE
            Close()
        return "charasheet"
