# -*- coding: utf-8 -*-

import pygame       # Mangumootor graafika ja helide jaoks
import sys          # Susteemi funktsioonid (programmist valjumine)
import random       # Juhuslike arvude genereerimine (toit, kivid)
import json         # Tulemuste salvestamine ja laadimine failist
import os           # Faili olemasolu kontroll kettal
import math         # Matemaatilised funktsioonid (sin, pi jne)

# --- KONSTANTID ---
LAIUS = 800             # Manguakna laius pikslites
KORGUS = 650            # Manguakna korgus pikslites
PANEEL_KORGUS = 80      # Info-paneeli korgus ekraani ulaosas

VALI_Y_ALGUS = PANEEL_KORGUS    # Manguvaljaku ulapiir (paneeli all)
VALI_Y_LOPP = KORGUS            # Manguvaljaku alapiir (akna alumine serv)
RUUT = 20                       # Uhe ruudustiku ruudu suurus pikslites

VALI_LAIUS  = LAIUS // RUUT             # Manguvaljaku laius ruutudes (= 40)
VALI_KORGUS = (KORGUS - PANEEL_KORGUS) // RUUT  # Manguvaljaku korgus ruutudes (= 28)

# --- VARVID (RGB) ---
MUST         = (0,   0,   0)     # Must varv (silmapupillid, taust)
VALGE        = (255, 255, 255)   # Valge varv (silmavalged, tekstid)
ROHELINE     = (34,  197, 94)    # Roheline varv (ussi keha)
TUM_ROHELINE = (22,  163, 74)    # Tume roheline (ussi pea)
PUNANE       = (239, 68,  68)    # Punane varv (tavaline toit)
HALL         = (107, 114, 128)   # Hall varv (takistused ja abitekstid)
TUM_HALL     = (55,  65,  81)    # Tume hall (kivide varjud ja jooned)
HELESININE   = (56,  189, 248)   # Hele sinine (boonustoit)
KOLLANE      = (250, 204, 21)    # Kollane (tase, animatsioonitekstid)
ROOSA        = (236, 72,  153)   # Roosa (boonuse taimeririba)
TAUSTAVARV   = (17,  24,  39)    # Peamine taustavarv (tume sinakashall)
PANEEL_VARV  = (30,  41,  59)    # Info-paneeli taustavarv
RUUDUSTIK    = (31,  41,  55)    # Ruudustiku joonte varv

# --- FAILID ---
TULEMUSTE_FAIL = "tulemused.json"   # Failinimi, kuhu korgeimad tulemused salvestatakse

# -------------------------------------------------------
#  ABIEFUNKTSIOONID
# -------------------------------------------------------

def ruut_pikseliks(rx, ry):
    """Teisendab ruudustiku koordinaadid ekraanikoordinaatideks."""
    return rx * RUUT, VALI_Y_ALGUS + ry * RUUT  # Arvutab piksli x ja y, arvestades paneeli korgust


# -------------------------------------------------------
#  TAIUSTUS 5: KORGEIMATE TULEMUSTE TABEL
# -------------------------------------------------------

def laadi_tulemused():
    """Laeb korgeimad tulemused JSON-failist."""
    if os.path.exists(TULEMUSTE_FAIL):  # Kontrollib, kas tulemustefail on olemas
        try:
            with open(TULEMUSTE_FAIL, "r") as f:  # Avab faili lugemiseks
                return json.load(f)  # Tagastab tulemuste nimekirja
        except Exception:
            pass  # Kui laadimine ebaonnestub, ignoreeritakse viga
    return []  # Tagastab tuhja nimekirja, kui faili pole


def salvesta_tulemused(nimekiri):
    """Salvestab top-5 tulemused JSON-faili."""
    nimekiri.sort(reverse=True)  # Sorteerib tulemused suurimast vaiksemani
    nimekiri = nimekiri[:5]      # Jatab alles ainult top 5 tulemust
    with open(TULEMUSTE_FAIL, "w") as f:  # Avab faili kirjutamiseks
        json.dump(nimekiri, f)   # Kirjutab tulemused JSON-formaadis faili
    return nimekiri              # Tagastab uuendatud nimekirja


# -------------------------------------------------------
#  TAIUSTUS 4: HELIEFEKTID
# -------------------------------------------------------

