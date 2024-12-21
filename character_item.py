# アイテム
class CharacterItem:
    def __init__(self, name, category="item", img_name=None):
        self.name = name
        self.img_name = img_name
        self.category = category

# 防具
class Armor(CharacterItem):
    def __init__(self, name, img_name, category="armor", armor_point=0):
        super().__init__(name, category ,img_name)
        self.armor_point = armor_point

# 武器
class Weapon(CharacterItem):
    def __init__(self, name, img_name, category="weapon", skill_point=0, damage_dice="", attack_range="", one_round=1, bullets=1, durability=1):
        super().__init__(name, category, img_name)
        
        self.skill_point = skill_point      # ％
        self.damage_dice = damage_dice      # ダメージ
        self.attack_range = attack_range    # 射程距離
        self.one_round = one_round          # 1ラウンドに何発撃てるか
        self.bullets = bullets              # 装弾数
        self.durability = durability        # 耐久力

# ２２口径ショート・オートマチック：２０％　(1d6 10m 1R3 装弾数6 耐久力6)