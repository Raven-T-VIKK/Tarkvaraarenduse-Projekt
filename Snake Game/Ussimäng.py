# -*- coding: utf-8 -*-

import pygame       # Mangumootor
import sys          # Susteemi funktsioonid
import random       # Juhuslike arvude genereerimine
import json         # Tulemuste salvestamine faili
import os           # Faili olemasolu kontroll
import math         # Matemaatilised funktsioonid

# --- KONSTANTID ---
LAIUS = 800             # Manguakna laius pikslites
KORGUS = 650            # Manguakna korgus pikslites
PANEEL_KORGUS = 80      # Info-paneeli korgus ekraani ulaosas

VALI_Y_ALGUS = PANEEL_KORGUS    # Manguvaljal ulapiir
VALI_Y_LOPP = KORGUS            # Manguvaljal alapiir
RUUT = 20                       # Ruudustiku suurus

VALI_LAIUS  = LAIUS // RUUT             # = 40 ruutu
VALI_KORGUS = (KORGUS - PANEEL_KORGUS) // RUUT  # = 28 ruutu

# --- VARVID (RGB) ---
MUST         = (0,   0,   0)
VALGE        = (255, 255, 255)
ROHELINE     = (34,  197, 94)    # Ussi keha
TUM_ROHELINE = (22,  163, 74)   # Ussi pea
PUNANE       = (239, 68,  68)   # Tavaline toit
HALL         = (107, 114, 128)  # Takistused/kivid
TUM_HALL     = (55,  65,  81)   # Taust
HELESININE   = (56,  189, 248)  # Boonustoit
KOLLANE      = (250, 204, 21)   # Tase / tekst
ROOSA        = (236, 72,  153)  # Boonuse taimer
TAUSTAVARV   = (17,  24,  39)   # Peamine taustavarv
PANEEL_VARV  = (30,  41,  59)   # Info-paneeli taustavarv
RUUDUSTIK    = (31,  41,  55)   # Ruudustiku joonte varv

# --- FAILID ---
TULEMUSTE_FAIL = "tulemused.json"   # Korgeimate tulemuste salvestuskoht

# -------------------------------------------------------
#  ABIEFUNKTSIOONID
# -------------------------------------------------------

def ruut_pikseliks(rx, ry):
    """Teisendab ruudustiku koordinaadid ekraanikoordinaatideks."""
    return rx * RUUT, VALI_Y_ALGUS + ry * RUUT


# -------------------------------------------------------
#  TAIUSTUS 5: KORGEIMATE TULEMUSTE TABEL
# -------------------------------------------------------

