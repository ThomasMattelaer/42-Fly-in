from typing import Optional


class Drone ():
    def __init__(self,
                 drone_id: int,
                 current_hub: str,
                 pos_x: int,
                 pos_y: int,
                 target_hub: Optional[str] = None) -> None:
        self.drone_id = drone_id
        self.current_hub = current_hub
        self.target_hub = target_hub
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.turns_left: int = 0

    @property
    def is_in_transit(self) -> bool:
        return self.turns_left > 0
