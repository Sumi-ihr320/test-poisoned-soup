from typing import Callable

from manager.scenario_manager import ScenarioManager
from manager.event_manager import EventManager
from playing.room_manager import RoomManager

class PlaySceneController:
    def __init__(self, room_manager: RoomManager, on_setup_navigation_callback: Callable):
        self.scenario_manager = None
        self.room_manager = room_manager

        self.on_setup_navigation_callback = on_setup_navigation_callback

    def set_scenario_manager(self, scenario_manager: ScenarioManager):
        self.scenario_manager = scenario_manager

    # イベントマネージャーから次のシナリオを受け取るためのコールバック関数
    def on_scenario_start_requested(self, next_scenario: str):
        self.scenario_manager.start_scenario(next_scenario)

    # イベントマネージャーから次の部屋に移るためのコールバック関数
    def on_room_transition_requested(self, room_id: str):
        next_room = room_id.split("-")[0]
        self.room_manager.move_to_room(next_room=next_room)
        self.on_setup_navigation_callback()
        self.scenario_manager.start_scenario(room_id)
        
    # 部屋の再作成をする（コールバック関数としても使う)
    def on_room_refresh_requested(self):
        self.room_manager.create_room()

    