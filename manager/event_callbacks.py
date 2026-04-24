from typing import Optional, Callable
from dataclasses import dataclass

@dataclass(frozen=True)
class EventCallbacks:
    on_scenario_start: Optional[Callable] = None
    on_room_transition: Optional[Callable] = None
    on_room_refresh: Optional[Callable] = None
    on_scene_state_change: Optional[Callable] = None
