from room import Room

class RoomManager:
    def __init__(self, screen, event_manager, flags, room_flag, direction_flag, east_room_flag, book_flag):
        self.screen = screen
        self.flags = flags

        self.room_flag = flags.get_flag("status", "room")
        self.direction_flag = flags.get_flag("status", "direction")

        self.east_room_flag = flags.get_flag("rooms", "east_room_visivle")
        self.book_flag = flags.get_flag("items", "book_found")

        self.event_manager = event_manager
        
        self.room = None
        self.create_room()

    # 部屋の作成
    def create_room(self):
        room2_flag = self.room2_flag_check()
        self.room = Room(self.screen, self.room_flag, self.direction_flag, room2_flag)

    # 二つ目の部屋表示チェック
    def room2_flag_check(self):
        if self.room_flag == "east":
            return self.east_room_flag
        elif self.room_flag == "west":
            return self.book_flag
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
            if self.book_flag["get"]:
                # 本を持って出ようとしたらイベント
                #self.event_manager.handle_event("book_exit")
                # 終了後は部屋のほうを向いている
                self.room_flag, self.direction_flag = "center", self.room_flag
                # 扉が元に戻ったことを説明
            else:
                self.room_flag, self.direction_flag = self.room_move_direction_get(self.room_flag)
            #self.status_label[3].update_text(ROOM_NAME[self.room_flag])
        else:
            self.direction_flag = self.direction_move_get(position, self.direction_flag)

        self.flags.set_flag("status", "room", self.room_flag)
        self.flags.set_flag("status", "direction", self.direction_flag)
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
