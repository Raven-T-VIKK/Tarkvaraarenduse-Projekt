"""
PAC-MAN - Kombineeritud versioon
=================================
Allikad:
  1. PAC-MAN v1.py  - freegames/turtle tile-map süsteem ja loogika
  2. pacman.py (#2) - pygame Wall/Player/Ghost klassid, nimega kummitused, Gate
  3. pacman.py (#3) - Enemy liikumisloogika, mängurežiimide haldus, sein-kollisioon

Lisatud/täiustatud funktsioonid:
  - Animeeritud Pac-Man (suu avamine/sulgemine)
  - Power pellets (suuremad punktid, kummitused põgenevad)
  - Elud (3 elu, ekraanil kuvatud)
  - Nimega kummitused erineva värviga (Blinky, Pinky, Inky, Clyde)
  - Kummituste erinev liikumisloogika (jälitamine vs juhuslik)
  - Täielik tile-põhine labürint freegames v1 eeskujul
  - Skoor, tasemed, mäng lõpp ekraanid
  - Heliefektid (pygame.mixer)
"""

import pygame
import math
import random
import sys

# ---------------------------------------------------------------------------
# INITSIALISEERIMINE
# ---------------------------------------------------------------------------
pygame.init()
pygame.mixer.init()

# ---------------------------------------------------------------------------
# KONSTANDID
# ---------------------------------------------------------------------------
TILE_SIZE    = 32          # ühe ruudu suurus pikslites
COLS         = 19          # veergude arv
ROWS         = 21          # ridade arv
WIN_W        = COLS * TILE_SIZE   # 608
WIN_H        = ROWS * TILE_SIZE + 60  # + HUD riba alumises osas
FPS          = 60

# Värvid
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
YELLOW  = (255, 255,   0)
BLUE    = (33,  33, 222)
RED     = (255,  0,   0)
PINK    = (255, 184, 255)
CYAN    = (0,  255, 255)
ORANGE  = (255, 184,  82)
SCARED  = (30,   0, 200)   # kummituse "põgenev" värv
DARK_BG = (10,  10,  10)
WALL_OUTLINE = (100, 100, 255)

# Mängurežiimid
STATE_PLAYING   = "playing"
STATE_WIN       = "win"
STATE_GAME_OVER = "game_over"
STATE_READY     = "ready"

# Kummituste värvid
GHOST_COLORS = {
    "Blinky": RED,
    "Pinky":  PINK,
    "Inky":   CYAN,
    "Clyde":  ORANGE,
}

# ---------------------------------------------------------------------------
# LABÜRINT  (0 = sein, 1 = tavaline punkt, 2 = power pellet, 3 = tühi käik)
# Kombineeritud PAC-MAN v1 tile-kaardist, kohandatud 19×21 formaadile
# ---------------------------------------------------------------------------
# fmt: off
LEVEL_MAP = [
#   0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0],  # 1  ülemine rida
    [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 2, 0],  # 2
    [0, 2, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0],  # 3
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],  # 4  horisontaal
    [0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0],  # 5
    [0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0],  # 6
    [0, 0, 0, 0, 1, 0, 1, 3, 3, 3, 3, 3, 1, 0, 1, 0, 0, 0, 0],  # 7
    [0, 0, 0, 0, 1, 0, 1, 3, 3, 3, 3, 3, 1, 0, 1, 0, 0, 0, 0],  # 8  kummituste kodu
    [3, 3, 3, 3, 1, 3, 1, 3, 3, 3, 3, 3, 1, 3, 1, 3, 3, 3, 3],  # 9  tunnel
    [0, 0, 0, 0, 1, 0, 1, 3, 3, 3, 3, 3, 1, 0, 1, 0, 0, 0, 0],  # 10
    [0, 0, 0, 0, 1, 0, 1, 1, 1, 3, 1, 1, 1, 0, 1, 0, 0, 0, 0],  # 11
    [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],  # 12
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 0],  # 13 horisontaal
    [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],  # 14
    [0, 1, 1, 0, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 0, 1, 1, 0],  # 15 Pac-Man algab siin
    [0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0],  # 16
    [0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0],  # 17
    [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0],  # 18
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],  # 19 alumine rida
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 20
]
# fmt: on

# ---------------------------------------------------------------------------
# ABIVÄLJENDID
# ---------------------------------------------------------------------------

