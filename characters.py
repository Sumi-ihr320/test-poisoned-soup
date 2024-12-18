# キャラクタークラス
class Character:
    def __init__(self, name="", STR=0, CON=0, SIZ=0, DEX=0, INT=0, POW=0, DB="", HP=0, MP=0, Avo=0, skill={}):
        # 基本情報
        self.name = name
        
        # ステータス
        self.STR = STR
        self.CON = CON
        self.SIZ = SIZ
        self.DEX = DEX
        self.INT = INT
        self.POW = POW
        
        self.DB = DB
        self.HP = HP
        self.MP = MP
        self.Avo = Avo
 
        # 技能
        self.skill = skill

    # 装甲があるかをチェック
    def check_armor(self):
        return 0

    # ダメージを受けた時の処理
    def take_damage(self, event, damage):
        state = None    # 状態
        # バトル中のダメージの場合は装甲がダメージを防ぐ
        if event == "battle":
            armor_point = self.check_armor()
            effective_damage = max(damage - armor_point, 0)     # 装甲分のポイントを引く
        else:
            # イベントでダメージを受けた場合は装甲は関係ない
            effective_damage = damage

        # HPが半分以上削られたかどうか判定
        if (self.hp / 2) < effective_damage:
            state = "shock"

        self.hp = max(self.hp - effective_damage, 0)            # HPを減らす (0未満にならない)

        # 瀕死判定
        if self.hp == 0:
            state = "dying"

        # 気絶判定
        elif self.hp <= 2:
            state = "faint"

        return state
    
# 人間クラス
class Human(Character):
    def __init__(self, name, STR, CON, SIZ, DEX, INT, POW, DB, HP, MP, Avo, skill, age=0, sex="man",
                 APP=0, EDU=0, Luck=0, Idea=0, Know=0, SAN=0, max_SAN=0, profession="", items={}):
        super().__init__(name, STR, CON, SIZ, DEX, INT, POW, Luck, Idea, Know, DB, HP, MP, Avo, SAN, max_SAN,
                         skill)
        
        # 基本情報
        self.age = age
        self.sex = sex     # man, woman, neuter

        # ステータス
        self.APP = APP
        self.EDU = EDU
        self.Luck = Luck
        self.Idea = Idea
        self.Know = Know
        self.SAN = SAN
        self.max_SAN = max_SAN
        
        # 職業
        self.profession = profession

        # 所持アイテム
        self.items = items

    # アイテムの追加
    def add_item(self, item_name, attributes):
        self.items[item_name] = attributes
        print(f"アイテムを追加しました: {item_name} - {attributes}")    # デバッグ用
    
    # アイテムの削除
    def remove_item(self, item_name):
        if item_name in self.items:
            del self.items[item_name]
            print(f"アイテムを削除しました: {item_name}")               # デバッグ用
        else:
            print(f"アイテムを持っていません: {item_name}")             # デバッグ用

    def check_armor(self):
        if self.items:
            for item in self.items:
                if item.key == "装甲":
                    return item["装甲"]
                    
    # SAN値が減った時
    def take_SAN_damage(self, damage):
        state = None    # 状態

        # 一時的狂気の判定
        if damage > 5:
            state = "temporary_madness"

        self.SAN = max(self.SAN - damage, 0)

        # 不定の狂気の判定
        if (self.max_SAN - self.SAN) > (int(self.max_SAN / 0.2)):
            state = "indeterminate_madness"

        return state

# 敵クラス
class Enemy(Character):
    def __init__(self, name, STR, CON, SIZ, DEX, INT, POW, DB, HP, MP, Avo, skill, armor):
        super().__init__(name, STR, CON, SIZ, DEX, INT, POW, DB, HP, MP, Avo, skill)
        self.armor = armor

    def check_armor(self):
        return self.armor

# 主人公クラス
class Player(Human):
    def __init__(self, name, age, sex, STR, CON, SIZ, DEX, APP, EDU, INT, POW, Luck, Idea, Know, 
                 DB, HP, MP, Avo, SAN, max_SAN, profession, skill, items):
        super().__init__(name, STR, CON, SIZ, DEX, INT, POW, DB, HP, MP, Avo, skill,
                         age, sex, APP, EDU, Luck, Idea, Know, SAN, max_SAN, profession, items)    

    # 辞書型にして返す
    def to_dict(self):
        return {
            "name":self.name, "age":self.age, "sex":self.sex,
            "STR":self.STR, "CON":self.CON, "SIZ":self.SIZ, "DEX":self.DEX,
            "APP":self.APP, "EDU":self.EDU, "INT":self.INT, "POW":self.POW,
            "Luck":self.Luck, "Idea":self.Idea, "Know":self.Know, "DB":self.DB,
            "HP":self.HP, "MP":self.MP, "Avo":self.Avo, "SAN":self.SAN, "max_SAN": self.max_SAN,
            "Profession":self.profession,
            "skill":self.skill,
            "items":self.items,
            "girl_like_ability":0
        }
    
    # 辞書からクラスインスタンスを作成
    @classmethod
    def from_dict(cls, data):
        player = cls()
        for key, value in data.items():
            if hasattr(player, key):
                setattr(player, key, value)
        return player
