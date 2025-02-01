from constans import *
from ui_elements import *

from characters import *
from character_item import *
from skill import *

from profession import ProfessionSelecter, HobbySelecter

class ProfessionPage:
    def __init__(self, screen, root, player, save_data, callback) -> None:
        self.screen = screen
        self.root = root
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)
        self.player = player
        self.save_data = save_data
        self.callback = callback

        self.prof_selecter = None
        self.end_button = None
        self.hoby_selecter = None
        
    def load_selecter(self, selected_hobby):
        # 職業選択画面
        self.prof_selecter = ProfessionSelecter(self.screen)

        # キャラ作成終了ボタン
        self.end_button = Button(self.screen, self.font, "キャラ作成\n終了", (640,340,100,50), self.end_button_event)

        # 趣味選択画面
        self.hoby_selecter = HobbySelecter(self.screen, selected_hobby)

    # 終了ボタンを押した時のイベント
    def end_button_event(self):
        manual_input_fields = { "name": "名前が入力されていません",
                                "age": "年齢が入力されていません",
                                "STR": "STRが入力されていません",
                                "CON": "CONが入力されていません",
                                "SIZ": "SIZが入力されていません",
                                "DEX": "DEXが入力されていません",
                                "APP": "APPが入力されていません",
                                "EDU": "EDUが入力されていません",
                                "INT": "INTが入力されていません",
                                "POW": "POWが入力されていません",
                                "Profession":"職業が選択されていません",
                                "Hobby":"趣味が選択されていません"
                                }
        texts = []

        # 手動入力が必要なステータスのみエラーチェックする
        for status, error_msg in manual_input_fields.items():
            if getattr(self.player, status) == "" or getattr(self.player, status) == 0:
                texts.append(error_msg)
        if texts:
            text = "\n".join(texts)
            with TopmostManager(self.root):
                messagebox.showerror("未入力", text)
        else:
            # セーブデータに主人公データを入れる
            self.save_data["player_status"] = self.player.to_dict()

            # セーブデータに少女のデータを入れる
            girl = Human("下僕の少女", 4, 6, 10, 5, 10, 10,"-1d4", 8, 10, 10,
                         {"目星":55, "聞き耳":55, "忍び歩き":40,"隠れる":40,"応急手当":50, "中国語（母国語）":40, "追跡":50, "その他言語（主人公の母国語）":31,"クトゥルフ神話":15, "拳銃":20},
                         17, "woman", 13, 6, 50, 50, 30, 0, 0, "放浪者")
            girl.add_item(ITEM_LIST["bloody_robe"])
            girl.add_item(ITEM_LIST["gun"])

            self.save_data["girl_status"] = girl.to_dict()

            self.callback(State.SAVE)

    def draw(self, selected_profession, is_pulldown_open):
        if self.prof_selecter:
            self.prof_selecter.draw()
        if selected_profession:
            selected_profession.image_draw(is_selected=True)
        self.end_button.draw()
        self.hoby_selecter.draw_item(is_pulldown_open)

    def handle_mouse_hover(self, pos, is_pulldown_open):
        if is_pulldown_open:
            return self.hoby_selecter.handle_mouse_hover(pos, is_pulldown_open)
        else:
            for prof in self.prof_selecter.prof_items:
                text = prof.handle_mouse_hover(pos)
                if text:
                    return text
                
            if self.end_button.rect.collidepoint(pos):
                self.end_button.update(pos)
                if not text:
                    return "キャラクター作成を終了します"
        return None
    
    def handle_click(self, pos, is_pulldown_open, selected_profession, selected_hobby):
        # プルダウンのクリック処理
        if self.hoby_selecter.pull.box.rect.collidepoint(pos):
            is_pulldown_open = not is_pulldown_open
            print(f"is_pulldown_open:{is_pulldown_open}")

        # プルダウンが開いているときは
        if is_pulldown_open:
            # 趣味欄のクリック処理
            selected_item = self.hoby_selecter.pull.handle_click(pos, is_pulldown_open)
            if selected_item:
                selected_hobby = selected_item
                self.player.Hobby = selected_item
                self.hoby_selecter.pull.update_label(f"{selected_item}")
                self.hobby_data_set(selected_hobby)
                is_pulldown_open = False
        else:
            # もしプルダウンが開いていなかったら
            # ボタンのクリック処理
            if self.end_button.is_clicked(pos):
                self.end_button.update(pos, True)
            else:
                # 職業のクリック処理
                selected_item = self.prof_selecter.handle_click(pos)
                if selected_item:
                    selected_profession = selected_item
                    self.player.Profession = selected_item.name
                    self.profession_data_set()

        return is_pulldown_open, selected_profession, selected_hobby

    # 選択した職業から主人公のステータスにデータを入れるよ
    def profession_data_set(self):
        # 主人公の所持スキルをリセット
        self.player.skill = {}
        # 回避もスキル一覧にあるので回避もリセット
        self.player.Dodge = self.player.DEX * 2

        profession_list = load_json(PROF_DATA_PATH)
        skill_list = load_json(SKILL_DATA_PATH)

        # 職業から設定されている技能一覧を取得
        current_profession = self.player.Profession
        profession_skills = profession_list[current_profession]["skill"]

        # 加算できる技能ポイントを算出する
        max_skill_points = self.player.EDU * 20
        remaining_points = max_skill_points
        for skill, percent in profession_skills.items():
            # 割り振る技能ポイントを計算
            bonus_points = int(max_skill_points * (percent / 100))

            # 基本技能ポイント
            if skill == "回避":
                current_skill_value = self.player.Dodge
            else:
                current_skill_value = skill_list[skill]

            # ポイントを計算する
            new_skill_value, surplus_points = Calculation(current_skill_value, bonus_points, 90)

            # 主人公のステータスにポイントを入力
            if skill == "回避":
                self.player.Dodge = new_skill_value
            else:
                self.player.skill[skill] = new_skill_value

            # 技能ポイント - 使用した技能ポイント + 余りの技能ポイント
            remaining_points = remaining_points - bonus_points + surplus_points

            # 技能ポイントが足りなかった場合
            if remaining_points < 0:
                print("技能ポイントが足りません")
                break

        # 全ての技能ポイント割り振り後にポイントが余った場合
        if remaining_points > 0:
            # ポイントが0になるまで繰り返す
            while remaining_points > 0:
                lists = {}
                # スキルリストから90以下のスキルをリスト化する
                for skill in self.player.skill:
                    skill_value = self.player.skill[skill]
                    if skill_value < 90:
                        lists[skill] = skill_value
                if len(lists) > 0:
                    # リストの数よりポイントが多い場合
                    if len(lists) < remaining_points:
                        # リストの数でポイントを割る
                        bonus_points = int(remaining_points / len(lists))
                        
                        # 計算していく
                        for skill, current_skill_value in lists.items():
                            new_skill_value, surplus_points = Calculation(current_skill_value, bonus_points, 90)
                            self.player.skill[skill] = new_skill_value
                            remaining_points = remaining_points - bonus_points + surplus_points
                    else:
                        select = random.choice(list(lists))
                        self.player.skill[select]  += remaining_points
                        remaining_points -= remaining_points

    # 選択した趣味から主人公のステータスにデータを入れるよ
    def hobby_data_set(self, selected_hobby):
        # 主人公の持っている技能データ
        my_skills = self.player.skill

        # 趣味リストの技能データ
        hobby_list = load_json(HOBBY_DATA_PATH)
        hobby_skills = hobby_list[selected_hobby]
        # 技能リスト
        skill_list = load_json(SKILL_DATA_PATH)

        # 最大振り分けポイント
        max_points = self.player.INT * 10
        # スキルの振り分け割合
        percent = [70,30]
        if max_points > 0:
            remaining_points = max_points
            for i, skill in enumerate(hobby_skills):
                # 元の技能ポイント
                if skill in my_skills:
                    current_value = my_skills[skill]
                else:
                    current_value = skill_list[skill]
                # 技能ポイントをパーセンテージ分算出
                bonus_points = int(max_points * (percent[i] / 100))
                # 計算する
                new_value, surplus_points = Calculation(current_value, bonus_points, 90)
                # スキルに値を入れる
                self.player.skill[skill] = new_value
                # 残りのポイントを算出
                remaining_points = remaining_points - bonus_points + surplus_points

            # ポイントが余った場合
            if remaining_points > 0:
                for i, skill in enumerate(hobby_skills):
                    current_value = my_skills[skill]
                    new_value, surplus_points = Calculation(current_value, remaining_points, 90)
                    self.player.skill[skill] = new_value
                    remaining_points = surplus_points
