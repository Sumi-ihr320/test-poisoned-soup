from typing import Tuple, Optional, Any
from pygame import Surface, Rect

from constans import STATUS_DATA_PATH, JSON_FOLDER
from utils import load_json
from ui.ui_container_element import ContainerLabel, ContainerButton, ContainerInputBox
from character_sheet.status import Status, SexChange
from models.characters import Player
from character_sheet.base_page import BasePage
from character_sheet.status_calculator import *

class StatusPage(BasePage):
    def __init__(self, screen, root, player: Player, ofset: Optional[Tuple[int, int]]=None):
        super().__init__(screen, root, player, ofset)

        self.status_data: Dict[str, Dict[str, Any]] = load_json(STATUS_DATA_PATH, JSON_FOLDER)

        self.sex_button = None  # 性別ボタン

    # ステータスアイテムの作成
    def create_status_items(self):
        font_data = self.font_datas[0]
        for status, items in self.status_data.items():
            item = Status(self.screen, self, self.root, font_data=font_data, name=items["name"], status_name=status, label_name=items["view_name"], status=getattr(self.player, status),
                        x=items["x"], y=items["y"], w=items["w"], h=items["h"], hover_text=items["text"],
                        button_flag=items["button_flag"], input_flag=items["input_flag"], box_flag=items["box_flag"], dice_text=items["dice_text"],
                        row=items["row"], col=items["col"])
            self.add_elements(item)
            if status == "sex":
                self.sex_button = SexChange(self.screen, parent=self, sheet_rect=self.rect, font_data=font_data, title_text=items["view_name"], 
                                            x=items["x"], y=items["y"], flag=self.player.sex,
                                            row=items["row"], col=items["col"])
                self.add_elements(self.sex_button)

    def load_status_items(self):
        if not self.elements:   # すでにアイテムがあるか確認
            self.create_status_items()
    
    # 更新されたデータをステータスに入力＋自動計算する
    def insert_data(self, status: Status):
        setattr(self.player, status.status_name, status.input.get_value())
        self.auto_calculation(status.status_name)

    # ステータスの自動計算
    def auto_calculation(self, name: str):
        # 各ステータスに対応する計算
        calculations = {"STR": [calculation_damage_bonus],
                        "SIZ": [calculation_damage_bonus, calculation_health_point],
                        "CON": [calculation_health_point],

                        "POW": [calculation_power_related],
                        "INT": [calculation_idea],
                        "EDU": [calculation_educated_point],
                        "DEX": [calculation_avoid_point]}

        # 計算結果により変化するステータス
        response_status = {calculation_damage_bonus: ["DB"],
                          calculation_health_point: ["HP"],
                          calculation_power_related: ["MP","Luck","SAN"],
                          calculation_idea: ["Idea"],
                          calculation_educated_point: ["Know"],
                          calculation_avoid_point: ["Dodge"]}

        if name in calculations:
            for calculation in calculations[name]:
                # 計算結果を取得する
                val = calculation(self.player)
                if name == "EDU":
                    val = val if val < 99 else 99
                # 計算結果をステータスに入力 & ラベルの更新
                if name == "POW":
                    for status, value in val.items():
                        setattr(self.player, status, value)
                for status in response_status[calculation]:
                    if name != "POW":
                        setattr(self.player, status, val)
                    self.update_status_label(status, getattr(self.player, status))
    
    # ステータスラベルの更新
    def update_status_label(self, name: str, val: int|str):
        for item in self.elements:
            if hasattr(item, "status_name") and item.status_name == name:
                item.input.update_label(f"{val}")
    
    # 画面サイズ変更時にポジション等を更新する
    def relayout(self, screen):
        super().relayout(screen)
        for item in self.elements:
            item.relayout(screen, self)
        self.sex_button.relayout(screen, self)

    def draw(self) -> Tuple[Surface, Rect]:
        surface, rect = super().draw()
        if self.sex_button:
            self.sex_button.draw()
        return surface, rect
    
    # マウスオーバー
    def handle_mouse_hover(self, pos: Tuple[int, int]) -> Optional[str]:
        for item in self.elements:
            text = item.handle_mouse_hover(pos)
            if text is not None:
                return text
        return None

    # クリックイベント
    def handle_click(self, element: ContainerLabel|ContainerButton|ContainerInputBox, result: Status|SexChange):
        if result == self.sex_button:
            flag = [k for k, v in self.sex_button.labels_dict.items() if v == element][0]
            self.sex_button.update_sex(flag)
            self.player.sex = flag
            self.player.image = f"silhouette_{flag}.png"
        else:
            self.insert_data(result)
