from typing import Dict
from ..sound_manager import sound_manager
from ..render_manager import RenderManager

class DisplayProcessor:
    """
    役割：テキスト、画像、サウンドなどの表示処理を担当

    処理するステップタイプ：
    - text: テキスト表示
    - sound: サウンド再生
    - image_display: アイテム画像表示
    - image_hidden: アイテム画像非表示
    - girl_display: 少女立ち絵表示
    - girl_hidden: 少女立ち絵非表示

    入力：step (dict)
    出力：None (直接実行型なので返り値なし)
    """
    def __init__(self, render_manager: RenderManager):
        """
        :render_manager: 画面描画を担当するマネージャー
        """
        self.render_manager = render_manager

    def process_display(self, step: Dict):
        """
        ステップタイプに応じて表示処理を実行する
        step (Dict): シナリオのステップ
        テキストの場合のみ text を返す（EventManager が状態管理に使用）
        """
        step_type = step.get("type")
        result = None

        if step_type == "text":
            # テキストの場合のみ返り値を使用（EventManager が状態管理に使用）
            result = self.handle_text(step)

        elif step_type == "sound":
            # 直接実行型：返り値なし
            self.handle_sound(step)

        elif step_type == "image_display":
            # 直接実行型：返り値なし
            self.handle_image_display(step)

        elif step_type == "image_hidden":
            # 直接実行型：返り値なし
            self.handle_image_hidden()

        elif step_type == "girl_display":
            # 直接実行型：返り値なし
            self.handle_girl_display(step)

        elif step_type == "girl_hidden":
            # 直接実行型：返り値なし
            self.handle_girl_hidden()

       # 毒摂取の画面効果を表示する
        elif step["type"] == "poison_start":
            pass

        # 毒摂取の画面効果表示を終了する
        elif step["type"] == "poison_stop":
            pass
 
        return result

    # テキスト処理
    def handle_text(self, step: Dict):
        text = step.get("text", None)
        return text

    # サウンド処理
    def handle_sound(self, step: Dict):
        sound_name = step.get("name", None)
        if sound_name in sound_manager.sounds:
            sound_manager.play(sound_name)
        else:
            print(f"その名前のサウンドは登録されていません。{sound_name}")  # デバッグ用

    # アイテム画像の表示
    def handle_image_display(self, step: Dict):
        image_path = step.get("image", None)
        if image_path:
            self.render_manager.show_item_image(image_path)

    # アイテム画像の非表示
    def handle_image_hidden(self):
        self.render_manager.hidden_item_image()

    # 少女立ち絵の表示
    def handle_girl_display(self, step: Dict):
        state = step.get("state", None)
        position = step.get("position", "right")
        self.render_manager.show_girl_image(state, position)
    
    # 少女立ち絵の非表示
    def handle_girl_hidden(self):
        self.render_manager.hidden_girl_image()