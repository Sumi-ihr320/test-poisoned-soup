class Skill:
    def __init__(self, name, ability_value):
        self.name = name
        self.ability_value = ability_value
    
    def to_dict(self):
        return {
            "name": self.name,
            "ability_value": self.ability_value
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["ability_value"])
    
class SkillList:
    def __init__(self):
        self.fist = Skill("こぶし", 50)
        self.kick = Skill("キック", 25)
        self.head_butt = Skill("頭突き", 10)
        self.grapple = Skill("組み付き", 25)
        self.throw = Skill("投擲", 25)
        self.handgun = Skill("拳銃", 20)
        self.rifle = Skill("ライフル", 25)
        self.shotgun = Skill("ショットガン", 30)
        self.submahine_gun = Skill("サブマシンガン", 15)
        self.machine_gun = Skill("マシンガン", 15)
        self.martial_arts = Skill("マーシャルアーツ", 1)

        self.spot_hidden = Skill("目星", 25)
        self.listen = Skill("聞き耳", 25)
        self.library_use = Skill("図書館", 25)
        self.first_aid = Skill("応急手当", 30)
        self.psychoanalysis = Skill("精神分析", 1)
        self.psychology = Skill("心理学", 5)

        self.climb = Skill("登攀", 40)
        self.jump = Skill("跳躍", 25)
        self.swim = Skill("水泳", 25)
        self.navigate = Skill("ナビゲート", 10)

        self.track = Skill("追跡", 10)
        self.conceal = Skill("隠す", 15)
        self.hide = Skill("隠れる", 15)
        self.sneak = Skill("忍び歩き", 10)
        self.disguise = Skill("変装", 1)
        self.drive_automobile = Skill("運転（自動車）", 20)
        self.pilot = Skill("操縦", 1)
        self.ride = Skill("乗馬", 5)

        self.locksmith = Skill("鍵開け", 1)
        self.photography = Skill("写真術", 10)
        self.craft = Skill("製作", 5)
        self.electrical_repair = Skill("電気修理", 10)
        self.mechanical_repair = Skill("機械修理", 20)
        self.operate_heavy_machine = Skill("重機械操作", 1)
        
        self.credit_rating = Skill("信用", 15)
        self.fast_talk = Skill("言いくるめ", 5)
        self.persuade = Skill("説得", 15)
        self.bargain = Skill("値切り", 5)
        self.other_language_english = Skill("他の言語（英語）", 1)
        self.other_language_latin = Skill("他の言語（ラテン語）", 1)
        self.own_language = Skill("母国語", 5)

        self.accounting = Skill("経理", 10)
        self.authropology = Skill("人類学", 1)
        self.archaeology = Skill("考古学", 1)
        self.art = Skill("芸術", 5)
        self.astronomy = Skill("天文学", 1)
        self.biology = Skill("生物学", 1)
        self.chemistry = Skill("化学", 1)
        self.computer_use = Skill("コンピューター", 1)
        self.cthulhu_mythos = Skill("クトゥルフ神話", 0)
        self.electronics = Skill("電子工学", 1)
        self.geology = Skill("地質学", 1)
        self.history = Skill("歴史", 20)
        self.law = Skill("法律", 5)
        self.medicine = Skill("医学", 5)
        self.natural_history = Skill("博物学", 10)
        self.occult = Skill("オカルト", 5)
        self.pharmacy = Skill("薬学", 1)
        self.physics = Skill("物理学", 1)
        
    def get_skill_value(self, skill_name):
        skill_obj = next((skill for skill in self if skill.name == skill_name), None)
        if skill_obj:
            return skill_obj.ability_value
        return None
    
    def set_skill_value(self, skill_name, new_value):
        skill_obj = next((skill for skill in self if skill.name == skill_name), None)
        if skill_obj:
            skill_obj.ability_value = new_value
        