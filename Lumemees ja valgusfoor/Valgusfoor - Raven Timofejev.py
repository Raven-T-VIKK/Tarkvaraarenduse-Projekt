import pygame
pygame.init()
pygame.display.set_caption("foor - Raven Timofejev")
screen = pygame.display.set_mode((300, 300))
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 0, 0))

    pygame.draw.line(screen, (100, 100, 100), (70, 25), (230, 25), 5)
    pygame.draw.line(screen, (100, 100, 100), (230, 25), (230, 275), 5)
    pygame.draw.line(screen, (100, 100, 100), (230, 275), (70, 275), 5)
    pygame.draw.line(screen, (100, 100, 100), (70, 275), (70, 25), 5)
    pygame.draw.circle(screen, (255, 0, 0), (150, 70), 35)
    pygame.draw.circle(screen, (255, 255, 0), (150, 150), 35)
    pygame.draw.circle(screen, (0, 255, 0), (150, 230), 35)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()