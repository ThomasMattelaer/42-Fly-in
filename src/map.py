import pygame
from parser import MapModel
from drone import Drone
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from fly_in import SimulationEngine


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

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        clock = pygame.time.Clock()
        running = True
        print(f"DRONES:{self.simulation.drones}")
        drone_img = pygame.image.load("./ressources/drone.png").convert_alpha()
        self.drone_img = pygame.transform.scale(drone_img, (50, 50))
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill("dark grey")
            self.draw_drones(screen, self.simulation.drones)
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

    def draw_drones(self, screen: pygame.Surface, drones: list[Drone]) -> None:
        for drone in (drones):
            screen.blit(self.drone_img, (drone.pos_x, drone.pos_y))
