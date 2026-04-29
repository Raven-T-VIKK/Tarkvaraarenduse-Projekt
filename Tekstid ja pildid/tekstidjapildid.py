import pygame
import sys

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

# Font
font = pygame.font.SysFont("Arial", 24, bold=False)
name_text = font.render("Tere, olen Raven", True, (255, 255, 255))

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Taust
    screen.blit(bg, (0, 0))

    # Müüa asukoht
    seller_x = 107
    seller_y = HEIGHT - 324
    screen.blit(seller, (seller_x, seller_y))

    # Tekstimulli asukoht
    chat_x = 245
    chat_y = 60
    screen.blit(chat, (chat_x, chat_y))

    # Tekst mis on tekstimulli sees
    text_x = chat_x + (chat.get_width() - name_text.get_width()) // 2
    text_y = chat_y + (chat.get_height() - name_text.get_height()) // 2 - 15
    screen.blit(name_text, (text_x, text_y))
    pygame.display.flip()

    clock.tick(60)