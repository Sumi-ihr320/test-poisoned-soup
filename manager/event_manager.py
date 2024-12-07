import re
from ui_elements import CommandMenu

class EventManager:
    def __init__(self, screen, scenario_manager, flags):
        self.screen = screen
        self.flags = flags

        self.scenario_manager = scenario_manager
        self.command_menu = None
        

    # アイテムがクリックされた際に呼び出される
    def tregger_item_event(self, item):
        print(f"アイテムクリック：{item.name}")     # デバッグ用
        self.scenario_manager.start_scenario(item.name)
        self.create_command_menu(item)

    # コマンドメニューの生成
    def create_command_menu(self, item):
        commands = self.get_item_commands(item.name)
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

    # シナリオから受け取ったアクションを実行する
    def handle_action(self, action, step):
        if action == "move_to_room":
            room_id = step.get("room_id", None)
            self.move_to_room(room_id)

        elif action == "set_flag":
            flag_name = step.get("flag_name", None)
            item = step.get("item", None)
            flag = step["flag"]
            value = step["value"]
            self.set_flag(flag_name, item, flag, value)

    # 部屋移動イベント
    def move_to_room(self, room_id):
        pass

    # フラグをセットするイベント
    def set_flag(self, flag_name, item, flag, value):
        if type(value) == str:
            obj = re.match(r"\+|-", value)
            if obj:
                value = value.split[1:]
            else:
                pass
        if flag_name:
            if item:
                self.flags[flag_name[item[flag]]] = value
            else:
                self.flags[flag_name[flag]] = value
        else:
            self.flags[flag] = value

        
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




        # 悩み中　item_managerかevent_managerを使う

        # doorのイベント
        # ドア画像表示
        # メニュー表示 → 入るで移動
        # 東の部屋は鍵開けイベント有り
        # 南の部屋は窓を覗く、聞き耳、入る（静かに・普通に・勢いよく）
    

        # centerMemoの時のイベントまとめ
        # memo1～3のシナリオ表示
        # memo1の時は1枚目の画像、memo3の時に２枚目の画像、memo4の時に３枚目の画像を表示
        # memoに目星コマンドでmemo_objectiveシナリオ表示 → 目星ダイスロール
        # 目星成功でmemo_objectiveシナリオ進行 → objectiveフラグtrue
        # memo1～4でシナリオが表示されるように

        # soupは医学成功で情報開示
        # あとは時間等で表示が変わる
