import pygame
import sys
import random

# --- Initsialiseerimine ---
pygame.init()

WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hiir")

clock = pygame.time.Clock()
FPS = 60

# --- Värvid ---
TAUST = (173, 216, 230)  # helesinne taust

# --- Konstandid ---
MAX_RINGID = 10       # maksimaalselt 10 ringi korraga
ALG_RAADIUS = 10      # iga uue ringi algraadius pikslites
KASVU_SAMM = 5        # mitu pikslit ring igal klikil kasvab

# --- Ringide nimekiri ---
# Iga ring on sõnastik: {'x', 'y', 'raadius', 'värv'}
ringid = []

def juhusvärv():
    """Tagastab juhusliku RGB värvi."""
    return (
        random.randint(0, 200),
        random.randint(0, 200),
        random.randint(0, 200)
    )

def lisa_ring(x, y):
    """
    Lisab uue ringi antud koordinaatidele.
    - Raadius on eelmisest ringist 5px suurem (kasvab iga klikiga)
    - Värvus on juhuslik
    - Kui ringe on juba 10, kustutatakse kõige vanem (esimene)
    """
    # Arvuta uus raadius: eelmine raadius + kasvu samm
    if ringid:
        uus_raadius = ringid[-1]['raadius'] + KASVU_SAMM
    else:
        uus_raadius = ALG_RAADIUS

    uus_ring = {
        'x': x,
        'y': y,
        'raadius': uus_raadius,
        'värv': juhusvärv()
    }

    ringid.append(uus_ring)

    # Kui üle 10 ringi, eemalda kõige vanem
    if len(ringid) > MAX_RINGID:
        ringid.pop(0)

def joonista_ringid(surface):
    """Joonistab kõik ringid ekraanile."""
    for ring in ringid:
        pygame.draw.circle(
            surface,
            ring['värv'],
            (ring['x'], ring['y']),
            ring['raadius'],
            2  # ainult piirjoon (mitte täidetud)
        )

# --- Infotelp ---
font = pygame.font.SysFont("Courier New", 16, bold=True)

def joonista_info(surface):
    """Kuvab ülaservas ringi arvu ja juhendi."""
    tekst = font.render(
        f"Ringe: {len(ringid)}/{MAX_RINGID}   |   Kliki ekraanile ringi lisamiseks",
        True, (30, 30, 100)
    )
    surface.blit(tekst, (10, 10))

# --- Peamine tsükkel ---
def main():
    while True:
        # --- Sündmuste töötlus ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Hiireklõps → lisa ring klõpsu kohale
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # vasak nupp
                    lisa_ring(*event.pos)

        # --- Joonistamine ---
        screen.fill(TAUST)
        joonista_ringid(screen)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()