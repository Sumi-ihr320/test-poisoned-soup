# 主人公のステータスクラス
class GameStatus:
    def __init__(self):
        # 現在の状況
        self.time = 600
        self.room = "center"
        self.direction = "north"

    def to_dict(self):
        return {
            "time": self.time,
            "room": self.room,
            "direction": self.direction
        }

    # 辞書からクラスインスタンスを作成    
    @classmethod
    def from_dict(cls, data):
        state = cls()
        for key, value in data.items():
            if hasattr(state, key):
                setattr(state, key, value)
        
        return state


# フラグ管理用のクラス
class Flags:
    def __init__(self):
        # 少女のフラグ 
        self.girl = {
            # 少女のフラグ (会ったか、置いてきているなら現在地、付いてきているか、一緒にダイスチェックをしてもらうか、
            #              担いでいるか、好感度、ポットの中を見ているか、狩りたてる恐怖を見ているか、気絶しているか、生きているか)
            "meet":False,
            "room":"east",
            "fellow":False,
            "dice_check":False,
            "carry":False,
            "like_ability":0,
            "pot_looked_g":False,
            "hunting_horrors_look_g":False,
            "faint":0,
            "alive":True
        }

        # 敵に関するフラグ（一度SANチェックをしたら二度目はSANチェックが起こらないように）
        self.enemys = {
            # 狩り立てる恐怖について（見ているか、ノックしたか、そこに居るか、倒したか、生贄を捧げたか）
            "hunting_horrors_look":False,
            "hunting_horrors_knock":False,
            "hunting_horrors_there":True,
            "hunting_horrors_defeated":False,
            "hunting_horrors_offered_sacrifice":False,
            # 無形の落とし子について
            "formless_spawn_look":False,
            # チャウグナー・フォーンについて
            "chaugnar_faugn_look":False
        }
        
        # 部屋の状態フラグ
        self.rooms = {
            # 中央の部屋 (初回シナリオが済んでいるか)
            "center_room_scenario":False,
            # 東の部屋 (鍵が開いてるか、室内が見えてるか、音を聞いてるか)
            "east_room_open":False,
            "east_room_visible":False,
            "east_room_listen":False,
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
            # スープに関するフラグ  (毒が入っているか、それが指に付いているか、血だと知っているか、飲んだか、捨てたか)
            "soup_know":False,
            "soup_in_poison":False,
            "soup_in_poison_to_finger":False,
            "soup_drink": False,
            "soup_destruction": False,
            # スープの器に関するフラグ（手に入れたか、中身があるか(新しいスープを補充したか)、毒を入れたか）
            "soup_bowl_get": False,
            "soup_bowl_in_soup": False,
            "soup_bowl_in_soup_in_poison":False,
            # 中央の部屋メモのフラグ (裏に気づいているか)
            "center_memo_objective":False,
            # 電球に関するフラグ (目星成功しているか, 外したか, 持っているか, 壊したか)
            "light_objective":False,
            "light_remove":False,
            "light_get":False,
            "light_break":False,
            # 東の部屋の死体に関するフラグ（見たことがあるか）
            "corpse_look":False,
            # 西の部屋の本に関するフラグ (見つけているか、入手しているか)
            "book_found":False,
            "book_get":False,
            # 西の部屋のろうそくに関するフラグ
            # （0:消してない 1:長い時に消した 2:短い時に消した 3:蝋が尽きた、所持しているか、別の部屋に置いているか）
            "candle_goes_out":0,
            "candle_get":False,
            "candle_out":False,
            # 西の部屋の本棚に関するフラグ（目星成功しているか）
            "bookshelf_objective":False,
            # 黒い液体に関するフラグ（手に付着しているか、それが毒だと知っているか、舐めてみたか）
            "black_liquid_to_hand":False,
            "black_liquid_know":False,
            "black_liquid_lick":False,
            # 毒の瓶に関するフラグ (持っているか、それが毒だと知っているか)
            "poison_bottle_get":False,
            "poison_bottle_know":False,
            # 北の部屋の鍋に関するフラグ（鍋の中身を見ているか、鍋の中身は残っているか）
            "pot_looked":False,
            "pot_in_nothing":False,
            # 北の部屋のメモに関するフラグ（発見しているか）
            "north_memo_discovery":False
        }

        self.ending = {
            "ending1": False,
            "ending2": False,
            "ending3": False,
            "ending4": False,
            "ending5": False
        }

    def update_flag(self, category, key, value):
        if category in self.__dict__ and isinstance(self.__dict__[category], dict):
            self.__dict__[category][key] = value

    def update_flag_key_only(self, key, value):
        for category in self.__dict__.values():
            if isinstance(category, dict) and key in category:
                category[key] = value
                break
        
    def get_flag(self, category, key):
        if category in self.__dict__:
            return self.__dict__[category].get(key, None)
        return None

    def get_flag_key_only(self, key):
        for category in self.__dict__.values():
            if isinstance(category, dict) and key in category:
                return category[key]
        return None

    def to_dict(self):
        return {
            "girl": self.girl,
            "enemys": self.enemys,
            "rooms": self.rooms,
            "items": self.items,
            "ending": self.ending
        }

    @classmethod
    def from_dict(cls, data):
        flags = cls()
        for key, value in data.items():
            if hasattr(flags, key):
                setattr(flags, key, value)
        
        return flags
