import re

from constans import *
from utils import *
from ui.ui_elements import ImageCache
from ui.ui_panels import TextFramePanel
from ui.ui_command import Command
from ui.log_view import LogView
from .render_manager import RenderManager
from .dice_service import DiceService
from .sound_manager import sound_manager
from .event_processors.dice_processor import DiceProcessor
from .event_processors.damage_processor import DamageProcessor
from .event_processors.conditional_processor import ConditionalProcessor
from .event_processors.status_effect_processor import StatusEffectProcessor

class EventManager:
    def __init__(self, screen, player=None, girl=None, game_state=None, flags=None, text_frame_panel=None, log_view=None,
                 next_scenario_call_back=None, move_to_room_call_back=None, room_new_view=None, set_state=None):
        self.screen = screen
        self.screen_size = self.screen.get_size()
        self.player = player
        self.girl = girl
        self.game_state = game_state
        self.flags = flags
        self.skill_list = load_json(SKILL_DATA_PATH, JSON_FOLDER)

        # コールバック関数
        self.next_scenario_call_back = next_scenario_call_back
        self.move_to_room_call_back = move_to_room_call_back
        self.room_new_view_call_back = room_new_view
        self.set_state_call_back = set_state

        # 表示関連
        self.image_cache = ImageCache()
        self.log_view = log_view if log_view else LogView(self.screen)
        self.text_frame_panel = text_frame_panel if text_frame_panel else TextFramePanel(self.screen)
        self.render_manager = RenderManager(
            self.screen, 
            self.image_cache, 
            self.text_frame_panel, 
            self.log_view,
            next_scenario_cb=self.to_callback_next_scenario)

        # プロセッサー
        self.dice_service = DiceService()
        self.dice_processor = DiceProcessor(self.dice_service, self.skill_list, self.flags)
        self.damage_processor = DamageProcessor(self.dice_service, self.take_damage)
        self.conditional_processor = ConditionalProcessor(self.flags, self.game_state, self.to_callback_next_scenario)
        self.status_effect_processor = StatusEffectProcessor(
            self.dice_service,
            self.take_damage,
            {"set_flag": self.set_flag,
             "next_scenario": self.to_callback_next_scenario,
             "black_out": self.render_manager.handle_black_out,
             "set_result_display": self.set_result_display}
        )

        self.pending_result_display = False # 結果表示待ちフラグ
        self.pending_dice_check = None      # 分岐情報
        self.current_display_text = None    # 描画用の処理済みデータ
        
        # handle_damageで使用
        self.player_roll_result = None     # ダイスロールの結果
        self.girl_roll_result = None

        self.state_record = {}      # キャラクターの特殊状態の記録

    # シナリオから受け取ったイベントを進行する
    def handle_scenario_event(self, step):
        # テキストを表示する or 結果を表示する
        if step["type"] == "text":
            self.current_display_text = step["text"]

            # 結果表示中でない場合のみ通常テキストを使用
            if self.pending_result_display:
                return
                    
        # 次のシナリオに進む
        elif step["type"] == "next_step":
            self.current_display_text = None
            self.to_callback_next_scenario(step["next"])
        
        # アクションを起こす
        elif step["type"] == "action":
            action = step["action"]
            self.handle_action(action, step)
            # アクション実行時はテキストをクリア
            self.current_display_text = None

        # 時間経過を行う
        elif step["type"] == "time_passage":
            self.handle_time_passage(step)
            self.current_display_text = None

        # ダイスチェックを行う
        elif step["type"] == "dice_check":
            self.handle_dice_check(step)

        # ダメージを計算したり適用する
        elif step["type"] == "damage":
            self.handle_damage(step)

        # 状態変化を行う
        elif step["type"] == "status_effect":
            self.handle_status_effect()
            self.current_display_text = None

        # 少女が一緒にいるかのチェック
        elif step["type"] == "girl_check":
            result = "true" if self.girl_fellow_check() else "false"
            self.current_display_text = None
            self.to_callback_next_scenario(step[result])

        # フラグによる分岐をおこなう
        elif step["type"] == "conditional":
            self.conditional_processor.process_conditional(step["conditions"])
            self.current_display_text = None

        # コマンドを表示する
        elif step["type"] == "interaction":
            commands = []
            for cmd in step["interactions"]:
                commands.append(Command(cmd["text"], cmd["next"]))
            target = step.get("target", None)
            self.render_manager.set_command_menu(commands, target)

        # 画像を表示する
        elif step["type"] == "image_display":
            self.render_manager.show_item_image(step["image"])

        # 画像を非表示にする
        elif step["type"] == "image_hidden":
            self.render_manager.hidden_item_image()
            self.current_display_text = None

        # 少女の立ち絵を表示する
        elif step["type"] == "girl_display":
            state = step.get("state", None)
            position = step.get("position", "right")
            self.render_manager.show_girl_image(state, position)

        # 少女の立ち絵を非表示にする
        elif step["type"] == "girl_hidden":
            self.render_manager.hidden_girl_image()
            self.current_display_text = None

        # サウンドを鳴らす
        elif step["type"] == "sound":
            self.handle_sound(step)

        # 毒摂取の画面効果を表示する
        elif step["type"] == "poison_start":
            pass

        # 毒摂取の画面効果表示を終了する
        elif step["type"] == "poison_stop":
            pass
        
        # エンディングに移行する
        elif step["type"] == "ending":
            self.current_display_text = None
            self.set_ending()

    # 少女が一緒にいるかどうかのフラグチェック
    def girl_fellow_check(self):
        return self.flags.get_flag("girl", "fellow")

    # 少女に参加してもらうかのフラグチェック
    def girl_flag_check(self):
        return self.flags.get_flag("girl", "dice_check")

    # アクションを実行する
    def handle_action(self, action, step):
        # 部屋移動
        if action == "move_to_room":
            self.game_state.time -= 2
            room_id = step.get("room_id", None)
            self.move_to_room(room_id)

        # フラグセット
        elif action == "set_flag":
            # どのフラグがどの部屋の表示に変更を与えるか
            room_flag_map = {"center-room":["light_remove",
                                            "soup_in_poison",
                                            "soup_drink",
                                            "soup_destruction",
                                            "soup_bowl_get"],
                             "east-room":["east_room_visivle"],
                             "west-room":["book_found",
                                          "book_get",
                                          "candle_get",
                                          "candle_goes_out"]}

            # フラグをセットする
            category = step["category"]
            flag = step["flag"]
            value = step["value"]
            self.set_flag(category, flag, value)

            # もしroom_flag_mapのフラグに該当していたら部屋情報を更新する
            room_id = None
            for room, key_flags in room_flag_map.items():
                for key_flag in key_flags:
                    if flag == key_flag:
                        room_id = room
                        break
            if room_id:
                self.room_new_view(room_id)

        # アイテムを取得する
        elif action == "get_item":
            target = step.get("target", None)
            item = ITEM_LIST[step["item"]]
            character = self.girl if target == "girl" else self.player
            character.add_item(item)
            #self.result_text = f"{character.name}は{item.name}を手に入れた。"
            text = f"{character.name}は{item.name}を手に入れた。"
            self.pending_result_display = True
            self.current_display_text = text
            #self.to_callback_next_scenario("result_text")

        # アイテムを手放す
        elif action == "lost_item":
            target = step.get("target", None)
            item = ITEM_LIST[step["item"]]
            character = self.girl if target == "girl" else self.player
            character.remove_item(item)
            #self.result_text = f"{character.name}は{item.name}を失った。"
            text = f"{character.name}は{item.name}を失った。"
            self.pending_result_display = True
            self.current_display_text = text
            #self.to_callback_next_scenario("result_text")

    # ダイスチェックをする
    def handle_dice_check(self, step):
        check_status = None
        player_check_result, girl_check_result = None, None
        result_text = ""
        status_text = ""

        # ダイスチェックのターゲット指定がもしあればそのキャラクターだけ行う
        target = step.get("target", None)
        player_flag, girl_flag = self.target_check(target)

        if player_flag:
            res = self.dice_processor.process_dice_roll(step, self.player)
            check_status = res["status"]
            player_check_result = res["ok"]
            result_text = res["text"]

        if girl_flag:
            res = self.dice_processor.process_dice_roll(step, self.girl)
            check_status = res["status"]
            girl_check_result = res["ok"]
            text = res["text"]

            if result_text:
                result_text += f"\n{text}"
            else:
                result_text = text

        # ダイス結果表示の《〇〇》の部分のテキストを取得する
        if step["check_type"] == "毒対抗ロール":
            status_text = step["check_type"]
        else:
            check_list = {"Idea":"アイデア",
                          "Dodge":"回避",
                          "Luck":"幸運"}
            status_text = check_list.get(check_status, check_status)

        # 半分の値で計算した場合は《〇〇 ÷ 2》と表示する
        if step.get("half", False):
            status_text += " ÷ 2"

        # SANチェックと毒対抗ロールとショックロールは各キャラクター毎に結果が異なるので成功、失敗の結果分岐をしない
        if step["check_type"] == "SANチェック" or step["check_type"] == "毒対抗ロール" or step["check_type"] == "shock_roll":        
            self.player_roll_result = player_check_result
            self.girl_roll_result = girl_check_result
            self.pending_dice_check = None  # 分岐情報なし
            # 結果表示フラグを立てる
            self.pending_result_display = True
            self.current_display_text = result_text
        else:
            # どちらかのダイス結果が成功していれば成功の結果表示、どちらも失敗していれば失敗の結果表示をする
            success = player_check_result or girl_check_result
            result_text = f"《{status_text}》 ⇒ {'成功' if success else '失敗'}！\n{result_text}"

            # 分岐情報を保存
            self.pending_dice_check = {
                "success": success,
                "on_success": step["on_success"],
                "on_failure": step["on_failure"]
            }

            # 結果表示フラグをON
            self.pending_result_display = True
            self.current_display_text = result_text

        print(f"[DEBUG] ダイスチェック完了")
        print(f" 結果: {result_text}")
        print(f" 分岐あり: {self.pending_dice_check is not None}")
        print(f" 表示フラグ: {self.pending_result_display}")

    # ダメージ計算をして表示するテキストを作成する
    def handle_damage(self, step):
        # 誰がダメージを受けるのか
        target = step.get("target", None)
        characters = {}
        player_flag, girl_flag = self.target_check(target)
        if player_flag:
            characters[self.player] = self.player_roll_result
        if girl_flag:
            characters[self.girl] = self.girl_roll_result

        res = self.damage_processor.process_damage(step, characters)

        result_text = "\n".join(res["texts"])
        self.state_record = res["state_record"]

        # 結果表示フラグを立てる
        self.pending_result_display =True
        self.current_display_text = result_text

        print(f"[DEBUG] ダメージ処理完了")
        print(f" player_roll_result: {self.player_roll_result}")
        print(f" girl_roll_result: {self.girl_roll_result}")
        print(f" state_record: {self.state_record}")
        print(f" display_text: {self.current_display_text}")
              
    def get_and_clear_pending_branch(self):
        """保留中の分岐情報を取得してクリアする"""
        if self.pending_dice_check:
            branch = self.pending_dice_check
            self.pending_dice_check = None
            return branch
        return None

    def clear_result_display(self):
        """結果表示フラグをクリアする"""
        self.pending_result_display = False
        self.current_display_text = None

    def set_result_display(self, text):
        """結果表示フラグをセットする"""
        self.pending_result_display = True
        self.current_display_text = text

    # 時間を経過させる
    def handle_time_passage(self, step):
        minutes = int(step["value"])
        self.game_state.time -= minutes

    # 状態異常に対応
    def handle_status_effect(self):
        state_map = {"Shock":"ショックロール",
                     "Faint":"気絶",
                     "Dying":"死んでしまった",
                     "Temporary_madness":"一時的狂気",
                     "Indeterminate_madness":"不定の狂気"}
        for character, state in self.state_record.items():
            name = "あなた" if character == self.player else character.name

            # 死んだ場合
            if state == "Dying":
                text = f"{name}は死んでしまった。"
                self.create_text_step(text)
                if character == self.player:
                    # 主人公が死んだらエンディングへ
                    next_step = {"type":"ending", "next":"ending1"}
                    self.handle_scenario_event(next_step)
                    return
                else:
                    self.set_flag("girl", "alive", False)
                    self.set_flag("girl", "fellow", False)
                    self.set_flag("girl", "dice_check", False)
                    self.set_flag("girl", "carry", False)

            # 気絶した場合
            elif state == "Faint":
                text = f"{name}は気絶してしまった。"
                #self.create_text_step(text)
                #next_step = {"type":"result_text", "progression":"click"}
                #self.handle_scenario_event(next_step)

                # 気絶した時間 - 気絶する時間 = 気絶から目覚める時間
                faint_time = self.game_state.time
                dice_result = self.dice_service.roll("1d10")
                wait_duration = dice_result * 100
                recovery_time = faint_time - dice_result

                if character == self.player:
                    # 主人公が気絶したらブラックアウトする
                    self.render_manager.handle_black_out(wait_duration)
                    self.game_state.time = recovery_time
                    #self.handle_black_out(wait_duration, recovery_time)
                else:
                    self.set_flag("girl", "faint", recovery_time)
                    self.set_flag("girl", "dice_check", False)
                    # 主人公が気絶していない場合
                    if not self.is_blackout_active:
                        # 次のシナリオへ移行する
                        self.to_callback_next_scenario("Faint_ver_girl")

            # ショックロール判定を行う
            elif state == "Shock":
                # 判定を行う
                target = "player" if character == self.player else "girl"
                next_step = {"type":"dice_check", "check_type":"shock_roll", "target":target}
                self.handle_dice_check(next_step)

                # 結果表示
                #self.to_callback_next_scenario("result_text")
                #next_step = {"type":"result_text", "progression":"click"}
                #self.handle_scenario_event(next_step)
                
                # ショックロールを失敗した場合
                if character == self.player and not self.player_roll_result:
                    self.state_record[self.player] = "Faint"
                elif character == self.girl and not self.girl_roll_result:
                    self.state_record[self.girl] = "Faint"

                # 失敗してレコードが書き換えられている場合はもう一度状態異常のシナリオへ
                if self.state_record[character] != state:
                    self.to_callback_next_scenario("Status_effect")
                    return
                
                text = f"{name}はなんとか耐えた。"
                self.pending_result_display = True
                self.current_display_text = text
                    
        self.state_record = {}

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
        if sound_name in sound_manager.sounds:
            sound_manager.play(sound_name)
        else:
            print(f"その名前のサウンドは登録されていません。{sound_name}")  # デバッグ用

    # テキストを表示するステップを作成して表示する
    def create_text_step(self, text):
        next_step = {"type":"text", "text":text, "progression":"click"}
        self.handle_scenario_event(next_step)

    # コールバック関数に次のシナリオ名を渡す
    def to_callback_next_scenario(self, next_scenario):
        self.next_scenario_call_back(next_scenario)

    # 部屋移動イベント
    def move_to_room(self, room_id):
        self.render_manager.hidden_item_image()
        self.render_manager.hidden_girl_image()
        self.move_to_room_call_back(room_id)

    # 部屋の状態変化による再描画
    def room_new_view(self, room_id):
        self.render_manager.hidden_item_image()
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

    # ターゲットが誰かのチェック
    def target_check(self, target):
        player_flag, girl_flag = False, False

        # ターゲット指定が主人公のみの場合は主人公のみ
        if target == "player":
            player_flag = True

        # ターゲット指定が少女のみの場合は少女のみ
        elif target == "girl":
            girl_flag = True

        # ターゲット指定が両方の場合は両方
        elif target == "all":
            player_flag = True
            girl_flag = True

        # 指定が無い場合プレイヤーは固定、少女はフラグの状態によって決定する
        else:
            player_flag = True
            if self.girl_flag_check():
                girl_flag = True

        return player_flag, girl_flag

    # ダメージ計算
    def damage_calculator(self, dice_text):
        result = self.dice_service.roll(dice_text)
        return result

    # ダメージを受けるイベント
    def take_damage(self, character, status, damage):
        if status == "SAN":
            state = character.take_SAN_damage(int(damage))
        elif status == "HP":
            state = character.take_damage("event", int(damage))

        return state
        #if state:
        #    self.to_callback_next_scenario(state)

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


    # 表示する
    def draw(self, step=None):
        if self.current_display_text:
            self.render_manager.draw_text(self.current_display_text)
        else:
            self.text_frame_panel.set_text("")

        self.render_manager.draw()
