import pygame
import math
import random

pygame.init()

# --- VÄRVID ---
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)
SCARED = (33, 33, 222)
DARK_BLUE = (0, 0, 139)

# --- AKEN ---
WIN_W = 606
WIN_H = 650
screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()
FPS = 60

font_big = pygame.font.SysFont("Arial", 36, bold=True)
font_med = pygame.font.SysFont("Arial", 24, bold=True)
font_small = pygame.font.SysFont("Arial", 18)

# --- SEINAD (hbokmann layout) ---
WALLS = [
    [0, 0, 6, 600], [0, 0, 600, 6], [0, 600, 606, 6], [600, 0, 6, 606],
    [300, 0, 6, 66],
    [60, 60, 186, 6], [360, 60, 186, 6],
    [60, 120, 66, 6], [60, 120, 6, 126],
    [180, 120, 246, 6], [300, 120, 6, 66],
    [480, 120, 66, 6], [540, 120, 6, 126],
    [120, 180, 126, 6], [120, 180, 6, 126],
    [360, 180, 126, 6], [480, 180, 6, 126],
    [180, 240, 6, 126], [180, 360, 246, 6], [420, 240, 6, 126],
    [240, 240, 42, 6], [324, 240, 42, 6],
    [240, 240, 6, 66], [240, 300, 126, 6], [360, 240, 6, 66],
    [0, 300, 66, 6], [540, 300, 66, 6],
    [60, 360, 66, 6], [60, 360, 6, 186],
    [480, 360, 66, 6], [540, 360, 6, 186],
    [120, 420, 366, 6], [120, 420, 6, 66], [480, 420, 6, 66],
    [180, 480, 246, 6], [300, 480, 6, 66],
    [120, 540, 126, 6], [360, 540, 126, 6],
]

# --- KODU UКС (ghost gate) ---
GATE = [282, 242, 42, 4]

# --- GHOST LIIKUMISRAJAD (hbokmann) ---
PINKY_DIRS = [
    [0, -30, 4], [15, 0, 9], [0, 15, 11], [-15, 0, 23], [0, 15, 7], [15, 0, 3],
    [0, -15, 3], [15, 0, 19], [0, 15, 3], [15, 0, 3], [0, 15, 3], [15, 0, 3],
    [0, -15, 15], [-15, 0, 7], [0, 15, 3], [-15, 0, 19], [0, -15, 11], [15, 0, 9]
]
BLINKY_DIRS = [
    [0, -15, 4], [15, 0, 9], [0, 15, 11], [15, 0, 3], [0, 15, 7], [-15, 0, 11],
    [0, 15, 3], [15, 0, 15], [0, -15, 15], [15, 0, 3], [0, -15, 11], [-15, 0, 3],
    [0, -15, 11], [-15, 0, 3], [0, -15, 3], [-15, 0, 7], [0, -15, 3], [15, 0, 15],
    [0, 15, 15], [-15, 0, 3], [0, 15, 3], [-15, 0, 3], [0, -15, 7], [-15, 0, 3],
    [0, 15, 7], [-15, 0, 11], [0, -15, 7], [15, 0, 5]
]
INKY_DIRS = [
    [30, 0, 2], [0, -15, 4], [15, 0, 10], [0, 15, 7], [15, 0, 3], [0, -15, 3],
    [15, 0, 3], [0, -15, 15], [-15, 0, 15], [0, 15, 3], [15, 0, 15], [0, 15, 11],
    [-15, 0, 3], [0, -15, 7], [-15, 0, 11], [0, 15, 3], [-15, 0, 11], [0, 15, 7],
    [-15, 0, 3], [0, -15, 3], [-15, 0, 3], [0, -15, 15], [15, 0, 15], [0, 15, 3],
    [-15, 0, 15], [0, 15, 11], [15, 0, 3], [0, -15, 11], [15, 0, 11], [0, 15, 3], [15, 0, 1]
]
CLYDE_DIRS = [
    [-30, 0, 2], [0, -15, 4], [15, 0, 5], [0, 15, 7], [-15, 0, 11], [0, -15, 7],
    [-15, 0, 3], [0, 15, 7], [-15, 0, 7], [0, 15, 15], [15, 0, 15], [0, -15, 3],
    [-15, 0, 11], [0, -15, 7], [15, 0, 3], [0, -15, 11], [15, 0, 9]
]


# --- KLASS: SEIN (sprite) ---
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=BLUE):
        super().__init__()
        self.image = pygame.Surface([w, h])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


