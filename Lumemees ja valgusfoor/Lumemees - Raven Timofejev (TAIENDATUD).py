import pygame
import sys
import math

pygame.init()

screen = pygame.display.set_mode((300, 300))
pygame.display.set_caption("Lumemees – Raven Timofejev")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
LIGHT_BLUE = (135, 206, 235)
BROWN = (101, 67, 33)
YELLOW = (255, 220, 0)
DARK_GRAY = (50, 50, 50)
GRAY = (180, 180, 180)

clock = pygame.time.Clock()


def draw_snowman(surface):
    # 4. Helesinine taust
    surface.fill(LIGHT_BLUE)

    # 7. Kolm pilve
    def draw_cloud(cx, cy):
        pygame.draw.circle(surface, WHITE, (cx, cy), 18)
        pygame.draw.circle(surface, WHITE, (cx + 20, cy - 5), 22)
        pygame.draw.circle(surface, WHITE, (cx + 42, cy), 18)
        pygame.draw.circle(surface, WHITE, (cx + 10, cy + 8), 16)
        pygame.draw.circle(surface, WHITE, (cx + 30, cy + 8), 16)

    draw_cloud(10, 30)
    draw_cloud(100, 15)
    draw_cloud(200, 35)

    # 6. Päike koos kiirtega (paremas ülanurgas)
    sun_x, sun_y = 260, 50
    sun_r = 22
    # Kiired
    for i in range(12):
        angle = math.radians(i * 30)
        x1 = int(sun_x + math.cos(angle) * (sun_r + 4))
        y1 = int(sun_y + math.sin(angle) * (sun_r + 4))
        x2 = int(sun_x + math.cos(angle) * (sun_r + 14))
        y2 = int(sun_y + math.sin(angle) * (sun_r + 14))
        pygame.draw.line(surface, YELLOW, (x1, y1), (x2, y2), 2)
    pygame.draw.circle(surface, YELLOW, (sun_x, sun_y), sun_r)

    # Alumine pall (suur)
    pygame.draw.circle(surface, WHITE, (150, 230), 55)

    # 2. Nööbid (3 tk) – alumisel pallil
    pygame.draw.circle(surface, BLACK, (150, 205), 5)
    pygame.draw.circle(surface, BLACK, (150, 220), 5)
    pygame.draw.circle(surface, BLACK, (150, 235), 5)

    # Keskmine pall
    pygame.draw.circle(surface, WHITE, (150, 150), 38)

    # Pea
    pygame.draw.circle(surface, WHITE, (150, 87), 27)

    # 3. Kübar/müts
    hat_brim_rect = pygame.Rect(120, 57, 62, 8)
    pygame.draw.rect(surface, DARK_GRAY, hat_brim_rect)
    hat_top_rect = pygame.Rect(130, 28, 42, 30)
    pygame.draw.rect(surface, DARK_GRAY, hat_top_rect)

    # Silmad
    pygame.draw.circle(surface, BLACK, (141, 75), 4)
    pygame.draw.circle(surface, BLACK, (159, 75), 4)

    # Nina (punane kolmnurk)
    nose_points = [(150, 79), (163, 84), (150, 89)]
    pygame.draw.polygon(surface, RED, nose_points)

    # 1. Käed (oksad)
    # Vasak käsi
    pygame.draw.line(surface, BROWN, (112, 150), (70, 120), 4)
    pygame.draw.line(surface, BROWN, (70, 120), (50, 108), 3)
    pygame.draw.line(surface, BROWN, (70, 120), (55, 130), 3)

    # Parem käsi
    pygame.draw.line(surface, BROWN, (188, 150), (230, 120), 4)
    pygame.draw.line(surface, BROWN, (230, 120), (250, 108), 3)
    pygame.draw.line(surface, BROWN, (230, 120), (245, 130), 3)

    # 5. Hari (luud) vasakus käes
    broom_handle_start = (70, 120)
    broom_handle_end = (45, 170)
    pygame.draw.line(surface, BROWN, broom_handle_start, broom_handle_end, 3)

    # Harja osa
    broom_tip = broom_handle_end
    pygame.draw.line(surface, BROWN, broom_tip, (30, 155), 2)
    pygame.draw.line(surface, BROWN, broom_tip, (35, 160), 2)
    pygame.draw.line(surface, BROWN, broom_tip, (32, 168), 2)
    pygame.draw.line(surface, BROWN, broom_tip, (40, 172), 2)
    pygame.draw.line(surface, BROWN, broom_tip, (38, 178), 2)
    pygame.draw.line(surface, BROWN, broom_tip, (46, 180), 2)
    pygame.draw.line(surface, BROWN, broom_tip, (44, 186), 2)


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