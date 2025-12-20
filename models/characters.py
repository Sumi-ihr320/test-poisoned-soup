from typing import Optional
from models.character_item import *

# キャラクタークラス
class Character:
    def __init__(self, name: str="", image: str="", STR: int=0, CON: int=0, SIZ: int=0, DEX: int=0, INT: int=0, POW: int=0, DB: str="", HP: int=0, MP: int=0, Dodge: int=0, skill: dict={}):
        # 基本情報
        self.name = name
        self.image = image
        
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
        self.Dodge = Dodge
 
        # 技能
        self.skill = skill

    # 装甲があるかをチェック
    def check_armor(self):
        return 0

    # ダメージを受けた時の処理
    def take_damage(self, event: str, damage: int) -> Optional[str]:
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
            state = "Shock"

        self.hp = max(self.hp - effective_damage, 0)            # HPを減らす (0未満にならない)

        # 瀕死判定
        if self.hp == 0:
            state = "Dying"

        # 気絶判定
        elif self.hp <= 2:
            state = "Faint"

        return state
    
    # 辞書型に変換
    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "name":self.name,
            "image":self.image,
            "STR":self.STR, "CON":self.CON, "SIZ":self.SIZ,
            "DEX":self.DEX, "INT":self.INT, "POW":self.POW,
            "DB":self.DB, "HP":self.HP, "MP":self.MP, "Dodge":self.Dodge,
            "skill": self.skill
        }
    
    # 辞書からクラスに変換
    @classmethod
    def from_dict(cls, data):
        if data["type"] == "Player":
            character = Player(data["name"], data["image"], data["age"], data["sex"], data["STR"], data["CON"], data["SIZ"],
                               data["DEX"], data["APP"], data["EDU"], data["INT"], data["POW"], data["Luck"],
                               data["Idea"], data["Know"], data["DB"], data["HP"], data["MP"], data["Dodge"],
                               data["SAN"], data["max_SAN"], data["Profession"], data["skill"], [], data["Hobby"], data["girl_like_ability"])

        elif data["type"] == "Human":
            character = Human(data["name"], data["image"], data["STR"], data["CON"], data["SIZ"], data["DEX"], data["INT"], data["POW"],
                            data["DB"], data["HP"], data["MP"], data["Dodge"], data["skill"],
                            data["age"], data["sex"], data["APP"], data["EDU"], data["Luck"], data["Idea"], data["Know"],
                            data["SAN"], data["max_SAN"], data["Profession"], [])
            character.inventory = [CharacterItem.from_dict(item) for item in data["inventory"]]

        elif data["type"] == "Enemy":
            character = Enemy(data["name"], data["image"], data["STR"], data["CON"], data["SIZ"], data["DEX"], data["INT"], data["POW"],
                            data["DB"], data["HP"], data["MP"], data["Dodge"], data["skill"], data["armor"])

        else:
            character = cls(data["name"], data["image"], data["STR"], data["CON"], data["SIZ"], data["DEX"], data["INT"], data["POW"],
                            data["DB"], data["HP"], data["MP"], data["Dodge"], data["skill"])

        return character

# 敵クラス
class Enemy(Character):
    def __init__(self, name: str="", image: str="", STR: int=0, CON: int=0, SIZ: int=0, DEX: int=0, INT: int=0, POW: int=0, DB: str="", HP: int=0, MP: int=0, Dodge: int=0, skill: dict={}, armor: int=0):
        super().__init__(name, image, STR, CON, SIZ, DEX, INT, POW, DB, HP, MP, Dodge, skill)
        self.armor = armor

    def check_armor(self):
        return self.armor
    
    def to_dict(self):
        data = super().to_dict()
        data["armor"] = self.armor
        return data

# 人間クラス
class Human(Character):
    def __init__(self, name: str="", image: str="", STR: int=0, CON: int=0, SIZ: int=0, DEX: int=0, INT: int=0, POW: int=0, DB: str="", HP: int=0, MP: int=0, Dodge: int=0, skill: dict={}, age: int=0, sex: str="man",
                 APP: int=0, EDU: int=0, Luck: int=0, Idea: int=0, Know: int=0, SAN: int=0, max_SAN: int=0, Profession: str="", inventory: list=[]):
        super().__init__(name, image, STR, CON, SIZ, DEX, INT, POW, DB, HP, MP, Dodge, skill)
        
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
        self.Profession = Profession

        # 所持アイテム
        self.inventory = inventory

    # アイテムの追加
    def add_item(self, item):
        self.inventory.append(item)
        print(f"アイテムを追加しました: {item.name}")    # デバッグ用
    
    # アイテムの削除
    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            print(f"アイテムを削除しました: {item.name}")               # デバッグ用
        else:
            print(f"アイテムを持っていません: {item.name}")             # デバッグ用

    def check_armor(self):
        if self.inventory:
            for item in self.inventory:
                if item.category == "armor":
                    return item.armor_point
        return 0
                    
    # SAN値が減った時
    def take_SAN_damage(self, damage):
        state = None    # 状態

        # 一時的狂気の判定
        if damage >= 5:
            state = "Temporary_madness"

        self.SAN = max(self.SAN - damage, 0)

        # 不定の狂気の判定
        if (self.max_SAN - self.SAN) > (int(self.max_SAN / 0.2)):
            state = "Indeterminate_madness"

        return state

    def to_dict(self):
        data = super().to_dict()
        data["age"] = self.age
        data["sex"] = self.sex
        data["APP"] = self.APP
        data["EDU"] = self.EDU
        data["Luck"] = self.Luck
        data["Idea"] = self.Idea
        data["Know"] = self.Know
        data["SAN"] = self.SAN
        data["max_SAN"] = self.max_SAN
        data["Profession"] = self.Profession
        data["inventory"] = [item.to_dict() for item in self.inventory]
        return data

# 主人公クラス
class Player(Human):
    def __init__(self, name: str="", image: str="silhouette_man.png", age: int=0, sex: str="man", STR: int=0, CON: int=0, SIZ: int=0, DEX: int=0, APP: int=0, EDU: int=0, INT: int=0, POW: int=0, Luck: int=0, Idea: int=0, Know: int=0, 
                 DB: str="", HP: int=0, MP: int=0, Dodge: int=0, SAN: int=0, max_SAN: int=0, profession: str="", skill: dict={}, inventory: list=[], hobby: str="", girl_like_ability: int=0):
        super().__init__(name, image, STR, CON, SIZ, DEX, INT, POW, DB, HP, MP, Dodge, skill,
                         age, sex, APP, EDU, Luck, Idea, Know, SAN, max_SAN, profession, inventory)
        self.Hobby = hobby
        self.girl_like_ability = girl_like_ability

    def to_dict(self):
        data = super().to_dict()
        data["Hobby"] = self.Hobby
        data["girl_like_ability"] = self.girl_like_ability
        return data
