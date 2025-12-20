from manager.dice import DiceEngine
from manager.sound_manager import sound_manager

class DiceService:
    def __init__(self, engine=None, sound_mgr=None, sound_name="ダイスを振る"):
        self.engine = engine if engine else DiceEngine()
        self.sound_mgr = sound_mgr if sound_mgr else sound_manager
        self.sound_name = sound_name

    # サウンドをロードする
    def _ensure_sound_loaded(self):
        try:
            sounds = getattr(self.sound_mgr, "sounds", None)
            if not sounds or self.sound_name not in sounds:
                self.sound_mgr.load_sound(self.sound_name, "W-DISE.mp3")
        except Exception:
            pass

    # サウンドを鳴らす
    def _sound_play(self):
        try:
            self._ensure_sound_loaded()
            self.sound_mgr.play(self.sound_name)
        except Exception:
            pass
    
    # ダイスを振ると音が鳴る
    def roll(self, dice_text, play_sound=True, animate_callback=None):
        if play_sound and self.sound_mgr:
            self._sound_play()

        result = self.engine.roll(dice_text)

        if animate_callback:
            try:animate_callback(result)
            except Exception: pass
        return result
    
    # 成否判定が必要なロール
    def check_threshold(self, dice_text, threshold, op="<=", play_sound=True, animate_callback=None):
        if play_sound and self.sound_mgr:
            self._sound_play()

        if not hasattr(self.engine, "check_threshold"):
            raise NotImplementedError("DiceEngineはcheck_thresholdを実装していません")
        
        check_result, value = self.engine.check_threshold(dice_text, threshold, op)

        if animate_callback:
            try: animate_callback((check_result, value))
            except Exception: pass

        return (check_result, value)
