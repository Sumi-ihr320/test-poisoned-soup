import re

from constans import *
from ui_elements import CommandMenu, DiceRoll, Image
from utils import TextDraw, opposition_percent, load_json
from .sound_manager import SoundManager

class EventManager:
    def __init__(self, screen, player=None, girl=None, game_state=None, flags=None,
                 next_scenario_call_back=None, move_to_room_call_back=None, room_new_view=None, set_state=None):
        self.screen = screen
        self.player = player
        self.girl = girl
        self.game_state = game_state
        self.flags = flags
        self.skill_list = load_json(SKILL_DATA_PATH)

        # コールバック関数
        self.next_scenario_call_back = next_scenario_call_back
        self.move_to_room_call_back = move_to_room_call_back
        self.room_new_view_call_back = room_new_view
        self.set_state_call_back = set_state

        # サウンドマネージャー
        self.sound_manager = SoundManager()

        self.command_menu = None
        self.item_image = None

        self.player_roll_result = None     # ダイスロールの結果
        self.girl_roll_result = None
        self.player_threshold = None       # ダイスロールの比較値
        self.girl_threshold = None
        self.damage_point = None    # ダメージポイント

    # コマンドメニューの生成
    def create_command_menu(self, commands):
        if commands:
            start_position = self.get_position()
            self.command_menu = CommandMenu(self.screen, commands, start_position)

    # 画像イメージの作成
    def create_image(self, file_name):
        size = 0.6 if "Memo" in file_name else (0.5 if "center-room_Light" in file_name else 0.35)
        img_path = f"{PATH}{PICTURE}{file_name}"
        self.item_image = Image(self.screen, img_path, size, x="center", centery=200, line_flag=True, bg_flag=True)

    # コマンドメニューの表示位置を取得
    def get_position(self):
        max_x, max_y = 650, 220     # これ以上端に配置すると見えなくなる

        # コマンド表示の指標となる画像位置。クリック時画像があればそこを起点とする。
        if self.item_image:
            image_rect = self.item_image.rect

            # 画像の右側にコマンドボタンを表示する。最大値以上になる場合は左側に配置する。
            x = image_rect.right + 30 if (image_rect.right + 30) <= max_x else image_rect.x - 130
            y = image_rect.y if image_rect.y <= max_y else image_rect.y - 50
        else:
            x, y = WINDOW_CENTER_X + 120, 100

        return (x, y)

    # シナリオから受け取ったイベントを進行する
    def handle_scenario_event(self, step):
        # テキストを表示する
        if step["type"] == "text":
            text = step["text"]
            self.display_text(text)

        # 次のシナリオに進む
        elif step["type"] == "next_step":
            self.to_callback_next_scenario(step["next"])
        
        # アクションを起こす
        elif step["type"] == "action":
            action = step["action"]
            if action == "damage":
                step["damage"] = self.damage_point
            self.handle_action(action, step)

        # ダイスチェックを行う
        elif step["type"] == "dice_check":
            player_check_result, girl_check_result = False, False
            self.player_roll_result, self.player_threshold, player_check_result = self.handle_dice_roll(step)
            if step.get("girl", False):
                self.girl_roll_result, self.girl_threshold, girl_check_result = self.handle_dice_roll(step)
            next_scenario = step["success"] if player_check_result or girl_check_result else step["failure"]
            self.to_callback_next_scenario(next_scenario)

        # ダメージを計算する
        elif step["type"] == "damage":
            self.damage_calculator(step)

        # フラグによる分岐をおこなう
        elif step["type"] == "conditional":
            self.handle_conditional(step["conditions"])

        # コマンドを表示する
        elif step["type"] == "interaction":
            item = step.get("item", None)
            self.create_command_menu(step["interactions"])

        # 画像を表示する
        elif step["type"] == "image_display":
            self.create_image(step["image"])

        # 画像を非表示にする
        elif step["type"] == "image_hidden":
            self.item_image = None

        # サウンドを鳴らす
        elif step["type"] == "sound":
            self.handle_sound(step)

        # エンディングに移行する
        elif step["type"] == "ending":
            self.set_ending()

    # アクションを実行する
    def handle_action(self, action, step):
        # 部屋移動
        if action == "move_to_room":
            self.game_state.time -= 2
            room_id = step.get("room_id", None)
            self.move_to_room(room_id)

        # フラグセット
        elif action == "set_flag":
            category = step["category"]
            flag = step["flag"]
            value = step["value"]
            self.set_flag(category, flag, value)
            if flag == "center_room_light" and value == True:
                self.room_new_view("center-room")
            elif flag == "east_room_visivle" and value == True:
                self.room_new_view("east-room")
            elif (flag == "book_found" and value == True) or (flag == "candle_goes_out" and value > 0):
                self.room_new_view("west-room")

        # ダメージを受ける
        elif action == "damage":
            status = step.get("status", None)
            damage = step.get("damage", None)
            self.take_damage(status, damage)

        # アイテムを取得する
        elif action == "get_item":
            self.player.add_item(ITEM_LIST[step["item"]])

        # アイテムを手放す
        elif action == "lost_item":
            self.player.remove_item(ITEM_LIST[step["item"]])

        # 時間を経過させる
        elif action == "time_passage":
            self.game_state.time -= step["time"]

    # ダイスロールを処理
    def handle_dice_roll(self, step):
        dice_text = step["dice"]
        check_type = step["check_type"]
        half = step.get("half", False)

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

        elif check_type == "status":
            threshold = getattr(self.player, step["status"])
        
        if half:
            threshold = threshold // 2

        dice = DiceRoll(dice_text)
        check_result = dice.check(threshold)

        return dice.result, threshold, check_result

    # フラグチェックを処理
    def handle_conditional(self, conditions):
        for condition in conditions:
            # 全部のフラグがtrueだったら次のシナリオ
            if all(self.flag_check(flag) for flag in condition["flags"]):
                self.to_callback_next_scenario(condition["next"])
                break

    # サウンド処理
    def handle_sound(self, step):
        sound_name = step["name"]
        if self.sound_manager:
            if not self.sound_manager.sounds or (sound_name not in self.sound_manager.sounds):
                self.sound_manager.load_sound(sound_name, step["path"], step.get("loop", False))
            self.sound_manager.play(sound_name)

    # 現在のテキストを描画する
    def display_text(self, text):
        if "{" in text:
            text = self.process_text_template(text)
        TextDraw(self.screen, text)

    # テンプレートにダイス結果等を表示
    def process_text_template(self, text_tamplate):
        format_kwargs = {}
        if "{player_roll}" in text_tamplate and self.player_roll_result is not None:
            format_kwargs["player_roll"] = self.player_roll_result
            format_kwargs["player_threshold"] = self.player_threshold
        if "{girl_roll}" in text_tamplate and self.girl_roll_result is not None:
            format_kwargs["girl_roll_result"] = self.girl_roll_result
            format_kwargs["girl_threshold"] = self.girl_threshold
        if "{damage}" in text_tamplate and self.damage_point is not None:
            format_kwargs["damage"] = self.damage_point

        return text_tamplate.format(**format_kwargs) if format_kwargs else text_tamplate

    # フラグをチェックする
    def flag_check(self, flags):
        if flags["category"] == "game_state":
            value = getattr(self.game_state, flags["flag"])
            if flags["flag"] == "time":
                if value > flags["value"]:
                    return True
            else:
                if value == flags["value"]:
                    return True
        else:
            if flags.get("not", False):
                if self.flags.get_flag(flags["category"], flags["flag"]) != flags["value"]:
                    return True
            else:
                if self.flags.get_flag(flags["category"], flags["flag"]) == flags["value"]:
                    return True
        return False

    # コールバック関数に次のシナリオ名を渡す
    def to_callback_next_scenario(self, next_scenario):
        self.next_scenario_call_back(next_scenario)

    # 部屋移動イベント
    def move_to_room(self, room_id):
        self.item_image = None
        self.move_to_room_call_back(room_id)

    # 部屋の状態変化による再描画
    def room_new_view(self, room_id):
        self.item_image = None
        self.room_new_view_call_back(room_id)
        
    # エンディングに移行するためにコールバック関数にステータスを渡す
    def set_ending(self):
        self.set_state_call_back(State.CLOSE)

    # フラグをセットするイベント
    def set_flag(self, category, flag, value):
        if type(value) == str:
            obj = re.match(r"\+|-", value)
            if obj:
                int_value = int(value[1:])
                flag_value = self.flags.get_flag(category, flag)
                if value[0] == "+":
                    value = flag_value + int_value
                else:
                    value = flag_value - int_value

        self.flags.update_flag(category, flag, value)

    # ダメージ計算
    def damage_calculator(self, step):
        dice = DiceRoll(step["dice"])
        self.damage_point = dice.result

    # ダメージを受けるイベント
    def take_damage(self, status, damage):
        if type(damage) == str:
            if damage == "1/2":
                status_point = getattr(self.player, status)
                damage = status_point // 2

        if status == "SAN":
            state = self.player.take_SAN_damage(int(damage))
        elif status == "HP":
            state = self.player.take_damage("event", int(damage))

        if state:
            self.to_callback_next_scenario(state)

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