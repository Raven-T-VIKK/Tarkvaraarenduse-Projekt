wimport pygame, sys, random

pygame.init()

# Värvid
red = [255, 0, 0]
green = [0, 255, 0]
blue = [0, 0, 255]
pink = [255, 153, 255]
lGreen = [153, 255, 153]
lBlue = [153, 204, 255]
white = [255, 255, 255]
yellow = [255, 220, 50]

# Ekraani seaded
screenX = 640
screenY = 480
screen = pygame.display.set_mode([screenX, screenY])
pygame.display.set_caption("Animeerimine - sissejuhatav ülesanne")
screen.fill(lBlue)
clock = pygame.time.Clock()

# --- PALL (kujund, mitte pilt) ---
ballSize = 30
ballX, ballY = 100, 100
speedX, speedY = 4, 3

# --- LANGEVAD RUUDUD ---
# Iga ruut on [x, y, kiirus, suurus, värv]
vaervid = [red, green, pink, yellow, white]
ruudud = []
for i in range(15):
    x = random.randint(0, screenX - 20)
    y = random.randint(-screenY, 0)   # algavad ekraanist üleval
    kiirus = random.randint(1, 5)
    suurus = random.randint(10, 25)
    varv = random.choice(vaervid)
    ruudud.append([x, y, kiirus, suurus, varv])

gameover = False
while not gameover:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    # Taustavärv
    screen.fill(lBlue)

    # --- Joonista ja liigu pall ---
    pygame.draw.circle(screen, blue, (int(ballX), int(ballY)), ballSize)
    # Highlight pallil
    pygame.draw.circle(screen, white, (int(ballX) - 8, int(ballY) - 8), 7)

    ballX += speedX
    ballY += speedY

    # Põrkamine äärtest (arvestab palli suurust)
    if ballX + ballSize >= screenX or ballX - ballSize <= 0:
        speedX = -speedX
        ballX = max(ballSize, min(ballX, screenX - ballSize))

    if ballY + ballSize >= screenY or ballY - ballSize <= 0:
        speedY = -speedY
        ballY = max(ballSize, min(ballY, screenY - ballSize))

    # --- Joonista ja liigu langevad ruudud ---
    for i in range(len(ruudud)):
        x, y, kiirus, suurus, varv = ruudud[i]
        pygame.draw.rect(screen, varv, [x, y, suurus, suurus])

        ruudud[i][1] += kiirus   # liigub alla

        # Kui jõuab alla, alustab uuesti ülevalt
        if ruudud[i][1] > screenY:
            ruudud[i][1] = random.randint(-60, -10)
            ruudud[i][0] = random.randint(0, screenX - suurus)

    pygame.display.flip()

pygame.quit()