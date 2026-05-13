from typing import Dict, Tuple, Any, Optional

from constans import SKILL_DATA_PATH, JSON_FOLDER, State
from utils import load_json
from ui.ui_cache import ImageCache
from ui.ui_panels import TextFramePanel
from ui.ui_command import Command
from ui.log_view import LogView
from input.focus_manager import FocusManager
from .render_manager import RenderManager
from .event_callbacks import EventCallbacks
from .dice_service import DiceService
from .event_processors.dice_processor import DiceProcessor
from .event_processors.damage_processor import DamageProcessor
from .event_processors.conditional_processor import ConditionalProcessor
from .event_processors.status_effect_processor import StatusEffectProcessor
from .event_processors.display_processor import DisplayProcessor
from .event_processors.action_processor import ActionProcessor

class EventManager:
    def __init__(self, screen, root, player=None, girl=None, game_state=None, flags=None, 
                 text_frame_panel: Optional[TextFramePanel]=None, log_view: Optional[LogView]=None, focus_manager: Optional[FocusManager]=None,
                 callbacks: Optional[EventCallbacks]=None):
        self.screen = screen
        self.screen_size = self.screen.get_size()
        self.root = root

        self.player = player
        self.girl = girl
        self.game_state = game_state
        self.flags = flags
        self.skill_list = load_json(SKILL_DATA_PATH, JSON_FOLDER)

        # コールバック関数
        self.callbacks = callbacks if callbacks else EventCallbacks()

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
        self.action_processor = ActionProcessor(self.player, self.girl, self.flags, self.callbacks.on_room_refresh, self.move_to_room)

        self.pending_result_display = False # 結果表示待ちフラグ
        self.pending_dice_check = None      # 分岐情報
        self.current_display_text = None    # 描画用の処理済みデータ
        
        # handle_damageで使用
        self.player_roll_result = None      # ダイスロールの結果
        self.girl_roll_result = None

        self.state_record = {}              # キャラクターの特殊状態の記録

        self.event_handlers = {
            "text": self.handle_text,
            "sound": self.display_processor.process_display,
            "image_display": self.display_processor.process_display,
            "image_hidden": self.display_processor.process_display,
            "girl_display": self.display_processor.process_display,
            "girl_hidden": self.display_processor.process_display,
            "next_step": self.handle_next_step,
            "action": self.action_processor.process_action,
            "time_passage": self.handle_time_passage,
            "dice_check": self.handle_dice_check,
            "damage": self.handle_damage,
            "status_effect": self.handle_status_effect,
            "girl_check": self.handle_girl_check,
            "conditional": self.handle_conditional,
            "interaction": self.handle_interaction,
            "ending": self.handle_ending
        }

        self.delete_display_text_action = ["image_hidden", "girl_hidden", "action", "conditional", "time_passage", "status_effect"]

    # シナリオから受け取ったイベントを進行する
    def handle_scenario_event(self, step: Dict[str, Any]):
        handler = self.event_handlers.get(step["type"], None)
        if handler:
            handler(step)

            if step["type"] in self.delete_display_text_action:
                self.current_display_text = None

    # テキストの処理
    def handle_text(self, step: Dict[str, Any]):
        # display_processor で処理
        text = self.display_processor.process_display(step)

        # テキストが返ってきた場合のみ特殊処理
        if text is not None:
            self.current_display_text = text

            # 結果表示中でない場合のみ通常テキストを使用
            if self.pending_result_display:
                return

    # 次のシナリオに進む
    def handle_next_step(self, step: Dict[str, Any]):
        self.current_display_text = None
        self.to_callback_next_scenario(step["next"])

    # ダイスチェックをする
    def handle_dice_check(self, step: Dict[str, Any]):
        check_status = None
        player_check_result, girl_check_result = None, None
        result_text = ""

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

        # SANチェックと毒対抗ロールとショックロールは各キャラクター毎に結果が異なるので成功、失敗の結果分岐をしない
        if step["check_type"] in ["SANチェック", "毒対抗ロール", "shock_roll"]:
            self.player_roll_result = player_check_result
            self.girl_roll_result = girl_check_result

            result_text = self.dice_processor.build_result_text(step, check_status, result_text)

            self.pending_dice_check = None  # 分岐情報なし

            # 結果表示フラグを立てる
            self.pending_result_display = True
            self.current_display_text = result_text
        else:
            # どちらかのダイス結果が成功していれば成功の結果表示、どちらも失敗していれば失敗の結果表示をする
            success = player_check_result or girl_check_result
            result_text = self.dice_processor.build_result_text(step, check_status, result_text, branch_flag=True, success=success)

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

    # 時間を経過させる
    def handle_time_passage(self, step: Dict[str, Any]):
        minutes = int(step["value"])
        self.game_state.time -= minutes

    # 状態異常に対応
    def handle_status_effect(self, step: Dict[str, Any]):
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
    def handle_conditional(self, step: Dict[str, Any]):
        conditions = step["conditions"]
        result = self.conditional_processor.process_conditional(conditions, step.get("conditional_type", None))
        if result is not None:
            if "text" in result:
                self.pending_result_display = True
                self.current_display_text = result["text"]

            if "image" in result:
                self.render_manager.show_item_image(result["image"])

            if "girl_image" in result:
                self.render_manager.show_girl_image(result["state"], result["position"])

            if "item" in result:
                self.action_processor.process_action({"action": "get_item", "item": result["item"], "target": "player"})

            if "flag" in result:
                self.action_processor.process_action({"action": "set_flag", "flag": result["flag"]})

            if "next" in result and result["next"] is not None:
                self.to_callback_next_scenario(result["next"])

        if step.get("next", None):
            self.to_callback_next_scenario(step["next"])

    # コマンドメニューを作成
    def handle_interaction(self, step: Dict[str, Any]):
        commands = []
        for cmd in step["interactions"]:
            if "show_if" in cmd:
                flag = cmd["show_if"]
                if all(self.conditional_processor.check_flag(key, value) for key, value in flag.items()):
                    commands.append(Command(cmd["text"], cmd["next"]))
            else:
                commands.append(Command(cmd["text"], cmd["next"]))
        target = step.get("target", None)
        self.render_manager.set_command_menu(commands, target)

    # 少女の同行チェック
    def handle_girl_check(self, step: Dict[str, Any]):
        result = "true" if self.girl_fellow_check() else "false"
        self.current_display_text = None
        self.to_callback_next_scenario(step[result])

    def handle_ending(self, step: Dict[str, Any]=None):
        self.current_display_text = None
        self.set_ending()

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

    # テキストを表示するステップを作成して表示する
    def create_text_step(self, text: str):
        next_step = {"type":"text", "text":text, "progression":"click"}
        self.handle_scenario_event(next_step)

    # コールバック関数に次のシナリオ名を渡す
    def to_callback_next_scenario(self, next_scenario: str):
        self.callbacks.on_scenario_start(next_scenario)

    # 部屋移動イベント
    def move_to_room(self, room_id: str):
        self.game_state.time -= 2
        self.render_manager.hidden_item_image()
        self.render_manager.hidden_girl_image()
        self.callbacks.on_room_transition(room_id)

    # 部屋の状態変化による再描画
    def on_room_refresh_requested(self):
        self.render_manager.hidden_item_image()
        self.callbacks.on_room_refresh()
        
    # エンディングに移行するためにコールバック関数にステータスを渡す
    def set_ending(self):
        self.callbacks.on_scene_state_change(State.CLOSE)

    # 少女が一緒にいるかどうかのフラグチェック
    def girl_fellow_check(self):
        return self.flags.get_flag("girl", "fellow")

    # 少女に参加してもらうかのフラグチェック
    def girl_flag_check(self):
        return self.flags.get_flag("girl", "dice_check")

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

    # ダメージを受けるイベント
    def take_damage(self, character, status: str, damage: int|str) -> Optional[str]:
        if status == "SAN":
            state = character.take_SAN_damage(int(damage))
        elif status == "HP":
            state = character.take_damage("event", int(damage))

        return state

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

    def relayout(self, screen):
        self.screen = screen
        self.screen_size = screen.get_size()
        self.render_manager.relayout(screen)

    # 表示する
    def draw(self):
        if self.current_display_text:
            self.render_manager.draw_text(self.current_display_text)
        else:
            self.text_frame_panel.set_text("")

        self.render_manager.draw()
