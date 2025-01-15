from room import Room

class RoomManager:
    def __init__(self, screen, event_manager, flags, game_state):
        self.screen = screen

        self.flags = flags
        self.game_state = game_state

        self.event_manager = event_manager
        
        self.room = None
        self.create_room()

    # 部屋の作成
    def create_room(self):
        room2_flag = self.room2_flag_check()
        self.room = Room(self.screen, self.game_state.room, self.game_state.direction, room2_flag)

    # 二つ目の部屋表示チェック
    def room2_flag_check(self):
        if self.room == "east":
            return self.flags.get_flag("rooms", "east_room_visivle")
        elif self.room == "west":
            return self.flags.get_flag("items", "book_found")
        else:
            return False

    # 向き移動先を取得
    def direction_move_get(self, position, direction):
        direction_map = {"right":{"north": "east", "east": "south", "south": "west", "west": "north"},
                         "left": {"north": "west", "west": "south", "south": "east", "east": "north"}}
        return direction_map.get(position, {}).get(direction, direction)

    # 部屋の戻り先を取得
    def room_move_direction_get(self, room):
        direction_map = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east"
        }
        return "center", direction_map.get(room, "north")

    # 部屋の移動を管理
    def move_to_room(self, position):
        if position == "under":
            if self.flags.get_flag("items", "book_get"):
                self.game_state.room, self.game_state.direction = "center", self.game_state.room
            else:
                self.game_state.room, self.game_state.direction = self.room_move_direction_get(self.game_state.room)
        else:
            self.game_state.direction = self.direction_move_get(position, self.game_state.direction)

        self.create_room()

    def handle_item_click(self, pos):
        clickd_item = None
        for item in self.room.items_select_list:
            if item.handle_click(pos):
                clickd_item = item
                break

        if clickd_item:
            self.event_manager.handle_event("item_click", {"item_name":clickd_item.name})

    def draw(self, selected_item, flags):
        self.room.draw(selected_item, flags)            # 部屋の表示
