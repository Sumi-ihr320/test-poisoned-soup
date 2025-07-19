from constans import SCENARIO_FILES, SCENARIO
from utils import load_json

class ScenarioManager:
    def __init__(self, screen, event_manager, scenario_id):
        self.screen = screen

        self.event_manager = event_manager

        # シナリオをロード
        self.scenario_data = {}
        self.load_scenario_file()
  
        self.current_scenario = None
        self.current_index = 0          # 現在の表示位置

        self.is_active = False

        self.wait_for_click = False     # クリック待ちフラグ

        self.start_scenario(scenario_id)

    # シナリオを各ファイルからロードして統合する
    def load_scenario_file(self):
        for file_path in SCENARIO_FILES:
            scenario_data = load_json(SCENARIO, file_path)
            self.scenario_data.update(scenario_data)

    # 指定したシナリオを開始
    def start_scenario(self, scenario_id):
        self.current_scenario = self.scenario_data.get(scenario_id, [])
        self.current_index = 0
        self.wait_for_click = False
        print(f"シナリオ開始：{scenario_id}")   # デバッグ用
        self.is_active = True

        if self.current_scenario:
            step = self.scenario_progress()
            if step:
                self.event_manager.draw(step)

    # シナリオ進行
    def scenario_progress(self):
        step = self.current_scenario[self.current_index]

        # 進行タイプに応じて処理を分岐
        progression = step.get("progression", "auto")       # デフォルトは自動進行

        # クリック待ちの場合は進行を停止
        if progression == "click" and self.wait_for_click:
            return None

        # 現在のステップがclickならクリック待ち状態を設定
        self.wait_for_click = progression == "click"
        return step

    # 次のシナリオステップを進める
    def update(self):
        if not self.current_scenario or self.current_index >= len(self.current_scenario):
            print("シナリオ終了")               # デバッグ用
            self.current_scenario = None
            self.is_active = False
            return

        step = self.scenario_progress()
        if not step:
            return

        # 次のステップに進む
        self.current_index += 1

        # イベント処理をevent_managerに委譲
        self.event_manager.handle_scenario_event(step)

    # クリックイベントを処理
    def on_click(self):
        if self.wait_for_click:
            # クリック待ちを解除して次のステップへ
            self. wait_for_click = False

            # ダイスチェックなら分岐ジャンプする
            if hasattr(self.event_manager, "last_dice_step"):
                step = self.event_manager.last_dice_step
                result = self.event_manager.dice_check_result
                next_id = step["success"] if result else step["failure"]
                del self.event_manager.last_dice_step
                self.start_scenario(next_id)
                return

            # ダメージによって状態異常が起こった場合
            elif self.event_manager.state_record:
                next_id = "Status_effect"
                self.start_scenario(next_id)
                return

            self.update()

    # 現在のステップの描画をイベントマネージャーに依頼
    def draw(self):
        if self.event_manager.girl_image:
            self.event_manager.girl_image.draw()
            
        if self.event_manager.item_image:
            self.event_manager.item_image.draw()

        if self.is_active and self.current_index < len(self.current_scenario):
            step = self.current_scenario[self.current_index]
            self.event_manager.draw(step)