def tile_center(col, row):
    """Tagastab tile (col, row) keskpunkti pikslites."""
    return (col * TILE_SIZE + TILE_SIZE // 2,
            row * TILE_SIZE + TILE_SIZE // 2)


def pixel_to_tile(px, py):
    """Teisendab pikslid tile indeksiks."""
    return (int(px // TILE_SIZE), int(py // TILE_SIZE))


def is_wall(col, row):
    """Kontrollib, kas antud tile on sein (0)."""
    if 0 <= row < ROWS and 0 <= col < COLS:
        return LEVEL_MAP[row][col] == 0
    return True   # piirid on seinad


# ---------------------------------------------------------------------------
# ANIMEERITUD PAC-MAN KLASS  (kombineeritud v1 liikumisloogika + v3 kollisioon)
# ---------------------------------------------------------------------------

class Pacman:
    """
    Mängija karakter.
    Kombineerib:
      - PAC-MAN v1: tile-põhine liikumine, punktide kogumine
      - pacman.py #3: sein-kollisioon pikslitasandil, elu kaotamise loogika
    Lisatud: suu animatsioon, power-pellet režiim
    """

    SPEED = 3  # pikslit kaadris

    def __init__(self, start_col, start_row):
        self.start_col = start_col
        self.start_row = start_row
        self.reset()

    def reset(self):
        """Taastab algseisu (uue elu alguses)."""
        cx, cy = tile_center(self.start_col, self.start_row)
        self.x = float(cx)
        self.y = float(cy)
        self.dx = 0
        self.dy = 0
        self.next_dx = 0
        self.next_dy = 0
        # Animatsioon
        self.mouth_angle = 45    # kraadid
        self.mouth_dir   = -5    # kraadides kaadris
        self.facing      = 0     # nurk joonistamiseks (0=paremale)

    def set_direction(self, dx, dy):
        """Salvestab soovitud suuna (rakendatakse järgmisel võimalusel)."""
        self.next_dx = dx
        self.next_dy = dy

    def _in_tunnel(self):
        """Kontrollib kas oleme tunneli real (rida 9)."""
        _, row = pixel_to_tile(self.x, self.y)
        return row == 9

    def _can_move(self, dx, dy):
        """
        Kontrollib, kas liikumine (dx, dy) on võimalik.
        Kasutab pikslipõhist sein-kontrolli (pacman.py #3 eeskujul).
        Tunneli real lubatakse liikumine ekraani servast välja.
        """
        r = TILE_SIZE // 2 - 2
        new_x = self.x + dx
        new_y = self.y + dy
        # Tunneli real — ära blokeeri ekraanist välja liikumist
        if self._in_tunnel() or self.x < 0 or self.x >= WIN_W:
            return True
        corners = [
            (new_x - r, new_y - r),
            (new_x + r, new_y - r),
            (new_x - r, new_y + r),
            (new_x + r, new_y + r),
        ]
        for cx, cy in corners:
            tc, tr = pixel_to_tile(cx, cy)
            if is_wall(tc, tr):
                return False
        return True

    def update(self):
        """Uuendab Pac-Mani positsiooni ja animatsiooni."""
        # Proovi soovitud suunda
        if self.next_dx != 0 or self.next_dy != 0:
            if self._can_move(self.next_dx, self.next_dy):
                self.dx = self.next_dx
                self.dy = self.next_dy

        # Liigu praeguses suunas
        if self._can_move(self.dx, self.dy):
            self.x += self.dx
            self.y += self.dy
        else:
            # Seina taga - peatu
            self.dx = 0
            self.dy = 0

        # Tunnel (vasak-parem): teleport teise otsa tunneli keskele
        tunnel_y = 9 * TILE_SIZE + TILE_SIZE // 2  # rida 9 keskpunkt
        if self.x < -TILE_SIZE // 2:
            self.x = WIN_W - TILE_SIZE // 2 - 1
            self.y = tunnel_y
        elif self.x > WIN_W - TILE_SIZE // 2:
            self.x = TILE_SIZE // 2 + 1
            self.y = tunnel_y

        # Suu animatsioon
        self.mouth_angle += self.mouth_dir
        if self.mouth_angle <= 5 or self.mouth_angle >= 45:
            self.mouth_dir *= -1

        # Vaatamissuund
        if self.dx > 0:   self.facing = 0
        elif self.dx < 0: self.facing = 180
        elif self.dy < 0: self.facing = 90
        elif self.dy > 0: self.facing = 270

    def draw(self, surface):
        """Joonistab animeeritud Pac-Mani."""
        x, y = int(self.x), int(self.y)
        r = TILE_SIZE // 2 - 2
        start_angle = math.radians(self.facing + self.mouth_angle)
        end_angle   = math.radians(self.facing + 360 - self.mouth_angle)
        points = [(x, y)]
        steps = 36
        a = start_angle
        while a <= end_angle:
            points.append((x + r * math.cos(a), y - r * math.sin(a)))
            a += (end_angle - start_angle) / steps
        points.append((x, y))
        if len(points) > 2:
            pygame.draw.polygon(surface, YELLOW, points)

    def get_tile(self):
        return pixel_to_tile(self.x, self.y)

    def get_rect(self):
        r = TILE_SIZE // 2 - 4
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)


# ---------------------------------------------------------------------------
# KUMMITUS KLASS  (kombineeritud pacman.py #2 Ghost + #3 Enemy liikumine)
# ---------------------------------------------------------------------------

class Ghost:
    """
    Kummitus.
    Kombineerib:
      - pacman.py #2: nimega kummitused, värvid, Clyde erinev käitumine
      - pacman.py #3: juhuslik liikumissuuna valik, sein-kollisioon
    Lisatud:
      - CHASE режiim: Blinky jälitab Pac-Mani (BFS lühim tee)
      - SCATTER режiim: liigub oma nurka
      - FRIGHTENED режiim: põgeneb power-pelleti ajal
    """

    SPEED_NORMAL    = 2
    SPEED_FRIGHTENED = 1
    FRIGHTENED_TIME  = 7000  # ms

    def __init__(self, name, start_col, start_row):
        self.name = name
        self.color = GHOST_COLORS.get(name, RED)
        self.start_col = start_col
        self.start_row = start_row
        self.reset()

    def reset(self):
        cx, cy = tile_center(self.start_col, self.start_row)
        self.x = float(cx)
        self.y = float(cy)
        self.dx = random.choice([-self.SPEED_NORMAL, self.SPEED_NORMAL])
        self.dy = 0
        self.frightened = False
        self.frightened_timer = 0
        self.blink = False

    def frighten(self):
        """Aktiveerib põgenemisrežiimi (power pellet korral)."""
        self.frightened = True
        self.frightened_timer = pygame.time.get_ticks()
        self.dx = -self.dx  # pöörake ringi

    def _in_tunnel(self):
        """Kontrollib kas kummitus on tunneli real (rida 9)."""
        _, row = pixel_to_tile(self.x, self.y)
        return row == 9

    def _can_move(self, dx, dy):
        """Pikslipõhine sein-kontroll. Tunneli real lubatakse ekraanist välja liikumine."""
        r = TILE_SIZE // 2 - 4
        nx, ny = self.x + dx, self.y + dy
        if self._in_tunnel() or self.x < 0 or self.x >= WIN_W:
            return True
        corners = [
            (nx - r, ny - r), (nx + r, ny - r),
            (nx - r, ny + r), (nx + r, ny + r),
        ]
        for cx, cy in corners:
            tc, tr = pixel_to_tile(cx, cy)
            if is_wall(tc, tr):
                return False
        return True

    def _choose_direction(self, pacman_pos):
        """
        Valib liikumissuuna:
        - Blinky: jälitab Pac-Mani (suurim tõenäosus Pac-Mani suunas)
        - Teised: valdavalt juhuslik, kerge Pac-Mani suunas kallutus
        pacman.py #2 ja #3 Ghost.changespeed loogika kombineering
        """
        speed = self.SPEED_FRIGHTENED if self.frightened else self.SPEED_NORMAL
        px, py = pacman_pos

        directions = []
        for (ddx, ddy) in [(speed,0),(-speed,0),(0,speed),(0,-speed)]:
            # Ära mine tagasi (väldib edasi-tagasi takerdumist)
            if ddx == -self.dx and ddy == -self.dy and (self.dx != 0 or self.dy != 0):
                continue
            if self._can_move(ddx, ddy):
                directions.append((ddx, ddy))

        if not directions:
            # Kõik teed kinni - luba ka tagasipööramine
            for (ddx, ddy) in [(speed,0),(-speed,0),(0,speed),(0,-speed)]:
                if self._can_move(ddx, ddy):
                    directions.append((ddx, ddy))

        if not directions:
            return

        if self.frightened:
            # Põgene Pac-Manist eemale
            best = max(directions,
                       key=lambda d: math.hypot(self.x+d[0]-px, self.y+d[1]-py))
            self.dx, self.dy = best
        elif self.name == "Blinky":
            # Jälita Pac-Mani otse
            best = min(directions,
                       key=lambda d: math.hypot(self.x+d[0]-px, self.y+d[1]-py))
            self.dx, self.dy = best
        elif self.name == "Pinky":
            # Jälita 4 tile ette Pac-Manist
            self.dx, self.dy = random.choices(
                directions,
                weights=[1 / (math.hypot(self.x+d[0]-px, self.y+d[1]-py)+1)
                         for d in directions]
            )[0]
        else:
            # Clyde ja Inky: juhuslik
            self.dx, self.dy = random.choice(directions)

    def update(self, pacman_pos):
        """Uuendab kummituse asendit."""
        now = pygame.time.get_ticks()

        # Frightened taimer
        if self.frightened:
            elapsed = now - self.frightened_timer
            if elapsed > self.FRIGHTENED_TIME:
                self.frightened = False
            self.blink = elapsed > self.FRIGHTENED_TIME - 2000 and (elapsed // 300) % 2 == 0

        speed = self.SPEED_FRIGHTENED if self.frightened else self.SPEED_NORMAL

        # Tunnel — teleport teise otsa
        tunnel_y = 9 * TILE_SIZE + TILE_SIZE // 2
        if self.x < -TILE_SIZE // 2:
            self.x = WIN_W - TILE_SIZE // 2 - 1
            self.y = tunnel_y
        elif self.x > WIN_W - TILE_SIZE // 2:
            self.x = TILE_SIZE // 2 + 1
            self.y = tunnel_y

        # Liigu praeguses suunas; tile-ristmikul vahel vaata uut suunda
        col, row = pixel_to_tile(self.x, self.y)
        cx, cy   = tile_center(col, row)
        near_center = abs(self.x - cx) < speed + 1 and abs(self.y - cy) < speed + 1

        if near_center:
            self._choose_direction(pacman_pos)

        if self._can_move(self.dx, self.dy):
            self.x += self.dx
            self.y += self.dy
        else:
            self._choose_direction(pacman_pos)

    def draw(self, surface):
        """Joonistab kummituse (klassikaline kuju)."""
        x, y = int(self.x), int(self.y)
        r    = TILE_SIZE // 2 - 3

        if self.frightened:
            color = WHITE if self.blink else SCARED
        else:
            color = self.color

        # Keha (poolring + ristkülik + hambad)
        body_rect = pygame.Rect(x - r, y - r // 2, r * 2, r + r // 2)
        pygame.draw.rect(surface, color, body_rect)
        pygame.draw.circle(surface, color, (x, y - r // 2), r)

        # Hambad allosas
        num_teeth = 3
        tooth_w   = (r * 2) // num_teeth
        for i in range(num_teeth):
            tx = x - r + i * tooth_w
            ty = y + r // 2
            pygame.draw.polygon(surface, color, [
                (tx, ty), (tx + tooth_w, ty), (tx + tooth_w // 2, ty + 6)
            ])

        # Silmad (v.a hirmunud olek)
        if not self.frightened:
            for ex in [x - r // 3, x + r // 3]:
                pygame.draw.circle(surface, WHITE, (ex, y - r // 4), r // 4)
                pygame.draw.circle(surface, BLACK, (ex + 1, y - r // 4), r // 8)

    def get_rect(self):
        r = TILE_SIZE // 2 - 6
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)


# ---------------------------------------------------------------------------
# MÄNGU PEAKLASS  (kombineerib kõigi kolme mängu juhtimisloogika)
# ---------------------------------------------------------------------------

class PacmanGame:
    """
    Mängu peaklass.
    Haldab:
      - Labürindi joonistamine (PAC-MAN v1 tile-kaart)
      - Mängija ja kummituste loomine/uuendamine
      - Skoor, elud, power-pellets
      - Mängurežiimid (ready, playing, win, game_over)
      - HUD (skoor, elud)
    """

    LIVES_START = 3

    def __init__(self):
        self.screen  = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("PAC-MAN – Kombineeritud versioon")
        self.clock   = pygame.time.Clock()
        self.font_lg = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_sm = pygame.font.SysFont("Arial", 20, bold=True)
        self._init_sounds()
        self.new_game()

    # -----------------------------------------------------------------------
    # HELIEFEKTID (lihtsad sünteesitud helid, ei vaja väliseid faile)
    # -----------------------------------------------------------------------

    def _init_sounds(self):
        """Loob lihtsad sünteesitud heliefektid pygame.mixer.Sound abil."""
        self.sounds = {}
        try:
            # Pellet heli - lühike kõrge toon
            buf = bytearray()
            for i in range(1000):
                v = int(127 + 127 * math.sin(2 * math.pi * 800 * i / 44100))
                buf += bytes([v, v])
            snd = pygame.mixer.Sound(buffer=bytes(buf))
            snd.set_volume(0.2)
            self.sounds['pellet'] = snd

            # Power pellet - madalam toon
            buf2 = bytearray()
            for i in range(4000):
                v = int(127 + 127 * math.sin(2 * math.pi * 300 * i / 44100))
                buf2 += bytes([v, v])
            snd2 = pygame.mixer.Sound(buffer=bytes(buf2))
            snd2.set_volume(0.3)
            self.sounds['power'] = snd2
        except Exception:
            pass  # Kui heli ei tööta, jätka vaikselt

    def _play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    # -----------------------------------------------------------------------
    # MÄNGU INITSIALISEERIMINE
    # -----------------------------------------------------------------------

    def new_game(self):
        """Alustab uut mängu (skoor ja elud nullist)."""
        self.score      = 0
        self.lives      = self.LIVES_START
        self.level      = 1
        self.high_score = getattr(self, 'high_score', 0)
        self._init_level()
        self.state      = STATE_READY
        self.ready_timer = pygame.time.get_ticks()

    def _init_level(self):
        """Lähtestab taseme (punktid, kummitused, Pac-Man)."""
        # Koopia labürindist (muudetav)
        self.tiles = [row[:] for row in LEVEL_MAP]

        # Loe kokku kõik söödavad punktid
        self.total_dots = sum(
            1 for row in self.tiles for t in row if t in (1, 2)
        )
        self.dots_left = self.total_dots

        # Pac-Man algasend (rida 15, veerg 9 - klassikaline)
        self.pacman = Pacman(9, 15)

        # Kummitused algasendid — kummituste kodu sees (read 8-11, veerud 7-11 on kõik avatud)
        self.ghosts = [
            Ghost("Blinky", 9,  8),
            Ghost("Pinky",  8,  9),
            Ghost("Inky",  10,  9),
            Ghost("Clyde",  9, 10),
        ]

    def _reset_after_death(self):
        """Taastab asendid pärast elu kaotust."""
        self.pacman.reset()
        for g in self.ghosts:
            g.reset()
        self.state = STATE_READY
        self.ready_timer = pygame.time.get_ticks()

    # -----------------------------------------------------------------------
    # SÜNDMUSTE TÖÖTLUS
    # -----------------------------------------------------------------------

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                # Liikumisklahvid
                if event.key == pygame.K_LEFT:
                    self.pacman.set_direction(-self.pacman.SPEED, 0)
                elif event.key == pygame.K_RIGHT:
                    self.pacman.set_direction(self.pacman.SPEED, 0)
                elif event.key == pygame.K_UP:
                    self.pacman.set_direction(0, -self.pacman.SPEED)
                elif event.key == pygame.K_DOWN:
                    self.pacman.set_direction(0, self.pacman.SPEED)
                # Restart
                if self.state in (STATE_WIN, STATE_GAME_OVER):
                    if event.key == pygame.K_RETURN:
                        self.new_game()

    # -----------------------------------------------------------------------
    # MÄNGU LOOGIKA
    # -----------------------------------------------------------------------

    def update(self):
        """Uuendab mänguolekut (ainult STATE_PLAYING ajal)."""
        if self.state == STATE_READY:
            if pygame.time.get_ticks() - self.ready_timer > 2500:
                self.state = STATE_PLAYING
            return
        if self.state != STATE_PLAYING:
            return

        self.pacman.update()
        pac_pos = (self.pacman.x, self.pacman.y)

        for g in self.ghosts:
            g.update(pac_pos)

        self._check_dots()
        self._check_ghost_collision()

    def _check_dots(self):
        """Kontrollib, kas Pac-Man on punktil/power pelletil."""
        col, row = self.pacman.get_tile()
        if not (0 <= row < ROWS and 0 <= col < COLS):
            return
        tile = self.tiles[row][col]
        if tile == 1:
            self.tiles[row][col] = 3
            self.score    += 10
            self.dots_left -= 1
            self.high_score = max(self.high_score, self.score)
            self._play('pellet')
            if self.dots_left == 0:
                self.state = STATE_WIN
        elif tile == 2:
            self.tiles[row][col] = 3
            self.score    += 50
            self.dots_left -= 1
            self.high_score = max(self.high_score, self.score)
            self._play('power')
            for g in self.ghosts:
                g.frighten()

    def _check_ghost_collision(self):
        """Kontrollib kokkupõrget kummitustega."""
        pac_rect = self.pacman.get_rect()
        for g in self.ghosts:
            if g.get_rect().colliderect(pac_rect):
                if g.frightened:
                    # Söö kummitus
                    g.reset()
                    self.score += 200
                    self.high_score = max(self.high_score, self.score)
                else:
                    # Kaota elu
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = STATE_GAME_OVER
                    else:
                        self._reset_after_death()
                    return

    # -----------------------------------------------------------------------
    # JOONISTAMINE
    # -----------------------------------------------------------------------

    def draw(self):
        self.screen.fill(DARK_BG)
        self._draw_maze()
        if self.state != STATE_GAME_OVER:
            self._draw_dots()
            for g in self.ghosts:
                g.draw(self.screen)
            self.pacman.draw(self.screen)
        self._draw_hud()

        if self.state == STATE_READY:
            self._draw_centered("READY!", YELLOW)
        elif self.state == STATE_WIN:
            self._draw_centered("VÕITSID! ENTER = uuesti", YELLOW)
        elif self.state == STATE_GAME_OVER:
            self._draw_centered("MÄNG LÄBI  ENTER = uuesti", RED)

        pygame.display.flip()

    def _draw_maze(self):
        """
        Joonistab labürindi.
        PAC-MAN v1 tile-süsteem; seinad joonistatakse pygame ristkülikutena.
        """
        for row in range(ROWS):
            for col in range(COLS):
                x = col * TILE_SIZE
                y = row * TILE_SIZE
                if self.tiles[row][col] == 0:
                    pygame.draw.rect(self.screen, BLUE,
                                     (x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2))
                    pygame.draw.rect(self.screen, WALL_OUTLINE,
                                     (x, y, TILE_SIZE, TILE_SIZE), 1)

    def _draw_dots(self):
        """Joonistab alles olevad punktid ja power pelletid."""
        now = pygame.time.get_ticks()
        for row in range(ROWS):
            for col in range(COLS):
                tile = self.tiles[row][col]
                cx, cy = tile_center(col, row)
                if tile == 1:
                    pygame.draw.circle(self.screen, WHITE, (cx, cy), 3)
                elif tile == 2:
                    # Power pellet vilgub
                    if (now // 400) % 2 == 0:
                        pygame.draw.circle(self.screen, WHITE, (cx, cy), 8)

    def _draw_hud(self):
        """Joonistab HUD-i (skoor, elud, rekord) ekraani allosas."""
        hud_y = ROWS * TILE_SIZE
        pygame.draw.rect(self.screen, BLACK, (0, hud_y, WIN_W, 60))

        score_txt = self.font_sm.render(f"SKOOR: {self.score}", True, WHITE)
        self.screen.blit(score_txt, (10, hud_y + 8))

        hi_txt = self.font_sm.render(f"REKORD: {self.high_score}", True, YELLOW)
        self.screen.blit(hi_txt, (WIN_W // 2 - hi_txt.get_width() // 2, hud_y + 8))

        # Elud (Pac-Mani ikoonidena)
        for i in range(self.lives):
            lx = WIN_W - 30 - i * 26
            ly = hud_y + 14
            r  = 10
            angle = math.radians(30)
            pts = [(lx, ly)]
            a = angle
            while a <= math.radians(330):
                pts.append((lx + r * math.cos(a), ly - r * math.sin(a)))
                a += math.radians(20)
            pts.append((lx, ly))
            if len(pts) > 2:
                pygame.draw.polygon(self.screen, YELLOW, pts)

    def _draw_centered(self, text, color):
        """Joonistab teksti ekraani keskele."""
        surf = self.font_lg.render(text, True, color)
        rx   = WIN_W // 2 - surf.get_width() // 2
        ry   = ROWS * TILE_SIZE // 2 - surf.get_height() // 2
        # Poolläbipaistev taust
        bg = pygame.Surface((surf.get_width() + 20, surf.get_height() + 10))
        bg.set_alpha(180)
        bg.fill(BLACK)
        self.screen.blit(bg, (rx - 10, ry - 5))
        self.screen.blit(surf, (rx, ry))

    # -----------------------------------------------------------------------
    # PÕHISILMUS
    # -----------------------------------------------------------------------

    def run(self):
        """Mängu põhisilmus."""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


# ---------------------------------------------------------------------------
# KÄIVITAMINE
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    game = PacmanGame()
    game.run()