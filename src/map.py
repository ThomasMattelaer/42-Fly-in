import pygame
from parser import MapModel, HubModel
from drone import Drone
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from fly_in import SimulationEngine


class CoordinateConverter():
    def __init__(self,
                 map_data: MapModel,
                 screen_width: int = 1280,
                 screen_height: int = 720,
                 margin: int = 100
                 ) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.margin = margin

        all_hubs: list[HubModel] = [map_data.start_hub, map_data.end_hub
                                    ] + map_data.hubs
        x_coords = [hub.x for hub in all_hubs]
        y_coords = [hub.y for hub in all_hubs]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        map_width = max(max_x - min_x, 1)
        map_height = max(max_y - min_y, 1)
        usable_width = screen_width - (2 * margin)
        usable_height = screen_height - (2 * margin)
        scale_x = usable_width / map_width
        scale_y = usable_height / map_height
        self.scale = min(scale_x, scale_y)
        self.offset_x = margin + (usable_width - (map_width * self.scale)
                                  ) / 2 - (min_x * self.scale)
        self.offset_y = margin + (usable_height - (map_height * self.scale)
                                  ) / 2 - (min_y * self.scale)

    def to_pixels(self, x: int, y: int) -> tuple[int, int]:
        pixel_x = int(x * self.scale + self.offset_x)
        pixel_y = int(y * self.scale + self.offset_y)
        return (pixel_x, pixel_y)


class MapVisualiser():
    def __init__(self,
                 map_data: MapModel,
                 simulation: "SimulationEngine",
                 width: int = 1280,
                 height: int = 720
                 ) -> None:
        self.map_data = map_data
        self.simulation = simulation
        self.width = width
        self.height = height
        self.drone_img: pygame.Surface
        self.converter = CoordinateConverter(map_data, width, height)

    def run(self):
        pygame.init()
        font = pygame.font.SysFont('Arial', 12)
        screen = pygame.display.set_mode((self.width, self.height))
        clock = pygame.time.Clock()
        running = True
        drone_img = pygame.image.load("./ressources/drone.png").convert_alpha()
        self.drone_img = pygame.transform.scale(drone_img, (50, 50))
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill("cadetblue4")
            self.draw_connections(screen)
            self.draw_hubs(screen, font)
            self.draw_drones(screen, self.simulation.drones)
            for drone in self.simulation.drones:
                print(drone.pos_x, drone.pos_y)
            pygame.display.flip()
            self.move_drones(self.simulation.drones)
            clock.tick(60)
        pygame.quit()

    def move_drones(self, drones: list[Drone]) -> None:
        for drone in drones:
            if drone.target_hub:
                drone.current_hub = drone.target_hub
            next_hub_name = self.get_next_hub_name(drone.current_hub)
            if next_hub_name:
                drone.target_hub = next_hub_name
            target_hub = self.get_hub(next_hub_name)
            if target_hub:
                drone.pos_x = target_hub.x
                drone.pos_y = target_hub.y

    def draw_drones(self, screen: pygame.Surface, drones: list[Drone]) -> None:
        for drone in (drones):
            coords_drone = self.converter.to_pixels(drone.pos_x, drone.pos_y)
            screen.blit(self.drone_img, coords_drone)

    def draw_hubs(self,
                  screen: pygame.Surface,
                  font: pygame.font.Font) -> None:
        map_data = self.map_data
        all_hub = [map_data.start_hub, map_data.end_hub] + map_data.hubs
        for hub in all_hub:
            coords_hub = self.converter.to_pixels(hub.x, hub.y)
            text = font.render(hub.name, True, "white")
            text_rect = text.get_rect(centerx=coords_hub[0], top=coords_hub[1]
                                      + 35)
            pygame.draw.circle(screen, hub.metadata.get("color", "blue"),
                               coords_hub, 30)
            screen.blit(text, text_rect)

    def draw_connections(self, screen: pygame.Surface) -> None:
        connections = self.map_data.connections
        for connection in connections:
            zone1 = self.get_hub(connection.zone1)
            zone2 = self.get_hub(connection.zone2)
            if zone1 and zone2:
                coord1 = self.converter.to_pixels(zone1.x, zone1.y)
                coord2 = self.converter.to_pixels(zone2.x, zone2.y)
                pygame.draw.line(screen, "grey", coord1, coord2)

    def get_hub(self, hub_name: str) -> HubModel:
        map_data = self.map_data
        all_hubs = [map_data.start_hub, map_data.end_hub] + map_data.hubs
        hubs_by_name = {hub.name: hub for hub in all_hubs}
        if hub_name not in hubs_by_name:
            raise ValueError(f"Hub: {hub_name} hasn't been found")
        return hubs_by_name[hub_name]

    def get_next_hub_name(self, current_hub_name: str) -> str:
        """Trouve la destination reliée à current_hub_name
        dans les connexions."""
        for conn in self.map_data.connections:
            if conn.zone1 == current_hub_name:
                return conn.zone2
            if conn.zone2 == current_hub_name:
                return conn.zone1
        return ""