# --- KLASS: PELLET (punktid) ---
class Pellet(pygame.sprite.Sprite):
    def __init__(self, x, y, big=False):
        super().__init__()
        self.big = big
        r = 8 if big else 4
        self.image = pygame.Surface([r * 2, r * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW if big else WHITE, (r, r), r)
        self.rect = self.image.get_rect(center=(x, y))


# --- KLASS: PACMAN ---
class Pacman(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.radius = 14
        self.speed = 3
        self.change_x = 0
        self.change_y = 0
        self.mouth_angle = 45
        self.mouth_dir = 1  # avab/sulgeb
        self.facing = 0  # kraadides: 0=parem, 180=vasak, 90=alla, 270=üles
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self._draw()

    def _draw(self):
        self.image.fill((0, 0, 0, 0))
        start_a = math.radians(self.facing + self.mouth_angle // 2)
        end_a = math.radians(self.facing - self.mouth_angle // 2 + 360)
        pygame.draw.circle(self.image, YELLOW, (self.radius, self.radius), self.radius)
        if self.mouth_angle > 0:
            # kata suu must kolmnurgaga
            points = [(self.radius, self.radius)]
            for deg in range(int(self.facing - self.mouth_angle // 2),
                             int(self.facing + self.mouth_angle // 2) + 1, 5):
                rad = math.radians(deg)
                px = self.radius + self.radius * math.cos(rad)
                py = self.radius - self.radius * math.sin(rad)
                points.append((px, py))
            if len(points) > 2:
                pygame.draw.polygon(self.image, BLACK, points)
        # silm
        eye_x = int(self.radius + 6 * math.cos(math.radians(self.facing + 70)))
        eye_y = int(self.radius - 6 * math.sin(math.radians(self.facing + 70)))
        pygame.draw.circle(self.image, BLACK, (eye_x, eye_y), 2)

    def animate(self):
        self.mouth_angle += 5 * self.mouth_dir
        if self.mouth_angle >= 45:
            self.mouth_dir = -1
        elif self.mouth_angle <= 0:
            self.mouth_dir = 1
        self._draw()

    def set_direction(self, dx, dy):
        self.change_x = dx
        self.change_y = dy
        if dx > 0:
            self.facing = 0
        elif dx < 0:
            self.facing = 180
        elif dy < 0:
            self.facing = 90
        elif dy > 0:
            self.facing = 270

    def update(self, walls, gate):
        old_x, old_y = self.rect.x, self.rect.y
        self.rect.x += self.change_x
        if pygame.sprite.spritecollideany(self, walls):
            self.rect.x = old_x
        if gate and pygame.sprite.spritecollideany(self, gate):
            self.rect.x = old_x

        self.rect.y += self.change_y
        if pygame.sprite.spritecollideany(self, walls):
            self.rect.y = old_y
        if gate and pygame.sprite.spritecollideany(self, gate):
            self.rect.y = old_y

        # tunneli wraparound
        if self.rect.right < 0:
            self.rect.left = WIN_W
        elif self.rect.left > WIN_W:
            self.rect.right = 0

        self.animate()

    @property
    def center(self):
        return self.rect.center


# --- KLASS: GHOST ---
class Ghost(pygame.sprite.Sprite):
    COLORS = {'blinky': RED, 'pinky': PINK, 'inky': CYAN, 'clyde': ORANGE}

    def __init__(self, x, y, name, dirs, dirs_len):
        super().__init__()
        self.name = name
        self.color = self.COLORS[name]
        self.radius = 13
        self.dirs = dirs
        self.dirs_len = dirs_len
        self.turn = 0
        self.steps = 0
        self.change_x = 0
        self.change_y = 0
        self.scared = False
        self.scared_timer = 0
        self.image = pygame.Surface([self.radius * 2 + 2, self.radius * 2 + 6], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self._draw()

    def _draw(self):
        self.image.fill((0, 0, 0, 0))
        w = self.image.get_width()
        h = self.image.get_height()
        color = SCARED if self.scared else self.color

        # Keha
        pygame.draw.ellipse(self.image, color, [0, 0, w, h - 4])
        pygame.draw.rect(self.image, color, [0, h // 2, w, h // 2 - 4])

        # Alumine sakkjas serv
        seg = w // 3
        for i in range(3):
            pygame.draw.polygon(self.image, BLACK, [
                (i * seg, h - 4),
                (i * seg + seg // 2, h),
                ((i + 1) * seg, h - 4)
            ])

        # Silmad
        if not self.scared:
            for ox, px in [(w // 3 - 3, w // 3 + 3), (2 * w // 3 - 3, 2 * w // 3 + 3)]:
                pygame.draw.circle(self.image, WHITE, (ox + 3, h // 3), 4)
                pygame.draw.circle(self.image, DARK_BLUE, (px, h // 3), 2)
        else:
            # hirmunud silmad
            pygame.draw.line(self.image, WHITE, (w // 3 - 3, h // 3 + 2), (w // 3 + 3, h // 3 - 2), 2)
            pygame.draw.line(self.image, WHITE, (2 * w // 3 - 3, h // 3 + 2), (2 * w // 3 + 3, h // 3 - 2), 2)

    def update_scared(self, scared, timer):
        was = self.scared
        self.scared = scared
        self.scared_timer = timer
        if was != scared:
            self._draw()

    def update(self, walls, _=None):
        SPEED = 2  # px per frame (1=aeglane, 3=kiire)
        old_x, old_y = self.rect.x, self.rect.y

        self.rect.x += self.change_x * SPEED
        self.rect.y += self.change_y * SPEED

        if pygame.sprite.spritecollideany(self, walls):
            self.rect.x = old_x
            self.rect.y = old_y
            dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            random.shuffle(dirs)
            moved = False
            for dx, dy in dirs:
                self.rect.x = old_x + dx * SPEED
                self.rect.y = old_y + dy * SPEED
                if not pygame.sprite.spritecollideany(self, walls):
                    self.change_x, self.change_y = dx, dy
                    moved = True
                    break
            if not moved:
                self.rect.x = old_x
                self.rect.y = old_y
        else:
            if random.randint(0, 80) == 0:
                dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                random.shuffle(dirs)
                for dx, dy in dirs:
                    tmp = self.rect.copy()
                    tmp.x += dx * SPEED
                    tmp.y += dy * SPEED
                    if not any(tmp.colliderect(w.rect) for w in walls):
                        self.change_x, self.change_y = dx, dy
                        break

        if self.rect.right < 0:
            self.rect.left = WIN_W
        elif self.rect.left > WIN_W:
            self.rect.right = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# --- MÄNGU SEADISTUS ---
def setup_level():
    all_sprites = pygame.sprite.RenderPlain()
    wall_list = pygame.sprite.RenderPlain()
    gate_group = pygame.sprite.RenderPlain()
    pellet_list = pygame.sprite.RenderPlain()

    # Seinad
    for w in WALLS:
        s = Wall(w[0], w[1], w[2], w[3])
        wall_list.add(s)
        all_sprites.add(s)

    # Värav
    g = Wall(GATE[0], GATE[1], GATE[2], GATE[3], WHITE)
    gate_group.add(g)
    all_sprites.add(g)

    # Pelletid — grid 19x19, vahele jäetakse seintega kattuvad
    power_positions = []
    tmp_pac = pygame.sprite.Sprite()
    tmp_pac.rect = pygame.Rect(303 - 16 - 7, int(7 * 60 + 19) - 7, 28, 28)

    for row in range(19):
        for col in range(19):
            px = (30 * col + 6) + 26
            py = (30 * row + 6) + 26
            # jäta ghost-maja piirkond vahele (read 7-8, veerud 8-10)
            if (row in (7, 8)) and (col in (8, 9, 10)):
                continue
            tmp = pygame.sprite.Sprite()
            tmp.rect = pygame.Rect(px - 2, py - 2, 4, 4)
            if pygame.sprite.spritecollideany(tmp, wall_list):
                continue
            if tmp.rect.colliderect(tmp_pac.rect):
                continue
            # nurgad → power pellet
            big = (row in (1, 17)) and (col in (1, 17))
            p = Pellet(px, py, big)
            pellet_list.add(p)
            all_sprites.add(p)

    return all_sprites, wall_list, gate_group, pellet_list


def draw_score(surface, score, bll, lives):
    txt = font_med.render(f"Score: {score}  Lives: {lives}", True, WHITE)
    surface.blit(txt, (10, 610))


def show_message(surface, line1, line2=""):
    overlay = pygame.Surface((400, 160), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (103, 220))
    t1 = font_big.render(line1, True, YELLOW)
    r1 = t1.get_rect(center=(WIN_W // 2, 270))
    surface.blit(t1, r1)
    if line2:
        t2 = font_small.render(line2, True, WHITE)
        r2 = t2.get_rect(center=(WIN_W // 2, 320))
        surface.blit(t2, r2)
    t3 = font_small.render("ENTER = mängi uuesti   ESC = välju", True, WHITE)
    r3 = t3.get_rect(center=(WIN_W // 2, 350))
    surface.blit(t3, r3)


# --- PEAMINE MÄNG ---
def start_game():
    all_sprites, wall_list, gate_group, pellet_list = setup_level()
    total_pellets = len(pellet_list)

    # Pac-man algpositsioon (hbokmann: w=303-16, p_h=7*60+19)
    pacman = Pacman(303 - 16 + 14, 7 * 60 + 19 + 14)
    all_sprites.add(pacman)

    # Ghostid (hbokmann positsioonid)
    w = 303 - 16
    b_h = 3 * 60 + 19
    m_h = 4 * 60 + 19
    i_w = 303 - 16 - 32
    c_w = 303 + (32 - 16)

    blinky = Ghost(w + 14, b_h + 14, 'blinky', BLINKY_DIRS, len(BLINKY_DIRS) - 1)
    pinky = Ghost(w + 14, m_h + 14, 'pinky', PINKY_DIRS, len(PINKY_DIRS) - 1)
    inky = Ghost(i_w + 14, m_h + 14, 'inky', INKY_DIRS, len(INKY_DIRS) - 1)
    clyde = Ghost(c_w + 14, m_h + 14, 'clyde', CLYDE_DIRS, len(CLYDE_DIRS) - 1)

    ghosts = [blinky, pinky, inky, clyde]
    ghost_group = pygame.sprite.RenderPlain(*ghosts)
    for g in ghosts:
        all_sprites.add(g)

    score = 0
    lives = 3
    powerup = False
    power_timer = 0
    POWER_DURATION = 300  # raame (5 sek 60fps)

    game_over = False
    game_won = False
    waiting = False  # ootab Enter klahvi

    running = True
    while running:
        clock.tick(FPS)

        # --- SÜNDMUSED ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key in (pygame.K_RETURN, pygame.K_SPACE) and waiting:
                    return True  # restart

                if not game_over and not game_won:
                    if event.key == pygame.K_LEFT:
                        pacman.set_direction(-pacman.speed, 0)
                    elif event.key == pygame.K_RIGHT:
                        pacman.set_direction(pacman.speed, 0)
                    elif event.key == pygame.K_UP:
                        pacman.set_direction(0, -pacman.speed)
                    elif event.key == pygame.K_DOWN:
                        pacman.set_direction(0, pacman.speed)

            if event.type == pygame.KEYUP:
                if not game_over and not game_won:
                    # ei peata liikumist (nagu originaalis)
                    pass

        if not game_over and not game_won:
            # --- LIIKUMINE ---
            pacman.update(wall_list, gate_group)
            for g in ghosts:
                g.update(wall_list)

            # --- PELLETID ---
            eaten = pygame.sprite.spritecollide(pacman, pellet_list, True)
            for p in eaten:
                if p.big:
                    score += 50
                    powerup = True
                    power_timer = POWER_DURATION
                    for g in ghosts:
                        g.update_scared(True, POWER_DURATION)
                else:
                    score += 10

            # --- POWER-UP TIMER ---
            if powerup:
                power_timer -= 1
                if power_timer <= 0:
                    powerup = False
                    for g in ghosts:
                        g.update_scared(False, 0)

            # --- VÕIT ---
            if len(pellet_list) == 0:
                game_won = True
                waiting = True

            # --- KOKKUPÕRGE GHOSTIGA ---
            for g in ghosts:
                if pacman.rect.colliderect(g.rect):
                    if powerup and not g.scared:
                        pass
                    elif powerup and g.scared:
                        score += 200
                        g.rect.center = (w + 14, b_h + 14)
                        g.turn = 0;
                        g.steps = 0
                        g.update_scared(False, 0)
                    else:
                        lives -= 1
                        if lives <= 0:
                            game_over = True
                            waiting = True
                        else:
                            # reset pacman + ghostid
                            pacman.rect.center = (303 - 16 + 14, 7 * 60 + 19 + 14)
                            pacman.change_x = 0;
                            pacman.change_y = 0
                            for gi, gh in enumerate(ghosts):
                                gh.turn = 0;
                                gh.steps = 0
                            powerup = False
                            for g2 in ghosts:
                                g2.update_scared(False, 0)
                        break

        # --- JOONISTAMINE ---
        screen.fill(BLACK)
        wall_list.draw(screen)
        gate_group.draw(screen)
        pellet_list.draw(screen)
        pacman.image = pacman.image  # juba uuendatud
        screen.blit(pacman.image, pacman.rect)
        for g in ghosts:
            g.draw(screen)

        draw_score(screen, score, total_pellets, lives)

        if game_over:
            show_message(screen, "GAME OVER", f"Skoor: {score}")
        elif game_won:
            show_message(screen, "VÕITSID!", f"Skoor: {score}")

        pygame.display.flip()

    return False


# --- KÄIVITAMINE ---
if __name__ == "__main__":
    again = True
    while again:
        again = start_game()
    pygame.quit()