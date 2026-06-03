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
except:
    sinine_auto = pygame.Surface((60, 100))
    sinine_auto.fill((0, 0, 255))

# ── TEE PAIGUTUS JA PIIRID ───────────────────────────────────────────────────
# Mängija auto ei saa neist piiridest välja sõita
TEE_VASAK = 150
TEE_PAREM = 490
AUTO_LAIUS = 60

# ── MÄNGIJA AUTO ALGPOSITSIOON ───────────────────────────────────────────────
# Paigutatakse ekraani allossa horisontaalselt keskele
punane_x = LAIUS // 2 - AUTO_LAIUS // 2
punane_y = KORGUS - 120

# ── VASTASTE AUTODE LOOMINE ──────────────────────────────────────────────────
# Iga auto saab juhusliku x-asukoha teel ja negatiivse y (tuleb ülevalt)
SINISTE_ARV = 4

def loo_sinine_auto(indeks):
    """Loob uue sinise auto juhuslikul positsioonil teel."""
    x = random.randint(TEE_VASAK, TEE_PAREM - AUTO_LAIUS)
    y = -100 - indeks * 120  # Alustavad erinevatelt kõrgustelt
    kiirus = random.randint(3, 7)
    return {"x": x, "y": y, "kiirus": kiirus}

sinised_autod = [loo_sinine_auto(i) for i in range(SINISTE_ARV)]

# ── SKOORI KUVAMINE ──────────────────────────────────────────────────────────
# Tekstile lisatakse must vari, et see oleks igal taustal loetav
skoor = 0
font = pygame.font.SysFont("Arial", 28, bold=True)

def kuva_skoor():
    tekst = font.render("Skoor: " + str(skoor), True, VALGE)
    varjutekst = font.render("Skoor: " + str(skoor), True, MUST)
    ekraan.blit(varjutekst, (12, 12))
    ekraan.blit(tekst, (10, 10))

# ── PEAMÄNGUSIL (käivitub iga kaadriga ~50 FPS) ──────────────────────────────
while True:
    kell.tick(50)

    # ── SÜNDMUSTE TÖÖTLUS (aken suletakse) ──────────────────────────────────
    for sundmus in pygame.event.get():
        if sundmus.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # ── VASTASTE LIIKUMINE JA SKOOR ──────────────────────────────────────────
    # Kui auto jõuab ekraani alla, loetakse see möödumiseks ja skoor tõuseb
    for auto in sinised_autod:
        auto["y"] += auto["kiirus"]
        if auto["y"] > KORGUS:
            skoor += 1
            auto["x"] = random.randint(TEE_VASAK, TEE_PAREM - AUTO_LAIUS)
            auto["y"] = random.randint(-200, -60)
            auto["kiirus"] = random.randint(3, 7)

    # ── JOONISTAMINE (järjekord on oluline: taust → vastased → mängija → UI) ─
    ekraan.blit(taust, (0, 0))

    for auto in sinised_autod:
        ekraan.blit(sinine_auto, (auto["x"], auto["y"]))

    ekraan.blit(punane_auto, (punane_x, punane_y))

    kuva_skoor()

    pygame.display.flip()