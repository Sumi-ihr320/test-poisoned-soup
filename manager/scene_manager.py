import pygame

from title import Title
from save_or_load import Save_or_Load
from setting import Settings
from opening import Opening
from character_sheet.character_sheet import CharacterSheet
from playing.playing import MainPlay
from ending import Ending

class SceneManager:
    def __init__(self, screen, root, setting_manager):
        self.screen = screen
        self.root = root
        self.setting_manager =setting_manager

        self.save_data = None
        
        self.event_name = "title"
        #self.event_name = "charasheet"
        #self.event_name = "play"
        self.provious_event = None

        self.event_map = {}
        self.create_event("title")

    # 現在のイベントを更新し、次のイベントへ遷移
    def update(self):
        if self.event_name not in self.event_map:
            return
        
        event = self.event_map[self.event_name]

        # 各イベントのupdate実行
        result = event.update()

        # 帰ってきたデータがタプル型だった場合
        if isinstance(result, tuple):
            next_name, data = result
        else:
            next_name, data = result, None

        # イベントが変わる際に前のイベントを記録
        if next_name != self.event_name:
            self.provious_event = self.event_name

        # 次のイベントに更新
        self.event_name = next_name

        # 設定変更 or セーブデータの更新が必要な場合は更新
        if data is not None:
            if isinstance(data, type(self.setting_manager)):
                self.setting_manager = data
                self.screen = pygame.display.get_surface()

            elif isinstance(data, dict):
                self.save_data = data
        
        self.create_event(self.event_name)

    def create_event(self, event_name):
        if not self.update_data(event_name):
            # データが無い場合のみインスタンスを作成
            if event_name == "title":
                self.event_map["title"] = Title(self.screen, self.root, self.setting_manager)
            elif event_name == "opening":
                self.event_map["opening"] = Opening(self.screen, self.root)
            elif event_name == "charasheet":
                self.event_map["charasheet"] = CharacterSheet(self.screen, self.root)
            elif event_name == "setting":
                self.event_map["setting"] = Settings(self.screen, self.root, self.setting_manager, self.provious_event)
            elif event_name == "save":
                self.event_map["save"] = Save_or_Load(self.screen, self.root, "save", self.provious_event, self.save_data)
            elif event_name == "load":
                self.event_map["load"] = Save_or_Load(self.screen, self.root, "load", self.provious_event, self.save_data)
            elif event_name == "play":
                self.event_map["play"] = MainPlay(self.screen, self.root, self.save_data)
            elif event_name == "ending":
                self.event_map["ending"] = Ending(self.screen, self.root, self.save_data)
            
    def update_data(self, event_name):
        # すでにデータがある場合はデータを更新
        if event_name in self.event_map:
            # スクリーンサイズの更新
            self.event_map[event_name].screen = self.screen

            # 設定画面
            if event_name == "setting":
                self.event_map[event_name].manager = self.setting_manager
            
            # 表示位置更新
            if event_name in ["title", "setting", "charasheet"]:
                if self.event_map[event_name].window_size != self.screen.get_size():
                    self.event_map[event_name].update_item_position()
            
            # 前のイベント
            if event_name in ["setting", "save", "load"]:
                self.event_map[event_name].befor_event = self.provious_event

            # セーブデータ
            if event_name in ["save", "load", "play"]:
                self.event_map[event_name].save_data = self.save_data

            return True
        False