def loo_heli_punkt(sagedus=880, kestus=0.05):
    """Loob luhikese 'ding' heli, kui uss soob toiduosakese."""
    try:
        import numpy as np                                      # Numpy on vajalik heliandmete arvutamiseks
        n = int(pygame.mixer.get_init()[0] * kestus)           # Arvutab proovide arvu (sagedus * kestus)
        t = np.linspace(0, kestus, n, False)                   # Loob ajavektori helikujule
        laine = np.sin(2 * math.pi * sagedus * t) * 0.3        # Genereerib siinuslaine antud sagedusel
        laine[-n//4:] *= np.linspace(1, 0, n//4)               # Vaigistab laine lopus (fade out)
        heli_andmed = (laine * 32767).astype(np.int16)          # Teisendab ujukomaarvud 16-bitiseks heliks
        stereo = np.column_stack([heli_andmed, heli_andmed])    # Loob stereokanali (vasak + parem)
        return pygame.sndarray.make_sound(stereo)               # Tagastab pygame heliojekti
    except Exception:
        return None  # Kui numpy pole olemas, tagastab None


def loo_heli_surm():
    """Loob laskuva tooni heli, kui uss sureb."""
    try:
        import numpy as np                                                              # Numpy heliarvutusteks
        kestus = 0.4                                                                    # Heli kestus sekundites
        n = int(pygame.mixer.get_init()[0] * kestus)                                   # Proovide arv
        sagedus = np.linspace(440, 110, n)                                              # Sagedus langeb 440 Hz-lt 110 Hz-le
        laine = np.sin(2 * math.pi * np.cumsum(sagedus) / pygame.mixer.get_init()[0]) * 0.4  # Laskuv siinuslaine
        laine[-n//3:] *= np.linspace(1, 0, n//3)                                       # Vaigistab laine lopus
        heli_andmed = (laine * 32767).astype(np.int16)                                  # Teisendab 16-bitiseks
        stereo = np.column_stack([heli_andmed, heli_andmed])                            # Stereokanal
        return pygame.sndarray.make_sound(stereo)                                       # Tagastab heliojekti
    except Exception:
        return None  # Kui numpy pole, tagastab None


def loo_heli_boonus():
    """Loob erilise heli boonustoidu soomisel."""
    try:
        import numpy as np                                          # Numpy heliarvutusteks
        kestus = 0.15                                               # Heli kestus sekundites
        n = int(pygame.mixer.get_init()[0] * kestus)               # Proovide arv
        t = np.linspace(0, kestus, n, False)                       # Ajavektor
        laine = (np.sin(2 * math.pi * 1047 * t) +
                 np.sin(2 * math.pi * 1319 * t)) * 0.2             # Kahe sageduse (C6 + E6) liitlaine
        laine[-n//4:] *= np.linspace(1, 0, n//4)                   # Vaigistab laine lopus
        heli_andmed = (laine * 32767).astype(np.int16)              # Teisendab 16-bitiseks
        stereo = np.column_stack([heli_andmed, heli_andmed])        # Stereokanal
        return pygame.sndarray.make_sound(stereo)                   # Tagastab heliojekti
    except Exception:
        return None  # Kui numpy pole, tagastab None


# -------------------------------------------------------
#  MANGU POHIKLASS
# -------------------------------------------------------

class SnakeMang:
    """Peamine mangu klass, mis haldab kogu mangu loogikat ja renderdamist."""

    def __init__(self):
        """Initsialiseerimine: seadistab pygame, akna, fondid ja helid."""
        pygame.init()  # Initsialiseerimine: kaivitab koik pygame moodulid
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)  # Helimootoori seadistus
            self.heliefektid_olemas = True   # Heliefektid on kasutatavad
        except Exception:
            self.heliefektid_olemas = False  # Heliefektid pole saadaval (vea korral)

        # --- Akna loomine ---
        self.ekraan = pygame.display.set_mode((LAIUS, KORGUS))  # Loob manguakna ettemaaratud suurusega
        pygame.display.set_caption("Sinu-Moodi Ussimang")       # Seab akna pealkirja
        self.kell = pygame.time.Clock()                          # Loob kella FPS piiramiseks

        # --- Fondid ---
        self.font_suur   = pygame.font.SysFont("Arial", 48, bold=True)  # Suur font (pealkiri, "mang labi")
        self.font_kesk   = pygame.font.SysFont("Arial", 28, bold=True)  # Keskmine font (skoor, tase)
        self.font_vaike  = pygame.font.SysFont("Arial", 18)             # Vaike font (juhised, tulemused)
        self.font_pisike = pygame.font.SysFont("Arial", 14)             # Pisike font (kiirus, boonustekst)

        # --- Helide laadimine ---
        if self.heliefektid_olemas:
            self.heli_punkt  = loo_heli_punkt()   # Heli tavatoidu soomisel
            self.heli_surm   = loo_heli_surm()    # Heli ussi surmisel
            self.heli_boonus = loo_heli_boonus()  # Heli boonustoidu soomisel
        else:
            self.heli_punkt = self.heli_surm = self.heli_boonus = None  # Helid puuduvad

        # --- Tulemuste laadimine ---
        self.parimad_tulemused = laadi_tulemused()  # Laeb salvestatud parima tulemused failist
        self.lahesta_mang()                          # Initsialiseeriib mangu muutujad

    # --------------------------------------------------
    #  MANGU LAHESTAMINE
    # --------------------------------------------------

    def lahesta_mang(self):
        """Lahestab koik mangu muutujad uue partii jaoks."""
        kesk_x = VALI_LAIUS  // 2  # Ussi alguspositsioon: valjaku horisontaalkeskpunkt
        kesk_y = VALI_KORGUS // 2  # Ussi alguspositsioon: valjaku vertikaalkeskpunkt
        self.uss = [
            (kesk_x,     kesk_y),   # Ussi pea ruudustikus
            (kesk_x - 1, kesk_y),   # Ussi keha esimene lull
            (kesk_x - 2, kesk_y),   # Ussi saba
        ]
        self.suund     = (1, 0)  # Algsuund: paremale (x kasvab)
        self.uus_suund = (1, 0)  # Järgmine suund (uuendatakse klahvivajutusel)

        # --- Skoor ja tase ---
        self.skoor  = 0   # Mangija punktiskoor nullitakse
        self.tase   = 1   # Algtase on 1
        self.kiirus = 8   # Algkiirus (FPS)

        # --- Mangu olekumuutujad ---
        self.mang_kaib = False  # Mang ei ole veel alanud
        self.mang_labi = False  # Mang ei ole veel labi
        self.paus      = False  # Paus ei ole aktiveeritud
        self.menuu     = True   # Peamenuu on nhtav

        # --- TAIUSTUS 1: TASEMESUSTEEM ---
        self.toidud_soodud      = 0  # Soodud toiduosakeste loendur tasemet ousu jaoks
        self.TOITU_TASEME_KOHTA = 5  # Mitu toiduosakest on vaja taseme tousteks

        # --- TAIUSTUS 3: BOONUSTOIT — peab olema defineeritud ENNE toit loomist ---
        self.boonus_toit      = None  # Boonustoidu positsioon (None = pole valjal)
        self.boonus_taimer    = 0     # Boonustoidu jarejaargnud tikke
        self.BOONUS_KESTUS    = 150   # Boonustoidu eluiga tikkides
        self.BOONUS_INTERVALL = 300   # Mitu tikki boonustoiduosakeste ilmumiste vahel
        self.tiki_loendur     = 0     # Koguarv tikke alates mangu algusest

        # --- TAIUSTUS 2: TAKISTUSED ---
        self.takistused = set()   # Tuhja hulk kivide positsioonide jaoks
        self.loo_takistused()     # Genereerib kivid vastavalt tasemele

        # --- Tavaline toit (boonus_toit peab juba olemas olema!) ---
        self.toit = self.loo_toit_positsioon()  # Paigutab esimese toiduosakese

        # --- Animatsioonid ---
        self.animatsioonid = []  # Tuhja nimekiri ujuvatele punktitekstidele

    # --------------------------------------------------
    #  TAIUSTUS 2: TAKISTUSTE GENEREERIMINE
    # --------------------------------------------------

    def loo_takistused(self):
        """Genereerib kivid manguvaljale. Rohkem kive korgematele tasemetele."""
        self.takistused = set()        # Tuhjenab eelmised kivid
        kivide_arv = self.tase * 3    # Kivide arv suureneb tasemega (tase 1 = 3 kivi)

        # --- Kaitstud ala ussi umber (ei tohi kive paigutada) ---
        kesk_x = VALI_LAIUS  // 2  # Ussi alguspositsiooni x-koordinaat
        kesk_y = VALI_KORGUS // 2  # Ussi alguspositsiooni y-koordinaat
        kaitstud = set()           # Hulk kaitstud positsioonidest
        for dx in range(-3, 4):    # Kaib labi x-suunalised naabrid (3 ruutu igas suunas)
            for dy in range(-3, 4):                          # Kaib labi y-suunalised naabrid
                kaitstud.add((kesk_x + dx, kesk_y + dy))    # Lisab positsiooni kaitstud hulka

        katsed = 0  # Katseloendur lõpmatu tsükli vältimiseks
        while len(self.takistused) < kivide_arv and katsed < 1000:  # Kordab kuni kivide arv taytub
            katsed += 1                                              # Suurendab katseloenduri
            x = random.randint(1, VALI_LAIUS  - 2)                  # Juhuslik x-koordinaat (servi vaeldab)
            y = random.randint(1, VALI_KORGUS - 2)                  # Juhuslik y-koordinaat (servi vaeldab)
            pos = (x, y)                                             # Moodustab positsioonipaari
            if pos not in kaitstud and pos not in self.takistused:   # Kontrollib, et koht oleks vaba
                self.takistused.add(pos)                             # Lisab kivi positsiooni hulka

    # --------------------------------------------------
    #  TOIDU POSITSIONEERIMINE
    # --------------------------------------------------

    def loo_toit_positsioon(self):
        """Loob uue toiduosakese positsiooni - mitte ussi ega kivi peal."""
        while True:                                     # Kordab kuni sobiv koht leitud
            x = random.randint(0, VALI_LAIUS  - 1)     # Juhuslik x-koordinaat valjaku sees
            y = random.randint(0, VALI_KORGUS - 1)     # Juhuslik y-koordinaat valjaku sees
            pos = (x, y)                                # Moodustab positsioonipaari
            if (pos not in self.uss and                 # Toit ei tohi ilmuda ussi peal
                pos not in self.takistused and          # Toit ei tohi ilmuda kivi peal
                pos != self.boonus_toit):               # Toit ei tohi kattuda boonustoiduga
                return pos                              # Tagastab sobiva positsiooni

    def loo_boonus_toit_positsioon(self):
        """Loob boonustoidu positsiooni."""
        while True:                                     # Kordab kuni sobiv koht leitud
            x = random.randint(0, VALI_LAIUS  - 1)     # Juhuslik x-koordinaat valjaku sees
            y = random.randint(0, VALI_KORGUS - 1)     # Juhuslik y-koordinaat valjaku sees
            pos = (x, y)                                # Moodustab positsioonipaari
            if (pos not in self.uss and                 # Boonustoit ei tohi ilmuda ussi peal
                pos not in self.takistused and          # Boonustoit ei tohi ilmuda kivi peal
                pos != self.toit):                      # Boonustoit ei tohi kattuda tavatoliduga
                return pos                              # Tagastab sobiva positsiooni

    # --------------------------------------------------
    #  SISENDI TOOTLEMINE
    # --------------------------------------------------

    def tootle_sundmused(self):
        """Loeb koik klaviatuurisundmused ja uuendab mangu olekut."""
        for sundmus in pygame.event.get():  # Kaib labi koik ootel olevad sundmused

            if sundmus.type == pygame.QUIT:  # Kasutaja sulgeb akna
                pygame.quit()               # Lopetab pygame
                sys.exit()                  # Valjub programmist

            if sundmus.type == pygame.KEYDOWN:  # Klahvi vajutamise sundmus

                # --- Menuu olekus: ainult SPACE alustab ---
                if self.menuu:
                    if sundmus.key == pygame.K_SPACE:  # Tuhikuklahv alustab mangu
                        self.menuu = False              # Peidab menuu
                        self.mang_kaib = True           # Aktiveerib manguloogika
                    return  # Teisi klahve menuus ei toodelda

                # --- Mang labi olekus: R = restart, Q = lopeta ---
                if self.mang_labi:
                    if sundmus.key == pygame.K_r:       # R-klahv alustab uue mangu
                        self.lahesta_mang()             # Lahestab koik muutujad
                        self.menuu = True               # Naaseb menuu ekraanile
                    elif sundmus.key == pygame.K_q:     # Q-klahv lopetab programmi
                        pygame.quit()                   # Lopetab pygame
                        sys.exit()                      # Valjub programmist
                    return  # Teisi klahve mang-labi olekus ei toodelda

                # --- Paus klahv ---
                if sundmus.key == pygame.K_p:           # P-klahv lulitab pausi sisse/valja
                    self.paus = not self.paus            # Poorab pausi oleku umber

                # --- Liikumisklahvid (ainult kui paus pole) ---
                if not self.paus:
                    if sundmus.key in (pygame.K_UP, pygame.K_w):       # Ules nool voi W
                        if self.suund != (0, 1):                        # Ei saa otse alla liikudes ulespoole poorata
                            self.uus_suund = (0, -1)                    # Seab uue suuna: ules
                    elif sundmus.key in (pygame.K_DOWN, pygame.K_s):   # Alla nool voi S
                        if self.suund != (0, -1):                       # Ei saa otse ules liikudes allapoole poorata
                            self.uus_suund = (0, 1)                     # Seab uue suuna: alla
                    elif sundmus.key in (pygame.K_LEFT, pygame.K_a):   # Vasak nool voi A
                        if self.suund != (1, 0):                        # Ei saa otse paremale liikudes vasakule poorata
                            self.uus_suund = (-1, 0)                    # Seab uue suuna: vasakule
                    elif sundmus.key in (pygame.K_RIGHT, pygame.K_d):  # Parem nool voi D
                        if self.suund != (-1, 0):                       # Ei saa otse vasakule liikudes paremale poorata
                            self.uus_suund = (1, 0)                     # Seab uue suuna: paremale

    # --------------------------------------------------
    #  MANGU LOOGIKA UUENDAMINE
    # --------------------------------------------------

    def uuenda(self):
        """Liigutab ussi, kontrollib kokkuporkeId, haldab toitu ja boonuseid."""
        if not self.mang_kaib or self.paus or self.mang_labi:  # Ei uuenda kui mang ei kaibe
            return

        self.tiki_loendur += 1           # Suurendab tikke loenduri iga kaadriga
        self.suund = self.uus_suund      # Rakendab kasutaja valitud suuna

        # --- Ussi uue pea positsiooni arvutamine ---
        pea_x, pea_y = self.uss[0]                               # Voetakse praegune pea positsioon
        uus_pea = (pea_x + self.suund[0], pea_y + self.suund[1]) # Liigutab pead suuna vorra

        # --- Kokkuporke kontroll: seinad ---
        if not (0 <= uus_pea[0] < VALI_LAIUS and 0 <= uus_pea[1] < VALI_KORGUS):  # Pea laheb valjaku piiridest valja
            self.ussi_surm()  # Uss sureb
            return

        # --- Kokkuporke kontroll: enda keha ---
        if uus_pea in self.uss[1:]:  # Pea puutub oma kehaga (alates teisest lullist)
            self.ussi_surm()         # Uss sureb
            return

        # --- TAIUSTUS 2: Kokkuporke kontroll: kivi ---
        if uus_pea in self.takistused:  # Pea puutub kiviga
            self.ussi_surm()            # Uss sureb
            return

        # --- Lisa uus pea nimekirja ette ---
        self.uss.insert(0, uus_pea)  # Lisab uue pea ussi nimekirja algusesse

        # --- Toidu soomise kontroll ---
        soi = False  # Lipp: kas sel tikul soodi midagi?

        if uus_pea == self.toit:                                         # Uss joudes tavatoidu peale
            punktid = 10 * self.tase                                     # Punkte saadakse: 10 korrautatud tasemega
            self.skoor += punktid                                        # Lisab punktid skoorile
            self.toidud_soodud += 1                                      # Suurendab soodud toiduosakeste arvu
            self.lisa_animatsioon("+" + str(punktid), uus_pea, VALGE)   # Kuvab ujuva punktiteksti
            self.toit = self.loo_toit_positsioon()                       # Tekitab uue toidu uude kohta
            soi = True                                                   # Margib, et soodi
            if self.heli_punkt:                                          # Kui heli on olemas
                self.heli_punkt.play()                                   # Mängib toidusoomise heli
            self.kontrolli_taseme_tousu()                                # Kontrollib, kas tase touseb

        elif uus_pea == self.boonus_toit:                                        # Uss joudes boonustoidu peale
            punktid = 50 * self.tase                                             # Boonuspunktid: 50 korrautatud tasemega
            self.skoor += punktid                                                # Lisab punktid skoorile
            self.lisa_animatsioon("BOONUS +" + str(punktid) + "!", uus_pea, KOLLANE)  # Kuvab boonusteksti
            self.boonus_toit = None                                              # Eemaldab boonustoidu valjalt
            self.boonus_taimer = 0                                               # Nullib boonustaimer
            soi = True                                                           # Margib, et soodi
            if self.heli_boonus:                                                 # Kui heli on olemas
                self.heli_boonus.play()                                          # Mangib boonussoomise heli

        if not soi:
            self.uss.pop()  # Uss ei kasva: eemaldab saba viimase luli

        # --- TAIUSTUS 3: Boonustoidu taimer ---
        if self.boonus_toit:                      # Kui boonustoit on valjal
            self.boonus_taimer -= 1               # Vahendab taimerit iga tikiga
            if self.boonus_taimer <= 0:           # Kui taimer on nulli joudiod
                self.boonus_toit = None           # Boonustoit kaob valjalt

        # --- Boonustoidu ilmumine kindla intervalliga ---
        if (self.boonus_toit is None and                          # Boonustoit pole praegu valjal
            self.tiki_loendur % self.BOONUS_INTERVALL == 0 and   # Intervalliloendur on taytunud
            self.tiki_loendur > 0):                               # Mang on juba alanud
            self.boonus_toit   = self.loo_boonus_toit_positsioon()  # Tekitab boonustoidu uude kohta
            self.boonus_taimer = self.BOONUS_KESTUS                  # Seab boonustaimer

        # --- Animatsioonide uuendamine ---
        self.animatsioonid = [
            [tekst, x, y - 0.5, eluiga - 1, varv]               # Liigutab teksti ules ja vahendab eluiga
            for tekst, x, y, eluiga, varv in self.animatsioonid  # Kaib labi koik animatsioonid
            if eluiga > 0                                         # Eemaldab animatsioonid, mille eluiga on loppenud
        ]

    def kontrolli_taseme_tousu(self):
        """TAIUSTUS 1: Tostab taset iga TOITU_TASEME_KOHTA soomisel."""
        if self.toidud_soodud >= self.TOITU_TASEME_KOHTA:                                # Kui piisavalt toitu soodud
            self.toidud_soodud = 0                                                        # Nullib soodud toidud
            self.tase += 1                                                                # Tostab taset
            self.kiirus = min(8 + self.tase * 2, 25)                                     # Suurendab kiirust (max 25 FPS)
            self.lisa_animatsioon("TASE " + str(self.tase) + "!", (VALI_LAIUS//2, VALI_KORGUS//2), KOLLANE)  # Kuvab taseanimatsioon
            self.loo_takistused()                                                          # Genereerib uued kivid uuele tasemele

    def ussi_surm(self):
        """Kasitleb ussi surma ja salvestab tulemuse."""
        self.mang_kaib = False                                    # Peatab manguloogika
        self.mang_labi = True                                     # Aktiveerib mang-labi oleku
        if self.heli_surm:                                        # Kui surmaheliol olemas
            self.heli_surm.play()                                 # Mangib surmaheliol
        self.parimad_tulemused.append(self.skoor)                 # Lisab skoori tulemuste nimekirja
        self.parimad_tulemused = salvesta_tulemused(self.parimad_tulemused)  # Salvestab top-5 faili

    def lisa_animatsioon(self, tekst, pos, varv=VALGE):
        """Lisab ujuva punktiteksti animatsiooni."""
        px, py = ruut_pikseliks(pos[0], pos[1])              # Teisendab ruudustikukoord ekraanikoord
        self.animatsioonid.append([tekst, px, float(py), 40, varv])  # Lisab animatsiooni nimekirja (eluiga=40)

    # --------------------------------------------------
    #  JOONISTAMINE
    # --------------------------------------------------

    def joonista(self):
        """Joonistab kogu mangu ekraanile."""
        self.ekraan.fill(TAUSTAVARV)   # Taitab tausta pohivarviga
        self.joonista_paneel()          # Joonistab alati nhtava info-paneeli

        if self.menuu:                  # Kui menuu on aktiivne
            self.joonista_menuu()       # Kuvab peamenuu ekraani
        elif self.mang_labi:            # Kui mang on labi
            self.joonista_mang_labi()   # Kuvab mang-labi ekraani
        else:
            self.joonista_manguvali()   # Joonistab ruudustiku
            self.joonista_takistused()  # Joonistab kivid
            self.joonista_uss()         # Joonistab ussi
            self.joonista_toit()        # Joonistab toidu
            self.joonista_animatsioonid()  # Joonistab ujuvad tekstid
            if self.paus:               # Kui paus on aktiveeritud
                self.joonista_paus()    # Kuvab pausi ulekattes

        pygame.display.flip()  # Uuendab ekraani (kuvab kaadri)

    def joonista_paneel(self):
        """Joonistab ulaosa info-paneeli: skoor, tase, rekord."""
        pygame.draw.rect(self.ekraan, PANEEL_VARV, (0, 0, LAIUS, PANEEL_KORGUS))               # Joonistab paneeli taust
        pygame.draw.line(self.ekraan, ROHELINE, (0, PANEEL_KORGUS), (LAIUS, PANEEL_KORGUS), 2) # Joonistab rohelise eraldusjoone

        skoor_tekst = self.font_kesk.render("Skoor: " + str(self.skoor), True, VALGE)          # Renderdab skooriteksit
        self.ekraan.blit(skoor_tekst, (20, 25))                                                  # Kuvab skoori vasakul

        tase_tekst = self.font_kesk.render("Tase: " + str(self.tase), True, KOLLANE)           # Renderdab taseteksti
        self.ekraan.blit(tase_tekst, (LAIUS//2 - tase_tekst.get_width()//2, 25))               # Kuvab tase keskel

        parim = max(self.parimad_tulemused) if self.parimad_tulemused else 0                    # Voetakse parim tulemus (voi 0)
        parim_tekst = self.font_vaike.render("Rekord: " + str(parim), True, HELESININE)        # Renderdab rekordteksti
        self.ekraan.blit(parim_tekst, (LAIUS - parim_tekst.get_width() - 20, 15))              # Kuvab rekord paremal

        kiirus_tekst = self.font_pisike.render("Kiirus: " + str(self.kiirus) + " FPS", True, HALL)  # Renderdab kiiruseteksti
        self.ekraan.blit(kiirus_tekst, (LAIUS - kiirus_tekst.get_width() - 20, 45))                 # Kuvab kiirus paremal all

        # --- TAIUSTUS 3: Boonustaimer riba ---
        if self.boonus_toit and self.mang_kaib:                                                          # Kuvab riba ainult siis kui boonustoit on valjal
            protsent = self.boonus_taimer / self.BOONUS_KESTUS                                           # Arvutab jarelajaanud aja protsendi
            riba_laius = 120                                                                              # Taieridriba laius pikslites
            pygame.draw.rect(self.ekraan, MUST,  (LAIUS//2 - riba_laius//2, 48, riba_laius, 10), border_radius=5)               # Joonistab taieridriba taust
            pygame.draw.rect(self.ekraan, ROOSA, (LAIUS//2 - riba_laius//2, 48, int(riba_laius * protsent), 10), border_radius=5)  # Joonistab jarelajaanud aja
            b_tekst = self.font_pisike.render("Boonus!", True, ROOSA)                                    # Renderdab boonusteksti
            self.ekraan.blit(b_tekst, (LAIUS//2 - b_tekst.get_width()//2, 60))                          # Kuvab boonusteksti taimerirba all

    def joonista_manguvali(self):
        """Joonistab manguvaljal ruudustiku."""
        for x in range(0, LAIUS, RUUT):                                           # Kaib labi vertikaalsed jooned
            pygame.draw.line(self.ekraan, RUUDUSTIK, (x, VALI_Y_ALGUS), (x, KORGUS))  # Joonistab vertikaalse ruudustikujoone
        for y in range(VALI_Y_ALGUS, KORGUS, RUUT):                              # Kaib labi horisontaalsed jooned
            pygame.draw.line(self.ekraan, RUUDUSTIK, (0, y), (LAIUS, y))         # Joonistab horisontaalse ruudustikujoone

    def joonista_takistused(self):
        """TAIUSTUS 2: Joonistab kivid manguvaljale."""
        for (kx, ky) in self.takistused:                                                              # Kaib labi koik kivi positsioonid
            px, py = ruut_pikseliks(kx, ky)                                                           # Teisendab ruudustikukoord pikseliteks
            pygame.draw.rect(self.ekraan, HALL,    (px+1, py+1, RUUT-2, RUUT-2), border_radius=3)    # Joonistab kivi hall taust
            pygame.draw.rect(self.ekraan, TUM_HALL,(px+1, py+1, RUUT-2, RUUT-2), 2, border_radius=3) # Joonistab kivi piirjoone
            pygame.draw.line(self.ekraan, TUM_HALL, (px+4, py+4), (px+RUUT-5, py+RUUT-5), 2)         # Joonistab kivi diagonaaljoone (tekstuur)
            pygame.draw.line(self.ekraan, TUM_HALL, (px+RUUT-5, py+4), (px+4, py+RUUT-5), 2)         # Joonistab kivi teise diagonaaljoone (tekstuur)

    def joonista_uss(self):
        """Joonistab ussi: pea silmadega, keha tuhmub saba poole."""
        for i, (ux, uy) in enumerate(self.uss):          # Kaib labi koik ussi lulid (i=0 on pea)
            px, py = ruut_pikseliks(ux, uy)              # Teisendab ruudustikukoord pikseliteks
            if i == 0:                                   # Esimene element on ussi pea
                pygame.draw.rect(self.ekraan, TUM_ROHELINE, (px+1, py+1, RUUT-2, RUUT-2), border_radius=6)  # Joonistab pea umara nelinurgana
                suund = self.suund                       # Voetakse praegune liikumissuund
                if suund == (1, 0):    silm1 = (px+14, py+5);  silm2 = (px+14, py+13)   # Silmade asukohad paremale liikudes
                elif suund == (-1, 0): silm1 = (px+5,  py+5);  silm2 = (px+5,  py+13)   # Silmade asukohad vasakule liikudes
                elif suund == (0, -1): silm1 = (px+5,  py+5);  silm2 = (px+13, py+5)    # Silmade asukohad ules liikudes
                else:                  silm1 = (px+5,  py+14); silm2 = (px+13, py+14)   # Silmade asukohad alla liikudes
                pygame.draw.circle(self.ekraan, VALGE, silm1, 3)   # Joonistab vasaku silmavalge
                pygame.draw.circle(self.ekraan, VALGE, silm2, 3)   # Joonistab parema silmavalge
                pygame.draw.circle(self.ekraan, MUST,  silm1, 1)   # Joonistab vasaku pupilli
                pygame.draw.circle(self.ekraan, MUST,  silm2, 1)   # Joonistab parema pupilli
            else:
                heledus = max(100, 255 - i * 5)                     # Keha heledus vahendub saba poole (min 100)
                varv = (0, heledus, 0)                               # Roheline varv, mille heledus soltub positsioonist
                pygame.draw.rect(self.ekraan, varv, (px+2, py+2, RUUT-4, RUUT-4), border_radius=4)  # Joonistab kehaluli umara nelinurgana

    def joonista_toit(self):
        """Joonistab tavatoidu (punane) ja boonustoidu (sinine, vilgub)."""
        px, py = ruut_pikseliks(*self.toit)                                                         # Teisendab tavatoidu koordinaadid pikseliteks
        suurus = RUUT//2 - 2 + int(math.sin(self.tiki_loendur * 0.2) * 2)                          # Animeeritud suurus (pulss-efekt siinusega)
        pygame.draw.circle(self.ekraan, PUNANE, (px + RUUT//2, py + RUUT//2), suurus)              # Joonistab punase toiduosakese

        if self.boonus_toit:                                                                         # Kui boonustoit on valjal
            bx, by = ruut_pikseliks(*self.boonus_toit)                                              # Teisendab boonustoidu koordinaadid pikseliteks
            suurus_b = RUUT//2 - 1 + int(math.sin(self.tiki_loendur * 0.5) * 3)                    # Kiirem pulss-animatsioon boonustoidule
            pygame.draw.circle(self.ekraan, HELESININE, (bx + RUUT//2, by + RUUT//2), suurus_b)    # Joonistab sinise boonustoidu
            pygame.draw.circle(self.ekraan, VALGE,      (bx + RUUT//2, by + RUUT//2), suurus_b + 2, 2)  # Joonistab valge raam boonustoidu umber

    def joonista_animatsioonid(self):
        """Joonistab ujuvad punktitekstid."""
        for andmed in self.animatsioonid:                              # Kaib labi koik aktiivsed animatsioonid
            tekst, x, y, eluiga, varv = andmed                        # Lahutab animatsiooni andmed
            alpha = min(255, eluiga * 6)                               # Arvutab labilasklikkuse (tuhmub lopus)
            surf = self.font_vaike.render(tekst, True, varv)          # Renderdab teksti pinnale
            surf.set_alpha(alpha)                                      # Seab labilasklikkuse
            self.ekraan.blit(surf, (int(x) - surf.get_width()//2, int(y)))  # Kuvab teksti ekraanile tsentreeritult

    def joonista_paus(self):
        """Kattab ekraani ja kuvab PAUS teksti."""
        kate = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)        # Loob poollabipaistev katepind
        kate.fill((0, 0, 0, 160))                                       # Taitab must poollabipaistev kattega
        self.ekraan.blit(kate, (0, 0))                                  # Kuvab katte kogu ekraanil
        tekst = self.font_suur.render("PAUS", True, KOLLANE)           # Renderdab "PAUS" teksti
        self.ekraan.blit(tekst, (LAIUS//2 - tekst.get_width()//2, KORGUS//2 - 30))   # Kuvab teksti ekraani keskel
        alitekst = self.font_vaike.render("Vajuta P jatkamiseks", True, VALGE)        # Renderdab juhisteksti
        self.ekraan.blit(alitekst, (LAIUS//2 - alitekst.get_width()//2, KORGUS//2 + 30))  # Kuvab juhis peateksti all

    def joonista_menuu(self):
        """Joonistab peamenuu juhiste ja tulemustega."""
        pealkiri = self.font_suur.render("SINU-MOODI USSIMANG", True, ROHELINE)            # Renderdab peakirja
        self.ekraan.blit(pealkiri, (LAIUS//2 - pealkiri.get_width()//2, 100))              # Kuvab peakiri ekraani ulosas keskel

        ali = self.font_vaike.render("Viie taiustusega PyGame ussimang!", True, HALL)      # Renderdab alapeakirja
        self.ekraan.blit(ali, (LAIUS//2 - ali.get_width()//2, 160))                        # Kuvab alapealkiri peakirja all

        juhised = [                              # Nimekiri klahv-kirjeldus paaridest
            ("Nooled / WASD", "- liikumine"),    # Liikumisklahvid
            ("P",             "- paus"),          # Paus klahv
            ("R",             "- restart"),       # Restart klahv
            ("Q",             "- lopeta"),        # Lopeta klahv
        ]
        y = 210                                  # Juhiste algus y-koordinaat
        for klahv, kirjeldus in juhised:         # Kaib labi koik juhised
            k_surf = self.font_vaike.render(klahv, True, KOLLANE)        # Renderdab klahvi nimetuse kollaselt
            k_kirj = self.font_vaike.render(kirjeldus, True, VALGE)      # Renderdab kirjelduse valgelt
            self.ekraan.blit(k_surf, (LAIUS//2 - 120, y))                # Kuvab klahvi nimi vasakul
            self.ekraan.blit(k_kirj, (LAIUS//2 - 20,  y))                # Kuvab kirjeldus paremal
            y += 30                                                        # Liigub jargneva juhise reale

        taiustused = [  # Nimekiri taiustuste kirjeldustest
            "1. Tasemesusteem - kiirus touseb iga 5 toiduosakese jarela",
            "2. Takistused - kivid muutuvad ohtlikumaks korgematele tasemetes",
            "3. Boonustoit - ajapiiranguga sinine toit (x5 punktid!)",
            "4. Heliefektid - helid soomisel ja surmisel",
            "5. Korgeimate tulemuste tabel - top 5 salvestatakse",
        ]
        y = 370                                                                      # Taiustuste sektsiooni algus
        t_pealk = self.font_vaike.render("Taiustused:", True, HELESININE)           # Renderdab "Taiustused:" peakirja
        self.ekraan.blit(t_pealk, (LAIUS//2 - t_pealk.get_width()//2, y - 25))     # Kuvab peakiri taiustuste kohal
        for t in taiustused:                                                          # Kaib labi koik taiustused
            surf = self.font_pisike.render(t, True, HALL)                           # Renderdab taiustuse teksti hallilt
            self.ekraan.blit(surf, (LAIUS//2 - surf.get_width()//2, y))             # Kuvab teksti tsentreeritult
            y += 22                                                                   # Liigub jargneva rea juurde

        # --- TAIUSTUS 5: Korgeimad tulemused menuus ---
        if self.parimad_tulemused:                                                   # Kuvab ainult siis kui tulemusi on
            y += 10                                                                   # Lisab vahe
            top_p = self.font_vaike.render("TOP 5 TULEMUSED:", True, KOLLANE)       # Renderdab sektsiooni peakirja
            self.ekraan.blit(top_p, (LAIUS//2 - top_p.get_width()//2, y))           # Kuvab peakiri tsentreeritult
            y += 28                                                                   # Liigub tulemuste loendi juurde
            for i, tulemus in enumerate(self.parimad_tulemused[:5]):                 # Kaib labi top-5 tulemused
                varv = [KOLLANE, VALGE, HALL, HALL, HALL][i]                        # Esimene tulemus on kollane, ulejainud valge/hall
                t_surf = self.font_pisike.render("#" + str(i+1) + "  " + str(tulemus) + " punkti", True, varv)  # Renderdab tulemuse teksti
                self.ekraan.blit(t_surf, (LAIUS//2 - t_surf.get_width()//2, y))     # Kuvab tulemus tsentreeritult
                y += 22                                                               # Liigub jargneva tulemuse reale

        # --- Vilkuv alustamisnupp ---
        aeg = pygame.time.get_ticks()                                                # Voetakse praegune aeg millisekundites
        if (aeg // 500) % 2 == 0:                                                    # Vilgub iga 500 ms tagant
            alusta = self.font_kesk.render("Vajuta SPACE alustamiseks", True, ROHELINE)  # Renderdab alustamisteksti
            self.ekraan.blit(alusta, (LAIUS//2 - alusta.get_width()//2, KORGUS - 55))   # Kuvab ekraani allosas keskel

    def joonista_mang_labi(self):
        """Joonistab mang-labi ekraani tulemuse ja edetabeliga."""
        kate = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)                         # Loob poollabipaistev pind
        kate.fill((0, 0, 0, 200))                                                        # Taitab tume poollabipaistev kattega
        self.ekraan.blit(kate, (0, 0))                                                   # Kuvab kate kogu ekraanil

        pealkiri = self.font_suur.render("MANG LABI", True, PUNANE)                     # Renderdab "MANG LABI" peakirja
        self.ekraan.blit(pealkiri, (LAIUS//2 - pealkiri.get_width()//2, 120))           # Kuvab pealkiri ekraani ulosas keskel

        skoor_t = self.font_kesk.render("Sinu skoor: " + str(self.skoor), True, KOLLANE)  # Renderdab lopptulemuse
        self.ekraan.blit(skoor_t, (LAIUS//2 - skoor_t.get_width()//2, 200))               # Kuvab lopptulemus keskel

        tase_t = self.font_vaike.render("Joudsid tasemeni: " + str(self.tase), True, VALGE)  # Renderdab tasemeteksti
        self.ekraan.blit(tase_t, (LAIUS//2 - tase_t.get_width()//2, 245))                    # Kuvab tase tekst skoori all

        # --- TAIUSTUS 5: Korgeimate tulemuste tabel mang-labi ekraanil ---
        y = 300                                                                              # Tulemuste sektsiooni algus
        top_p = self.font_kesk.render("KORGEIMAD TULEMUSED", True, HELESININE)             # Renderdab sektsiooni peakirja
        self.ekraan.blit(top_p, (LAIUS//2 - top_p.get_width()//2, y))                      # Kuvab peakirja tsentreeritult
        y += 45                                                                              # Liigub tulemuste loendi juurde
        for i, tulemus in enumerate(self.parimad_tulemused[:5]):                            # Kaib labi top-5 tulemused
            varv = KOLLANE if i == 0 else VALGE                                             # Esimene tulemus kollane, ulejainud valge
            t_surf = self.font_vaike.render("#" + str(i+1) + "  " + str(tulemus) + " punkti", True, varv)  # Renderdab tulemuse rea
            self.ekraan.blit(t_surf, (LAIUS//2 - t_surf.get_width()//2, y))                # Kuvab tulemus tsentreeritult
            y += 30                                                                          # Liigub jargneva rea juurde

        r_surf = self.font_vaike.render("R - uus mang", True, ROHELINE)                    # Renderdab "uus mang" nupp
        q_surf = self.font_vaike.render("Q - lopeta",   True, PUNANE)                      # Renderdab "lopeta" nupp
        self.ekraan.blit(r_surf, (LAIUS//2 - 120, y + 20))                                 # Kuvab R-nupp vasakul
        self.ekraan.blit(q_surf, (LAIUS//2 + 20,  y + 20))                                 # Kuvab Q-nupp paremal

    # --------------------------------------------------
    #  POHISTSUKKEL
    # --------------------------------------------------

    def kaivita(self):
        """Mangu pohistsukkel: sundmused -> uuendus -> joonistamine -> kordus."""
        while True:                                                                    # Loimatu tsukkel kuni programmist valju
            self.tootle_sundmused()                                                    # Tootleb kasutaja sisendi
            self.uuenda()                                                              # Uuendab manguloogika
            self.joonista()                                                            # Joonistab kaadri ekraanile
            self.kell.tick(self.kiirus if self.mang_kaib and not self.paus else 30)   # Piirab FPS-i (mang: kiirus, muul juhul: 30)


# -------------------------------------------------------
#  PROGRAMMI KAIVITAMINE
# -------------------------------------------------------

if __name__ == "__main__":
    mang = SnakeMang()   # Loob mangu objekti ja initsialiseeriib koik
    mang.kaivita()        # Kaivitab pohistsuklilk1