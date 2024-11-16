
class EventManager:
    def __init__(self, screen) -> None:
        pass

    def handle_event(self, event_name, *args, **kwargs):
        """
        イベントを処理
        :param event_name: 発生するイベント名
        :param args: イベントに渡す引数
        """
        if event_name == "book_exit":
            self.handle_book_exit(*args, **kwargs)

        elif event_name == "fight_start":
            self.start_fight(*args, **kwargs)

        # 他のイベントを追加
        else:
            print(f"No handler for event: {event_name}")

    # 部屋から本を持ちだそうとした際に起こるイベント
    def handle_book_exit(self):
        """本を持ち出したときのイベント"""
        print("You tried to leave the room with the book!")

        # 戦闘を開始するイベントを発生
        self.handle_event("fight_start", enemy="Guardian")

    # 戦闘イベント
    def start_fight(self, enemy):
        """戦闘イベントを開始"""
        print(f"Starting fight with {enemy}")
