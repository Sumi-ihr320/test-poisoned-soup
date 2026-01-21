from typing import Dict
from ..sound_manager import sound_manager

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
    def __init__(self, render_manager):
        """
        :render_manager: 画面描画を担当するマネージャー
        """
        self.render_manager = render_manager

    def process_display(self, step: Dict):
        """
        ステップタイプに応じて表示処理を実行する

        step (Dict): シナリオのステップ
        """
        step_type = step.get("type")

        if step_type == "text":
            self.handle_text(step["text"])
        elif step_type == "sound":
            self.handle_sound(step["name"])
        elif step_type == "image_display":
            self.handle_image_display(step["item"])
        elif step_type == "image_hidden":
            self.handle_image_hidden()
        elif step_type == "girl_display":
            self.handle_girl_display(step)
        elif step_type == "girl_hidden":
            self.handle_girl_hidden()

    # テキスト処理
    def handle_text(self, text: str):
        self.current_display_text = text
            # 結果表示中でない場合のみ通常テキストを使用
            #if self.pending_result_display:
            #    return
        pass

    # サウンド処理
    def handle_sound(self, sound_name: str):
        if sound_name in sound_manager.sounds:
            sound_manager.play(sound_name)
        else:
            print(f"その名前のサウンドは登録されていません。{sound_name}")  # デバッグ用

    # アイテム画像の表示
    def handle_image_display(self, item_name: str):
        self.render_manager.show_item_image(item_name)

    # アイテム画像の非表示
    def handle_image_hidden(self):
        self.render_manager.hidden_item_image()
        #self.current_display_text = None
