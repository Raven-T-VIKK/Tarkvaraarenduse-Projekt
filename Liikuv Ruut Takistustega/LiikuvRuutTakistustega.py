import pygame
import sys
import random

# --- Initsialiseerimine ---
pygame.init()

WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Takistuste mäng")

clock = pygame.time.Clock()
FPS = 60

# --- Värvid ---
BG_COLOR       = (30, 30, 40)
PLAYER_COLOR   = (80, 180, 255)
PLAYER_HIT     = (220, 40, 40)
OBSTACLE_COLOR = (20, 20, 20)
OBSTACLE_BORDER= (80, 80, 80)
TEXT_COLOR     = (255, 255, 255)
TEXT_DIM       = (160, 160, 160)

# --- Font ---
font     = pygame.font.SysFont("Courier New", 22, bold=True)
font_big = pygame.font.SysFont("Courier New", 40, bold=True)
font_sub = pygame.font.SysFont("Courier New", 18)

# --- Konstandid ---
PLAYER_SIZE    = 20
PLAYER_SPEED   = 4
OBSTACLE_COUNT = 10
OBS_MIN_W, OBS_MAX_W = 40, 120
OBS_MIN_H, OBS_MAX_H = 20, 60


def generate_obstacles(player_rect):
    """Loob OBSTACLE_COUNT takistust suvalistes kohtades, mis ei kattu mängijaga."""
    obstacles = []
    attempts  = 0
    while len(obstacles) < OBSTACLE_COUNT and attempts < 1000:
        attempts += 1
        w = random.randint(OBS_MIN_W, OBS_MAX_W)
        h = random.randint(OBS_MIN_H, OBS_MAX_H)
        x = random.randint(0, WIDTH  - w)
        y = random.randint(0, HEIGHT - h)
        rect = pygame.Rect(x, y, w, h)
        # Ära aseta mängija alguspositsioonile liiga lähedale
        if not rect.colliderect(player_rect.inflate(60, 60)):
            obstacles.append(rect)
    return obstacles


class Game:
    def __init__(self):
        self.state = "start"   # "start" | "playing" | "gameover"
        self.reset()

    def reset(self):
        # Mängija keskel ekraani
        self.player_x   = float(WIDTH  // 2 - PLAYER_SIZE // 2)
        self.player_y   = float(HEIGHT // 2 - PLAYER_SIZE // 2)
        self.player_rect = pygame.Rect(int(self.player_x), int(self.player_y),
                                       PLAYER_SIZE, PLAYER_SIZE)
        self.hit        = False
        # Takistused salvestatakse listi
        self.obstacles  = generate_obstacles(self.player_rect)

    def start(self):
        self.reset()
        self.state = "playing"

    def update(self):
        if self.state != "playing":
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.player_x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.player_x += PLAYER_SPEED
        if keys[pygame.K_UP]    or keys[pygame.K_w]: self.player_y -= PLAYER_SPEED
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.player_y += PLAYER_SPEED

        # Mängija ei lähe ekraanist välja
        self.player_x = max(0.0, min(float(WIDTH  - PLAYER_SIZE), self.player_x))
        self.player_y = max(0.0, min(float(HEIGHT - PLAYER_SIZE), self.player_y))

        self.player_rect = pygame.Rect(int(self.player_x), int(self.player_y),
                                       PLAYER_SIZE, PLAYER_SIZE)

        # Kokkupõrke kontroll – itereeritakse listi kaudu
        for obs in self.obstacles:
            if self.player_rect.colliderect(obs):
                self.hit   = True
                self.state = "gameover"
                break

    def draw(self, surface):
        surface.fill(BG_COLOR)

        # Joonista takistused listist
        for obs in self.obstacles:
            pygame.draw.rect(surface, OBSTACLE_COLOR, obs)
            pygame.draw.rect(surface, OBSTACLE_BORDER, obs, 2)

        # Mängija värv sõltub seisundist
        color = PLAYER_HIT if self.hit else PLAYER_COLOR
        pygame.draw.rect(surface, color, self.player_rect)
        pygame.draw.rect(surface, (255, 255, 255), self.player_rect, 2)

        # Takistuste arv ekraanil
        count_surf = font.render(f"Takistusi: {len(self.obstacles)}", True, TEXT_DIM)
        surface.blit(count_surf, (10, 10))

        # Algusekraan
        if self.state == "start":
            self._draw_overlay(surface,
                "TAKISTUSTE MÄNG",
                ["Liigu: nooleklahvid või WASD",
                 "Väldi musti ristkülikuid!",
                 "",
                 "Vajuta TÜHIKUT alustamiseks"])

        # Mäng läbi
        elif self.state == "gameover":
            self._draw_overlay(surface,
                "MÄNG LÄBI!",
                ["Puudutasid takistust.",
                 "",
                 "Vajuta TÜHIKUT uuesti mängimiseks"])

    def _draw_overlay(self, surface, title, lines):
        # Poolläbipaistev taust
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # Pealkiri
        title_surf = font_big.render(title, True, (255, 220, 60))
        tx = (WIDTH - title_surf.get_width()) // 2
        ty = HEIGHT // 2 - 80
        surface.blit(title_surf, (tx, ty))

        # Alamread
        for i, line in enumerate(lines):
            if line == "":
                continue
            s = font_sub.render(line, True, TEXT_COLOR)
            x = (WIDTH - s.get_width()) // 2
            y = ty + 70 + i * 28
            surface.blit(s, (x, y))


# --- Peamine tsükkel ---
def main():
    game = Game()

    while True:
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

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()