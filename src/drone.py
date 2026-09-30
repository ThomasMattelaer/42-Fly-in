from typing import Optional


class Drone ():
    """Represents an autonomous drone traversing the network.

    Attributes:
        drone_id (int): Unique identifier for the drone.
        current_hub (str): Name of the hub where the drone is located.
        target_hub (Optional[str]): Name of the destination hub if the drone
            is in transit, otherwise None.
        pos_x (int): X-coordinate position of the drone on the map grid.
        pos_y (int): Y-coordinate position of the drone on the map grid.
        turns_left (int): Remaining movement turns before reaching target_hub.
    """
    def __init__(self,
                 drone_id: int,
                 current_hub: str,
                 pos_x: int,
                 pos_y: int,
                 target_hub: Optional[str] = None) -> None:
        """Initializes a new Drone instance.

        Args:
            drone_id (int): Unique identifier for the drone.
            current_hub (str): Starting hub name for the drone.
            pos_x (int): Initial X-coordinate position.
            pos_y (int): Initial Y-coordinate position.
            target_hub (Optional[str], optional): Initial destination hub name.
                Defaults to None.
        """
        self.drone_id = drone_id
        self.current_hub = current_hub
        self.target_hub = target_hub
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.path: list[tuple[str, int]] = []
