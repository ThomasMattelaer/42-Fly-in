from menu import Menu, MapModel
from drone import Drone
from map import MapVisualiser
import sys


class SimulationEngine:
    def __init__(self, map_data: MapModel) -> None:
        self.map_data = map_data
        self.drones: list[Drone] = self.init_drones()

    def init_drones(self) -> list[Drone]:
        start_hub = map_data.start_hub
        drones: list[Drone] = []
        for i in range(self.map_data.drones):
            drone = Drone(drone_id=i,
                          current_hub=start_hub.name,
                          pos_x=start_hub.x,
                          pos_y=start_hub.y
                          )
            drones.append(drone)
        return drones


if __name__ == "__main__":
    menu = Menu()
    try:
        map_data = menu.select_map_menu()
        simulation = SimulationEngine(map_data)
        map = MapVisualiser(map_data, simulation)
        map.run()
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt error")
        sys.exit(0)
