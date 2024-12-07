from utils import TextDraw, load_scenario, opposition_percent
from ui_elements import DiceRoll

class ScenarioManager:
    def __init__(self, screen, scenario_id, flags, on_action=None):
        self.screen = screen
        self.flags = flags

        # シナリオをロード
        self.scenario_data = {}
        self.load_scenario_file()
  
        self.current_scenario = None
        self.current_index = 0      # 現在の表示位置

        self.roll_result = None
        self.threshold = None
        self.damage_point = None

        self.is_active = False
        self.on_action = on_action  # アクション発生時のコールバック
    
        self.start_scenario(scenario_id)

    # シナリオを各ファイルからロードして統合する
    def load_scenario_file(self):
        scenario_files = [
            "Opening.json",
            "CenterRoom.json",
            "Door.json",
            "Light.json",
            "Soup.json",
            "CenterMemo.json",
            "EastRoom.json",
            "SouthRoom.json",
            "WestRoom.json"
        ]
        for file_path in scenario_files:
            scenario_data = load_scenario(file_path)
            self.scenario_data.update(scenario_data)

    # 指定したシナリオを開始
    def start_scenario(self, scenario_id):
        self.current_scenario = self.scenario_data.get(scenario_id, [])
        self.current_index = 0
        print(f"シナリオ開始：{scenario_id}")
        self.is_active = True

    # 次のシナリオステップを進める
    def update(self):
        if not self.current_scenario or self.current_index >= len(self.current_scenario):
            print("シナリオ終了")       # デバッグ用
            self.current_scenario = None
            self.is_active = False
            return

        # ステップを進める        
        step = self.current_scenario[self.current_index]
        self.current_index += 1

        if step["type"] == "text":
            text = step["text"]
            if "\{" in text:
                text = self.process_text_template(text)
            self.display_text(text)

        elif step["type"] == "next_step":
            self.start_scenario(step["next"])

        elif step["type"] == "action":
            self.handle_action(step)

        elif step["type"] == "dice_check":
            self.roll_result, self.threshold = self.handle_dice_roll(step)

        elif step["type"] == "interaction":
            pass

        elif step["type"] == "conditional":
            self.handle_conditional(step["conditions"])
        
        
    # 現在のテキストを描画する
    def display_text(self, text):
        TextDraw(self.screen, text)

    # テンプレートにダイス結果等を表示
    def process_text_template(self, text_tamplate):
        if "\{roll\}" in text_tamplate and self.roll_result is not None:
            text = text_tamplate.format(roll=self.roll_result, threshold=self.threshold)
        elif "\{damage\}" in text_tamplate:
            text = text_tamplate.format(damage=self.damage_point)
        else:
            text = text_tamplate
        return text

    # 外部アクションをトリガー
    def handle_action(self, step):
        action = step["action"]
        if self.on_action:
            self.on_action(action, step)
        
    # ダイスロールを処理
    def handle_dice_roll(self, step, hero_data):
        dice_text = step["dice"]
        check_type = step["check_type"]
        if check_type == "VS_active":
            active = hero_data[step["status"]]
            passive = step["enemy_status"]
            threshold = opposition_percent(active, passive)

        elif check_type == ["VS_passive"] :
            active = step["enemy_status"]
            passive = hero_data[step["status"]]
            threshold = opposition_percent(active, passive)
        
        elif check_type == ["skill"]:
            skill = step["skill"]
            threshold = hero_data["skill"][skill]
        
        elif check_type == ["SAN"]:
            threshold = hero_data["SAN"]

        dice = DiceRoll(dice_text)
        roll_result = dice.check(threshold)

        return roll_result, threshold
        
    # フラグチェックを処理
    def handle_conditional(self, conditions):
        for condition in conditions:
            # 全部のフラグがtrueだったら次のシナリオ
            if all(self.flag_check(flag) for flag in condition["flags"]):
                self.start_scenario(condition["next"])
                return
        
    # フラグをチェックする
    def flag_check(self, flags):
        flag_name = flags["flag_name"]
        item = flags["item"]
        flag = flags["flag"]
        value = flags["value"]

        # flag_nameがある場合
        if flag_name:

            # item がある場合
            if item and self.flags.get(flag_name.get(item[flag])) == value:
                return True

            # item がない場合
            if not item and self.flags.get[flag_name.get(flag)] == value:
                return True

        # flag_nameがない場合
        elif self.flags[flag] == value:
            return True
        
        return False

    # 現在のステップを再描画
    def draw(self):
        if self.is_active and self.current_index > 0:
            step = self.current_scenario[self.current_index - 1]
            if step["type"] == "text":
                self.display_text(step["text"])