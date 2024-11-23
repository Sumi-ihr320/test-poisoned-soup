from utils import TextDraw, load_json, opposition_percent
from ui_elements import DiceRoll

class ScenarioManager:
    def __init__(self, screen, scenario_id):
        self.screen = screen

        # シナリオをロード
        self.scenario_data = load_json("Scenario.json")
  
        self.current_scenario = None
        self.current_index = 0      # 現在の表示位置

        self.is_active = False
    
        self.start_scenario(scenario_id)


    # 指定したシナリオを開始
    def start_scenario(self, scenario_id):
            self.current_scenario = self.scenario_data.get(scenario_id, [])
            self.current_index = 0
            print(f"シナリオ開始：{scenario_id}")
            self.is_active = True

    # 次のシナリオステップを進める
    def next(self):
        if not self.current_scenario or self.current_index >= len(self.current_scenario):
            print("シナリオ終了")       # デバッグ用
            self.current_scenario = None
            self.is_active = False
            return

        # ステップを進める        
        step = self.current_scenario[self.current_index]
        self.current_index += 1

        if step["type"] == "text":
            self.display_text(step["text"])

        elif step["type"] == "action":
            self.perform_action(step)

        elif step["type"] == "dice":
            self.perform_dice_roll(step)
    
    # 現在のテキストを描画する
    def display_text(self, text):
        TextDraw(self.screen, text)

    # 外部アクションをトリガー
    def perform_action(self, step):
        action = step["action"]
        item_id = step.get("item_id", None)
        print(f"アクション：{action}, アイテム：{item_id}")

    # ダイスロールを処理
    def perform_dice_roll(self, step, hero_data):
        dice_text = step["dice"]
        check_type = step["check_type"]
        if check_type == "VS_active":
            active = step["status"]
            passive = step["enemy_status"]
            threshold = opposition_percent(active, passive)

        elif check_type == ["VS_passive"] :
            active = step["enemy_status"]
            passive = step["status"]
            threshold = opposition_percent(active, passive)
        
        elif check_type == ["skill"]:
            skill = step["skill"]
            threshold = hero_data["skill"][skill]

        dice = DiceRoll(dice_text)
        result = dice.check(threshold)

        # 成否判定に応じた次のシナリオを開始
        if result:
            self.display_text(f"{dice.result} / {threshold}  成功！")
            self.start_scenario(step["success"])
        else:
            self.display_text(f"{dice.result} / {threshold}  失敗！")
            self.start_scenario(step["failure"])

    # 現在のステップを再描画
    def draw(self):
        if self.is_active and self.current_index > 0:
            step = self.current_scenario[self.current_index - 1]
            if step["type"] == "text":
                self.display_text(step["text"])