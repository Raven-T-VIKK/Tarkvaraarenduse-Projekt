import pygame
import random

# ── MÄNGU KÄIVITAMINE JA AKNA SEADISTAMINE ──────────────────────────────────
pygame.init()

screenX = 640
screenY = 480
screen = pygame.display.set_mode([screenX, screenY])
pygame.display.set_caption("Kokkupõrke tuvastamine")
clock = pygame.time.Clock()

# ── VÄRVIKONSTANTID ──────────────────────────────────────────────────────────
red    = [255, 0, 0]
green  = [0, 255, 0]
blue   = [0, 0, 255]
pink   = [255, 153, 255]
lGreen = [153, 255, 153]
lBlue  = [153, 204, 255]
VALGE  = (255, 255, 255)
MUST   = (0, 0, 0)

screen.fill(lBlue)

# ── MÄNGIJA – Rect määrab asukoha ja suuruse, pilt laaditakse sisse ──────────
posX, posY     = 0, 0
speedX, speedY = 3, 4

player = pygame.Rect(posX, posY, 120, 140)

try:
    playerImage = pygame.image.load("Mängija.png")
    playerImage = pygame.transform.scale(playerImage, [player.width, player.height])
    playerImage.set_colorkey((0, 0, 0))
except:
    playerImage = pygame.Surface([player.width, player.height])
    playerImage.fill(green)

# ── VAENLASED – 5 juhuslikku Rect objekti ekraanil ──────────────────────────
enemies = []
for i in range(5):
    enemies.append(pygame.Rect(
        random.randint(0, screenX - 100),
        random.randint(0, screenY - 100),
        60, 73
    ))

try:
    enemyImage = pygame.image.load("Vaenlane.png")
    enemyImage = pygame.transform.scale(enemyImage, [enemies[0].width, enemies[0].height])
    enemyImage.set_colorkey((0, 0, 0))
except:
    enemyImage = pygame.Surface([enemies[0].width, enemies[0].height])
    enemyImage.fill(red)

# ── SKOOR JA FONT ─────────────────────────────────────────────────────────────
# Skoor kuvatakse ekraanil
score = 0
font  = pygame.font.SysFont("Arial", 28, bold=True)

def kuva_skoor():
    tekst     = font.render("Skoor: " + str(score), True, VALGE)
    varjutekst = font.render("Skoor: " + str(score), True, MUST)
    screen.blit(varjutekst, (12, 12))
    screen.blit(tekst,      (10, 10))

# ── VAENLASTE LOENDUR ────────────────────────────────────────────────────────
# totalEnemies määrab mitu kaadrit ootab enne uut vaenlast (suurem = aeglasem)
enemyCounter = 0
totalEnemies = 150  # 60 FPS juures ≈ iga 2,5 sekundi tagant uus vaenlane

# ── PEAMÄNGUSIL (60 FPS) ─────────────────────────────────────────────────────
gameover = False
while not gameover:
    clock.tick(60)

    # ── SÜNDMUSTE TÖÖTLUS ────────────────────────────────────────────────────
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        break

    # ── MÄNGIJA LIIKUMINE JA PÕRKAMINE SEINTELT ──────────────────────────────
    player = pygame.Rect(posX, posY, 120, 140)

    posX += speedX
    posY += speedY

    if posX > screenX - playerImage.get_rect().width or posX < 0:
        speedX = -speedX
    if posY > screenY - playerImage.get_rect().height or posY < 0:
        speedY = -speedY

    # ── UUTE VAENLASTE LISAMINE ──────────────────────────────────────────────
    enemyCounter += 1
    if enemyCounter >= totalEnemies:
        enemyCounter = 0
        enemies.append(pygame.Rect(
            random.randint(0, screenX - 100),
            random.randint(0, screenY - 100),
            60, 73
        ))

    # ── KOKKUPÕRKE TUVASTAMINE ───────────────────────────────────────────────
    for enemy in enemies[:]:
        if player.colliderect(enemy):
            enemies.remove(enemy)
            score += 1

    # ── JOONISTAMINE (taust → vaenlased → mängija → UI) ──────────────────────
    for enemy in enemies:
        screen.blit(enemyImage, enemy)
    screen.blit(playerImage, player)
    kuva_skoor()

    pygame.display.flip()
    screen.fill(lBlue)

    # ── VÕIDUTINGIMUS ────────────────────────────────────────────────────────
    if score == 20:
        gameover = True

pygame.quit()