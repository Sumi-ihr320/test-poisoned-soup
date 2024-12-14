import re

from constans import *
from ui_elements import CommandMenu

class EventManager:
    def __init__(self, screen, scenario_manager, flags):
        self.screen = screen
        self.flags = flags

        self.scenario_manager = scenario_manager
        self.command_menu = None
        
    # コマンドメニューの生成
    def create_command_menu(self, commands, item):
        if commands:
            start_position = item.get_position() if item else (WINDOW_CENTER_X-60, 100)
            self.command_menu = CommandMenu(self.screen, commands, start_position)

    def handle_mouse_hover(self, pos):
        if self.command_menu:
            self.command_menu.handle_mouse_hover(pos)

    # コマンドメニューがクリックされた際に実行
    def handle_command_click(self, pos):
        if self.command_menu:
            next_scenario = self.command_menu.handle_click(pos)
            if next_scenario:
                self.scenario_manager.start_scenario(next_scenario)
                self.command_menu = None    # コマンドメニューを閉じる

    # シナリオから受け取ったアクションを実行する
    def handle_action(self, action, step):
        if action == "move_to_room":
            room_id = step.get("room_id", None)
            self.move_to_room(room_id)

        elif action == "set_flag":
            category = step["category"]
            flag = step["flag"]
            value = step["value"]
            self.set_flag(category, flag, value)

        elif action == "damage":
            status = step.get("status", None)
            dice = step.get("dice", None)

    # 部屋移動イベント
    def move_to_room(self, room_id):
        pass

    # フラグをセットするイベント
    def set_flag(self, category, flag, value):
        if type(value) == str:
            obj = re.match(r"\+|-", value)
            if obj:
                value = value.split[1:]
                flag_value = self.flags.get_flag(category, flag)
                if obj.group == "+":
                    value = flag_value + value
                else:
                    value = flag_value - value

        self.flags.set_flag(category, flag, value)

    # ダメージを受けるイベント
    def damage(self, status, dice):
        pass

    # イベントを処理
    def handle_event(self, event_name, event_data):
        if event_name == "item_click":
            item_name = event_data.get("item_name")
            self.scenario_manager.start_scenario(item_name)

        elif event_name == "book_exit":
            self.handle_book_exit(event_data)

        elif event_name == "fight_start":
            self.start_fight(event_data)

        # 他のイベントを追加
        else:
            print(f"No handler for event: {event_name}")

    # 部屋から本を持ちだそうとした際に起こるイベント
    def handle_book_exit(self):
        """本を持ち出したときのイベント"""
        print("You tried to leave the room with the book!")

        # 戦闘を開始するイベントを発生
        self.handle_event("fight_start", enemy="Guardian")

    # 戦闘イベント
    def start_fight(self, enemy):
        """戦闘イベントを開始"""
        print(f"Starting fight with {enemy}")




        # 悩み中　item_managerかevent_managerを使う

        # centerMemoの時のイベントまとめ
        # memo1～3のシナリオ表示
        # memo1の時は1枚目の画像、memo3の時に２枚目の画像、memo4の時に３枚目の画像を表示

