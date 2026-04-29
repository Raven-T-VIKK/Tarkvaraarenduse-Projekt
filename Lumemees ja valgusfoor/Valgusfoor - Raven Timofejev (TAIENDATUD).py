import pygame
pygame.init()
pygame.display.set_caption("Valgusfoor - Raven Timofejev")
screen = pygame.display.set_mode((300, 300))
clock = pygame.time.Clock()

GRAY  = (100, 100, 100)
BLUE  = (0, 114, 206)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

BOX_X1, BOX_Y1 = 90, 15
BOX_X2, BOX_Y2 = 210, 195
BOX_CX = (BOX_X1 + BOX_X2) // 2  # 150

POST_W   = 12
POST_X   = BOX_CX - POST_W // 2
POST_TOP = BOX_Y2
POST_BOT = 255

TIP   = (BOX_CX, POST_BOT)
LEFT  = (BOX_CX - 50, 295)
RIGHT = (BOX_CX + 50, 295)

def draw_flag_triangle(surface, tip, left, right):
    total_h = left[1] - tip[1]
    if total_h == 0:
        return
    def get_x(y):
        t = (y - tip[1]) / total_h
        lx = tip[0] + t * (left[0] - tip[0])
        rx = tip[0] + t * (right[0] - tip[0])
        return lx, rx
    h3 = total_h // 3
    bands = [
        (tip[1],        tip[1] + h3,   BLUE),
        (tip[1] + h3,   tip[1]+2*h3,   BLACK),
        (tip[1]+2*h3,   left[1],       WHITE),
    ]
    for ya, yb, color in bands:
        poly = []
        for y in range(ya, yb + 1):
            lx, rx = get_x(y)
            poly.append((lx, y))
        for y in range(yb, ya - 1, -1):
            lx, rx = get_x(y)
            poly.append((rx, y))
        if len(poly) >= 3:
            pygame.draw.polygon(surface, color, poly)
    pygame.draw.polygon(surface, GRAY, [tip, left, right], 2)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    pygame.draw.rect(screen, GRAY, (POST_X, POST_TOP, POST_W, POST_BOT - POST_TOP))
    draw_flag_triangle(screen, TIP, LEFT, RIGHT)

    # Kast
    pygame.draw.rect(screen, GRAY, (BOX_X1, BOX_Y1, BOX_X2 - BOX_X1, BOX_Y2 - BOX_Y1), 4)

    # Tuled – väiksem raadius (22 asemel 20), paigutus nii et kõik mahuvad kasti sisse
    R = 20
    box_h = BOX_Y2 - BOX_Y1          # 180
    segment = box_h // 3              # 60
    pygame.draw.circle(screen, (255, 0, 0),   (BOX_CX, BOX_Y1 + segment // 2),         R)
    pygame.draw.circle(screen, (255, 255, 0), (BOX_CX, BOX_Y1 + segment + segment // 2), R)
    pygame.draw.circle(screen, (0, 255, 0),   (BOX_CX, BOX_Y1 + 2*segment + segment // 2), R)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()