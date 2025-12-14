from constans import InputMode

class InputModeManager:
    def __init__(self):
        self.mode = InputMode.MOUSE
        self.before_mode = None

    def load_mode(self, setting_manager):
        self.mode = setting_manager.get("input_mode")

    def set_mode(self, mode=InputMode):
        self.before_mode = self.mode
        self.mode = mode

    def get_mode(self):
        return self.mode
    
    def get_before_mode(self):
        return self.before_mode
    
    def is_mouse(self):
        return self.mode == InputMode.MOUSE
    
    def is_cursor(self):
        return self.mode == InputMode.CURSOR
    
    def is_keyboard(self):
        return self.mode == InputMode.KEYBOARD

    # 特定キーで切り替える用
    def toggle_cursor_keyboard(self):
        if self.is_cursor():
            self.set_mode(InputMode.KEYBOARD)
        else:
            self.set_mode(InputMode.CURSOR)

input_mode_manager = InputModeManager()