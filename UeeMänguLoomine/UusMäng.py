import pygame
import sys
import random

# --- INITSIALISEERIMINE ---
pygame.init()

WIDTH, HEIGHT = 640, 480          # ← MUUDA: akna suurus (laius, kõrgus)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hiir")  # ← MUUDA: akna pealkiri

clock = pygame.time.Clock()
FPS = 60                           # ← MUUDA: kaadrisagedus (suurem = sujuvam, kuid rohkem CPU)

# --- VÄRVID ---
TAUST = (173, 216, 230)            # ← MUUDA: taustavärv (R, G, B) — praegu helesinene

# --- KONSTANDID ---
MAX_RINGID = 10                    # ← MUUDA: mitu ringi korraga ekraanil (FIFO piirang)
ALG_RAADIUS = 10                   # ← MUUDA: esimese ringi suurus pikslites
KASVU_SAMM = 5                     # ← MUUDA: mitu pikslit iga järgmine ring eelmisest suurem on

# --- RINGIDE NIMEKIRI ---
# Iga ring on sõnastik: {'x', 'y', 'raadius', 'värv'}
ringid = []

def juhusvärv():
    """Tagastab juhusliku RGB värvi."""
    return (
        random.randint(0, 200),    # ← MUUDA: punase kanali vahemik (0–255)
        random.randint(0, 200),    # ← MUUDA: rohelise kanali vahemik (0–255)
        random.randint(0, 200)     # ← MUUDA: sinise kanali vahemik (0–255)
    )

def lisa_ring(x, y):
    """
    Lisab uue ringi antud koordinaatidele.
    - Raadius on eelmisest ringist 5px suurem (kasvab iga klikiga)
    - Värvus on juhuslik
    - Kui ringe on juba 10, kustutatakse kõige vanem (esimene)
    """
    if ringid:
        uus_raadius = ringid[-1]['raadius'] + KASVU_SAMM
    else:
        uus_raadius = ALG_RAADIUS

    uus_ring = {
        'x': x,
        'y': y,
        'raadius': uus_raadius,
        'värv': juhusvärv()        # ← MUUDA: asenda juhusvärv() kindla värviga nt (255, 0, 0)
    }

    ringid.append(uus_ring)

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
            2   # ← MUUDA: joone paksus pikslites; 0 = täidetud ring (mitte ainult piirjoon)
        )

# --- PEAMINE TSÜKKEL ---
def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:          # ← MUUDA: 1=vasak, 2=keskmine, 3=parem hiirenupp
                    lisa_ring(*event.pos)

        screen.fill(TAUST)
        joonista_ringid(screen)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()