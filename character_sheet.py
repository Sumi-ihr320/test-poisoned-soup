import pygame
import pygame.draw
from pygame.locals import *

from data import *
from fanction_summary import *
from class_summary import *

# キャラクターシート作成画面をクラス化してみる
class CharacterSheet:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZ)

        self.page_navi = None   # ナビゲーションバー
        self.now_page = 0       # 現在のページ
        self.sex_button = None  # 男女ボタン
        self.status_items = []  # ステータスのアイテム一覧
        self.end_flag = False   # キャラシ作成を終わるフラグ

        self.selected_profession = None     # 選択中の職業

        self.is_pulludown_open = False      # プルダウン用のフラグ
        self.selected_hobby = ""            # 選択中の趣味

        # 設定する主人公のステータス
        chara_data = load_json(CHARA_DATA_PATH)
        self.hero_data = chara_data["Hero"]

    # シートの描画
    def draw_sheet(self):
        pygame.draw.rect(self.screen, SHEET_COLOR, SHEET_RECT)
        
    # テキストフレームの表示
    def draw_frame(self):
        create_frame(self.screen)

    # ページを表示する
    def draw_page(self):
        self.create_navigation(self.now_page)
        if self.now_page == 0:
            self.create_status_page()
            for item in self.status_items:
                item.draw()
            if self.sex_button:
                self.sex_button.draw(self.hero_data["sex"])
        else:
            self.create_profession_page()
            self.prof_selecter.draw()
            if self.selected_profession:
                self.selected_profession.image_draw(is_selected=True)
            self.end_button.draw()
            self.hoby_selecter.draw_item()
            
    # キャラステータス作成画面を作る
    def create_status_page(self):
        status_json = load_json(STATUS_DATA_PATH)
        if not self.status_items:   # すでにアイテムがあるか確認
            for status in status_json:
                items = status_json[status]
                item = Status(self.screen, items["name"], status, items["view_name"],
                            items["x"], items["y"], items["w"], items["h"], items["text"],
                            items["button_flag"], items["input_flag"], items["box_flag"], items["dice_text"])
                self.status_items.append(item)
                if status == "sex":
                    self.sex_button = SexChange(self.screen, 310, 80, self.hero_data["sex"])
    
    # 職業ページを作る
    def create_profession_page(self):
        # 職業選択画面
        self.prof_selecter = ProfessionSelecter(self.screen)

        # キャラ作成終了ボタン
        self.end_button = Button(self.screen, self.font, (600,330,100,50), "キャラ作成\n終了", self.end_button_event)        

        # 趣味選択画面
        self.hoby_selecter = HobbySelecter(self.screen, self.is_pulludown_open, self.selected_hobby)

    # ナビゲーションバーを作る
    def create_navigation(self, page):
        position = RIGHT if page == 0 else LEFT
        self.page_navi = PageNavigation(self.screen, position)

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
            messagebox.showerror("未入力", text)
        else:
            self.end_flag = True

    # マウスオーバーイベント
    def handle_mouse_hover(self):
        # マウスオーバーでテキスト表示するよ
        key = pygame.mouse.get_pos()
        horver_text = None

        # ページによって変わる
        if self.now_page == 0:
            for stat in self.status_items:
                if stat.button:
                    stat.button.update(key)
                text = stat.handle_mouse_hover(key)
                if text is not None:
                    horver_text = text
                    break
        else:
            horver_text = self.hoby_selecter.handle_mouse_hover(key, self.is_pulludown_open)

            if not self.is_pulludown_open:
                for prof in self.prof_selecter.prof_items:
                    text = prof.handle_mouse_hover(key)
                    if text is not None:
                        horver_text = text
                        break
                if self.end_button.rect.collidepoint(key):
                    self.end_button.update(key)
                    if horver_text is None:
                        horver_text = "キャラクター作成を終了します"

        if horver_text:
            TextDraw(self.screen, horver_text)

    # イベントハンドラ
    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンかESCキーで終了
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                Close()
            # マウス左クリック時
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.handle_mouse_click(event.pos)

    # マウスクリック時
    def handle_mouse_click(self, pos):
        # １ページ目だったら
        if self.now_page == 0:
            self.handle_first_page_click(pos)
        else:
        # 2ページ目だったら
            self.handle_second_page_click(pos)

    # 1ページ目の処理
    def handle_first_page_click(self, pos):
        # ページ移動
        if self.page_navi.handle_click(pos):
            self.now_page = 1
        # 男ボタン
        elif self.sex_button and self.sex_button.man.rect.collidepoint(pos):
            self.hero_data["sex"] = True
            self.sex_button.update_sex(True)
        # 女ボタン
        elif self.sex_button and self.sex_button.woman.rect.collidepoint(pos):
            self.hero_data["sex"] = False
            self.sex_button.update_sex(False)
        else:
            # 他のステータスをリストでまとめた
            for status in self.status_items:
                # インプットボックス
                if status.input and status.input.rect.collidepoint(pos) and status.input_flag:   # かつ入力フラグがonの場合
                    status.input_process(self.hero_data["EDU"])
                    self.insart_data(status)
                    break
                # ダイスボタン
                if status.button:
                    if status.button.update(pos, True):
                        self.insart_data(status)
                        break

    # 更新されたデータをステータスに入力＋自動計算する
    def insart_data(self, status):
        self.hero_data[status.status_name] = status.input.get_value()
        self.auto_calculation(status.status_name)

    # ステータスの自動計算
    def auto_calculation(self, name):
        calculations = {"STR": [self.calculation_damege_bonus],
                        "SIZ": [self.calculation_damege_bonus, self.calculation_health_point],
                        "CON": [self.calculation_health_point],
                        "POW": [self.calculation_power_related],
                        "INT": [self.calculation_idea],
                        "EDU": [self.calculation_educated_point],
                        "DEX": [self.calculation_avoid_point]}

        if name in calculations:
            for calculation in calculations[name]:
                calculation()

    # ダメージボーナスの計算
    def calculation_damege_bonus(self):
        st = self.hero_data["STR"] + self.hero_data["SIZ"]
        if 2 <= st <= 12:       val = "-1D6"
        elif 13 <= st <= 16:    val = "-1D4"
        elif 25 <= st <= 32:    val = "+1D4"
        elif 33 <= st <= 40:    val = "+1D6"
        else:                   val = "0"
        self.hero_data["DB"] = val
        self.update_status_label("DB", val)

    # HPの計算
    def calculation_health_point(self):
        self.hero_data["HP"] = (self.hero_data["CON"] + self.hero_data["SIZ"]) // 2
        self.update_status_label("HP", self.hero_data["HP"])

    # POW 関連の計算
    def calculation_power_related(self):
        # MP、幸運、SAN値の計算
        self.hero_data["MP"] = self.hero_data["POW"]
        val = self.hero_data["POW"] * 5
        self.hero_data["Luck"] = val
        self.hero_data["SAN"] = val
        self.update_status_label("MP", self.hero_data["MP"])
        self.update_status_label("Luck", val)
        self.update_status_label("SAN", val)

    # アイデアの計算
    def calculation_idea(self):
        self.hero_data["Idea"] = self.hero_data["INT"] * 5
        self.update_status_label("Idea", self.hero_data["Idea"])

    # 知識の計算
    def calculation_educated_point(self):
        val = self.hero_data["EDU"] * 5
        self.hero_data["Know"] = val if val < 99 else 99
        self.update_status_label("Know", self.hero_data["Know"])
        
    # 回避の計算
    def calculation_avoid_point(self):
        self.hero_data["Avo"] = self.hero_data["DEX"] * 2
        self.update_status_label("Avo", self.hero_data["Avo"])

    # ステータスラベルの更新
    def update_status_label(self, name, val):
        for item in self.status_items:
            if item.status_name == name:
                item.input.update_label(f"{val}")

    # 2ページ目の処理
    def handle_second_page_click(self, pos):
        # ページ移動
        if self.page_navi.handle_click(pos):
            self.now_page = 0
            # もし趣味のプルダウンが開いていたら閉じる
            if self.is_pulludown_open:
                self.is_pulludown_open = False

        # プルダウンのクリック処理
        elif self.hoby_selecter.pull.box.rect.collidepoint(pos):
            self.is_pulludown_open = not self.is_pulludown_open

        # プルダウンが開いているときは
        if self.is_pulludown_open:
            # 趣味欄のクリック処理
            selected_item = self.hoby_selecter.pull.handle_click(pos, self.is_pulludown_open)
            if selected_item:
                self.selected_hobby = selected_item
                self.hero_data["Hobby"] = selected_item
                self.hoby_selecter.pull.update_label(f"{selected_item}")
                self.hobby_data_set()
                self.is_pulludown_open = False
        else:
            # もしプルダウンが開いていなかったら

            # ボタンのクリック処理
            if self.end_button.is_clicked(pos):
                self.end_button.update(pos, True)
            else:
                # 職業のクリック処理
                selected_item = self.prof_selecter.handle_click(pos)
                if selected_item:
                    self.selected_profession = selected_item
                    self.hero_data["Profession"] = selected_item.name
                    self.profession_data_set()

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
        max_points = CharaStatus["INT"] * 10
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
                for i, skill in enumerate(hobby_list):
                    current_value = my_skills[skill]
                    new_value, surplus_points = Calculation(current_value, remaining_points, 90)
                    self.hero_data["skill"][skill] = new_value
                    remaining_points = surplus_points

    def update(self):
        self.draw_sheet()        
        self.draw_frame()
        self.draw_page()    # ページに応じた描画
        self.handle_mouse_hover()
        self.handle_events()
        return self.next_state()

    def next_state(self):
        if self.end_flag:
            return "save", "play"
        return "charasheet", ""        
