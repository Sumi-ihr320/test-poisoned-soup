from manager.render_manager import RenderManager

class DisplayText:
    def __init__(self, render_manager: RenderManager):
        self.render_manager = render_manager
        self.text = ""
        
    def set_text(self, text: str):
        self.text = text
        self.render_manager.show_current_text(text)

    def clear_text(self):
        self.text = ""
        self.render_manager.hide_current_text()
