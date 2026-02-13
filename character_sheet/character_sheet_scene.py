from typing import Tuple
from tkinter import messagebox

import pygame
from pygame.locals import *

from constans import ITEM_LIST, JSON_FOLDER, State
from utils import load_json, Close, TopmostManager
from models.characters import Player, Human
from input.focus_manager import FocusManager

from ui.ui_panels import TextFramePanel
from ui.navigation import CharasheetNavigation
from character_sheet.status_calculator import *
from character_sheet.status import Status
from character_sheet.status_page import StatusPage
from character_sheet.profession_page import ProfessionPage
from character_sheet.confirm_page import ConfirmPage
from base_scene import BaseScene

# キャラクターシート作成画面をクラス化してみる
class CharacterSheetScene(BaseScene):
    def __init__(self, screen, root):
        super().__init__(screen, root)


        self.selected_profession = None     # 選択中の職業
        self.is_pulldown_open = False       # プルダウン用のフラグ
        self.selected_hobby = ""            # 選択中の趣味

        # 設定する主人公のステータス
        self.player = Player()
        self.player.add_item(ITEM_LIST["white_robe"])

        # 初期セーブデータ
        self.save_data = load_json("SaveData.json", JSON_FOLDER)
        
        # テキストフレーム
        enabled_flags = {"セーブ": False, "ロード": True, "ログ": False}
        self.text_frame_panel = TextFramePanel(self.screen, enabled_flags=enabled_flags, next_callback=self.set_state)
        frame_rect = self.text_frame_panel.rect

        # ページ管理
        self.pages = []
        self.create_pages(frame_rect)

        # 現在のページ
        self.current_page = 0
        # 次のページ
        self.target_page = 1

        # スライド関係
        self.is_sliding = False
        self.slide_offset = 0
        self.slide_speed = 40

        # ナビゲーション
        surface_rect = self.status_page.rect
        self.navigation = CharasheetNavigation(self.screen, surface_rect)

        # フォーカスマネージャー
        self.focus_manager = FocusManager(self.screen)

        # 状態フラグ
        self.state = State.NONE
    
    # ページの作成
    def create_pages(self, frame_rect: pygame.Rect):
        self.status_page = StatusPage(self.screen, self.root, frame_rect, self.player)
        self.status_page.load_status_items()
        self.profession_page = ProfessionPage(self.screen, self.root, frame_rect, self.player)
        self.profession_page.load_selector(self.selected_hobby)
        self.confirm_page = ConfirmPage(self.screen, self.root, frame_rect, self.player, self.save_data, self.set_state)

        self.pages.append(self.status_page)
        self.pages.append(self.profession_page)
        self.pages.append(self.confirm_page)

    # すべての要素をフォーカスマネージャーに登録する
    def register_all(self):
        for page in self.pages:
            page.register_all(self.focus_manager)
        self.navigation.register_all(self.focus_manager)
        self.text_frame_panel.register_all(self.focus_manager)

    # 更新されたデータをステータスに入力＋自動計算する
    def insert_data(self, status: Status):
        setattr(self.player, status.status_name, status.input.get_value())
        self.auto_calculation(status.status_name)

    # ステータスの自動計算
    def auto_calculation(self, name: str):
        # 各ステータスに対応する計算
        calculations = {"STR": [calculation_damage_bonus],
                        "SIZ": [calculation_damage_bonus, calculation_health_point],
                        "CON": [calculation_health_point],

                        "POW": [calculation_power_related],
                        "INT": [calculation_idea],
                        "EDU": [calculation_educated_point],
                        "DEX": [calculation_avoid_point]}

        # 計算結果により変化するステータス
        response_status = {calculation_damage_bonus: ["DB"],
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
    def update_status_label(self, name: str, val: int|str):
        for item in self.status_page.elements:
            if item.status_name == name:
                item.input.update_label(f"{val}")

    # 完了ボタンを押した時のイベント
    def event_enter_button(self):
        manual_input_fields = { "name": "名前が入力されていません",
                                "age": "年齢が入力されていません",
                                "STR": "STRが入力されていません",
                                "CON": "CONが入力されていません",
                                "SIZ": "SIZが入力されていません",
                                "DEX": "DEXが入力されていません",
                                "APP": "APPが入力されていません",
                                "EDU": "EDUが入力されていません",
                                "INT": "INTが入力されていません",
                                "POW": "POWが入力されていません",
                                "Profession":"職業が選択されていません",
                                "Hobby":"趣味が選択されていません"
                                }
        texts = []

        # 手動入力が必要なステータスのみエラーチェックする
        for status, error_msg in manual_input_fields.items():
            if getattr(self.player, status) == "" or getattr(self.player, status) == 0:
                texts.append(error_msg)
        if texts:
            text = "\n".join(texts)
            with TopmostManager(self.root):
                messagebox.showerror("未入力", text)
        else:
            # セーブデータに主人公データを入れる
            self.save_data["player_status"] = self.player.to_dict()

            # セーブデータに少女のデータを入れる
            girl = Human("下僕の少女", "Girl.png", 4, 6, 10, 5, 10, 10,"-1d4", 8, 10, 10,
                         {"目星":55, "聞き耳":55, "忍び歩き":40,"隠れる":40,"応急手当":50, "中国語（母国語）":40, "追跡":50, "その他言語（主人公の母国語）":31,"クトゥルフ神話":15, "拳銃":20},
                         17, "woman", 13, 6, 50, 50, 30, 0, 0, "放浪者")
            girl.add_item(ITEM_LIST["bloody_robe"])
            girl.add_item(ITEM_LIST["gun"])

            self.save_data["girl_status"] = girl.to_dict()

            #self.callback(State.SAVE, self.save_data)
            self.state = State.SAVE


    # ページを表示する
    def draw_page(self):
        current, current_rect = self.draw_page_get_surface_and_rect(self.current_page)
        current_x = current_rect.x - self.slide_offset
        self.screen.blit(current, (current_x, current_rect.y))

        if self.is_sliding:
            target, target_rect = self.draw_page_get_surface_and_rect(self.target_page)
            target_x = self.screen_size[0] - self.slide_offset if self.target_page > self.current_page else - self.screen_size[0] - self.slide_offset
            self.screen.blit(target, (target_x, target_rect.y))

        self.navigation.draw(self.current_page)
        self.text_frame_panel.draw()

    # ページを表示してSurfaceとRectを返す
    def draw_page_get_surface_and_rect(self, page: int) -> Tuple[pygame.Surface, pygame.Rect]:
        if self.pages[page] == self.profession_page:
            return self.pages[page].draw(self.selected_profession, self.is_pulldown_open)
        else:
            return self.pages[page].draw()

    # 次のページを表示
    def next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.target_page = self.current_page + 1
            self.is_sliding = True
    
    # 前のページを表示
    def prev_page(self):
        if self.current_page > 0:
            self.target_page = self.current_page - 1
            self.is_sliding = True

    # マウスオーバーイベント
    def handle_mouse_hover(self):
        # マウスオーバーでテキスト表示するよ
        key = pygame.mouse.get_pos()
        horver_text = None

        #self.menu_controller.handle_mouse_hover(key)
        self.text_frame_panel.handle_mouse_hover(key)
        
        # ページによって変わる
        if self.current_page == 0:
            horver_text = self.status_page.handle_mouse_hover(key)
        elif self.current_page == 1:
            horver_text = self.profession_page.handle_mouse_hover(key, self.is_pulldown_open)

        if horver_text:
            self.text_frame_panel.set_text(horver_text)
        else:
            self.text_frame_panel.set_text("")

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
    def handle_mouse_click(self, pos: Tuple[int, int]):
        if self.text_frame_panel.handle_click(pos):
            return
        
        # ページ移動
        result = self.navigation.handle_click(self.current_page, pos)
        if result:
            if self.current_page == 1 and self.is_pulldown_open:
                self.is_pulldown_open = False
            if result == "enter":
                self.event_enter_button()
            else:
                self.is_sliding = True
                if result == "next":
                    self.next_page()
                else:
                    self.prev_page()
            
        # １ページ目だったら
        if self.current_page == 0:
            item = self.status_page.handle_click(pos)
            if item:
                self.insert_data(item)
        elif self.current_page == 1:
        # 2ページ目だったら
            self.is_pulldown_open, self.selected_profession, self.selected_hobby = self.profession_page.handle_click(pos, self.is_pulldown_open, self.selected_profession, self.selected_hobby)

    # 画面サイズ更新時にポジションを変更する
    def relayout(self, screen: pygame.Surface):
        super().relayout(screen)
        self.text_frame_panel.relayout(screen)
        # ステータスページをupdate
        self.status_page.relayout(screen)
        # 職業ページをupdate
        self.profession_page.relayout(screen)
        # 確認ページをupdate
        self.confirm_page.relayout(screen)
        # ナビゲーションをupdate
        self.navigation.relayout(screen, self.status_page.rect)

    def update(self):
        # スライドアニメーションの進行
        if self.is_sliding:
            direction = 1 if self.target_page > self.current_page else -1
            self.slide_offset += self.slide_speed * direction

            # 1ページ分スライドしきったら
            if abs(self.slide_offset) >= self.screen_size[0]:
                self.current_page = self.target_page
                self.slide_offset = 0
                self.is_sliding = False

        self.draw_page()    # ページに応じた描画
        self.handle_mouse_hover()
        self.handle_events()
        return self.next_state()

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