def laadi_tulemused():
    """Laeb korgeimad tulemused JSON-failist."""
    if os.path.exists(TULEMUSTE_FAIL):
        try:
            with open(TULEMUSTE_FAIL, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def salvesta_tulemused(nimekiri):
    """Salvestab top-5 tulemused JSON-faili."""
    nimekiri.sort(reverse=True)
    nimekiri = nimekiri[:5]
    with open(TULEMUSTE_FAIL, "w") as f:
        json.dump(nimekiri, f)
    return nimekiri


# -------------------------------------------------------
#  TAIUSTUS 4: HELIEFEKTID
# -------------------------------------------------------

def loo_heli_punkt(sagedus=880, kestus=0.05):
    """Loob luhikese 'ding' heli, kui uss soob toiduosakese."""
    try:
        import numpy as np
        n = int(pygame.mixer.get_init()[0] * kestus)
        t = np.linspace(0, kestus, n, False)
        laine = np.sin(2 * math.pi * sagedus * t) * 0.3
        laine[-n//4:] *= np.linspace(1, 0, n//4)
        heli_andmed = (laine * 32767).astype(np.int16)
        stereo = np.column_stack([heli_andmed, heli_andmed])
        return pygame.sndarray.make_sound(stereo)
    except Exception:
        return None


def loo_heli_surm():
    """Loob laskuva tooni heli, kui uss sureb."""
    try:
        import numpy as np
        kestus = 0.4
        n = int(pygame.mixer.get_init()[0] * kestus)
        sagedus = np.linspace(440, 110, n)
        laine = np.sin(2 * math.pi * np.cumsum(sagedus) / pygame.mixer.get_init()[0]) * 0.4
        laine[-n//3:] *= np.linspace(1, 0, n//3)
        heli_andmed = (laine * 32767).astype(np.int16)
        stereo = np.column_stack([heli_andmed, heli_andmed])
        return pygame.sndarray.make_sound(stereo)
    except Exception:
        return None


def loo_heli_boonus():
    """Loob erilise heli boonustoidu soomisel."""
    try:
        import numpy as np
        kestus = 0.15
        n = int(pygame.mixer.get_init()[0] * kestus)
        t = np.linspace(0, kestus, n, False)
        laine = (np.sin(2 * math.pi * 1047 * t) +
                 np.sin(2 * math.pi * 1319 * t)) * 0.2
        laine[-n//4:] *= np.linspace(1, 0, n//4)
        heli_andmed = (laine * 32767).astype(np.int16)
        stereo = np.column_stack([heli_andmed, heli_andmed])
        return pygame.sndarray.make_sound(stereo)
    except Exception:
        return None


# -------------------------------------------------------
#  MANGU POHIKLASS
# -------------------------------------------------------

class SnakeMang:
    """Peamine mangu klass, mis haldab kogu mangu loogikat ja renderdamist."""

    def __init__(self):
        """Initsialiseerimine: seadistab pygame, akna, fondid ja helid."""
        pygame.init()
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.heliefektid_olemas = True
        except Exception:
            self.heliefektid_olemas = False

        # Aken
        self.ekraan = pygame.display.set_mode((LAIUS, KORGUS))
        pygame.display.set_caption("Sinu-Moodi Ussimang")
        self.kell = pygame.time.Clock()

        # Fondid
        self.font_suur   = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_kesk   = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_vaike  = pygame.font.SysFont("Arial", 18)
        self.font_pisike = pygame.font.SysFont("Arial", 14)

        # Helid
        if self.heliefektid_olemas:
            self.heli_punkt  = loo_heli_punkt()
            self.heli_surm   = loo_heli_surm()
            self.heli_boonus = loo_heli_boonus()
        else:
            self.heli_punkt = self.heli_surm = self.heli_boonus = None

        # Tulemuste nimekiri
        self.parimad_tulemused = laadi_tulemused()
        self.lahesta_mang()

    # --------------------------------------------------
    #  MANGU LAHESTAMINE
    # --------------------------------------------------

    def lahesta_mang(self):
        """Lahestab koik mangu muutujad uue partii jaoks."""
        kesk_x = VALI_LAIUS  // 2
        kesk_y = VALI_KORGUS // 2
        self.uss = [
            (kesk_x,     kesk_y),
            (kesk_x - 1, kesk_y),
            (kesk_x - 2, kesk_y),
        ]
        self.suund     = (1, 0)
        self.uus_suund = (1, 0)

        # Skoor ja tase
        self.skoor  = 0
        self.tase   = 1
        self.kiirus = 8

        # Mangu olekud
        self.mang_kaib = False
        self.mang_labi = False
        self.paus      = False
        self.menuu     = True

        # TAIUSTUS 1: TASEMESUSTEEM
        self.toidud_soodud      = 0
        self.TOITU_TASEME_KOHTA = 5

        # TAIUSTUS 2: TAKISTUSED
        self.takistused = set()
        self.loo_takistused()

        # Tavaline toit
        self.toit = self.loo_toit_positsioon()

        # TAIUSTUS 3: BOONUSTOIT
        self.boonus_toit      = None
        self.boonus_taimer    = 0
        self.BOONUS_KESTUS    = 150
        self.BOONUS_INTERVALL = 300
        self.tiki_loendur     = 0

        # Animatsioonid
        self.animatsioonid = []

    # --------------------------------------------------
    #  TAIUSTUS 2: TAKISTUSTE GENEREERIMINE
    # --------------------------------------------------

    def loo_takistused(self):
        """Genereerib kivid manguvaljale. Rohkem kive korgematele tasemetele."""
        self.takistused = set()
        kivide_arv = self.tase * 3

        # Kaitstud ala ussi umber
        kesk_x = VALI_LAIUS  // 2
        kesk_y = VALI_KORGUS // 2
        kaitstud = set()
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                kaitstud.add((kesk_x + dx, kesk_y + dy))

        katsed = 0
        while len(self.takistused) < kivide_arv and katsed < 1000:
            katsed += 1
            x = random.randint(1, VALI_LAIUS  - 2)
            y = random.randint(1, VALI_KORGUS - 2)
            pos = (x, y)
            if pos not in kaitstud and pos not in self.takistused:
                self.takistused.add(pos)

    # --------------------------------------------------
    #  TOIDU POSITSIONEERIMINE
    # --------------------------------------------------

    def loo_toit_positsioon(self):
        """Loob uue toiduosakese positsiooni - mitte ussi ega kivi peal."""
        while True:
            x = random.randint(0, VALI_LAIUS  - 1)
            y = random.randint(0, VALI_KORGUS - 1)
            pos = (x, y)
            if (pos not in self.uss and
                pos not in self.takistused and
                pos != self.boonus_toit):
                return pos

    def loo_boonus_toit_positsioon(self):
        """Loob boonustoidu positsiooni."""
        while True:
            x = random.randint(0, VALI_LAIUS  - 1)
            y = random.randint(0, VALI_KORGUS - 1)
            pos = (x, y)
            if (pos not in self.uss and
                pos not in self.takistused and
                pos != self.toit):
                return pos

    # --------------------------------------------------
    #  SISENDI TOOTLEMINE
    # --------------------------------------------------

    def tootle_sundmused(self):
        """Loeb koik klaviatuurisundmused ja uuendab mangu olekut."""
        for sundmus in pygame.event.get():

            if sundmus.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if sundmus.type == pygame.KEYDOWN:

                # Menuu: vajuta SPACE et alustada
                if self.menuu:
                    if sundmus.key == pygame.K_SPACE:
                        self.menuu = False
                        self.mang_kaib = True
                    return

                # Mang labi: R = restart, Q = lopeta
                if self.mang_labi:
                    if sundmus.key == pygame.K_r:
                        self.lahesta_mang()
                        self.menuu = True
                    elif sundmus.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    return

                # Paus
                if sundmus.key == pygame.K_p:
                    self.paus = not self.paus

                # Liikumisklahvid
                if not self.paus:
                    if sundmus.key in (pygame.K_UP, pygame.K_w):
                        if self.suund != (0, 1):
                            self.uus_suund = (0, -1)
                    elif sundmus.key in (pygame.K_DOWN, pygame.K_s):
                        if self.suund != (0, -1):
                            self.uus_suund = (0, 1)
                    elif sundmus.key in (pygame.K_LEFT, pygame.K_a):
                        if self.suund != (1, 0):
                            self.uus_suund = (-1, 0)
                    elif sundmus.key in (pygame.K_RIGHT, pygame.K_d):
                        if self.suund != (-1, 0):
                            self.uus_suund = (1, 0)

    # --------------------------------------------------
    #  MANGU LOOGIKA UUENDAMINE
    # --------------------------------------------------

    def uuenda(self):
        """Liigutab ussi, kontrollib kokkuporkeId, haldab toitu ja boonuseid."""
        if not self.mang_kaib or self.paus or self.mang_labi:
            return

        self.tiki_loendur += 1
        self.suund = self.uus_suund

        # Ussi uue pea positsioon
        pea_x, pea_y = self.uss[0]
        uus_pea = (pea_x + self.suund[0], pea_y + self.suund[1])

        # Kokkuporke kontroll: seinad
        if not (0 <= uus_pea[0] < VALI_LAIUS and 0 <= uus_pea[1] < VALI_KORGUS):
            self.ussi_surm()
            return

        # Kokkuporke kontroll: enda keha
        if uus_pea in self.uss[1:]:
            self.ussi_surm()
            return

        # TAIUSTUS 2: Kokkuporke kontroll: kivi
        if uus_pea in self.takistused:
            self.ussi_surm()
            return

        # Lisa uus pea
        self.uss.insert(0, uus_pea)

        # Toidu soomine
        soi = False

        if uus_pea == self.toit:
            # Tavaline toit: +10 x tase punkti
            punktid = 10 * self.tase
            self.skoor += punktid
            self.toidud_soodud += 1
            self.lisa_animatsioon("+" + str(punktid), uus_pea, VALGE)
            self.toit = self.loo_toit_positsioon()
            soi = True
            if self.heli_punkt:
                self.heli_punkt.play()
            # TAIUSTUS 1: Taseme tous
            self.kontrolli_taseme_tousu()

        elif uus_pea == self.boonus_toit:
            # TAIUSTUS 3: Boonustoit: +50 x tase punkti
            punktid = 50 * self.tase
            self.skoor += punktid
            self.lisa_animatsioon("BOONUS +" + str(punktid) + "!", uus_pea, KOLLANE)
            self.boonus_toit = None
            self.boonus_taimer = 0
            soi = True
            if self.heli_boonus:
                self.heli_boonus.play()

        if not soi:
            self.uss.pop()  # Uss ei kasva, saba eemaldatakse

        # TAIUSTUS 3: Boonustoidu taimer
        if self.boonus_toit:
            self.boonus_taimer -= 1
            if self.boonus_taimer <= 0:
                self.boonus_toit = None

        # Boonustoidu ilmumine
        if (self.boonus_toit is None and
            self.tiki_loendur % self.BOONUS_INTERVALL == 0 and
            self.tiki_loendur > 0):
            self.boonus_toit   = self.loo_boonus_toit_positsioon()
            self.boonus_taimer = self.BOONUS_KESTUS

        # Uuenda animatsioone
        self.animatsioonid = [
            [tekst, x, y - 0.5, eluiga - 1, varv]
            for tekst, x, y, eluiga, varv in self.animatsioonid
            if eluiga > 0
        ]

    def kontrolli_taseme_tousu(self):
        """TAIUSTUS 1: Tostab taset iga TOITU_TASEME_KOHTA soomisel."""
        if self.toidud_soodud >= self.TOITU_TASEME_KOHTA:
            self.toidud_soodud = 0
            self.tase += 1
            self.kiirus = min(8 + self.tase * 2, 25)  # Kiirus kasvab, max 25
            self.lisa_animatsioon("TASE " + str(self.tase) + "!", (VALI_LAIUS//2, VALI_KORGUS//2), KOLLANE)
            self.loo_takistused()  # Uued kivid uue taseme jaoks

    def ussi_surm(self):
        """Kasitleb ussi surma ja salvestab tulemuse."""
        self.mang_kaib = False
        self.mang_labi = True
        if self.heli_surm:
            self.heli_surm.play()
        self.parimad_tulemused.append(self.skoor)
        self.parimad_tulemused = salvesta_tulemused(self.parimad_tulemused)

    def lisa_animatsioon(self, tekst, pos, varv=VALGE):
        """Lisab ujuva punktiteksti animatsiooni."""
        px, py = ruut_pikseliks(pos[0], pos[1])
        self.animatsioonid.append([tekst, px, float(py), 40, varv])

    # --------------------------------------------------
    #  JOONISTAMINE
    # --------------------------------------------------

    def joonista(self):
        """Joonistab kogu mangu ekraanile."""
        self.ekraan.fill(TAUSTAVARV)
        self.joonista_paneel()

        if self.menuu:
            self.joonista_menuu()
        elif self.mang_labi:
            self.joonista_mang_labi()
        else:
            self.joonista_manguvali()
            self.joonista_takistused()
            self.joonista_uss()
            self.joonista_toit()
            self.joonista_animatsioonid()
            if self.paus:
                self.joonista_paus()

        pygame.display.flip()

    def joonista_paneel(self):
        """Joonistab ulaosa info-paneeli: skoor, tase, rekord."""
        pygame.draw.rect(self.ekraan, PANEEL_VARV, (0, 0, LAIUS, PANEEL_KORGUS))
        pygame.draw.line(self.ekraan, ROHELINE, (0, PANEEL_KORGUS), (LAIUS, PANEEL_KORGUS), 2)

        skoor_tekst = self.font_kesk.render("Skoor: " + str(self.skoor), True, VALGE)
        self.ekraan.blit(skoor_tekst, (20, 25))

        tase_tekst = self.font_kesk.render("Tase: " + str(self.tase), True, KOLLANE)
        self.ekraan.blit(tase_tekst, (LAIUS//2 - tase_tekst.get_width()//2, 25))

        parim = max(self.parimad_tulemused) if self.parimad_tulemused else 0
        parim_tekst = self.font_vaike.render("Rekord: " + str(parim), True, HELESININE)
        self.ekraan.blit(parim_tekst, (LAIUS - parim_tekst.get_width() - 20, 15))

        kiirus_tekst = self.font_pisike.render("Kiirus: " + str(self.kiirus) + " FPS", True, HALL)
        self.ekraan.blit(kiirus_tekst, (LAIUS - kiirus_tekst.get_width() - 20, 45))

        # TAIUSTUS 3: Boonustaimer riba
        if self.boonus_toit and self.mang_kaib:
            protsent = self.boonus_taimer / self.BOONUS_KESTUS
            riba_laius = 120
            pygame.draw.rect(self.ekraan, MUST,  (LAIUS//2 - riba_laius//2, 48, riba_laius, 10), border_radius=5)
            pygame.draw.rect(self.ekraan, ROOSA, (LAIUS//2 - riba_laius//2, 48, int(riba_laius * protsent), 10), border_radius=5)
            b_tekst = self.font_pisike.render("Boonus!", True, ROOSA)
            self.ekraan.blit(b_tekst, (LAIUS//2 - b_tekst.get_width()//2, 60))

    def joonista_manguvali(self):
        """Joonistab manguvaljal ruudustiku."""
        for x in range(0, LAIUS, RUUT):
            pygame.draw.line(self.ekraan, RUUDUSTIK, (x, VALI_Y_ALGUS), (x, KORGUS))
        for y in range(VALI_Y_ALGUS, KORGUS, RUUT):
            pygame.draw.line(self.ekraan, RUUDUSTIK, (0, y), (LAIUS, y))

    def joonista_takistused(self):
        """TAIUSTUS 2: Joonistab kivid manguvaljale."""
        for (kx, ky) in self.takistused:
            px, py = ruut_pikseliks(kx, ky)
            pygame.draw.rect(self.ekraan, HALL,    (px+1, py+1, RUUT-2, RUUT-2), border_radius=3)
            pygame.draw.rect(self.ekraan, TUM_HALL,(px+1, py+1, RUUT-2, RUUT-2), 2, border_radius=3)
            pygame.draw.line(self.ekraan, TUM_HALL, (px+4, py+4), (px+RUUT-5, py+RUUT-5), 2)
            pygame.draw.line(self.ekraan, TUM_HALL, (px+RUUT-5, py+4), (px+4, py+RUUT-5), 2)

    def joonista_uss(self):
        """Joonistab ussi: pea silmadega, keha tuhmub saba poole."""
        for i, (ux, uy) in enumerate(self.uss):
            px, py = ruut_pikseliks(ux, uy)
            if i == 0:
                # Pea
                pygame.draw.rect(self.ekraan, TUM_ROHELINE, (px+1, py+1, RUUT-2, RUUT-2), border_radius=6)
                # Silmad
                suund = self.suund
                if suund == (1, 0):    silm1 = (px+14, py+5);  silm2 = (px+14, py+13)
                elif suund == (-1, 0): silm1 = (px+5,  py+5);  silm2 = (px+5,  py+13)
                elif suund == (0, -1): silm1 = (px+5,  py+5);  silm2 = (px+13, py+5)
                else:                  silm1 = (px+5,  py+14); silm2 = (px+13, py+14)
                pygame.draw.circle(self.ekraan, VALGE, silm1, 3)
                pygame.draw.circle(self.ekraan, VALGE, silm2, 3)
                pygame.draw.circle(self.ekraan, MUST,  silm1, 1)
                pygame.draw.circle(self.ekraan, MUST,  silm2, 1)
            else:
                # Keha - tuhmub saba poole
                heledus = max(100, 255 - i * 5)
                varv = (0, heledus, 0)
                pygame.draw.rect(self.ekraan, varv, (px+2, py+2, RUUT-4, RUUT-4), border_radius=4)

    def joonista_toit(self):
        """Joonistab tavatoidu (punane) ja boonustoidu (sinine, vilgub)."""
        # Tavaline toit
        px, py = ruut_pikseliks(*self.toit)
        suurus = RUUT//2 - 2 + int(math.sin(self.tiki_loendur * 0.2) * 2)
        pygame.draw.circle(self.ekraan, PUNANE, (px + RUUT//2, py + RUUT//2), suurus)

        # TAIUSTUS 3: Boonustoit
        if self.boonus_toit:
            bx, by = ruut_pikseliks(*self.boonus_toit)
            suurus_b = RUUT//2 - 1 + int(math.sin(self.tiki_loendur * 0.5) * 3)
            pygame.draw.circle(self.ekraan, HELESININE, (bx + RUUT//2, by + RUUT//2), suurus_b)
            pygame.draw.circle(self.ekraan, VALGE,      (bx + RUUT//2, by + RUUT//2), suurus_b + 2, 2)

    def joonista_animatsioonid(self):
        """Joonistab ujuvad punktitekstid."""
        for andmed in self.animatsioonid:
            tekst, x, y, eluiga, varv = andmed
            alpha = min(255, eluiga * 6)
            surf = self.font_vaike.render(tekst, True, varv)
            surf.set_alpha(alpha)
            self.ekraan.blit(surf, (int(x) - surf.get_width()//2, int(y)))

    def joonista_paus(self):
        """Kattab ekraani ja kuvab PAUS teksti."""
        kate = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)
        kate.fill((0, 0, 0, 160))
        self.ekraan.blit(kate, (0, 0))
        tekst = self.font_suur.render("PAUS", True, KOLLANE)
        self.ekraan.blit(tekst, (LAIUS//2 - tekst.get_width()//2, KORGUS//2 - 30))
        alitekst = self.font_vaike.render("Vajuta P jatkamiseks", True, VALGE)
        self.ekraan.blit(alitekst, (LAIUS//2 - alitekst.get_width()//2, KORGUS//2 + 30))

    def joonista_menuu(self):
        """Joonistab peamenuu juhiste ja tulemustega."""
        pealkiri = self.font_suur.render("SINU-MOODI USSIMANG", True, ROHELINE)
        self.ekraan.blit(pealkiri, (LAIUS//2 - pealkiri.get_width()//2, 100))

        ali = self.font_vaike.render("Viie taiustusega PyGame ussimang!", True, HALL)
        self.ekraan.blit(ali, (LAIUS//2 - ali.get_width()//2, 160))

        juhised = [
            ("Nooled / WASD", "- liikumine"),
            ("P",             "- paus"),
            ("R",             "- restart"),
            ("Q",             "- lopeta"),
        ]
        y = 210
        for klahv, kirjeldus in juhised:
            k_surf = self.font_vaike.render(klahv, True, KOLLANE)
            k_kirj = self.font_vaike.render(kirjeldus, True, VALGE)
            self.ekraan.blit(k_surf, (LAIUS//2 - 120, y))
            self.ekraan.blit(k_kirj, (LAIUS//2 - 20,  y))
            y += 30

        taiustused = [
            "1. Tasemesusteem - kiirus touseb iga 5 toiduosakese jarela",
            "2. Takistused - kivid muutuvad ohtlikumaks korgematele tasemetes",
            "3. Boonustoit - ajapiiranguga sinine toit (x5 punktid!)",
            "4. Heliefektid - helid soomisel ja surmisel",
            "5. Korgeimate tulemuste tabel - top 5 salvestatakse",
        ]
        y = 370
        t_pealk = self.font_vaike.render("Taiustused:", True, HELESININE)
        self.ekraan.blit(t_pealk, (LAIUS//2 - t_pealk.get_width()//2, y - 25))
        for t in taiustused:
            surf = self.font_pisike.render(t, True, HALL)
            self.ekraan.blit(surf, (LAIUS//2 - surf.get_width()//2, y))
            y += 22

        # TAIUSTUS 5: Korgeimad tulemused
        if self.parimad_tulemused:
            y += 10
            top_p = self.font_vaike.render("TOP 5 TULEMUSED:", True, KOLLANE)
            self.ekraan.blit(top_p, (LAIUS//2 - top_p.get_width()//2, y))
            y += 28
            for i, tulemus in enumerate(self.parimad_tulemused[:5]):
                varv = [KOLLANE, VALGE, HALL, HALL, HALL][i]
                t_surf = self.font_pisike.render("#" + str(i+1) + "  " + str(tulemus) + " punkti", True, varv)
                self.ekraan.blit(t_surf, (LAIUS//2 - t_surf.get_width()//2, y))
                y += 22

        # Vilkuv alustamisnupp
        aeg = pygame.time.get_ticks()
        if (aeg // 500) % 2 == 0:
            alusta = self.font_kesk.render("Vajuta SPACE alustamiseks", True, ROHELINE)
            self.ekraan.blit(alusta, (LAIUS//2 - alusta.get_width()//2, KORGUS - 55))

    def joonista_mang_labi(self):
        """Joonistab mang-labi ekraani tulemuse ja edetabeliga."""
        kate = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)
        kate.fill((0, 0, 0, 200))
        self.ekraan.blit(kate, (0, 0))

        pealkiri = self.font_suur.render("MANG LABI", True, PUNANE)
        self.ekraan.blit(pealkiri, (LAIUS//2 - pealkiri.get_width()//2, 120))

        skoor_t = self.font_kesk.render("Sinu skoor: " + str(self.skoor), True, KOLLANE)
        self.ekraan.blit(skoor_t, (LAIUS//2 - skoor_t.get_width()//2, 200))

        tase_t = self.font_vaike.render("Joudsid tasemeni: " + str(self.tase), True, VALGE)
        self.ekraan.blit(tase_t, (LAIUS//2 - tase_t.get_width()//2, 245))

        # TAIUSTUS 5: Korgeimate tulemuste tabel
        y = 300
        top_p = self.font_kesk.render("KORGEIMAD TULEMUSED", True, HELESININE)
        self.ekraan.blit(top_p, (LAIUS//2 - top_p.get_width()//2, y))
        y += 45
        for i, tulemus in enumerate(self.parimad_tulemused[:5]):
            varv = KOLLANE if i == 0 else VALGE
            t_surf = self.font_vaike.render("#" + str(i+1) + "  " + str(tulemus) + " punkti", True, varv)
            self.ekraan.blit(t_surf, (LAIUS//2 - t_surf.get_width()//2, y))
            y += 30

        r_surf = self.font_vaike.render("R - uus mang", True, ROHELINE)
        q_surf = self.font_vaike.render("Q - lopeta",   True, PUNANE)
        self.ekraan.blit(r_surf, (LAIUS//2 - 120, y + 20))
        self.ekraan.blit(q_surf, (LAIUS//2 + 20,  y + 20))

    # --------------------------------------------------
    #  POHISTSUKKEL
    # --------------------------------------------------

    def kaivita(self):
        """Mangu pohistsukkel: sundmused -> uuendus -> joonistamine -> kordus."""
        while True:
            self.tootle_sundmused()
            self.uuenda()
            self.joonista()
            self.kell.tick(self.kiirus if self.mang_kaib and not self.paus else 30)


# -------------------------------------------------------
#  PROGRAMMI KAIVITAMINE
# -------------------------------------------------------

if __name__ == "__main__":
    mang = SnakeMang()   # Loo mangu objekt
    mang.kaivita()        # Kaivita pohistsukkel