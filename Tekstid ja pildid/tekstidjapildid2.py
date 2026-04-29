import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Harjutamine")

# Pildid
bg = pygame.image.load("bg_shop.jpg")
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

seller_raw = pygame.image.load("seller.png").convert_alpha()
seller = pygame.transform.scale(seller_raw, (260, 310))

chat_raw = pygame.image.load("chat.png").convert_alpha()
chat = pygame.transform.scale(chat_raw, (260, 220))

# VIKK logo
vikk_raw = pygame.image.load("VIKK_logo.png").convert_alpha()
vikk_korgus = 350
vikk_laius = int(vikk_raw.get_width() * vikk_korgus / vikk_raw.get_height())
vikk = pygame.transform.scale(vikk_raw, (vikk_laius, vikk_korgus))

# Tort
tort_raw = pygame.image.load("tort.png").convert_alpha()
tort = pygame.transform.scale(tort_raw, (90, 90))
for x in range(tort.get_width()):
    for y in range(tort.get_height()):
        r, g, b, a = tort.get_at((x, y))
        if r < 30 and g < 30 and b < 30:
            tort.set_at((x, y), (0, 0, 0, 0))

# Mõõk
mook_raw = pygame.image.load("Mõõk.png").convert_alpha()
mook = pygame.transform.scale(mook_raw, (180, 150))
for x in range(mook.get_width()):
    for y in range(mook.get_height()):
        r, g, b, a = mook.get_at((x, y))
        if r < 30 and g < 30 and b < 30:
            mook.set_at((x, y), (0, 0, 0, 0))

# Fondid
font = pygame.font.SysFont("Arial", 24, bold=False)
name_text = font.render("Tere, olen Raven", True, (255, 255, 255))

arc_font = pygame.font.SysFont("Arial", 16, bold=True)

def draw_arc_text(surface, text, cx, cy, radius, start_angle_deg, color):
    for i, char in enumerate(text):
        angle_deg = start_angle_deg + i * -3.5
        angle_rad = math.radians(angle_deg)
        x = int(cx + radius * math.cos(angle_rad))
        y = int(cy - radius * math.sin(angle_rad))
        char_surf = arc_font.render(char, True, color)
        rotated = pygame.transform.rotate(char_surf, angle_deg - 90)
        rect = rotated.get_rect(center=(x, y))
        surface.blit(rotated, rect)

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Taust
    screen.blit(bg, (0, 0))

    # Mõõk seinale
    screen.blit(mook, (475, 112))
    mook = pygame.transform.scale(mook_raw, (180, 150))
    mook = pygame.transform.rotate(mook, 130)

    # Tort laua peale
    screen.blit(tort, (340, 200))

    # Müüja
    seller_x = 107
    seller_y = HEIGHT - 324
    screen.blit(seller, (seller_x, seller_y))

    # Jutumull
    chat_x = 245
    chat_y = 60
    screen.blit(chat, (chat_x, chat_y))

    # Tekst jutumullis
    text_x = chat_x + (chat.get_width() - name_text.get_width()) // 2
    text_y = chat_y + (chat.get_height() - name_text.get_height()) // 2 - 15
    screen.blit(name_text, (text_x, text_y))

    # VIKK logo
    screen.blit(vikk, (5, 5))

    pygame.display.flip()
    clock.tick(60)