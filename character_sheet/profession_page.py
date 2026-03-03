import random
from typing import Tuple, Optional
from pygame import Surface, Rect

from constans import JSON_FOLDER, PROF_DATA_PATH, SKILL_DATA_PATH, HOBBY_DATA_PATH
from utils import load_json, Calculation
from models.characters import Player
from manager.sound_manager import sound_manager

from character_sheet.base_page import BasePage
from character_sheet.profession import ProfessionSelector, HobbySelector, Profession

class ProfessionPage(BasePage):
    def __init__(self, screen, root, player: Player, ofset: Optional[Tuple[int, int]]=None):
        super().__init__(screen, root, player, ofset)

        self.prof_selector = None
        self.hobby_selector = None

    def load_selector(self, selected_hobby: Optional[str]=None):
        # 職業選択画面
        self.prof_selector = ProfessionSelector(self.screen, self, self.rect, self.font_datas)

        # 趣味選択画面
        self.hobby_selector = HobbySelector(self.screen, self, selected_hobby, self.font_datas, self.prof_selector.rect)

    def relayout(self, screen):
        super().relayout(screen)
        self.prof_selector.relayout(screen, self, self.rect)
        self.hobby_selector.relayout(screen, self)
        
    def draw(self, selected_profession: Optional[Profession], is_pulldown_open: bool) -> Tuple[Surface, Rect]:
        surface, rect = super().draw()
        if self.prof_selector:
            self.prof_selector.draw()
        if selected_profession:
            selected_profession.draw(is_selected=True)
        self.hobby_selector.draw(is_pulldown_open)
        return surface, rect

    def handle_mouse_hover(self, pos, is_pulldown_open: bool) -> Optional[str]:
        pos = self.pos_calculation(pos)
        if is_pulldown_open:
            return self.hobby_selector.handle_mouse_hover(pos, is_pulldown_open)
        else:
            for prof in self.prof_selector.prof_items:
                text = prof.handle_mouse_hover(pos)
                if text:
                    return text
        return None
    
    def handle_click(self, pos, is_pulldown_open: bool, selected_profession: Optional[Profession], selected_hobby: Optional[str]) -> Tuple[bool, Optional[Profession], Optional[str]]:
        # プルダウンのクリック処理
        if self.hobby_selector.pull.collidepoint(pos):
            is_pulldown_open = not is_pulldown_open
            print(f"is_pulldown_open:{is_pulldown_open}")

        # プルダウンが開いているときは
        if is_pulldown_open:
            # 趣味欄のクリック処理
            selected_item = self.hobby_selector.pull.handle_click(pos, is_pulldown_open)
            if selected_item:
                sound_manager.play("クリック")
                selected_hobby = selected_item
                self.player.Hobby = selected_item
                self.hobby_selector.pull.update_label(f"{selected_item}")
                self.set_to_skills_from_hobby(selected_hobby)
                is_pulldown_open = False
        else:
            # もしプルダウンが開いていなかったら
            # 職業のクリック処理
            selected_item = self.prof_selector.handle_click(pos)
            if selected_item:
                selected_profession = selected_item
                self.player.Profession = selected_item.name
                self.set_to_skills_from_profession()

        return is_pulldown_open, selected_profession, selected_hobby

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
    def set_to_skills_from_hobby(self, selected_hobby: Optional[str]):
        # 主人公の持っている技能データ
        my_skills = self.player.skill

        # 趣味リストの技能データ
        hobby_list = load_json(HOBBY_DATA_PATH, JSON_FOLDER)
        hobby_skills = hobby_list[selected_hobby]
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
