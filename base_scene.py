from constans import *

class BaseScene:
    def __init__(self, screen, root):
        self.screen = screen
        self.root = root

        # 現在の画面サイズ
        self.screen_size = self.screen.get_size()

        # 状態管理
        self.state = State.NONE

    # 画面サイズ変更時に呼び出す
    def relayout(self, screen):
        self.screen = screen
        self.screen_size = self.screen.get_size()

    # メニューボタン用のコールバック関数
    def set_state(self, state=State.NONE):
        self.state = state

    def draw(self):
        pass

    # マウスオーバーイベント
    def handle_mouse_hover(self):
        pass

    # クリックイベント
    def handle_click(self, pos):
        pass

    # イベント
    def handle_events(self):
        pass

    # 更新
    def update(self):
        pass

    # 次のステージ
    def next_state(self):
        pass