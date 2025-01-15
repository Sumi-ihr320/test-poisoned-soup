import re

from constans import *
from ui_elements import CommandMenu, DiceRoll
from utils import TextDraw, opposition_percent, load_json

class EventManager:
    def __init__(self, screen, player=None, game_state=None, flags=None, next_scenario_call_back=None):
        self.screen = screen
        self.player = player
        self.game_state = game_state
        self.flags = flags
        self.skill_list = load_json(SKILL_DATA_PATH)

        self.next_scenario_call_back = next_scenario_call_back

        self.command_menu = None

        self.roll_result = None     # ダイスロールの結果
        self.threshold = None       # ダイスロールの比較値
        self.damage_point = None    # ダメージポイント

    # コマンドメニューの生成
    def create_command_menu(self, commands, item=None):
        if commands:
            start_position = item.get_position() if item else (WINDOW_CENTER_X+100, 100)
            self.command_menu = CommandMenu(self.screen, commands, start_position)

    # シナリオから受け取ったイベントを進行する
    def handle_scenario_event(self, step):
        if step["type"] == "text":
            text = step["text"]
            if "{" in text:
                text = self.process_text_template(text)
            self.display_text(text)

        elif step["type"] == "next_step":
            self.to_callback_next_scenario(step["next"])
        
        elif step["type"] == "action":
            action = step["action"]
            if action == "damage":
                step["damage"] = self.damage_point
            self.handle_action(action, step)

        elif step["type"] == "dice_check":
            self.roll_result, self.threshold, check_result = self.handle_dice_roll(step)
            next_scenario = step["success"] if check_result else step["failure"]
            self.to_callback_next_scenario(next_scenario)

        elif step["type"] == "damage":
            self.damage_calculator(step)

        elif step["type"] == "conditional":
            self.handle_conditional(step["conditions"])

        elif step["type"] == "interaction":
            self.create_command_menu(step["interactions"])

    # アクションを実行する
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
            damage = step.get("damage", None)
            self.take_damage(status, damage)

    # ダイスロールを処理
    def handle_dice_roll(self, step):
        dice_text = step["dice"]
        check_type = step["check_type"]

        if check_type == "VS_active":
            active = getattr(self.player, step["status"])
            passive = step["enemy_status"]
            threshold = opposition_percent(active, passive)

        elif check_type == "VS_passive" :
            active = step["enemy_status"]
            passive = getattr(self.player, step["status"])
            threshold = opposition_percent(active, passive)
        
        elif check_type == "skill":
            skill = step["skill"]
            threshold = self.player.skill.get(skill, self.skill_list[skill])
        
        elif check_type == "SAN":
            threshold = self.player.SAN

        dice = DiceRoll(dice_text)
        check_result = dice.check(threshold)

        return dice.result, threshold, check_result

    # フラグチェックを処理
    def handle_conditional(self, conditions):
        for condition in conditions:
            # 全部のフラグがtrueだったら次のシナリオ
            if all(self.flag_check(flag) for flag in condition["flags"]):
                self.to_callback_next_scenario(condition["next"])

    # 現在のテキストを描画する
    def display_text(self, text):
        TextDraw(self.screen, text)

    # テンプレートにダイス結果等を表示
    def process_text_template(self, text_tamplate):
        if "{roll}" in text_tamplate and self.roll_result is not None:
            text = text_tamplate.format(roll=self.roll_result, threshold=self.threshold)
        elif "{damage}" in text_tamplate and self.damage_point is not None:
            text = text_tamplate.format(damage=self.damage_point)
        else:
            text = text_tamplate
        return text

    # フラグをチェックする
    def flag_check(self, flags):
        if self.flags.get_flag(flags["category"], flags["flag"]) == flags["value"]:
            return True        
        return False

    # コールバック関数にデータを渡す
    def to_callback_next_scenario(self, next_scenario):
        self.next_scenario_call_back(next_scenario)

    # 部屋移動イベント
    def move_to_room(self, room_id):
        self.game_state.room = room_id

        
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

        self.flags.update_flag(category, flag, value)

    # ダメージ計算
    def damage_calculator(self, step):
        dice = DiceRoll(step["dice"])
        self.damage_point = dice.result

    # ダメージを受けるイベント
    def take_damage(self, status, damage):
        if status == "SAN":
            self.player.take_SAN_damage(damage)
        elif status == "HP":
            self.player.take_damage("event", damage)

    # イベントを処理
    def handle_event(self, event_name, event_data):
        if event_name == "item_click":
            #item_name = event_data.get("item_name")
            #self.scenario_manager.start_scenario(item_name)
            pass

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

    # コマンドメニューのマウスオーバー
    def handle_mouse_hover(self, pos):
        if self.command_menu:
            self.command_menu.handle_mouse_hover(pos)

    # コマンドメニューがクリックされた際に実行
    def handle_command_click(self, pos):
        if self.command_menu:
            next_scenario = self.command_menu.handle_click(pos)
            if next_scenario:
                self.to_callback_next_scenario(next_scenario)
            
            self.command_menu = None    # コマンドメニューを閉じる

    def draw(self, step):
        if step["type"] == "text":
            self.display_text(step["text"])

        elif step["type"] == "interaction" and self.command_menu:
            self.command_menu.draw()