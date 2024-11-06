import pygame
import pygame.draw
from pygame.locals import *

from constans import *
from utils import *
from ui_elements import *

from room import Room

# プレイ画面
class MainPlay:
    def __init__(self, screen, root, save_data=None):
        self.screen = screen
        self.root = root
        self.save_data = save_data
        self.hero_status = save_data["hero_status"]  # 主人公のステータス
        
        # フラグをセットする
        self.set_flag(save_data["flag"])

        # メニューを作る
        self.menu = None
        self.create_menu()
    
        # ナビゲーションバー
        self.right_navi = None
        self.left_navi = None
        self.under_navi = None
        self.create_navigetion()

        # 部屋を作る
        self.room = None
        self.create_room()

        # 主人公のステータス表示
        self.status_label = None
        self.create_hero_label()

        # 表示するシナリオのリスト
        self.scenario_list = []
        # テキストフレームに表示するテキスト
        self.text = ""

        # 選択されたアイテム
        self.selected_item = None
        self.item_max_flag = 0

    # メニューの作成
    def create_menu(self):
        self.menu = Menu(self.screen, self.root, self.set_state)

    # 部屋の作成
    def create_room(self):
        room2_flag = self.room2_flag_check(self.room_flag)
        self.room = Room(self.screen, self.room_flag, self.direction_flag, room2_flag)
        self.max_room_scenario_flag = len(self.room.scenario_list)
        print(self.room.scenario_list)  # デバッグ用

    # 二つ目の部屋表示チェック
    def room2_flag_check(self, room):
        if room == "east":
            return self.east_room_flag["visivle"]
        elif room == "west":
            return self.book_flag["found"]
        else:
            return False

    # 主人公の名前・HP・MP・現在地を右上に表示する
    def create_hero_label(self):
        font = pygame.font.Font(FONT_PATH, SMALL_SIZ)
        name_label = Label(self.screen, font, self.hero_status["name"], 500, 10, position="right", color=WHITE)
        hp_label = Label(self.screen, font, f"HP/{self.hero_status["HP"]}", 590, 10, position="right", color=WHITE)
        mp_label = Label(self.screen, font, f"MP/{self.hero_status["MP"]}", 650, 10, position="right", color=WHITE)
        current_room_label = Label(self.screen, font, ROOM_NAME[self.room_flag], 770, 10, position="right", color=WHITE)
        self.status_label = [name_label, hp_label, mp_label, current_room_label]

    # フラグをセットする
    def set_flag(self, play_flags):
        # フラグ一覧
        self.state = State.NONE     # saveやload等の状態管理フラグ
        self.time = play_flags.get("time", 60)  # 残り時間フラグ（分）
        self.room_flag = play_flags.get("room_flag", "center")              # どの部屋にいるかフラグ
        self.direction_flag = play_flags.get("direction_flag", "north")     # どの方角を向いているかフラグ
        self.girl_flag = play_flags.get("girl_flag", False)                 # 少女を見つけてるかフラグ

        self.room_scenario_flag = play_flags.get("room_scenario_flag", {"center":0, "north":0, "south":0, "east":0, "west":0})    # 各部屋のシナリオフラグ
        self.max_room_scenario_flag = 0             # シナリオフラグの最大値
        self.light_flag = play_flags.get("light_flag", False)               # 電球が取られていないかフラグ
        self.east_room_flag = play_flags.get("east_room_flag", {"open":False, "visivle":False})     # 東の部屋のフラグ
        self.poison_get_flag = play_flags.get("poison_get_flag", False)     # 毒を見つけているかフラグ

        # アイテムの状態フラグ
        self.soup_flag = play_flags.get("soup_flag", {"poison":False, "know":False, "drink":False, "temperature":0}) # スープに関するフラグ
        self.center_memo_flag = play_flags.get("center_memo_flag", {"scenario":0, "objective":False})       # 真ん中の部屋のメモに関するフラグ
        self.book_flag = play_flags.get("book_flag", {"found":False, "get":False})  # 西の部屋の本に関するフラグ

    # セーブデータを作る
    def create_save_data(self):
        save_data = {}
        save_data["hero_status"] = self.hero_status
        flag = {"time":self.time,
                "room_flag":self.room_flag,
                "direction_flag":self.direction_flag,
                "girl_flag":self.girl_flag,
                "room_scenario_flag":self.room_scenario_flag,
                "light_flag":self.light_flag,
                "east_room_flag":self.east_room_flag,
                "poison_get_flag":self.poison_get_flag,
                "soup_flag":self.soup_flag,
                "center_memo_flag":self.center_memo_flag,
                "book_flag":self.book_flag
                }
        save_data["flag"] = flag
        self.save_data = save_data

    # ナビゲーションバーを作成
    def create_navigetion(self):
        # ナビゲーションバーの表示
        if self.room_flag == "center":
            self.right_navi = PageNavigation(self.screen, RIGHT)
            self.left_navi = PageNavigation(self.screen, LEFT)
        else:
            self.under_navi = PageNavigation(self.screen, UNDER)

    # 向き移動先を取得
    def direction_move_get(self, position, direction):
        if position == "right":
            if direction == "north":
                return "east"
            elif direction == "east":
                return "south"
            elif direction == "south":
                return "west"
            else:
                return "north"
        elif position == "left":
            if direction == "north":
                return "west"
            elif direction == "west":
                return "south"
            elif direction == "south":
                return "east"
            else:
                return "north"
            
        # 扉からの移動先
        elif position == "center":
            return direction
                
        else:
            return direction

    # 部屋の戻り先を取得
    def room_move_direction_get(self, room):
        if room == "north":
            direction = "south"
        elif room == "south":
            direction = "north"
        elif room == "east":
            direction = "west"
        else:
            direction = "east"
        return "center", direction

    # 部屋移動をまとめる
    def move_room(self, position):
        if position == "under":
            if self.book_flag["get"]:
                # 本を持って出ようとしたらイベント
                pass
                # 戦闘終了後は部屋のほうを向いている
                self.room_flag, self.direction_flag = "center", self.room_flag
                # 扉が元に戻ったことを説明
            else:
                self.room_flag, self.direction_flag = self.room_move_direction_get(self.room_flag)
            self.status_label[3].update_text(ROOM_NAME[self.room_flag])
        else:
            self.direction_flag = self.direction_move_get(position, self.direction_flag)
        self.create_room()

    # 部屋に最初に入った時に起こるイベント   ※イベント中は他のクリックイベントは作動しない
    def first_room_scenario_count(self, room):
        if self.room_scenario_flag[room] < self.max_room_scenario_flag:
            self.room_scenario_flag[room] += 1
            return True
        return False
    
    # アイテムが選択された時のシナリオフラグカウント（うまくいってない）
    def selected_item_scenario_count(self, item):
        if item == "centerMemo":
            if self.center_memo_flag["scenario"] < self.item_max_flag:
                self.center_memo_flag["scenario"] += 1
                return True
        return False

    # アイテムクリック時のイベントをまとめる
    def handle_item_click_event(self, event):
        for item in self.room.items_select_list:
            if item.handle_click(event.pos):
                if self.selected_item:
                    self.selected_item = None
                    self.screen.fill(BLACK)
                    self.main_draw()
                self.selected_item = item
                print(item.name)                # デバッグ用
                print(item.scenario_path_list)  # デバッグ用
                return True
        self.selected_item = None
        return False

    def handle_mouse_hover(self):
        key = pygame.mouse.get_pos()
        for button in self.menu.buttons:
            button.update(key)
        if self.selected_item and self.selected_item.menu_buttons:
            for button in self.selected_item.menu_buttons:
                button.update(key)

    def handle_events(self):
        for event in pygame.event.get():
            # 閉じるボタンで終了
            if event.type == QUIT:
                Close(self.root)
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                Close(self.root)
            # マウスクリック時
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event)

    def handle_click(self, event):
        if not self.first_room_scenario_count(self.room_flag):
            if not self.selected_item_scenario_count(self.selected_item):
                # メニューボタン
                for button in self.menu.buttons:
                    if button.update(event.pos, True):
                        return

                if self.room_flag == "center":
                    # ナビゲーションバーによる移動
                    if self.right_navi and self.right_navi.handle_click(event.pos):
                        self.move_room("right")
                        self.selected_item = None
                    elif self.left_navi and self.left_navi.handle_click(event.pos):
                        self.move_room("left")
                        self.selected_item = None
                    else:
                        if self.handle_item_click_event(event):
                            return
                else:
                    # ナビゲーションバーによる移動
                    if self.under_navi and self.under_navi.handle_click(event.pos):
                        self.move_room("under")
                    else:
                        if self.handle_item_click_event(event):
                            return

    

    def draw(self):
        self.main_draw()
        if self.selected_item:
            img_number = 0
            if self.selected_item == "Soup":
                if self.soup_flag["drink"]:
                    img_number = 1
                elif self.soup_flag["poison"]:
                    img_number = 2
            self.selected_item.draw(is_selected=True, img_number=img_number)
        else:
            # 選択されたアイテムが無い場合は再描画
            self.screen.fill(BLACK)
            #self.main_draw()
    
    # 基本の描画をまとめてみた
    def main_draw(self):
        create_frame(self.screen)   # テキストフレームの表示
        self.menu.draw()            # メニューの表示
        self.room.draw()            # 部屋の表示

        # ナビゲーションバーの表示
        if self.left_navi:
            self.left_navi.draw()
        if self.right_navi:
            self.right_navi.draw()
        if self.under_navi:
            self.under_navi.draw()

        # 主人公のステータスの表示
        for status in self.status_label:
            status.draw()

    # シナリオを作成する
    def create_scenario(self):
        self.text = ""
        file_name = ""
        if self.room_scenario_flag[self.room_flag] < self.max_room_scenario_flag:
            if self.room.scenario_list:
                file_name = self.room.scenario_list[self.room_scenario_flag[self.room_flag]]
        else:
            if self.selected_item:
                if self.selected_item.name == "Soup":
                    if self.time >= 45:
                        time = 1
                    elif self.time >= 30:
                        time = 2
                    elif self.time >= 15:
                        time = 3
                    else:
                        time = 4
                    event = "know" if self.soup_flag["know"] else ""
                    file_name = create_scenario_path(item="Soup", event=event, time=time)[0]
                elif self.selected_item.name == "centerMemo":
                    self.item_max_flag = 4 if self.center_memo_flag["objective"] else 3
                    if self.center_memo_flag["scenario"] < self.item_max_flag:
                        file_name = self.selected_item.scenario_path_list[self.center_memo_flag["scenario"]]
                elif self.selected_item.scenario_path_list:
                    file_name = self.selected_item.scenario_path_list[0]
        if file_name:
            self.text = load_text(file_name)

    def item_event(self):
        # menuを表示

        # doorのイベント
        # ドア画像表示
        # メニュー表示 → 入るで移動
        # 東の部屋は鍵開けイベント有り
        # 南の部屋は窓を覗く、聞き耳、入る（静かに・普通に・勢いよく）
    

        # centerMemoの時のイベントまとめ
        # memo1～3のシナリオ表示
        # memo1の時は1枚目の画像、memo3の時に２枚目の画像、memo4の時に３枚目の画像を表示
        # memoに目星コマンドでmemo_objectiveシナリオ表示 → 目星ダイスロール
        # 目星成功でmemo_objectiveシナリオ進行 → objectiveフラグtrue
        # memo1～4でシナリオが表示されるように

        # soupは医学成功で情報開示
        # あとは時間等で表示が変わる

        pass
    
    # シナリオ表示用
    def draw_scenario(self):
        self.create_scenario()
        TextDraw(self.screen, self.text)

    def update(self):
        self.draw()
        self.handle_mouse_hover()
        self.handle_events()
        self.draw_scenario()
        return self.next_state()

    # メニューボタン用のコールバック関数
    def set_state(self, state=State.NONE):
        self.create_save_data()
        self.state = state

    def next_state(self):
        if self.state == State.SAVE:
            self.state = State.NONE
            return "save", self.save_data
        elif self.state == State.LOAD:
            self.state = State.NONE
            return "load", self.save_data
        return "play", self.save_data
