import pygame
from parser import MapModel


class MapVisualiser():
    def __init__(self,
                 map_data: MapModel,
                 width: int = 800,
                 height: int = 600
                 ) -> None:
        self.map_data = map_data
        self.width = width
        self.height = height

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((1280, 720))
        clock = pygame.time.Clock()
        running = True
        print(self.map_data.drones)
        color = pygame.Color('lightskyblue3')

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill("purple")
            input_rect = pygame.Rect(200, 200, 140, 30)
            pygame.draw.rect(screen, color, input_rect)
            # RENDER YOUR GAME HERE
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()
