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
        font = pygame.font.SysFont('Calibri', 12, bold=True)
        pygame.display.set_caption('FLY-IN')
        icon = pygame.image.load("./ressources/icon.png")
        pygame.display.set_icon(icon)
        screen = pygame.display.set_mode((self.width, self.height))
        clock = pygame.time.Clock()
        bg_surface = pygame.Surface((self.width, self.height))
        self.draw_background(bg_surface)
        running = True
        turn = 0
        drone_img = pygame.image.load("./ressources/drone.png").convert_alpha()
        self.drone_img = pygame.transform.scale(drone_img, (40, 40))
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.simulation.move_drones(self.simulation.drones)
                        turn += 1
            screen.blit(bg_surface, (0, 0))
            mouse_pos = pygame.mouse.get_pos()
            hovered_hub = self.get_hovered_hub(mouse_pos)
            self.draw_connections(screen)
            self.draw_hubs(screen, hovered_hub, font)
            self.draw_drones(screen, self.simulation.drones)
            self.draw_bottom_info_bar(screen, font, hovered_hub)
            self.draw_header(screen, font, turn)
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

    def draw_drones(self, screen: pygame.Surface, drones: list[Drone]) -> None:
        for drone in (drones):
            coords_drone = self.converter.to_pixels(drone.pos_x, drone.pos_y)
            glow_radius = 22
            glow_surface = pygame.Surface(
                (glow_radius * 2, glow_radius * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                glow_surface,
                (0, 210, 255, 60),
                (glow_radius, glow_radius),
                glow_radius,
            )
            screen.blit(
                glow_surface,
                (coords_drone[0] - glow_radius, coords_drone[1] - glow_radius),
            )
            drone_rect = self.drone_img.get_rect(center=coords_drone)
            screen.blit(self.drone_img, drone_rect)

    def draw_hubs(self,
                  screen: pygame.Surface,
                  hovered_hub: HubModel | None,
                  font: pygame.font.Font) -> None:
        map_data = self.map_data
        all_hub = [map_data.start_hub, map_data.end_hub] + map_data.hubs
        font_sub = pygame.font.SysFont("Consolas", 10, bold=True)
        for hub in all_hub:
            px, py = self.converter.to_pixels(hub.x, hub.y)
            hub_rect = pygame.Rect(
                px - 40 // 2, py - 40 // 2, 40, 40
            )
            color = hub.metadata.get("color", "blue")
            text = font_sub.render(hub.name, True, "white")
            text_rect = text.get_rect(centerx=px, top=py + 35)

            if hub == hovered_hub:
                pygame.draw.rect(
                    screen, color,
                    hub_rect, border_radius=10, width=2
                )
            else:

                glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
                glow_color = pygame.Color(color)
                pygame.draw.rect(
                    glow_surf,
                    (glow_color.r, glow_color.g, glow_color.b, 80),
                    (0, 0, 60, 60),
                    border_radius=15,
                )
                pygame.draw.rect(
                    screen, (10, 22, 40), hub_rect, border_radius=10
                )
                pygame.draw.rect(
                                    screen, color,
                                    hub_rect, border_radius=10
                                )
            screen.blit(glow_surf, (px - 30, py - 30))
            screen.blit(text, text_rect)

    def draw_connections(self, screen: pygame.Surface) -> None:
        connections = self.map_data.connections
        for connection in connections:
            zone1 = self.simulation.get_hub(connection.zone1)
            zone2 = self.simulation.get_hub(connection.zone2)
            if zone1 and zone2:
                coord1 = self.converter.to_pixels(zone1.x, zone1.y)
                coord2 = self.converter.to_pixels(zone2.x, zone2.y)
                pygame.draw.line(screen, "gold", coord1, coord2)

    def draw_background(self,
                        screen: pygame.Surface,
                        cell_size: int = 20,
                        sub_divider: int = 5) -> None:
        screen.fill((10, 22, 40))
        color_light = (18, 38, 65)  # Discret
        color_main = (28, 58, 95)  # Visible
        for x in range(0, self.width, cell_size):
            color = color_main if x % (cell_size *
                                       sub_divider) == 0 else color_light
            pygame.draw.line(screen, color, (x, 0), (x, self.height))

        for y in range(0, self.height, cell_size):
            color = color_main if y % (cell_size *
                                       sub_divider) == 0 else color_light
            pygame.draw.line(screen, color, (0, y), (self.width, y))

    def draw_bottom_info_bar(self,
                             screen: pygame.Surface,
                             font: pygame.font.Font,
                             hovered_hub: HubModel | None) -> None:
        """Affiche une barre d'informations en bas de l'écran si un
        hub est survolé."""
        if hovered_hub is None:
            return
        screen_width, screen_height = screen.get_size()
        zone = hovered_hub.metadata.get("zone", "normal")
        max_d = hovered_hub.metadata.get("max_drones", "//")
        occupancy = hovered_hub.occupancy
        text = (f"Hub: {hovered_hub.name} | Zone: {zone} | Max Drones:"
                f"{max_d} | Occupancy; {occupancy})")
        text_surface = font.render(text, True, "antiquewhite2")
        text_rect = text_surface.get_rect()
        padding_x = 20
        padding_y = 10
        margin_bottom = 20
        rect_width = text_rect.width + (padding_x * 2)
        rect_height = text_rect.height + (padding_y * 2)
        rect_x = (screen_width - rect_width) // 2
        rect_y = screen_height - rect_height - margin_bottom
        box_rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
        pygame.draw.rect(
            screen, hovered_hub.metadata.get('color', 'blue'),
            box_rect, border_radius=8
        )
        pygame.draw.rect(
            screen, "antiquewhite2",
            box_rect, width=2, border_radius=8
        )
        text_rect.center = box_rect.center
        screen.blit(text_surface, text_rect)

    def get_hovered_hub(self, mouse_pos) -> HubModel | None:
        """Retourne le hub actuellement survolé par la souris (basé sur des
        rectangles)."""
        for hub in self.map_data.hubs:
            px, py = self.converter.to_pixels(hub.x, hub.y)
            hub_rect = pygame.Rect(
                px - 40 // 2, py - 40 // 2, 40, 40
            )
            if hub_rect.collidepoint(mouse_pos):
                return hub
        return None

    def draw_header(self,
                    screen: pygame.Surface,
                    font: pygame.font.Font,
                    turn: int) -> None:
        """Display the turn counter of the simulaiton"""
        header_surf = pygame.Surface((260, 100), pygame.SRCALPHA)
        header_surf.fill((10, 22, 40, 210))
        pygame.draw.rect(
            header_surf, (0, 210, 255), (0, 0, 260, 100), width=1,
            border_radius=6
        )
        pygame.draw.rect(
            header_surf, (0, 210, 255), (0, 0, 8, 100),
            border_top_left_radius=6, border_bottom_left_radius=6
        )
        title_surface = font.render("FLY-IN SIMULATOR", True, "white")
        map_surface = font.render(f"{self.map_data.name}", True, "white")
        drone_surface = font.render(
            f"Active drones:  {len(self.simulation.drones)}", True, "white"
        )
        turn_surface = font.render(
            f"Turn :  {turn}", True, "white"
        )
        header_surf.blit(title_surface, (16, 12))
        header_surf.blit(map_surface, (16, 38))
        header_surf.blit(drone_surface, (16, 64))
        header_surf.blit(turn_surface, (16, 85))
        screen.blit(header_surf, (20, 20))
