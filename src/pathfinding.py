import heapq
import sys
from parser import HubModel, MapModel


def dijkstra_distance(map_data: MapModel, goal_hub: str) -> dict[str, int]:
    """Calculates minimal distance from each hub to the goal using Dijkstra.

    Args:
        map_data (MapModel): Complete map structure.
        goal_hub (str): Name of the target destination hub.

    Returns:
        dict[str, int]: Mapping of hub names to their shortest path distance.
    """
    all_hubs = [map_data.start_hub, map_data.end_hub] + map_data.hubs
    distances: dict[str, int] = {hub.name: sys.maxsize for hub in all_hubs}
    distances[map_data.end_hub.name] = 0
    heap: list[tuple[int, str]] = []
    heapq.heappush(heap, (0, map_data.end_hub.name))
    while heap:
        dist, current_hub = heapq.heappop(heap)
        if dist > distances[current_hub]:
            continue
        for neighbor in get_neighbors(map_data, current_hub):
            if not can_reach_start_from(
                map_data,
                start_hub=neighbor,
                forbidden_hub=current_hub,
                goal_name=map_data.start_hub.name,
            ):
                continue
            weight = get_hub_weight(all_hubs, neighbor)
            new_dist = dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))
    return distances


def get_hub_weight(all_hubs: list[HubModel], hub_name: str) -> int:
    """Retrieves movement cost weight for entering a specific hub zone.

    Args:
        all_hubs (list[HubModel]): List of all hubs in the map.
        hub_name (str): Target hub name.

    Returns:
        int: Cost weight based on hub zone type.
    """
    hub = next((hub for hub in all_hubs if hub.name == hub_name), None)
    if not hub:
        return 4
    zone_type = hub.metadata.get("zone", "normal")
    if zone_type == "blocked":
        return sys.maxsize
    if zone_type == "restricted":
        return 8
    if zone_type == "priority":
        return 3
    else:
        return 4


def get_neighbors(map_data: MapModel, current_hub: str) -> list[str]:
    """Retrieves all directly connected neighbor hubs for a given hub.

    Args:
        map_data (MapModel): Complete map structure.
        current_hub (str): Hub name to find neighbors for.

    Returns:
        list[str]: Names of neighboring hubs.
    """
    neighbors = []
    for conn in map_data.connections:
        if conn.zone1 == current_hub:
            neighbors.append(conn.zone2)
        elif conn.zone2 == current_hub:
            neighbors.append(conn.zone1)
    return neighbors


def can_reach_start_from(
    map_data: MapModel, start_hub: str, forbidden_hub: str, goal_name: str
) -> bool:
    """Checks if a destination goal hub is reachable without visiting a
        forbidden hub.

    Args:
        map_data (MapModel): Complete map structure.
        start_hub (str): Starting hub for reachability check.
        forbidden_hub (str): Hub that must be avoided.
        goal_name (str): Target hub name to reach.

    Returns:
        bool: True if goal is reachable, False otherwise.
    """
    stack = [start_hub]
    visited: set[str] = {forbidden_hub, start_hub}
    if start_hub == goal_name:
        return True
    while stack:
        current_hub = stack.pop()
        if current_hub == goal_name:
            return True
        for neighbor in get_neighbors(map_data, current_hub):
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)
    return False
