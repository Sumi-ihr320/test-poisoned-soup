from constans import *
from ui_elements import *

from profession import ProfessionSelecter, HobbySelecter

class ProfessionPage:
    def __init__(self, screen, root, hero_data, save_data) -> None:
        self.screen = screen
        self.root = root
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)
        self.hero_data = hero_data
        self.save_data = save_data

        self.prof_selecter = None
        self.end_button = None
        self.hoby_selecter = None
        
    def load_selecter(self, is_pulldown_open, selected_hobby):
        # 職業選択画面
        self.prof_selecter = ProfessionSelecter(self.screen)

        # キャラ作成終了ボタン
        self.end_button = Button(self.screen, self.font, "キャラ作成\n終了", (640,340,100,50), self.end_button_event)

        # 趣味選択画面
        self.hoby_selecter = HobbySelecter(self.screen, is_pulldown_open, selected_hobby)

    # 終了ボタンを押した時のイベント
    def end_button_event(self):
        manual_input_fields = { "name":"名前が入力されていません",
                                "age":"年齢が入力されていません",
                                "STR":"STRが入力されていません",
                                "CON":"CONが入力されていません",
                                "SIZ":"SIZが入力されていません",
                                "DEX":"DEXが入力されていません",
                                "APP":"APPが入力されていません",
                                "EDU":"EDUが入力されていません",
                                "INT":"INTが入力されていません",
                                "POW":"POWが入力されていません",
                                "Profession":"職業が選択されていません",
                                "Hobby":"趣味が選択されていません"
                                }
        texts = []

        # 手動入力が必要なステータスのみエラーチェックする
        for status, error_msg in manual_input_fields.items():
            if self.hero_data.get(status) == "" or self.hero_data.get(status) == 0:
                texts.append(error_msg)
        if texts:
            text = "\n".join(texts)
            with TopmostManager(self.root):
                messagebox.showerror("未入力", text)
        else:
            # セーブデータに主人公データを入れる
            self.save_data["hero_status"] = self.hero_data
            self.end_flag = True

    def draw(self, selected_profession):
        if self.prof_selecter:
            self.prof_selecter.draw()
        if selected_profession:
            selected_profession.image_draw(is_selected=True)
        self.end_button.draw()
        self.hoby_selecter.draw_item()

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
    
    def handle_click(self, pos, is_pulludown_open):
        selected_profession = None
        selected_hobby = None

        # プルダウンのクリック処理
        if self.hoby_selecter.pull.box.rect.collidepoint(pos):
            is_pulludown_open = not is_pulludown_open

        # プルダウンが開いているときは
        if is_pulludown_open:
            # 趣味欄のクリック処理
            selected_item = self.hoby_selecter.pull.handle_click(pos, is_pulludown_open)
            if selected_item:
                selected_hobby = selected_item
                self.hero_data["Hobby"] = selected_item
                self.hoby_selecter.pull.update_label(f"{selected_item}")
                self.hobby_data_set()
                is_pulludown_open = False
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
                    self.hero_data["Profession"] = selected_item.name
                    self.profession_data_set()

        return is_pulludown_open, selected_profession, selected_hobby

    # 選択した職業から主人公のステータスにデータを入れるよ
    def profession_data_set(self):
        # 主人公の所持スキルをリセット
        self.hero_data["skill"] = {}
        # 回避もスキル一覧にあるので回避もリセット
        self.hero_data["Avo"] = self.hero_data["DEX"] * 2

        profession_list = load_json(PROF_DATA_PATH)
        skill_list = load_json(SKILL_DATA_PATH)

        # 職業から設定されている技能一覧を取得
        current_profession = self.hero_data["Profession"]
        profession_skills = profession_list[current_profession]["skill"]

        # 加算できる技能ポイントを算出する
        max_skill_points = self.hero_data["EDU"] * 20
        remaining_points = max_skill_points
        for skill, percent in profession_skills.items():
            # 割り振る技能ポイントを計算
            bonus_points = int(max_skill_points * (percent / 100))

            # 基本技能ポイント
            if skill == "回避":
                current_skill_value = self.hero_data["Avo"]
            else:
                current_skill_value = skill_list[skill]

            # ポイントを計算する
            new_skill_value, surplus_points = Calculation(current_skill_value, bonus_points, 90)

            # 主人公のステータスにポイントを入力
            if skill == "回避":
                self.hero_data["Avo"] = new_skill_value
            else:
                self.hero_data["skill"][skill] = new_skill_value

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
                for skill in self.hero_data["skill"]:
                    skill_value = self.hero_data["skill"][skill]
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
                            self.hero_data["skill"][skill] = new_skill_value
                            remaining_points = remaining_points - bonus_points + surplus_points
                    else:
                        select = random.choice(list(lists))
                        self.hero_data["skill"][select]  += remaining_points
                        remaining_points -= remaining_points

    # 選択した趣味から主人公のステータスにデータを入れるよ
    def hobby_data_set(self):
        # 主人公の持っている技能データ
        my_skills = self.hero_data["skill"]

        # 趣味リストの技能データ
        hobby_list = load_json(HOBBY_DATA_PATH)
        hobby_skills = hobby_list[self.selected_hobby]
        # 技能リスト
        skill_list = load_json(SKILL_DATA_PATH)

        # 最大振り分けポイント
        max_points = self.hero_data["INT"] * 10
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
                self.hero_data["skill"][skill] = new_value
                # 残りのポイントを算出
                remaining_points = remaining_points - bonus_points + surplus_points

            # ポイントが余った場合
            if remaining_points > 0:
                for i, skill in enumerate(hobby_skills):
                    current_value = my_skills[skill]
                    new_value, surplus_points = Calculation(current_value, remaining_points, 90)
                    self.hero_data["skill"][skill] = new_value
                    remaining_points = surplus_points
