from map import MapModel
import sys


def dijkstra_distance(map_data: MapModel, goal_hub: str) -> dict[str, int]:
    """ Calcul the minimal distance for each hub from the goal"""

    all_hubs = [map_data.start_hub, map_data.end_hub] + map_data.hubs
    distances: dict[str, int] = {hub.name: sys.maxsize for hub in all_hubs}
    distances[map_data.end_hub.name] = 0
    print(distances)
    return distances
