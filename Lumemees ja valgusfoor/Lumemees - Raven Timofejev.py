import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((300, 300))
pygame.display.set_caption("Lumemees – Raven Timofejev")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)

clock = pygame.time.Clock()

def draw_snowman(surface):
    # Must taust
    surface.fill(BLACK)

    # Alumine pall (suur)
    pygame.draw.circle(surface, WHITE, (150, 230), 55)

    # Keskmine pall
    pygame.draw.circle(surface, WHITE, (150, 150), 38)

    # Pea
    pygame.draw.circle(surface, WHITE, (150, 87), 27)

    # Silmad
    pygame.draw.circle(surface, BLACK, (141, 75), 4)
    pygame.draw.circle(surface, BLACK, (159, 75), 4)

    # Nina (punane kolmnurk)
    nose_points = [(150, 79), (163, 84), (150, 89)]
    pygame.draw.polygon(surface, RED, nose_points)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_snowman(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()