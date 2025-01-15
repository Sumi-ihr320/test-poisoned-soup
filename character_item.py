# アイテム
class CharacterItem:
    def __init__(self, name="", category="item", img_name=None):
        self.name = name
        self.img_name = img_name
        self.category = category

    def to_dict(self):
        return {
            "name":self.name,
            "img_name": self.img_name,
            "category": self.category
        }

    @classmethod
    def from_dict(cls, data):
        if data["category"] == "armor":
            return Armor(data["name"], data["img_name"], data["category"], data["armor_point"])
        
        elif data["category"] == "weapon":
            return Weapon(data["name"], data["img_name"], data["category"], data["skill_point"],
                          data["damage_dice"], data["attack_range"], data["one_round"], data["bullets"], data["durability"])
        
        return cls(data["name"], data["img_name"], data["category"])

# 防具
class Armor(CharacterItem):
    def __init__(self, name="", img_name=None, category="armor", armor_point=0):
        super().__init__(name, category ,img_name)
        self.armor_point = armor_point

    def to_dict(self):
        data = super().to_dict()
        data["armor_point"] = self.armor_point
        return data

# 武器
class Weapon(CharacterItem):
    def __init__(self, name="", img_name=None, category="weapon", skill_point=0, damage_dice="", attack_range="", one_round=1, bullets=1, durability=1):
        super().__init__(name, category, img_name)
        
        self.skill_point = skill_point      # ％
        self.damage_dice = damage_dice      # ダメージ
        self.attack_range = attack_range    # 射程距離
        self.one_round = one_round          # 1ラウンドに何発撃てるか
        self.bullets = bullets              # 装弾数
        self.durability = durability        # 耐久力

    def to_dict(self):
        data = super().to_dict()
        data["skill_point"] = self.skill_point
        data["damage_dice"] = self.damage_dice
        data["attack_range"] = self.attack_range
        data["one_round"] = self.one_round
        data["bullets"] = self.bullets
        data["durability"] = self.durability
        return data
