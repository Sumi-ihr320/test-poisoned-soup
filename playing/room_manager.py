from playing.room import Room
from ui.ui_cache import ImageCache

class RoomManager:
    def __init__(self, screen, frame_rect, flags, game_state):
        self.screen = screen

        self.frame_rect = frame_rect

        self.flags = flags
        self.game_state = game_state

        self.image_cache = ImageCache()

        self.room = None
        self.create_room()

    # 部屋の作成
    def create_room(self):
        room_change_flag = self.room_change_flag_check()
        self.room = Room(self.screen, frame_rect=self.frame_rect, room=self.game_state.room, direction=self.game_state.direction, 
                         room_change_flag=room_change_flag, image_cache=self.image_cache)

    # フラグによって変化する部屋の表示チェック
    def room_change_flag_check(self):
        flag = {}
        if self.game_state.room == "center":
            flag["light_remove"] = self.flags.get_flag("items", "light_remove")
            flag["soup_in_poison"] = self.flags.get_flag("items", "soup_in_poison")
            flag["soup_drink"] = self.flags.get_flag("items", "soup_drink")
            flag["soup_destruction"] = self.flags.get_flag("items", "soup_destruction")
            flag["soup_bowl_get"] = self.flags.get_flag("items", "soup_bowl_get")
        elif self.game_state.room == "east":
            flag["east_room_visible"] = self.flags.get_flag("rooms", "east_room_visible")
        elif self.game_state.room == "west":
            flag["book_found"] = self.flags.get_flag("items", "book_found")
            flag["candle_get"] = self.flags.get_flag("items", "candle_get")
            flag["candle_goes_out"] = self.flags.get_flag("items", "candle_goes_out")
            flag["candle_out"] = self.flags.get_flag("items", "candle_out")
        elif self.game_state.room == "south":
            flag["hunting_horrors_offered_sacrifice"] = self.flags.get_flag("enemys", "hunting_horrors_offered_sacrifice")
        
        return flag if flag else None

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
    def move_to_room(self, position=None, next_room=None):
        if position == "under":
            if self.flags.get_flag("items", "book_get"):
                self.game_state.room, self.game_state.direction = "center", self.game_state.room
            else:
                self.game_state.room, self.game_state.direction = self.room_move_direction_get(self.game_state.room)
        elif position == "right" or position == "left":
            self.game_state.direction = self.direction_move_get(position, self.game_state.direction)

        elif next_room:
            self.game_state.room = next_room

        if self.girl_fellow_check():
            self.flags.update_flag("girl", "room", self.game_state.room)

        self.create_room()

    def girl_fellow_check(self):
        return self.flags.get_flag("girl", "fellow")

    def handle_mouse_hover(self, pos):
        self.room.handle_mouse_hover(pos)

    def handle_click(self, pos):
        self.room.handle_click(pos)

    def draw(self):
        self.room.draw()            # 部屋の表示
