import re
from typing import List, Dict, Tuple, Any, Optional, Callable

from constans import SKILL_DATA_PATH, JSON_FOLDER, ITEM_LIST, State
from utils import load_json
from ui.ui_cache import ImageCache
from ui.ui_panels import TextFramePanel
from ui.ui_command import Command
from ui.log_view import LogView
from input.focus_manager import FocusManager
from .render_manager import RenderManager
from .dice_service import DiceService
from .event_processors.dice_processor import DiceProcessor
from .event_processors.damage_processor import DamageProcessor
from .event_processors.conditional_processor import ConditionalProcessor
from .event_processors.status_effect_processor import StatusEffectProcessor
from .event_processors.display_processor import DisplayProcessor

class EventManager:
    def __init__(self, screen, root, player=None, girl=None, game_state=None, flags=None, 
                 text_frame_panel: Optional[TextFramePanel]=None, log_view: Optional[LogView]=None, focus_manager: Optional[FocusManager]=None,
                 on_scenario_start_callback: Optional[Callable]=None, 
                 on_room_transition_callback: Optional[Callable]=None, on_room_refresh_callback: Optional[Callable]=None, on_scene_state_change_callback: Optional[Callable]=None):
        self.screen = screen
        self.screen_size = self.screen.get_size()
        self.root = root

        self.player = player
        self.girl = girl
        self.game_state = game_state
        self.flags = flags
        self.skill_list = load_json(SKILL_DATA_PATH, JSON_FOLDER)

        # コールバック関数
        self.on_scenario_start_callback = on_scenario_start_callback
        self.on_room_transition_callback = on_room_transition_callback
        self.on_room_refresh_callback = on_room_refresh_callback
        self.on_scene_state_callback = on_scene_state_change_callback

        # 表示関連
        self.image_cache = ImageCache()
        self.log_view = log_view if log_view else LogView(self.screen)
        self.text_frame_panel = text_frame_panel if text_frame_panel else TextFramePanel(self.screen, self.root)
        self.focus_manager = focus_manager if focus_manager else FocusManager(self.screen)
        self.render_manager = RenderManager(
            self.screen, 
            self.image_cache, 
            self.text_frame_panel, 
            self.log_view,
            self.focus_manager,
            next_scenario_cb=self.to_callback_next_scenario)

        # プロセッサー
        self.dice_service = DiceService()
        self.dice_processor = DiceProcessor(self.dice_service, self.skill_list, self.flags)
        self.damage_processor = DamageProcessor(self.dice_service, self.take_damage)
        self.conditional_processor = ConditionalProcessor(self.flags, self.game_state, self.to_callback_next_scenario)
        self.status_effect_processor = StatusEffectProcessor(self.dice_service, self.take_damage)
        self.display_processor = DisplayProcessor(self.render_manager)

        self.pending_result_display = False # 結果表示待ちフラグ
        self.pending_dice_check = None      # 分岐情報
        self.current_display_text = None    # 描画用の処理済みデータ
        
        # handle_damageで使用
        self.player_roll_result = None      # ダイスロールの結果
        self.girl_roll_result = None

        self.state_record = {}              # キャラクターの特殊状態の記録
        self.is_blackout_active = False     # ブラックアウト状態かどうか

    # シナリオから受け取ったイベントを進行する
    def handle_scenario_event(self, step: Dict[str, Any]):
        # 表示関連のステップ処理
        if step["type"] == "text":
            # display_processor で処理
            text = self.display_processor.process_display(step)

            # テキストが返ってきた場合のみ特殊処理
            if text is not None:
                self.current_display_text = text

                # 結果表示中でない場合のみ通常テキストを使用
                if self.pending_result_display:
                    return

        elif step["type"] in ["sound", "image_display", "image_hidden", "girl_display", "girl_hidden"]:
            # display_processor で処理
            self.display_processor.process_display(step)

            # 画像非表示のタイミングでテキストもクリア
            if step["type"] in ["image_hidden", "girl_hidden"]:
                self.current_display_text = None

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
    def handle_action(self, action: str, step: Dict[str, Any]):
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
                self.on_room_refresh_requested()

        # アイテムを取得する
        elif action == "get_item":
            target = step.get("target", None)
            item = ITEM_LIST[step["item"]]
            character = self.girl if target == "girl" else self.player
            character.add_item(item)

        # アイテムを手放す
        elif action == "lost_item":
            target = step.get("target", None)
            item = ITEM_LIST[step["item"]]
            character = self.girl if target == "girl" else self.player
            character.remove_item(item)

    # ダイスチェックをする
    def handle_dice_check(self, step: Dict[str, Any]):
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
    def handle_damage(self, step: Dict[str, Any]):
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

    # 保留中の分岐情報を取得してクリアする      
    def get_and_clear_pending_branch(self):
        if self.pending_dice_check:
            branch = self.pending_dice_check
            self.pending_dice_check = None
            return branch
        return None

    # 結果表示フラグをクリアする
    def clear_result_display(self):
        self.pending_result_display = False
        self.current_display_text = None

    # 結果表示フラグをセットする
    def set_result_display(self, text: str):
        self.pending_result_display = True
        self.current_display_text = text

    # 時間を経過させる
    def handle_time_passage(self, step: Dict[str, Any]):
        minutes = int(step["value"])
        self.game_state.time -= minutes

    # 状態異常に対応
    def handle_status_effect(self):
        characters = {"player": self.player,
                      "girl": self.girl}
        results = self.status_effect_processor.process_status_effects(self.state_record, characters, self.game_state)

        for result in results:
            text = result.get("text", None)
            if text:
                self.pending_result_display = True
                self.current_display_text = text
            
            if result["action"] == "black_out":
                self.render_manager.handle_black_out(result["wait_duration"])
                self.game_state.time = result["recovery_time"]                

            elif result["action"] == "need_dice_check":
                # ダイスチェック実行
                step = {
                    "type": "dice_check",
                    "check_type": result["type"],
                    "target": result["target"]
                    }
                self.handle_dice_check(step)

                character = result["character"]
                # ショックロールを失敗した場合
                if character == self.player and not self.player_roll_result:
                    self.state_record[self.player] = "Faint"
                elif character == self.girl and not self.girl_roll_result:
                    self.state_record[self.girl] = "Faint"

                # 失敗してレコードが書き換えられている場合はもう一度状態異常のシナリオへ
                if self.state_record[character] != "Shock":
                    self.to_callback_next_scenario("Status_effect")
                    return
                else:
                    # 成功した場合は成功シナリオに移動
                    if character == self.player:
                        self.to_callback_next_scenario("Shock_success_player")
                    else:
                        self.to_callback_next_scenario("Shock_success_girl")

            elif result["action"] == "set_flags":
                for flag in result["flags"]:
                    self.set_flag(flag["category"], flag["flag"], flag["value"])
                question = result.get("if_question", None)
                if question and question == "player_fainted":
                    if not self.render_manager.is_player_blackout_active():
                        self.to_callback_next_scenario(result["next"])

            elif result["action"] == "next_scenario":
                self.to_callback_next_scenario(result["next"])
        self.state_record = {}

    # フラグチェックを処理
    def handle_conditional(self, conditions: List[Dict[str, Any]]):
        for condition in conditions:
            # 全部のフラグがtrueだったら次のシナリオ
            if all(self.flag_check(flag) for flag in condition["flags"]):
                self.to_callback_next_scenario(condition["next"])
                break

    # テキストを表示するステップを作成して表示する
    def create_text_step(self, text: str):
        next_step = {"type":"text", "text":text, "progression":"click"}
        self.handle_scenario_event(next_step)

    # コールバック関数に次のシナリオ名を渡す
    def to_callback_next_scenario(self, next_scenario: str):
        self.on_scenario_start_callback(next_scenario)

    # 部屋移動イベント
    def move_to_room(self, room_id: str):
        self.render_manager.hidden_item_image()
        self.render_manager.hidden_girl_image()
        self.move_to_room_call_back(room_id)

    # 部屋の状態変化による再描画
    def on_room_refresh_requested(self):
        self.render_manager.hidden_item_image()
        self.on_room_refresh_callback()
        
    # エンディングに移行するためにコールバック関数にステータスを渡す
    def set_ending(self):
        self.on_scene_state_change_callback(State.CLOSE)

    # フラグをセットするイベント
    def set_flag(self, category: str, flag: str, value: Any):
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
    def target_check(self, target: str) -> Tuple[bool, bool]:
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
    def damage_calculator(self, dice_text: str) -> int:
        result = self.dice_service.roll(dice_text)
        return result

    # ダメージを受けるイベント
    def take_damage(self, character, status: str, damage: int|str) -> Optional[str]:
        if status == "SAN":
            state = character.take_SAN_damage(int(damage))
        elif status == "HP":
            state = character.take_damage("event", int(damage))

        return state
        #if state:
        #    self.to_callback_next_scenario(state)

    # イベントを処理（未完成※使用するか不明）
    def handle_event(self, event_name: str, event_data: Dict[str, Any]):
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

    # 部屋から本を持ちだそうとした際に起こるイベント（未完成）
    def handle_book_exit(self):
        """本を持ち出したときのイベント"""
        print("You tried to leave the room with the book!")

        # 戦闘を開始するイベントを発生
        self.handle_event("fight_start", enemy="Guardian")

    # 戦闘イベント
    def start_fight(self, enemy: str):
        """戦闘イベントを開始"""
        print(f"Starting fight with {enemy}")

    # フォーカス登録
    def register_all(self, focus_manager):
        self.render_manager.register_all(focus_manager)

    # フォーカス削除
    def unregister_all(self, focus_manager):
        self.render_manager.unregister_all(focus_manager)

    # 表示する
    def draw(self):
        if self.current_display_text:
            self.render_manager.draw_text(self.current_display_text)
        else:
            self.text_frame_panel.set_text("")

        self.render_manager.draw()
