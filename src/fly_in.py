from menu import Menu, MapModel
from drone import Drone
from map import MapVisualiser
import sys


class SimulationEngine:
    def __init__(self, map_data: MapModel) -> None:
        self.map_data = map_data
        self.drones: list[Drone]

    def init_drones(self) -> None:
        start_hub = map_data.start_hub
        for i in range(self.map_data.drones):
            drone = Drone(id=i,
                          current_hub=start_hub.name,
                          pos_x=start_hub.x,
                          pos_y=start_hub.y,
                          in_transit=False)
            self.drones.append(drone)



if __name__ == "__main__":
    menu = Menu()
    try:
        map_data = menu.select_map_menu()
        simulation = SimulationEngine(map_data)
        simulation.init_drones()
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt error")
        sys.exit(0)
