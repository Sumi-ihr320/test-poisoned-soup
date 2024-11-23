from ui_elements import CommandMenu

class EventManager:
    def __init__(self, screen, scenario_manager):
        self.screen = screen

        self.scenario_manager = scenario_manager
        self.command_menu = None

    # アイテムがクリックされた際に呼び出される
    def tregger_item_event(self, item):
        print(f"アイテムクリック：{item.name}")     # デバッグ用
        self.scenario_manager.start_scenario(item.name)
        self.create_command_menu(item)

    # コマンドメニューの生成
    def create_command_menu(self, item):
        commands = self.get_item_commands(item.scenario_key)
        if commands:
            start_position = item.get_position()
            self.command_menu = CommandMenu(self.screen, commands, start_position)

    # アイテムに関連するコマンドリストを取得
    def get_item_commands(self, scenario_key):
        scenario_data = self.scenario_manager.get_scenario(scenario_key)
        if scenario_data and scenario_data["type"] == "intaraction":
            return scenario_data["intaractions"]
        return None

    def handle_mouse_hover(self, pos):
        if self.command_menu:
            self.command_menu.handle_mouse_hover(pos)

    # コマンドメニューがクリックされた際に実行
    def handle_command_click(self, pos):
        if self.command_menu:
            event = self.command_menu.handle_click(pos)
            if event:
                self.scenario_manager.trigger_event(event)
                self.command_menu = None    # コマンドメニューを閉じる

    def handle_event(self, event_name, *args, **kwargs):
        """
        イベントを処理
        :param event_name: 発生するイベント名
        :param args: イベントに渡す引数
        """
        if event_name == "book_exit":
            self.handle_book_exit(*args, **kwargs)

        elif event_name == "fight_start":
            self.start_fight(*args, **kwargs)

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
