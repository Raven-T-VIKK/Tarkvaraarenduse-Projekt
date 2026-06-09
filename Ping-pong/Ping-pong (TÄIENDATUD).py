import pygame
import sys
import random
import os

# --- Initsialiseerimine ---
pygame.init()

# --- Heli initsialiseerimine ---
try:
    pygame.mixer.init()
    mixer_ok = True
except pygame.error:
    mixer_ok = False

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

# --- Helifaili laadimine ---
def laadi_heli(failinimi):
    """Otsib helifaili skripti kaustast ja töökataloogist."""
    if not mixer_ok:
        return None
    script_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    cwd = os.path.abspath(os.getcwd())
    kandidaadid = [
        os.path.join(script_dir, failinimi),
        os.path.join(cwd, failinimi),
    ]
    for tee in kandidaadid:
        if os.path.exists(tee):
            try:
                return pygame.mixer.Sound(tee)
            except pygame.error:
                continue
    return None

heli_hit = laadi_heli("hit.mp3")  # Heli kui pall põrkab vastu platvormi
heli_end = laadi_heli("end.mp3")  # Heli kui mäng lõpeb

# --- Taustamuusika laadimine ---
def laadi_taustamuusika(failinimi):
    """Laeb taustamuusika pygame.mixer.music mooduli abil."""
    if not mixer_ok:
        return False
    script_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    cwd = os.path.abspath(os.getcwd())
    kandidaadid = [
        os.path.join(script_dir, failinimi),
        os.path.join(cwd, failinimi),
    ]
    for tee in kandidaadid:
        if os.path.exists(tee):
            try:
                pygame.mixer.music.load(tee)
                return True
            except pygame.error:
                continue
    return False

tausta_muusika_ok = laadi_taustamuusika("background.wav")

# --- Taustamuusika laadimine ---
def laadi_taustamuusika(failinimi):
    """Laeb taustamuusika pygame.mixer.music abil."""
    if not mixer_ok:
        return False
    script_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    cwd = os.path.abspath(os.getcwd())
    kandidaadid = [
        os.path.join(script_dir, failinimi),
        os.path.join(cwd, failinimi),
    ]
    for tee in kandidaadid:
        if os.path.exists(tee):
            try:
                pygame.mixer.music.load(tee)
                return True
            except pygame.error:
                continue
    return False

muusika_ok = laadi_taustamuusika("background.wav")

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

# --- Konstandid ---
BALL_SIZE = 20
PAD_W, PAD_H = 120, 20
PAD_Y = int(HEIGHT / 1.5)
PAD_SPEED = 6  # Klaviatuuri liikumiskiirus

