
class ScenarioManager:
    def __init__(self, screen):
        self.screen = screen

        self.scenario = []      # 現在進行中のシナリオ（テキストのリスト)
        self.current_index = 0  # 現在の表示位置
        self.is_running = False # シナリオが進行中かどうか

    # シナリオを開始
    def start_scenario(self, scenario_list):
        pass