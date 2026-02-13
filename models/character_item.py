from typing import Optional, Dict, Any

# アイテム
class CharacterItem:
    def __init__(self, name: str="", category: str="item", img_name: Optional[str]=None):
        self.name = name
        self.img_name = img_name
        self.category = category

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name":self.name,
            "img_name": self.img_name,
            "category": self.category
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterItem':
        if data["category"] == "armor":
            return Armor(data["name"], data["img_name"], data["category"], data["armor_point"])
        
        elif data["category"] == "weapon":
            return Weapon(data["name"], data["img_name"], data["category"], data["skill"],
                          data["damage_dice"], data["attack_range"], data["one_round"], data["bullets"], data["durability"])
        
        return cls(data["name"], data["img_name"], data["category"])

# 防具
class Armor(CharacterItem):
    def __init__(self, name: str="", img_name: Optional[str]=None, category: str="armor", armor_point: int=0):
        super().__init__(name, category, img_name)
        self.armor_point = armor_point

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["armor_point"] = self.armor_point
        return data

# 武器
class Weapon(CharacterItem):
    def __init__(self, name: str="", img_name: Optional[str]=None, category: str="weapon", skill: str="", damage_dice: str="", attack_range: str="", one_round: int=1, bullets: int=1, durability: int=1):
        super().__init__(name, category, img_name)
        
        self.skill = skill                  # 対応スキル(使うのに必要なスキル)
        self.damage_dice = damage_dice      # ダメージ
        self.attack_range = attack_range    # 射程距離
        self.one_round = one_round          # 1ラウンドに何発撃てるか
        self.bullets = bullets              # 装弾数
        self.durability = durability        # 耐久力

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["skill"] = self.skill
        data["damage_dice"] = self.damage_dice
        data["attack_range"] = self.attack_range
        data["one_round"] = self.one_round
        data["bullets"] = self.bullets
        data["durability"] = self.durability
        return data
