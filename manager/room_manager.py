from room import Room
from manager.event_manager import EventManager

class RoomManager:
    def __init__(self, screen, room_flag, direction_flag, east_room_flag, book_flag):
        self.screen = screen

        self.room_flag = room_flag
        self.direction_flag = direction_flag

        self.east_room_flag = east_room_flag
        self.book_flag = book_flag

        self.event_manager = EventManager(self.screen)
        
        self.room = None
        self.create_room()

    # 部屋の作成
    def create_room(self):
        room2_flag = self.room2_flag_check()
        self.room = Room(self.screen, self.room_flag, self.direction_flag, room2_flag)
        #self.max_room_scenario_flag = len(self.room.scenario_list)
        #print(self.room.scenario_list)  # デバッグ用

    # 二つ目の部屋表示チェック
    def room2_flag_check(self):
        if self.room_flag == "east":
            return self.east_room_flag["visivle"]
        elif self.room_flag == "west":
            return self.book_flag["found"]
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
    def move_room(self, position):
        if position == "under":
            if self.book_flag["get"]:
                # 本を持って出ようとしたらイベント
                self.event_manager.handle_event("book_exit")
                # 終了後は部屋のほうを向いている
                # self.room_flag, self.direction_flag = "center", self.room_flag
                # 扉が元に戻ったことを説明
            else:
                self.room_flag, self.direction_flag = self.room_move_direction_get(self.room_flag)
            #self.status_label[3].update_text(ROOM_NAME[self.room_flag])
        else:
            self.direction_flag = self.direction_move_get(position, self.direction_flag)
        self.create_room()


    def draw(self, selected_item, soup_flag):
        self.room.draw(selected_item, soup_flag)            # 部屋の表示
