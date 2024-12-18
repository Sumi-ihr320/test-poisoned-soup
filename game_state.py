
# 主人公のステータスクラス
class GameStatus:
    def __init__(self):
        # 現在の状況
        self.time = 60
        self.room = "center"
        self.direction = "north"

        # フラグの状態
        self.flags = Flags()


# フラグ管理用のクラス
class Flags:
    def __init__(self):
        # キャラクター関連のフラグ 
        self.characters = {
            # 少女のフラグ (仲間になってるか、好感度、死んだか)
            "girl_fellow":False,
            "girl_like_ability":0,
            "girl_death":False
        }
        
        # 部屋の状態フラグ
        self.rooms = {
            # 中央の部屋 (初回シナリオが済んでいるか、電球が取られてないか)
            "center_room_scenario":False,
            "center_room_light":False,
            # 東の部屋 (鍵が開いてるか、初回シナリオが済んでいるか、室内が見えてるか、少女と遭遇するまでの時間経過)
            "east_room_open":False,
            "east_room_scenario":False,
            "east_room_visivle":False,
            "east_room_time":5,
            # 西の部屋 (初回シナリオが済んでいるか)
            "west_room_scenario":False,
            # 北の部屋
            "north_room_scenario":False,
            # 南の部屋 (初回シナリオが済んでいるか、敵を見つけているか、敵と戦って逃げたか、敵がそこにいるか)
            "south_room_scenario":False,
            "south_room_find_enemy":False,
            "south_room_escape_enemy":False,
            "south_room_there_enemy":True
        }

        # アイテムの状態フラグ
        self.items = {
            # スープに関するフラグ  (毒が入っているか、血だと知っているか、飲んだか、捨てたか、時間経過)
            "soup_know":False,
            "soup_in_poison":False,
            "soup_drink": False,
            "soup_destruction": False,
            "soup_temperature":0,
            # 中央の部屋メモのフラグ (裏に気づいているか)
            "center_memo_objective":False,
            # 西の部屋の本に関するフラグ (見つけているか、入手しているか)
            "book_found":False,
            "book_get":False,
            # 毒に関するフラグ (持っているか)
            "poison_get":False
        }

    def update_flag(self, categry, key, value):
        if categry in self.__dict__ and isinstance(self.__dict__[categry], dict):
            self.__dict__[categry][key] = value
        
    def get_flag(self, categry, key):
        if categry in self.__dict__:
            return self.__dict__[categry].get(key, None)
        return None

    def to_dict(self):
        return {
            "characters": self.characters,
            "rooms": self.rooms,
            "items": self.items
        }

    @classmethod
    def from_dict(cls, data):
        flags = cls()
        for key, value in data.items():
            if hasattr(flags, key):
                setattr(flags, key, value)
        
        return flags
