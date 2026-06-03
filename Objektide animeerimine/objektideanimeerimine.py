import pygame
import random
import sys

# ── MÄNGU KÄIVITAMINE JA AKNA SEADISTAMINE ──────────────────────────────────
pygame.init()

LAIUS = 640
KORGUS = 480
ekraan = pygame.display.set_mode((LAIUS, KORGUS))
pygame.display.set_caption("Rally Mäng")
kell = pygame.time.Clock()

# ── VÄRVIKONSTANTID ──────────────────────────────────────────────────────────
VALGE = (255, 255, 255)
MUST = (0, 0, 0)

# ── PILTIDE LAADIMINE (kui fail puudub, kasutatakse värvilisi asenduspindu) ──
try:
    taust = pygame.image.load("bg_rally.jpg")
    taust = pygame.transform.scale(taust, (LAIUS, KORGUS))
except:
    taust = pygame.Surface((LAIUS, KORGUS))
    taust.fill((50, 150, 50))

try:
    punane_auto = pygame.image.load("f1_red.png")
    punane_auto = pygame.transform.scale(punane_auto, (60, 100))
except:
    punane_auto = pygame.Surface((60, 100))
    punane_auto.fill((255, 0, 0))

try:
    sinine_auto = pygame.image.load("f1_blue.png")
    sinine_auto = pygame.transform.scale(sinine_auto, (60, 100))
    sinine_auto = pygame.transform.rotate(sinine_auto, 180)  # pööra õiget pidi
except:
    sinine_auto = pygame.Surface((60, 100))
    sinine_auto.fill((0, 0, 255))

# ── TEE PAIGUTUS JA KOLM RIDA ────────────────────────────────────────────────
TEE_VASAK = 150
TEE_PAREM = 490
AUTO_LAIUS = 60
AUTO_KORGUS = 100
TURVA_VAHE = 20

RADADE_ARV = 3
RADA_LAIUS = (TEE_PAREM - TEE_VASAK) // RADADE_ARV

RADA_X = [
    TEE_VASAK + i * RADA_LAIUS + (RADA_LAIUS - AUTO_LAIUS) // 2
    for i in range(RADADE_ARV)
]

# ── KIIRUS – kõik autod sõidavad alati sama kiirusega ───────────────────────
KIIRUS = 5

# ── MÄNGIJA AUTO – paigal kesk-rajal ────────────────────────────────────────
punane_x = RADA_X[1]
punane_y = KORGUS - 120

# ── VASTASTE AUTODE LOOMINE ──────────────────────────────────────────────────
# Autod saavad juhusliku algpositsiooni – muster on iga kord erinev
SINISTE_ARV = 4

def loo_sinine_auto(rada):
    """Loob sinise auto kindlal rajal juhusliku y-positsiooniga."""
    return {
        "x": RADA_X[rada],
        "y": random.randint(-500, -80),
        "kiirus": KIIRUS,
        "rada": rada
    }

# Loome autod ja tagame, et sama raja autod ei spawni üksteise peale
sinised_autod = []
for rada in [0, 1, 2, 0]:
    auto = loo_sinine_auto(rada)
    for teine in sinised_autod:
        if teine["rada"] == auto["rada"]:
            if abs(auto["y"] - teine["y"]) < AUTO_KORGUS + TURVA_VAHE:
                auto["y"] = teine["y"] - AUTO_KORGUS - TURVA_VAHE - random.randint(0, 150)
    sinised_autod.append(auto)

# ── SKOOR ────────────────────────────────────────────────────────────────────
skoor = 0
font = pygame.font.SysFont("Arial", 28, bold=True)

def kuva_skoor():
    tekst = font.render("Skoor: " + str(skoor), True, VALGE)
    varjutekst = font.render("Skoor: " + str(skoor), True, MUST)
    ekraan.blit(varjutekst, (12, 12))
    ekraan.blit(tekst, (10, 10))

# ── PEAMÄNGUSIL (50 FPS) ─────────────────────────────────────────────────────
while True:
    kell.tick(50)

    # ── SÜNDMUSTE TÖÖTLUS ────────────────────────────────────────────────────
    for sundmus in pygame.event.get():
        if sundmus.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # ── VASTASTE LIIKUMINE ───────────────────────────────────────────────────
    for auto in sinised_autod:
        auto["y"] += KIIRUS

        # ── TAASKÄIVITUS – juhuslik spawn, mitte alati sama koht ────────────
        if auto["y"] > KORGUS:
            skoor += 1
            auto["y"] = random.randint(-400, -80)

            # Lükkame kaugemale üles, kui sama raja auto on liiga lähedal
            for teine in sinised_autod:
                if teine is not auto and teine["rada"] == auto["rada"]:
                    if auto["y"] + AUTO_KORGUS + TURVA_VAHE > teine["y"]:
                        auto["y"] = teine["y"] - AUTO_KORGUS - TURVA_VAHE

    # ── JOONISTAMINE (taust → vastased → mängija → UI) ───────────────────────
    ekraan.blit(taust, (0, 0))

    for auto in sinised_autod:
        ekraan.blit(sinine_auto, (auto["x"], auto["y"]))

    ekraan.blit(punane_auto, (punane_x, punane_y))

    kuva_skoor()

    pygame.display.flip()