import pygame
import random

# ── MÄNGU KÄIVITAMINE JA AKNA SEADISTAMINE ──────────────────────────────────
# pygame.init() käivitab kõik PyGame moodulid
# display.set_mode() loob akna määratud laiuse ja kõrgusega
# set_caption() määrab akna pealkirja
pygame.init()

screenX = 640
screenY = 480
screen = pygame.display.set_mode([screenX, screenY])
pygame.display.set_caption("Kokkupõrke tuvastamine")
clock = pygame.time.Clock()

# ── VÄRVIKONSTANTID ──────────────────────────────────────────────────────────
# RGB värvid – igal värvil on punase, rohelise ja sinise väärtus (0–255)
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
# Rect objekt hoiab mängija koordinaate ja mõõtmeid – kasutatakse nii
# joonistamisel kui ka hiljem kokkupõrke tuvastamisel
# try/except tagab, et programm töötab ka siis, kui pildifail puudub
posX, posY     = 0, 0
speedX, speedY = 3, 4

player = pygame.Rect(posX, posY, 120, 140)

try:
    playerImage = pygame.image.load("Mängija.png")
    playerImage = pygame.transform.scale(playerImage, [player.width, player.height])
    playerImage.set_colorkey((0, 0, 0))  # must värv muutub läbipaistvaks
except:
    playerImage = pygame.Surface([player.width, player.height])
    playerImage.fill(green)

# ── VAENLASED – 5 juhuslikku Rect objekti ekraanil ──────────────────────────
# Loome loendi enemies[], kuhu lisame 5 Rect objekti juhuslikesse kohtadesse
# Iga Rect on 60×73 px suurune ja asub ekraanil suvalises kohas
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
    enemyImage.set_colorkey((0, 0, 0))  # must värv muutub läbipaistvaks
except:
    enemyImage = pygame.Surface([enemies[0].width, enemies[0].height])
    enemyImage.fill(red)

# ── SKOOR JA FONT ─────────────────────────────────────────────────────────────
# Skoor tõuseb iga kokkupõrke korral
# kuva_skoor() joonistab skoori varjuefektiga: must nihutatud tekst + valge peale
score = 0
font  = pygame.font.SysFont("Arial", 28, bold=True)

def kuva_skoor():
    tekst      = font.render("Skoor: " + str(score), True, VALGE)
    varjutekst = font.render("Skoor: " + str(score), True, MUST)
    screen.blit(varjutekst, (12, 12))
    screen.blit(tekst,      (10, 10))

# ── VAENLASTE LOENDUR ────────────────────────────────────────────────────────
# enemyCounter loeb kaadreid – kui jõuab totalEnemies piirini, lisatakse uus vaenlane
# totalEnemies = 150 tähendab 60 FPS juures ≈ iga 2,5 sekundi tagant uus vaenlane
enemyCounter = 0
totalEnemies = 150

# ── PEAMÄNGUSIL (60 FPS) ─────────────────────────────────────────────────────
# Kõik mängu loogika ja joonistamine toimub selles tsüklis
# clock.tick(60) piirab mängu kiirust 60 kaadri sekundis
gameover = False
while not gameover:
    clock.tick(60)

    # ── SÜNDMUSTE TÖÖTLUS ────────────────────────────────────────────────────
    # Kontrollime kas kasutaja on akna sulgenud – kui on, väljume tsüklist
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        break

    # ── MÄNGIJA LIIKUMINE JA PÕRKAMINE SEINTELT ──────────────────────────────
    # Loome Rect objekti uuesti iga kaader, et see vastaks uutele koordinaatidele
    # Lisame kiirusvektorid posX ja posY-le – mängija liigub diagonaalis
    # Kui mängija jõuab ekraani ääreni (arvestades pildi tegelikku laiust/kõrgust),
    # pööratakse vastav kiiruse suund ümber
    player = pygame.Rect(posX, posY, 120, 140)

    posX += speedX
    posY += speedY

    if posX > screenX - playerImage.get_rect().width or posX < 0:
        speedX = -speedX
    if posY > screenY - playerImage.get_rect().height or posY < 0:
        speedY = -speedY

    # ── UUTE VAENLASTE LISAMINE ──────────────────────────────────────────────
    # Iga kaadriga suureneb loendur ühe võrra
    # Kui loendur jõuab piirini, lisatakse enemies[] loendisse uus juhuslik vaenlane
    enemyCounter += 1
    if enemyCounter >= totalEnemies:
        enemyCounter = 0
        enemies.append(pygame.Rect(
            random.randint(0, screenX - 100),
            random.randint(0, screenY - 100),
            60, 73
        ))

    # ── KOKKUPÕRKE TUVASTAMINE ───────────────────────────────────────────────
    # Itereerime enemies[:] koopiat, et saaks originaalloendist turvaliselt kustutada
    # colliderect() tagastab True kui kaks Rect objekti kattuvad
    # Kokkupõrke korral eemaldatakse vaenlane loendist ja skoor tõuseb
    for enemy in enemies[:]:
        if player.colliderect(enemy):
            enemies.remove(enemy)
            score += 1

    # ── JOONISTAMINE (taust → vaenlased → mängija → UI) ──────────────────────
    # Joonistame kihiti: vaenlased alla, mängija peale, skoor kõige peale
    # blit() joonistab pildi ekraanile antud koordinaatidele
    for enemy in enemies:
        screen.blit(enemyImage, enemy)
    screen.blit(playerImage, player)
    kuva_skoor()

    # display.flip() kuvab kõik joonistatud objektid korraga ekraanile
    pygame.display.flip()
    # screen.fill() täidab tausta uuesti – kustutab eelmise kaadri objektid
    screen.fill(lBlue)

    # ── VÕIDUTINGIMUS ────────────────────────────────────────────────────────
    # Kui skoor jõuab 20-ni, lõpeb mängutsükkel ja programm sulgub
    if score == 20:
        gameover = True

pygame.quit()