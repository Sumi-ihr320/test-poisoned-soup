import random
from typing import Tuple, Optional
from pygame import Surface, Rect

from constans import JSON_FOLDER, PROF_DATA_PATH, SKILL_DATA_PATH, HOBBY_DATA_PATH
from utils import load_json, Calculation
from models.characters import Player
from ui.ui_container_element import ContainerImage, ContainerPullDown

from character_sheet.base_page import BasePage
from character_sheet.profession import ProfessionSelector, HobbySelector, Profession

class ProfessionPage(BasePage):
    def __init__(self, screen, root, text_frame_rect: Rect, player: Player, offset: Optional[Tuple[int, int]] = None):
        super().__init__(screen, root, text_frame_rect, player, offset)

        self.prof_selector = None
        self.hobby_selector = None

    def load_selector(self):
        # 職業選択画面
        self.prof_selector = ProfessionSelector(self.screen, parent=self, sheet_rect=self.rect, font_datas=self.font_datas)

        # 趣味選択画面
        self.hobby_selector = HobbySelector(self.screen, parent=self, font_datas=self.font_datas, profession_rect=self.prof_selector.rect)

    def register_all(self, focus_manager):
        self.hobby_selector.register_all(focus_manager)
        self.prof_selector.register_all(focus_manager)
    
    def unregister_all(self, focus_manager):
        self.hobby_selector.unregister_all(focus_manager)
        self.prof_selector.unregister_all(focus_manager)

    def relayout(self, screen):
        super().relayout(screen)
        self.prof_selector.relayout(screen, self, self.rect)
        self.hobby_selector.relayout(screen, self)
        
    def draw(self) -> Tuple[Surface, Rect]:
        surface, rect = super().draw()
        if self.prof_selector:
            self.prof_selector.draw()
        if self.hobby_selector:
            self.hobby_selector.draw()
        return surface, rect
    
    def handle_click(self, element: ContainerImage|ContainerPullDown, result: Profession|HobbySelector):
        if result == self.hobby_selector:
            if hasattr(element, "selected_item"):
                self.hobby_selector.selected_hobby = element.selected_item
                self.player.Hobby = element.selected_item
                if self.player.Hobby:
                    self.set_to_skills_from_hobby()

        elif result in self.prof_selector.children:
            self.prof_selector.selected_profession = result
            self.player.Profession = result.name
            self.set_to_skills_from_profession()


    # 選択した職業から主人公のステータスにデータを入れるよ
    def set_to_skills_from_profession(self):
        # 主人公の所持スキルをリセット
        self.player.skill = {}
        # 回避もスキル一覧にあるので回避もリセット
        self.player.Dodge = self.player.DEX * 2

        profession_list = load_json(PROF_DATA_PATH, JSON_FOLDER)
        skill_list = load_json(SKILL_DATA_PATH, JSON_FOLDER)

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
    def set_to_skills_from_hobby(self):
        # 主人公の持っている技能データ
        my_skills = self.player.skill

        # 趣味リストの技能データ
        hobby_list = load_json(HOBBY_DATA_PATH, JSON_FOLDER)
        hobby_skills = hobby_list[self.player.Hobby]
        # 技能リスト
        skill_list = load_json(SKILL_DATA_PATH, JSON_FOLDER)

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
