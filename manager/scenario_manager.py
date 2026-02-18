from constans import SCENARIO_FILES
from utils import load_and_normalize_json

class ScenarioManager:
    def __init__(self, screen, event_manager, scenario_id, auto_start=True):
        self.screen = screen

        self.event_manager = event_manager

        # シナリオをロード
        self.scenarios_by_id = {}
        self.load_all_scenarios()
  
        self.current_scenario_id = ""       # 現在再生中のシナリオID
        self.current_steps = None  # 現在進行中のsteps
        self.current_index = 0              # 現在のstepの表示index
        self.display_index = 0            # 表示用のindex 

        self.is_active = False

        self.wait_for_click = False         # クリック待ちフラグ

        if auto_start and scenario_id:
            self.start_scenario(scenario_id)

    # シナリオを各ファイルからロードして統合する
    def load_all_scenarios(self):
        for file_path in SCENARIO_FILES:
            scenarios_by_id = load_and_normalize_json(file_path, full_path=False)
            self.scenarios_by_id.update(scenarios_by_id)

    # 指定したシナリオを開始
    def start_scenario(self, scenario_id):
        self.current_scenario_id = scenario_id
        self.current_steps = self.scenarios_by_id.get(scenario_id, [])
        self.current_index = 0
        self.display_index = 0
        self.wait_for_click = False
        print(f"シナリオ開始：{scenario_id}")   # デバッグ用
        self.is_active = True

        if self.current_steps:
            step = self.scenario_progress()
            if step:
                self.display_index = self.current_index
                self.event_manager.handle_scenario_event(step)
                # 結果表示中なら即クリック待ち
                if self.event_manager.pending_result_display:
                    self.wait_for_click = True

    # シナリオ進行
    def scenario_progress(self):
        step = self.current_steps[self.current_index]

        print(f"[DEBUG] シナリオ進行: {step}")

        # 結果表示中は強制的にクリック待ち
        if self.event_manager.pending_result_display:
            self.wait_for_click = True
            print(f" クリック待ち中: {self.wait_for_click}")
            return None

        # 進行タイプに応じて処理を分岐
        progression = step.get("progression", "auto")       # デフォルトは自動進行

        # クリック待ちの場合は進行を停止
        if progression == "click" and self.wait_for_click:
            print(f" クリック待ち中: {self.wait_for_click}")
            return None

        # 現在のステップがclickならクリック待ち状態を設定
        self.wait_for_click = progression == "click"
        print(f" クリック待ち中: {self.wait_for_click}")
        return step

    # 次のシナリオステップを進める
    def update(self):
        print(f"[DEBUG] シナリオ更新呼び出し")
        if self.event_manager.pending_result_display:
            self.wait_for_click = True
            return

        if not self.current_steps or self.current_index >= len(self.current_steps):
            print("シナリオ終了")               # デバッグ用
            self.current_scenario_id = ""
            self.current_steps = None
            self.is_active = False
            return

        step = self.scenario_progress()
        if not step:
            return

        # 次のステップに進む
        self.current_index += 1
        self.display_index = self.current_index

        # イベント処理をevent_managerに委譲
        self.event_manager.handle_scenario_event(step)

    # クリックイベントを処理
    def on_click(self):
        branch_info = None
        if self.wait_for_click:
            # クリック待ちを解除して次のステップへ
            self. wait_for_click = False


            # 結果表示中か確認
            if self.event_manager.pending_result_display:
                self.event_manager.clear_result_display()

                # 分岐情報があるか確認
                branch_info = self.event_manager.get_and_clear_pending_branch()
                if branch_info:
                    # 分岐処理
                    next_step = branch_info["on_success"] if branch_info["success"] else branch_info["on_failure"]
                    self.event_manager.handle_scenario_event(next_step)
                    return

            # ダメージによって状態異常が起こった場合
            if self.event_manager.state_record:
                next_id = "Status_effect"
                self.start_scenario(next_id)
                return

            self.update()        
        print(f"[DEBUG] クリック検出")
        print(f" クリック待ち中: {self.wait_for_click}")
        print(f" 結果表示中: {self.event_manager.pending_result_display}")
        print(f" 分岐情報: {branch_info}")

    # 現在のステップの描画をイベントマネージャーに依頼
    def draw(self):
        #if self.is_active and self.current_index < len(self.current_steps):
        #    step = self.current_steps[self.display_index]
        self.event_manager.draw()