# --- Mängu olek ---
class Game:
    def __init__(self):
        self.score = 0
        self.running_game = False
        self.game_over = False
        self.reset_ball()
        self.pad_x = (WIDTH - PAD_W) // 2

    # --- Palli lähtestamine ---
    def reset_ball(self):
        self.ball_x = 0.0
        self.ball_y = 0.0
        self.ball_sx = -4.0
        self.ball_sy = 4.0

    # --- Mängu käivitamine ---
    def start(self):
        self.running_game = True
        self.game_over = False
        self.score = 0
        self.reset_ball()
        self.pad_x = (WIDTH - PAD_W) // 2
        # Käivita taustamuusika lõputus tsüklis (-1)
        if tausta_muusika_ok:
            pygame.mixer.music.play(-1)
        # Taustamuusika käivitamine (lõputu kordus)
        if muusika_ok:
            pygame.mixer.music.play(-1)

    def update(self, keys):
        if not self.running_game or self.game_over:
            return

        # --- Aluse juhtimine klaviatuuriga (← →) ---
        if keys[pygame.K_LEFT]:
            self.pad_x -= PAD_SPEED
        if keys[pygame.K_RIGHT]:
            self.pad_x += PAD_SPEED

        # --- Alus ei lähe mängu piiridest välja ---
        if self.pad_x < 0:
            self.pad_x = 0
        if self.pad_x + PAD_W > WIDTH:
            self.pad_x = WIDTH - PAD_W

        # --- Palli liikumine ---
        self.ball_x += self.ball_sx
        self.ball_y += self.ball_sy

        # --- Seintelt põrkamine ---
        if self.ball_x <= 0:
            self.ball_x = 0
            self.ball_sx = abs(self.ball_sx)
        if self.ball_x + BALL_SIZE >= WIDTH:
            self.ball_x = WIDTH - BALL_SIZE
            self.ball_sx = -abs(self.ball_sx)
        if self.ball_y <= 0:
            self.ball_y = 0
            self.ball_sy = abs(self.ball_sy)

        # --- Kokkupõrge: pall ja alus ---
        ball_rect = pygame.Rect(int(self.ball_x), int(self.ball_y), BALL_SIZE, BALL_SIZE)
        pad_rect = pygame.Rect(int(self.pad_x), PAD_Y, PAD_W, PAD_H)

        if self.ball_sy > 0 and ball_rect.colliderect(pad_rect):
            self.ball_sy = -abs(self.ball_sy)
            self.ball_y = PAD_Y - BALL_SIZE
            self.score += 1
            if heli_hit:
                heli_hit.play()

        # --- Pall puudutab alumist äärt → mäng lõpeb ---
        if self.ball_y + BALL_SIZE >= HEIGHT:
            self.game_over = True
            self.running_game = False
            # Peata taustamuusika ja mängi lõpuheli
            if tausta_muusika_ok:
                pygame.mixer.music.stop()
            if heli_end:
                heli_end.play()

    def draw(self, surface):
        # --- Joonistamine (taust → alus → pall → UI) ---
        surface.blit(background, (0, 0))
        surface.blit(pad_img, (int(self.pad_x), PAD_Y))
        surface.blit(ball_img, (int(self.ball_x), int(self.ball_y)))

        # --- Skoor ---
        score_surf = font.render(f"SKOOR: {self.score}", True, (255, 255, 255))
        score_bg = pygame.Surface((score_surf.get_width() + 20, 36), pygame.SRCALPHA)
        score_bg.fill((30, 30, 80, 150))
        surface.blit(score_bg, (8, 8))
        surface.blit(score_surf, (18, 12))

        # --- Algusekraan ---
        if not self.running_game and not self.game_over:
            msg = font.render("Vajuta TÜHIKUT alustamiseks", True, (50, 50, 120))
            x = (WIDTH - msg.get_width()) // 2
            y = HEIGHT // 2 - 20
            bg = pygame.Surface((msg.get_width() + 24, msg.get_height() + 12), pygame.SRCALPHA)
            bg.fill((255, 255, 255, 160))
            surface.blit(bg, (x - 12, y - 6))
            surface.blit(msg, (x, y))

        # --- Mäng läbi ekraan ---
        if self.game_over:
            # Pealkiri "MÄNG LÄBI"
            over_surf = font.render("MÄNG LÄBI!", True, (180, 30, 30))
            ox = (WIDTH - over_surf.get_width()) // 2
            oy = HEIGHT // 2 - 40
            over_bg = pygame.Surface((over_surf.get_width() + 24, over_surf.get_height() + 12), pygame.SRCALPHA)
            over_bg.fill((255, 255, 255, 180))
            surface.blit(over_bg, (ox - 12, oy - 6))
            surface.blit(over_surf, (ox, oy))

            # Lõplik skoor
            final_surf = font.render(f"Lõplik skoor: {self.score}", True, (50, 50, 120))
            fx = (WIDTH - final_surf.get_width()) // 2
            fy = oy + 40
            final_bg = pygame.Surface((final_surf.get_width() + 24, final_surf.get_height() + 12), pygame.SRCALPHA)
            final_bg.fill((255, 255, 255, 160))
            surface.blit(final_bg, (fx - 12, fy - 6))
            surface.blit(final_surf, (fx, fy))

            # Uuesti mängimise juhis
            restart_surf = font.render("Vajuta TÜHIKUT uuesti mängimiseks", True, (50, 50, 120))
            rx = (WIDTH - restart_surf.get_width()) // 2
            ry = fy + 40
            restart_bg = pygame.Surface((restart_surf.get_width() + 24, restart_surf.get_height() + 12), pygame.SRCALPHA)
            restart_bg.fill((255, 255, 255, 160))
            surface.blit(restart_bg, (rx - 12, ry - 6))
            surface.blit(restart_surf, (rx, ry))


# --- Peamine tsükkel ---
def main():
    game = Game()

    while True:
        keys = pygame.key.get_pressed()

        # --- Sündmuste töötlus ---
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

        # --- Uuendamine ja joonistamine ---
        game.update(keys)
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()