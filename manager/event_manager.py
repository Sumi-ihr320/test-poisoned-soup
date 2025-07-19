import re

from constans import *
from ui.ui_elements import CommandMenu, DiceRoll, Image
from utils import *
from .sound_manager import SoundManager

class EventManager:
    def __init__(self, screen, player=None, girl=None, game_state=None, flags=None,
                 next_scenario_call_back=None, move_to_room_call_back=None, room_new_view=None, set_state=None):
        self.screen = screen
        self.window_size = self.screen.get_size()
        self.player = player
        self.girl = girl
        self.game_state = game_state
        self.flags = flags
        self.skill_list = load_json(JSON_FOLDER, SKILL_DATA_PATH)

        # コールバック関数
        self.next_scenario_call_back = next_scenario_call_back
        self.move_to_room_call_back = move_to_room_call_back
        self.room_new_view_call_back = room_new_view
        self.set_state_call_back = set_state

        # サウンドマネージャー
        self.sound_manager = SoundManager()

        self.command_menu = None
        self.item_image = None

        # 少女の立ち絵
        self.girl_image = None

        self.player_roll_result = None     # ダイスロールの結果
        self.girl_roll_result = None
        self.result_text = None             # 結果の表示テキスト
        self.dice_check_result = None       # ダイスロールの総合結果
        self.damage_point = None    # ダメージポイント
        self.state_record = {}      # キャラクターの特殊状態の記録        self.blackout_index = 5

        self.blackout_index = 6         # ブラックアウト画像のインデックス
        self.blackout_timer = None      # ブラックアウトのタイマー
        self.blackout_phase = None      # ブラックアウトのフェーズ
        self.blackout_wait = None       # ブラックアウトの待ち時間
        self.blackout_done = False      # ブラックアウトの完了フラグ
        self.is_blackout_active = False  # ブラックアウトの状態フラグ
        self.next_after_black_out = {}    # ブラックアウトの後のステップ

    # コマンドメニューの生成
    def create_command_menu(self, commands):
        if commands:
            start_position = self.get_position()
            self.command_menu = CommandMenu(self.screen, commands, start_position)

    # 画像イメージの作成
    def create_image(self, file_name):
        size = 0.6 if "Memo" in file_name or file_name == "Book1" else (0.5 if "center-room_Light" in file_name else 0.35)
        self.item_image = Image(self.screen, file_name, size, x="center", centery=200, line_flag=True, bg_flag=True)

    # 少女の立ち絵の作成
    def create_girl(self, state=None, position="right"):
        if state:
            file_name = f"Girl_{state}.png"
        else:
            file_name = "Girl.png"
        percent_w, percent_h = RATIO[self.window_size]
        scale = 0.6 * percent_h
        frame_rect = get_frame_rect(self.screen)
        x = 500 if position == "right" else (100 if position == "left" else "center")
        if x != "center":
            x = x * percent_w
        self.girl_image = Image(self.screen, file_name, scale, x, frame_rect.top, position="bottom")

    # コマンドメニューの表示位置を取得
    def get_position(self):
        #self.window_size = self.screen.get_size()
        max_x, max_y = self.window_size[0] // 4 * 3, self.window_size[1] // 2      # これ以上端に配置すると見えなくなる

        # コマンド表示の指標となる画像位置。クリック時画像があればそこを起点とする。
        if self.item_image:
            image_rect = self.item_image.rect

            # 画像の右側にコマンドボタンを表示する。最大値以上になる場合は左側に配置する。
            x = image_rect.right + 30 if (image_rect.right + 30) <= max_x else image_rect.x - 130
            y = image_rect.y if image_rect.y <= max_y else image_rect.y - 50
        else:
            x, y = self.window_size[0]//2 + 120, 100

        return (x, y)

    # シナリオから受け取ったイベントを進行する
    def handle_scenario_event(self, step):
        # テキストを表示する
        if step["type"] == "text" or step["type"] == "result_text":
            self.draw(step)
            #text = step["text"]
            #self.display_text(text)

        # 結果を表示する
        #elif step["type"] == "result_text":
        #    self.draw(step)

        # 次のシナリオに進む
        elif step["type"] == "next_step":
            self.to_callback_next_scenario(step["next"])
        
        # アクションを起こす
        elif step["type"] == "action":
            action = step["action"]
            self.handle_action(action, step)

        # 時間経過を行う
        elif step["type"] == "time_passage":
            self.handle_time_passage(step)

        # ダイスチェックを行う
        elif step["type"] == "dice_check":
            self.handle_dice_check(step)

        # ダメージを計算する
        elif step["type"] == "damage":
            self.handle_damage(step)

        # 状態変化を行う
        elif step["type"] == "status_effect":
            self.handle_status_effect()

        # 少女が一緒にいるかのチェック
        elif step["type"] == "girl_check":
            result = "true" if self.girl_fellow_check() else "false"
            self.to_callback_next_scenario(step[result])

        # フラグによる分岐をおこなう
        elif step["type"] == "conditional":
            self.handle_conditional(step["conditions"])

        # コマンドを表示する
        elif step["type"] == "interaction":
            self.create_command_menu(step["interactions"])

        # 画像を表示する
        elif step["type"] == "image_display":
            self.create_image(step["image"])

        # 画像を非表示にする
        elif step["type"] == "image_hidden":
            self.item_image = None

        # 少女の立ち絵を表示する
        elif step["type"] == "girl_display":
            state = step.get("state", None)
            position = step.get("position", "right")
            self.create_girl(state, position)

        # 少女の立ち絵を非表示にする
        elif step["type"] == "girl_hidden":
            self.girl_image = None

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

        # ダメージを受ける
        elif action == "damage":
            status = step.get("status", None)
            damage = step.get("damage", None)
            if damage == "damage_point" and self.damage_point:
                damage = self.damage_point
            self.take_damage(status, damage)

        # アイテムを取得する
        elif action == "get_item":
            target = step.get("target", None)
            item = ITEM_LIST[step["item"]]
            character = self.girl if target == "girl" else self.player
            character.add_item(item)
            self.result_text = f"{character.name}は{item.name}を手に入れた。"
            #self.to_callback_next_scenario("result_text")

        # アイテムを手放す
        elif action == "lost_item":
            target = step.get("target", None)
            item = ITEM_LIST[step["item"]]
            character = self.girl if target == "girl" else self.player
            character.remove_item(item)
            self.result_text = f"{character.name}は{item.name}を失った。"
            #self.to_callback_next_scenario("result_text")

    # ダイスチェックをする
    def handle_dice_check(self, step):
        check_status = None
        player_check_result, girl_check_result = None, None
        result_text = ""
        status_text = ""

        # ダイスチェックのターゲット指定がもしあればそのキャラクターだけ行う
        player_flag, girl_flag = self.target_check(step)

        if player_flag:
            check_status, player_check_result, result_text = self.handle_dice_roll(step, self.player)

        if girl_flag:
            check_status, girl_check_result, text= self.handle_dice_roll(step, self.girl)
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
            self.result_text = result_text
        else:
            # どちらかのダイス結果が成功していれば成功の結果表示、どちらも失敗していれば失敗の結果表示をする
            if player_check_result or girl_check_result:
                self.dice_check_result = True
                self.result_text = f"《{status_text}》 ⇒ 成功！\n" + result_text
            else:
                self.dice_check_result = False
                self.result_text = f"《{status_text}》 ⇒ 失敗！\n" + result_text
            self.last_dice_step = step
            #self.to_callback_next_scenario("result_text")
        

    # ダイスロールを処理
    def handle_dice_roll(self, step, character):
        dice_text = step.get("dice", "1d100")
        check_type = step["check_type"]
        half = step.get("half", False)      # 半分の値でチェックする
        status = step.get("status", step.get("skill", None))

        if check_type == "VS_active":
            active = getattr(character, status)
            passive = step["enemy_status"]
            threshold = opposition_percent(active, passive)

        elif check_type == "VS_passive":
            active = step["enemy_status"]
            passive = getattr(character, status)
            threshold = opposition_percent(active, passive)

        elif check_type == "毒対抗ロール":
            active = step["POT"]
            status = "CON"
            passive = getattr(character, status)
            threshold = opposition_percent(active, passive)

        elif check_type == "shock_roll":
            status = "CON"
            threshold = getattr(character, status) * 5

        elif check_type == "SANチェック":
            status = "SAN"
            threshold = getattr(character, status)


        elif check_type == "skill":
            #skill = step["skill"]
            threshold = character.skill.get(status, self.skill_list[status])

        elif check_type == "status":
            check_list = {"回避":"Dodge",
                          "幸運":"Luck"}
            status = check_list.get(status, status)
            threshold = getattr(character, status)
        
        if half:
            threshold = threshold // 2

        dice = DiceRoll(dice_text)
        check_result = dice.check(threshold)

        result_text = f"{character.name}：成功！ <color=blue>{dice.result}<color/>/{threshold}" if check_result == True else f"{character.name}：失敗！ <color=red>{dice.result}<color/>/{threshold}"
        return status, check_result, result_text

    # ダメージ計算をして表示するテキストを作成する
    def handle_damage(self, step):
        self.result_text = ""
        self.state_record = {}

        # 誰がダメージを受けるのか
        characters = {}
        player_flag, girl_flag = self.target_check(step)
        if player_flag:
            characters[self.player] = self.player_roll_result
        if girl_flag:
            characters[self.girl] = self.girl_roll_result

        value = step.get("value", None)
        status = step.get("status", None)
        failure_text = step.get("text", "")

        # ダメージを受ける人数分繰り返す
        for character, roll_result in characters.items():

            # 半分のダメージを受ける場合
            if value == "1/2":
                status_point = getattr(character, status)
                damage_point = status_point // 2

            # 成否によるダメージの値を取得する
            elif "/" in value:
                success, failure = value.split("/")
                # dが入っていればダイスロールで値を出す
                if "d" in failure:
                    damage_point = self.damage_calculator(failure)
                else:
                    damage_point = int(failure)
                success = int(success)

            # 固定ダメージの場合はそのまま
            else:
                damage_point = value

            # どのステータスが減るか
            if status:
                # SANチェック後の正気度ダメージの場合
                if status == "SAN":
                    if roll_result:
                        if success == 0:
                            text = f"{character.name}は正気度が減らずに済んだ"
                        else:
                            state = self.take_damage(character, status, success)
                            text = f"{character.name}は{success}ポイントの正気度を失った"
                    else:
                        state = self.take_damage(character, status, damage_point)
                        text = f"{character.name}は{damage_point}ポイントの正気度を失った"

                else:
                    state = self.take_damage(character, status, damage_point)
                    text = f"{character.name}は{damage_point}ポイントのダメージを受けた"

                # ダメージの量によって何らかの特殊状態になった場合(狂気、ショック、気絶、死亡)
                if state:
                    self.state_record[character] = state

            # 表示するテキスト
            if self.result_text:
                self.result_text = f"{self.result_text}\n{text}"
            else:
                self.result_text = text

        if failure_text:
            self.result_text = f"{failure_text}\n{self.result_text}"


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
                self.result_text = f"{name}は死んでしまった。"
                self.create_text_step(self.result_text)
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
                self.result_text = f"{name}は気絶してしまった。"
                #self.create_text_step(self.result_text)
                #next_step = {"type":"result_text", "progression":"click"}
                #self.handle_scenario_event(next_step)

                # 気絶した時間 - 気絶する時間 = 気絶から目覚める時間
                faint_time = self.game_state.time
                dice_roll = DiceRoll("1d10")
                wait_duration = dice_roll * 100
                recovery_time = faint_time - dice_roll.result

                if character == self.player:
                    # 主人公が気絶したらブラックアウトする
                    self.handle_black_out(wait_duration, recovery_time)
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
                
                self.result_text = f"{name}はなんとか耐えた。"
                self.to_callback_next_scenario("result_text")
                    
        self.state_record = {}

    # フラグチェックを処理
    def handle_conditional(self, conditions):
        for condition in conditions:
            # 全部のフラグがtrueだったら次のシナリオ
            if all(self.flag_check(flag) for flag in condition["flags"]):
                self.to_callback_next_scenario(condition["next"])
                break

    # ブラックアウト処理
    def handle_black_out(self, wait_duration, recovery_time):
        # 画像の拡大率を計算する
        parcent = RATIO[self.window_size][1]
        scale = 0.2 * parcent
        # 画像の表示位置を得る
        room_rect = get_room_rect(self.screen)

        # 徐々に黒になる画像0～5を用意する
        image_paths = [f"to_black{i}.png" for i in range(6)]
        self.blackout_images = []
        for path in image_paths:
            self.blackout_images.append(Image(self.screen, path, scale, centerx=room_rect.centerx, centery=room_rect.centery))
        self.blackout_index = 5

        # タイマー
        self.blackout_timer = pygame.time.get_ticks()

        # フェーズ
        self.blackout_phase = "fade_out"

        # 待ち時間
        self.blackout_wait = wait_duration

        # ブラックアウト完了フラグ
        self.blackout_done = False

        # UI表示のための状態フラグ
        self.is_blackout_active = True

        # ゲーム時間の進行処理
        self.game_state.time = recovery_time

        # 次ステップ遷移を予約しておく
        self.next_after_black_out = {"type":"text", "text":f"しばらく経ったあとあなたは目を覚ました。", "progression":"click"}

    # サウンド処理
    def handle_sound(self, step):
        sound_name = step["name"]
        if self.sound_manager:
            if not self.sound_manager.sounds or (sound_name not in self.sound_manager.sounds):
                self.sound_manager.load_sound(sound_name, step["path"], step.get("loop", False))
            self.sound_manager.play(sound_name)

    # テキストを表示するステップを作成して表示する
    def create_text_step(self, text):
        next_step = {"type":"text", "text":text, "progression":"click"}
        self.handle_scenario_event(next_step)

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
        self.girl_image = None
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

    # ターゲットが誰かのチェック
    def target_check(self, step):
        target = step.get("target", None)
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
        dice = DiceRoll(dice_text)
        return dice.result

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

    # 少女がクリックされた際に実行
    def handle_girl_click(self, pos):
        if self.girl_image:
            if self.girl_image.rect.collidepoint(pos):
                pass
        pass

    # 表示する
    def draw(self, step):
        # ブラックアウトの処理
        if self.is_blackout_active:
            now = pygame.time.get_ticks()

            if self.blackout_phase == "fade_out":
                if now - self.blackout_timer > 100:
                    self.blackout_index -= 1
                    self.blackout_timer = now

                    # 画像が最後の1枚になったら
                    if self.blackout_index <= 0:
                        self.blackout_phase == "black"
                        self.blackout_timer = now

                self.blackout_images[self.blackout_index].draw()
            
            elif self.blackout_phase == "black":
                if now - self.blackout_timer > self.blackout_wait:
                    self.blackout_phase = "fade_in"
                    self.blackout_index = 0
                    self.blackout_timer = now
            
            elif self.blackout_phase == "fade_in":
                if now - self.blackout_timer > 100:
                    self.blackout_index += 1
                    self.blackout_timer = now
                    if self.blackout_index >= len(self.blackout_images):
                        self.is_blackout_active = False
                        # ブラックアウトが終了したら目覚めのシナリオへ
                        self.to_callback_next_scenario("Wake_up")
                        return
                self.blackout_images[self.blackout_index].draw()
            return

        # テキストを表示する
        if step["type"] == "text":
            self.display_text(step["text"])

        # 結果を表示する
        elif step["type"] == "result_text" and self.result_text:
            self.display_text(self.result_text)
        
        # コマンドメニューを表示する
        elif step["type"] == "interaction" and self.command_menu:
            self.command_menu.draw()