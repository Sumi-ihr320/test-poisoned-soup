
class ItemManager:
    def __init__(self, screen):
        self.screen = screen
        self.items = []
    
    def add_item(self, item):
        self.items.append(item)

    # アイテムのクリック処理
    def handle_click(self, pos):
        for item in self.items:
            if item.handle_click(pos):
                self.run_event(item)
                return item
        return None
    
    # クリックされたアイテムのイベントを実行
    def run_event(self, item):
        if item.name == "Light":
            print("Light event triggered!")
        elif item.name == "Soup":
            print("Soup event triggered!")