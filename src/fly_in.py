from menu import Menu, MapModel
from parser import HubModel
from drone import Drone
from map import MapVisualiser
from pathfinding import dijkstra_distance, get_neighbors
import sys


class SimulationEngine:
    def __init__(self, map_data: MapModel) -> None:
        self.map_data = map_data
        self.drones: list[Drone] = self.init_drones()
        self.pathfinding = dijkstra_distance(map_data, map_data.end_hub.name)

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
        occupancy:  dict[tuple[str, str], int] = {}
        for drone in drones:
            neighbors = get_neighbors(self.map_data, drone.current_hub)
            target = min(
                neighbors, key=lambda hub_name: self.pathfinding[hub_name]
                )
            if (self.is_conn_free(drone.current_hub, target, occupancy)
                    and self.is_hub_free(target)):
                drone.target_hub = target
                target_obj = self.get_hub(drone.target_hub)
                if target_obj:
                    origin_obj = self.get_hub(drone.current_hub)
                    is_restricted = target_obj.metadata.get(
                        "zone") == "restricted"
                    if is_restricted and drone.target_hub != drone.current_hub:
                        drone.pos_x = int(origin_obj.x +
                                            (target_obj.x - origin_obj.x) * 0.5)
                        drone.pos_y = int(origin_obj.y +
                                            (target_obj.y - origin_obj.y) * 0.5)
                        drone.in_transit = True
                    else:
                        drone.pos_x = target_obj.x
                        drone.pos_y = target_obj.y
                        drone.current_hub = drone.target_hub
                        drone.in_transit = False

    def get_hub(self, hub_name: str) -> HubModel:
        map_data = self.map_data
        all_hubs = [map_data.start_hub, map_data.end_hub] + map_data.hubs
        hubs_by_name = {hub.name: hub for hub in all_hubs}
        if hub_name not in hubs_by_name:
            raise ValueError(f"Hub: {hub_name} hasn't been found")
        return hubs_by_name[hub_name]

    def is_conn_free(self,
                     zone1: str,
                     zone2: str,
                     occupancy: dict[tuple[str, str], int]) -> bool:
        """Check wether or not if the conneciton is available"""
        a, b = sorted((zone1, zone2))
        link_key: tuple[str, str] = (a, b)
        current_usage = occupancy.get(link_key, 0)
        max_link_capacity = self.get_max_link_capacity(zone1, zone2)
        return current_usage < max_link_capacity

    def get_max_link_capacity(self, zone1: str, zone2: str) -> int:
        """Return the max_link_capacity of a connection"""
        for connection in self.map_data.connections:
            if (connection.zone1 == zone1 and connection.zone2 == zone2) or (
                    connection.zone1 == zone2 and connection.zone2 == zone1):
                return connection.metadata.get("max_link_capacity", 1)
        return 0

    def is_hub_free(self, target_hub: str) -> bool:
        """Check wether or not if the hub is available"""
        if target_hub == self.map_data.end_hub.name:
            return True
        for hub in self.map_data.hubs:
            if hub.name == target_hub:
                return hub.occupancy < hub.metadata.get("max_drones", 1)
        return False


if __name__ == "__main__":
    menu = Menu()
    try:
        map_data = menu.select_map_menu()
        simulation = SimulationEngine(map_data)
        map = MapVisualiser(map_data, simulation)
        print(simulation.pathfinding)
        map.run()
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt error")
        sys.exit(0)
