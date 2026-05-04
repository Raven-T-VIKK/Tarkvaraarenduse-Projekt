import pygame
import sys
import random

# --- Initsialiseerimine ---
pygame.init()

WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PingPong")

clock = pygame.time.Clock()
FPS = 60

# --- Värvid ---
SKY_TOP = (168, 216, 234)
SKY_BOTTOM = (201, 232, 245)
TEXT_COLOR = (30, 30, 80)
SCORE_BG = (30, 30, 80, 140)

# --- Pildid ---
ball_img_raw = pygame.image.load("ball.png").convert_alpha()
ball_img = pygame.transform.scale(ball_img_raw, (20, 20))

pad_img_raw = pygame.image.load("pad.png").convert_alpha()
pad_img = pygame.transform.scale(pad_img_raw, (120, 20))

# --- Fondi laadimine ---
font = pygame.font.SysFont("Courier New", 22, bold=True)

# --- Taustagradiendi loomine ---
def make_background():
    surf = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))
    return surf

background = make_background()

# --- Mängija andmed ---
BALL_SIZE = 20
PAD_W, PAD_H = 120, 20
PAD_Y = int(HEIGHT / 1.5)

# --- Mängu olek ---
class Game:
    def __init__(self):
        self.score = 0
        self.running_game = False
        self.reset_ball()
        self.pad_x = (WIDTH - PAD_W) // 2
        self.pad_speed = 3

    def reset_ball(self):
        self.ball_x = float(WIDTH // 2 - BALL_SIZE // 2)
        self.ball_y = float(60)
        self.ball_sx = random.choice([-1, 1]) * 4.0
        self.ball_sy = 4.0

    def start(self):
        self.running_game = True
        self.score = 0
        self.reset_ball()
        self.pad_x = (WIDTH - PAD_W) // 2
        self.pad_speed = 3

    def update(self):
        if not self.running_game:
            return

        # Pall liigub
        self.ball_x += self.ball_sx
        self.ball_y += self.ball_sy

        # Pall põrkab vasakult/paremalt seinalt
        if self.ball_x <= 0:
            self.ball_x = 0
            self.ball_sx = abs(self.ball_sx)
        if self.ball_x + BALL_SIZE >= WIDTH:
            self.ball_x = WIDTH - BALL_SIZE
            self.ball_sx = -abs(self.ball_sx)

        # Pall põrkab ülemiselt seinalt
        if self.ball_y <= 0:
            self.ball_y = 0
            self.ball_sy = abs(self.ball_sy)

        # Alus liigub
        self.pad_x += self.pad_speed
        if self.pad_x <= 0:
            self.pad_x = 0
            self.pad_speed = abs(self.pad_speed)
        if self.pad_x + PAD_W >= WIDTH:
            self.pad_x = WIDTH - PAD_W
            self.pad_speed = -abs(self.pad_speed)

        # Kokkupõrge: pall ja alus
        ball_rect = pygame.Rect(int(self.ball_x), int(self.ball_y), BALL_SIZE, BALL_SIZE)
        pad_rect = pygame.Rect(int(self.pad_x), PAD_Y, PAD_W, PAD_H)

        if self.ball_sy > 0 and ball_rect.colliderect(pad_rect):
            self.ball_sy = -abs(self.ball_sy)
            self.ball_y = PAD_Y - BALL_SIZE
            self.score += 1

            # Nurga varieerimine sõltuvalt tabamiskohast
            hit_offset = (self.ball_x + BALL_SIZE / 2) - (self.pad_x + PAD_W / 2)
            self.ball_sx += hit_offset * 0.07
            self.ball_sx = max(-7.0, min(7.0, self.ball_sx))

        # Pall puudutab alumist äärt
        if self.ball_y + BALL_SIZE >= HEIGHT:
            self.score -= 1
            self.reset_ball()

    def draw(self, surface):
        # Taust
        surface.blit(background, (0, 0))

        # Alus
        surface.blit(pad_img, (int(self.pad_x), PAD_Y))

        # Pall
        surface.blit(ball_img, (int(self.ball_x), int(self.ball_y)))

        # Skoor
        score_surf = font.render(f"SKOOR: {self.score}", True, (255, 255, 255))
        score_bg = pygame.Surface((score_surf.get_width() + 20, 36), pygame.SRCALPHA)
        score_bg.fill((30, 30, 80, 150))
        surface.blit(score_bg, (8, 8))
        surface.blit(score_surf, (18, 12))

        # Algusekraan
        if not self.running_game:
            msg = font.render("Vajuta TÜHIKUT alustamiseks", True, (50, 50, 120))
            x = (WIDTH - msg.get_width()) // 2
            y = HEIGHT // 2 - 20
            bg = pygame.Surface((msg.get_width() + 24, msg.get_height() + 12), pygame.SRCALPHA)
            bg.fill((255, 255, 255, 160))
            surface.blit(bg, (x - 12, y - 6))
            surface.blit(msg, (x, y))


# --- Peamine tsükkel ---
def main():
    game = Game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game.running_game:
                        game.start()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not game.running_game:
                    game.start()

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()