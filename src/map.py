import pygame
from parser import MapModel
from drone import Drone


class MapVisualiser():
    def __init__(self,
                 map_data: MapModel,
                 width: int = 1280,
                 height: int = 720
                 ) -> None:
        self.map_data = map_data
        self.width = width
        self.height = height
        self.drone_img: pygame.Surface

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        clock = pygame.time.Clock()
        running = True
        drone_img = pygame.image.load("./ressources/drone.png").convert_alpha()
        self.drone_img = pygame.transform.scale(drone_img, (50, 50))
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill("dark grey")
            self.draw_drones(screen)
            self.render(screen)
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

    def draw_drones(self, screen: pygame.Surface, drone: Drone) -> None:
        for x in range(self.map_data.drones):
            screen.blit(self.drone_img, (map_data))
