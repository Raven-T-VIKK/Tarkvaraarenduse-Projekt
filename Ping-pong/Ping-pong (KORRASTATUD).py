import pygame
import sys
import random

# --- INITSIALISEERIMINE ---
pygame.init()

# --- HELI INITSIALISEERIMINE ---
heli_ok = False
try:
    pygame.mixer.init()
    heli_ok = True
except pygame.error:
    print("Hoiatus: helikaart ei ole kättesaadav, mäng jätkab ilma helita.")

WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PingPong")

clock = pygame.time.Clock()
FPS = 60

# --- VÄRVID ---
SKY_TOP    = (168, 216, 234)
SKY_BOTTOM = (201, 232, 245)

# --- PILDID ---
ball_img_raw = pygame.image.load("ball.png").convert_alpha()
ball_img     = pygame.transform.scale(ball_img_raw, (20, 20))

pad_img_raw = pygame.image.load("pad.png").convert_alpha()
pad_img     = pygame.transform.scale(pad_img_raw, (120, 20))

# --- FONT ---
font     = pygame.font.SysFont("Courier New", 22, bold=True)
font_big = pygame.font.SysFont("Courier New", 36, bold=True)

# --- TAUSTAMUUSIKA ---
if heli_ok:
    try:
        pygame.mixer.music.load("music/background.ogg")
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)   # -1 = mängib lõpmatult
    except pygame.error:
        print("Hoiatus: muusikafaili ei leitud või ei saa mängida.")

# --- TAUSTAGRADIENDI LOOMINE ---
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

# --- KONSTANDID ---
BALL_SIZE    = 20
PAD_W, PAD_H = 120, 20
PAD_Y        = int(HEIGHT / 1.5)
PAD_SPEED    = 6


# ---------------------------------------------------------------
class Game:
    def __init__(self):
        self.score      = 0
        self.state      = "start"   # "start" | "playing" | "gameover"
        self.reset_ball()
        self.pad_x      = float((WIDTH - PAD_W) // 2)

    # --- PALLI LÄHTESTAMINE ---
    def reset_ball(self):
        self.ball_x  = float(WIDTH // 2 - BALL_SIZE // 2)
        self.ball_y  = float(60)
        self.ball_sx = random.choice([-1, 1]) * 4.0
        self.ball_sy = 4.0

    # --- MÄNGU KÄIVITAMINE ---
    def start(self):
        self.score  = 0
        self.state  = "playing"
        self.pad_x  = float((WIDTH - PAD_W) // 2)
        self.reset_ball()
        if heli_ok:
            try:
                pygame.mixer.music.play(-1)
            except pygame.error:
                pass

    def update(self):
        if self.state != "playing":
            return

        # --- KLAVIATUURIGA ALUSE JUHTIMINE ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.pad_x -= PAD_SPEED
        if keys[pygame.K_RIGHT]:
            self.pad_x += PAD_SPEED

        self.pad_x = max(0.0, min(float(WIDTH - PAD_W), self.pad_x))

        # --- PALLI LIIKUMINE ---
        self.ball_x += self.ball_sx
        self.ball_y += self.ball_sy

        # --- SEINTELT PÕRKAMINE ---
        if self.ball_x <= 0:
            self.ball_x  = 0
            self.ball_sx = abs(self.ball_sx)
        if self.ball_x + BALL_SIZE >= WIDTH:
            self.ball_x  = WIDTH - BALL_SIZE
            self.ball_sx = -abs(self.ball_sx)
        if self.ball_y <= 0:
            self.ball_y  = 0
            self.ball_sy = abs(self.ball_sy)

        # --- KOKKUPÕRGE: PALL JA ALUS ---
        ball_rect = pygame.Rect(int(self.ball_x), int(self.ball_y), BALL_SIZE, BALL_SIZE)
        pad_rect  = pygame.Rect(int(self.pad_x),  PAD_Y,            PAD_W,     PAD_H)

        if self.ball_sy > 0 and ball_rect.colliderect(pad_rect):
            self.ball_sy  = -abs(self.ball_sy)
            self.ball_y   = PAD_Y - BALL_SIZE
            self.score   += 1
            offset        = (self.ball_x + BALL_SIZE / 2) - (self.pad_x + PAD_W / 2)
            self.ball_sx += offset * 0.07
            self.ball_sx  = max(-7.0, min(7.0, self.ball_sx))

        # --- PALL JÕUAB ALUMISE ÄÄRENI ---
        if self.ball_y + BALL_SIZE >= HEIGHT:
            self.state = "gameover"
            if heli_ok:
                pygame.mixer.music.stop()

    def draw(self, surface):
        # --- JOONISTAMINE (taust → alus → pall → UI) ---
        surface.blit(background, (0, 0))
        surface.blit(pad_img,  (int(self.pad_x), PAD_Y))
        surface.blit(ball_img, (int(self.ball_x), int(self.ball_y)))

        # --- SKOOR ---
        score_surf = font.render(f"SKOOR: {self.score}", True, (255, 255, 255))
        score_bg   = pygame.Surface((score_surf.get_width() + 20, 36), pygame.SRCALPHA)
        score_bg.fill((30, 30, 80, 150))
        surface.blit(score_bg,   (8, 8))
        surface.blit(score_surf, (18, 12))

        # --- OLEKUPÕHISED EKRAANID ---
        if self.state == "start":
            self._overlay(surface, "Vajuta TÜHIKUT alustamiseks", (50, 50, 120))

        elif self.state == "gameover":
            self._overlay(surface, f"MÄNG LÄBI!  Skoor: {self.score}", (160, 20, 20))
            sub = font.render("Vajuta TÜHIKUT uuesti mängimiseks", True, (80, 20, 20))
            sx  = (WIDTH - sub.get_width()) // 2
            sy  = HEIGHT // 2 + 30
            sbg = pygame.Surface((sub.get_width() + 24, sub.get_height() + 12), pygame.SRCALPHA)
            sbg.fill((255, 255, 255, 150))
            surface.blit(sbg, (sx - 12, sy - 6))
            surface.blit(sub, (sx, sy))

    # --- OVERLAY ABIFUNKTSIOON ---
    def _overlay(self, surface, text, color):
        msg = font_big.render(text, True, color)
        x   = (WIDTH  - msg.get_width())  // 2
        y   = HEIGHT // 2 - 30
        bg  = pygame.Surface((msg.get_width() + 24, msg.get_height() + 12), pygame.SRCALPHA)
        bg.fill((255, 255, 255, 170))
        surface.blit(bg,  (x - 12, y - 6))
        surface.blit(msg, (x, y))


# --- PEAMINE TSÜKKEL ---
def main():
    game = Game()

    while True:
        # --- SÜNDMUSTE TÖÖTLUS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    if game.state in ("start", "gameover"):
                        game.start()

        # --- UUENDAMINE JA JOONISTAMINE ---
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()