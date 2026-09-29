import sys
import heapq
from drone import Drone
from map import MapVisualiser
from menu import Menu
from parser import HubModel, ParsingError, MapModel
from pathfinding import dijkstra_distance, get_neighbors


class SimulationEngine:
    """Active simulation.

    Attributes:
        map_data (MapModel): Map configuration data.
        drones (list[Drone]): Active drones in the simulation.
        pathfinding (dict[str, int]): Shortest distances from hubs to goal.
        hubs_by_name (dict[str, HubModel]): Map of hub names to hub objects.
    """

    def __init__(self, map_data: MapModel) -> None:
        """Initializes the simulation engine.

        Args:
            map_data (MapModel): Parsed map data to simulate.
        """
        self.map_data = map_data
        all_hubs = (
            [self.map_data.start_hub, self.map_data.end_hub]
            + self.map_data.hubs
        )
        self.hubs_by_name: dict[str, HubModel] = {
            hub.name: hub for hub in all_hubs
        }
        self.drones: list[Drone] = self.init_drones()
        self.pathfinding = dijkstra_distance(map_data, map_data.end_hub.name)
        self.hub_usage: dict[tuple[str, int], int] = {}
        self.conn_usage: dict[tuple[tuple[str, str], int], int] = {}
        self.plan_all(max_turn=50)

    def init_drones(self) -> list[Drone]:
        """Creates and places initial drones at the start hub.

        Returns:
            list[Drone]: List of initialized drones.
        """
        start_hub = self.map_data.start_hub
        drones: list[Drone] = []
        for i in range(self.map_data.drones):
            drone = Drone(
                drone_id=i,
                current_hub=start_hub.name,
                pos_x=start_hub.x,
                pos_y=start_hub.y,
            )
            drones.append(drone)
        start_hub.occupancy = len(drones)
        return drones

    def move_drones(self, current_turn: int) -> None:
        for drone in self.drones:
            path: list[tuple[str, int]] = drone.path
            for state in path:
                hub_name, turn = state
                if turn == current_turn:
                    old_hub = self.get_hub(drone.current_hub)
                    hub = self.get_hub(hub_name)
                    drone.pos_x = hub.x
                    drone.current_hub = hub_name
                    drone.pos_y = hub.y
                    old_hub.occupancy -= 1
                    hub.occupancy += 1
                else:
                    for connexion in self.conn_usage:
                        conn, turn_conn = connexion
                        if turn_conn == current_turn:
                            zone1, zone2 = conn
        self.print_output(current_turn)

    def print_output(self, current_turn: int) -> None:
        turn_movements = []
        for drone in self.drones:
            for i in range(len(drone.path) - 1):
                hub, turn = drone.path[i]
                next_hub, next_turn = drone.path[i + 1]
                if current_turn - 1 == turn:
                    if hub == next_hub:
                        continue
                    cost = self.travel_cost(next_hub)
                    if cost > 1:
                        conn_name = f"D{drone.drone_id}: {hub}-{next_hub}"
                        turn_movements.append(conn_name)
                    else:
                        turn_movements.append(f"D{drone.drone_id}: {next_hub}")
        print(" ".join(turn_movements))

    def plan_all(self, max_turn: int) -> None:
        for drone in self.drones:
            path = self.plan_drone(max_turn)
            if path is None:
                break
            drone.path = path
            self.reserve(path)

    def get_hub(self, hub_name: str) -> HubModel:
        """Retrieves a hub object by name.

        Args:
            hub_name (str): Name of target hub.

        Returns:
            HubModel: Requested hub instance.
        """
        if hub_name not in self.hubs_by_name:
            raise ValueError(f"Hub: {hub_name} hasn't been found")
        return self.hubs_by_name[hub_name]

    def get_max_link_capacity(self, zone1: str, zone2: str) -> int:
        """Gets maximum capacity for a connection.

        Args:
            zone1 (str): First hub name.
            zone2 (str): Second hub name.

        Returns:
            int: Maximum allowed drones on the connection.
        """
        for connection in self.map_data.connections:
            if (connection.zone1 == zone1 and connection.zone2 == zone2) or (
                connection.zone1 == zone2 and connection.zone2 == zone1
            ):
                try:
                    result = connection.metadata.get("max_link_capacity", 1)
                    return int(result)
                except ValueError as e:
                    raise ValueError(e)
        return 0

    def conn_key(self, zone1: str, zone2: str) -> tuple[str, str]:
        """sort the connection A-B == B-A
        Args: zone(str): the name of the zone of the connexion
        returns: a tuple of the connexion
        """
        return (zone1, zone2) if zone1 < zone2 else (zone2, zone1)

    def travel_cost(self, hub_name: str) -> int:
        """Check the cost of travelling to this hub
        Args: hub_name: the destiantion
        returns: a int of 1 or 2
        """
        hub = self.get_hub(hub_name)
        zone = hub.metadata.get("zone", "normal")
        if zone == "restricted":
            return 2
        return 1

    def hub_has_room(self, hub_name: str, turn: int) -> bool:
        """check if the hub has space at a specific timing
        args: hub_name: the name of the destination turn:the time we at
        returns: a bool
        """
        hub = self.get_hub(hub_name)
        if (
            hub_name == self.map_data.start_hub.name
                or hub_name == self.map_data.end_hub.name):
            return True
        try:
            max_drones = hub.metadata.get("max_drones", 1)
            return self.hub_usage.get((hub_name, turn), 0) < int(max_drones)
        except ValueError as e:
            raise ValueError(e)

    def conn_has_room(self, zone1: str, zone2: str, turn: int) -> bool:
        """check if the conn has space at a specific timing
            args: zones: the name of the connexion turn:the time we at
            returns: a bool
        """
        conn = self.conn_key(zone1, zone2)
        return (self.conn_usage.get((conn, turn), 0) <
                self.get_max_link_capacity(zone1, zone2))

    def drone_can_move(self, hub_name: str, next_hub: str, turn: int) -> bool:

        cost = self.travel_cost(next_hub)
        if hub_name == next_hub:
            return self.hub_has_room(hub_name, turn + 1)
        if not (self.conn_has_room(hub_name, next_hub, turn)):
            return False
        if not self.hub_has_room(next_hub, turn + cost):
            return False
        return True

    def plan_drone(self, max_turn: int) -> list[tuple[str, int]] | None:
        start = self.map_data.start_hub.name
        goal = self.map_data.end_hub.name
        open_set: list[tuple[int, int, str]] = []
        came_from: dict[tuple[str, int], tuple[str, int]] = {}
        seen = set()
        heapq.heappush(open_set, (((0 + self.pathfinding[start]), 0, start)))
        seen.add((start, 0))
        while open_set:
            total, turn, hub = heapq.heappop(open_set)
            if hub == goal:
                return self.rebuild_path((hub, turn), came_from)
            if turn >= max_turn:
                continue
            options = [hub, *get_neighbors(self.map_data, hub)]
            for neighbor in options:
                if not self.drone_can_move(hub, neighbor, turn):
                    continue
                if neighbor == hub:
                    arrive = turn + 1
                else:
                    arrive = turn + self.travel_cost(neighbor)
                new_state = (neighbor, arrive)
                if new_state in seen:
                    continue
                seen.add(new_state)
                came_from[new_state] = (hub, turn)
                heapq.heappush(open_set,
                               ((arrive + self.pathfinding[neighbor]), arrive,
                                neighbor))
        return None

    def reserve(self, path: list[tuple[str, int]]) -> None:
        for hub, turn in path:
            state = (hub, turn)
            self.hub_usage[state] = self.hub_usage.get(state, 0) + 1
        for i in range(len(path) - 1):
            hub1, turn1 = path[i]
            hub2, turn2 = path[i + 1]
            if hub1 == hub2:
                continue
            conn = self.conn_key(hub1, hub2)
            key = (conn, turn1)
            self.conn_usage[key] = self.conn_usage.get(key, 0) + 1

    def rebuild_path(self,
                     last_hub: tuple[str, int],
                     came_from: dict[tuple[str, int], tuple[str, int]]
                     ) -> list[tuple[str, int]]:
        path = [last_hub]
        while last_hub in came_from:
            last_hub = came_from[last_hub]
            path.append(last_hub)
        path.reverse()
        return path

    def reset(self) -> None:
        """Resets simulation state, drones, and hub counts."""
        self.drones = self.init_drones()
        self.hub_usage.clear()
        self.conn_usage.clear()
        self.plan_all(max_turn=50)
        for hub in self.hubs_by_name.values():
            hub.occupancy = 0

    @property
    def is_finished(self) -> bool:
        """Checks if all drones reached the end hub.

        Returns:
            bool: True if simulation is completed.
        """
        return all(
            drone.current_hub == self.map_data.end_hub.name
            for drone in self.drones
        )


if __name__ == "__main__":
    menu = Menu()
    try:
        map_data = menu.select_map_menu()
        simulation = SimulationEngine(map_data)
        map = MapVisualiser(map_data, simulation)
        print(simulation.pathfinding)
        map.run()

    except ParsingError as e:
        print(f"\033[31mParsing Error:\033[0m {e}", file=sys.stderr)
        sys.exit(1)

    except KeyboardInterrupt:
        print("\nKeyboard Interrupt error")
        sys.exit(0)
