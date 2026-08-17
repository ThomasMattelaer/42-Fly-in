from menu import Menu, MapModel
from parser import HubModel
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

    def move_drones(self, drones: list[Drone]) -> None:
        for drone in drones:
            next_destination = self.get_next_hub_name(drone.current_hub)
            if next_destination:
                drone.target_hub = next_destination
                target_obj = self.get_hub(next_destination)
                if target_obj:
                    drone.pos_x = target_obj.x
                    drone.pos_y = target_obj.y
                    drone.current_hub = drone.target_hub

    def get_next_hub_name(self, current_hub_name: str) -> str:
        """Trouve la destination reliée à current_hub_name
        dans les connexions."""
        for conn in self.map_data.connections:
            if conn.zone1 == current_hub_name:
                return conn.zone2
        return ""

    def get_hub(self, hub_name: str) -> HubModel:
        map_data = self.map_data
        all_hubs = [map_data.start_hub, map_data.end_hub] + map_data.hubs
        hubs_by_name = {hub.name: hub for hub in all_hubs}
        if hub_name not in hubs_by_name:
            raise ValueError(f"Hub: {hub_name} hasn't been found")
        return hubs_by_name[hub_name]


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
