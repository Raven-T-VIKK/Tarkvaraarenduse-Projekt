# -*- coding: utf-8 -*-
# Faili kodeering on UTF-8, et eesti tähed töötaksid korrektselt

import pygame       # Mängumootor graafika, helide ja sündmuste jaoks
import sys          # Süsteemifunktsioonid, kasutatakse programmist väljumiseks
import random       # Juhuslike arvude genereerimine toidu ja kivide asukohtade jaoks
import json         # JSON-formaadis andmete lugemine ja kirjutamine faili
import os           # Operatsioonisüsteemi funktsioonid, kasutatakse faili olemasolu kontrolliks
import math         # Matemaatilised funktsioonid, kasutatakse siinuslaine arvutamiseks

# --- KONSTANTID ---
LAIUS = 800             # Mänguakna laius pikslites
KORGUS = 650            # Mänguakna kõrgus pikslites
PANEEL_KORGUS = 80      # Ülaosas asuva info-paneeli kõrgus pikslites

VALI_Y_ALGUS = PANEEL_KORGUS    # Mänguväljakut algab paneeli alumisest servast
VALI_Y_LOPP = KORGUS            # Mänguväljak lõpeb akna alumise servaga
RUUT = 20                       # Ühe ruudustikulahtri suurus pikslites

VALI_LAIUS  = LAIUS // RUUT             # Mänguväljaku laius ruutudes (800/20 = 40)
VALI_KORGUS = (KORGUS - PANEEL_KORGUS) // RUUT  # Mänguväljaku kõrgus ruutudes (570/20 = 28)

# --- VÄRVID (RGB) ---
MUST         = (0,   0,   0)     # Must värv, kasutatakse pupillide ja tausta jaoks
VALGE        = (255, 255, 255)   # Valge värv, kasutatakse silmavalgete ja tekstide jaoks
ROHELINE     = (34,  197, 94)    # Roheline värv, kasutatakse ussi keha jaoks
TUM_ROHELINE = (22,  163, 74)    # Tume roheline, kasutatakse ussi pea jaoks
PUNANE       = (239, 68,  68)    # Punane värv, kasutatakse tavatoidu jaoks
HALL         = (107, 114, 128)   # Hall värv, kasutatakse kivide ja abitekstide jaoks
TUM_HALL     = (55,  65,  81)    # Tume hall, kasutatakse kivide varjude ja joonte jaoks
HELESININE   = (56,  189, 248)   # Hele sinine, kasutatakse boonustoidu jaoks
KOLLANE      = (250, 204, 21)    # Kollane värv, kasutatakse taseme ja animatsioonitekstide jaoks
ROOSA        = (236, 72,  153)   # Roosa värv, kasutatakse boonuse taimeririba jaoks
TAUSTAVARV   = (17,  24,  39)    # Peamine taustavärv, tume sinakashall
PANEEL_VARV  = (30,  41,  59)    # Info-paneeli taustavärv, veidi heledam kui taust
RUUDUSTIK    = (31,  41,  55)    # Ruudustiku joonte värv, peaaegu taustavärviga sama

TULEMUSTE_FAIL = "tulemused.json"   # Failinimi, kuhu kõrgeimad tulemused salvestatakse

LOOP_FPS = 60  # Mängutsükli maksimaalne kaadrisagedus — input loetakse alati 60x sekundis

# -------------------------------------------------------
#  ABIEFUNKTSIOONID
# -------------------------------------------------------

def ruut_pikseliks(rx, ry):
    # Teisendab ruudustiku x-koordinaadi ekraani piksliks, korrutades ruudu suurusega
    # Teisendab ruudustiku y-koordinaadi ekraani piksliks, lisades paneeli kõrguse nihke
    return rx * RUUT, VALI_Y_ALGUS + ry * RUUT


# -------------------------------------------------------
#  KÕRGEIMATE TULEMUSTE TABEL
# -------------------------------------------------------

def laadi_tulemused():
    # Kontrollib, kas tulemustefail on kettal olemas
    if os.path.exists(TULEMUSTE_FAIL):
        try:
            # Avab tulemustefaili lugemisrežiimis
            with open(TULEMUSTE_FAIL, "r") as f:
                # Loeb JSON-failist tulemuste nimekirja ja tagastab selle
                return json.load(f)
        except Exception:
            # Kui faili lugemine ebaõnnestub mingil põhjusel, jätkatakse vaikimisi väärtusega
            pass
    # Tagastab tühja nimekirja kui faili pole või lugemine ebaõnnestus
    return []


def salvesta_tulemused(nimekiri):
    # Sorteerib tulemused kahanevas järjekorras (suurim esimene)
    nimekiri.sort(reverse=True)
    # Jätab alles ainult viis parimat tulemust
    nimekiri = nimekiri[:5]
    # Avab tulemustefaili kirjutamisrežiimis (loob uue või kirjutab üle)
    with open(TULEMUSTE_FAIL, "w") as f:
        # Kirjutab tulemuste nimekirja JSON-formaadis faili
        json.dump(nimekiri, f)
    # Tagastab uuendatud top-5 nimekirja
    return nimekiri


# -------------------------------------------------------
#  HELIEFEKTID
# -------------------------------------------------------

def loo_heli_punkt(sagedus=880, kestus=0.05):
    try:
        import numpy as np                                      # Impordib numpy teegi heliandmete arvutamiseks
        n = int(pygame.mixer.get_init()[0] * kestus)           # Arvutab vajalike heliproovide koguarvu
        t = np.linspace(0, kestus, n, False)                   # Loob ühtlaselt jaotatud ajavektori
        laine = np.sin(2 * math.pi * sagedus * t) * 0.3        # Genereerib siinuslaine antud sagedusel, vaiksemaks skaleeritud
        laine[-n//4:] *= np.linspace(1, 0, n//4)               # Vaigistab laine viimase veerandi (fade out efekt)
        heli_andmed = (laine * 32767).astype(np.int16)          # Teisendab ujukomaarvud 16-bitiseks täisarvuks
        stereo = np.column_stack([heli_andmed, heli_andmed])    # Dubleerib mono heli stereo kanaliteks
        return pygame.sndarray.make_sound(stereo)               # Loob ja tagastab pygame helisobjekti
    except Exception:
        # Kui numpy pole paigaldatud, tagastab None (heli lihtsalt puudub)
        return None


def loo_heli_surm():
    try:
        import numpy as np                                                              # Impordib numpy teegi heliarvutusteks
        kestus = 0.4                                                                    # Määrab surmahelile 0.4 sekundit pikkuse
        n = int(pygame.mixer.get_init()[0] * kestus)                                   # Arvutab heliproovide arvu kestuse põhjal
        sagedus = np.linspace(440, 110, n)                                              # Loob sageduse, mis langeb 440 Hz-lt 110 Hz-le
        laine = np.sin(2 * math.pi * np.cumsum(sagedus) / pygame.mixer.get_init()[0]) * 0.4  # Genereerib laskuva kõrgusega siinuslaine
        laine[-n//3:] *= np.linspace(1, 0, n//3)                                       # Vaigistab laine viimase kolmandiku
        heli_andmed = (laine * 32767).astype(np.int16)                                  # Teisendab heliandmed 16-bitiseks formaadiks
        stereo = np.column_stack([heli_andmed, heli_andmed])                            # Loob stereokanali mono heli dubleerimisega
        return pygame.sndarray.make_sound(stereo)                                       # Tagastab pygame helisobjekti
    except Exception:
        # Kui numpy pole, tagastab None
        return None


def loo_heli_boonus():
    try:
        import numpy as np                                          # Impordib numpy teegi heliarvutusteks
        kestus = 0.15                                               # Määrab boonushelile 0.15 sekundit pikkuse
        n = int(pygame.mixer.get_init()[0] * kestus)               # Arvutab heliproovide arvu
        t = np.linspace(0, kestus, n, False)                       # Loob ajavektori helikujule
        laine = (np.sin(2 * math.pi * 1047 * t) +
                 np.sin(2 * math.pi * 1319 * t)) * 0.2             # Liidab kaks sagedust (C6 + E6) kokku, moodustades akordiheli
        laine[-n//4:] *= np.linspace(1, 0, n//4)                   # Vaigistab heli lõpus
        heli_andmed = (laine * 32767).astype(np.int16)              # Teisendab 16-bitiseks heliforMAAdiks
        stereo = np.column_stack([heli_andmed, heli_andmed])        # Loob stereokanali
        return pygame.sndarray.make_sound(stereo)                   # Tagastab pygame helisobjekti
    except Exception:
        # Kui numpy pole, tagastab None
        return None


# -------------------------------------------------------
#  MÄNGU PÕHIKLASS
# -------------------------------------------------------

class SnakeMang:
    # Defineerib peamise mänguklassi, mis haldab kogu loogikat ja joonistamist

    def __init__(self):
        # Käivitab kõik pygame moodulid (graafika, heli, jne)
        pygame.init()
        try:
            # Proovib helimootorit seadistada: 44100 Hz sagedus, 16-bitine, stereo, 512 puhver
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            # Märgib et heliefektid on edukalt käivitatud
            self.heliefektid_olemas = True
        except Exception:
            # Kui heli seadistamine ebaõnnestub, märgib et helisid pole
            self.heliefektid_olemas = False

        # Loob mänguakna määratud laiuse ja kõrgusega
        self.ekraan = pygame.display.set_mode((LAIUS, KORGUS))
        # Seab akna tiitliribale pealkirja
        pygame.display.set_caption("Sinu-Moodi Ussimang")
        # Loob kella, millega piiratakse mängu kaadrisagedust
        self.kell = pygame.time.Clock()

        # Loob suure fondi (48pt, rasvane) pealkirjade jaoks
        self.font_suur   = pygame.font.SysFont("Arial", 48, bold=True)
        # Loob keskmise fondi (28pt, rasvane) skoori ja taseme kuvamiseks
        self.font_kesk   = pygame.font.SysFont("Arial", 28, bold=True)
        # Loob väikese fondi (18pt) juhiste ja tulemuste kuvamiseks
        self.font_vaike  = pygame.font.SysFont("Arial", 18)
        # Loob pisikese fondi (14pt) kiiruse ja boonustekstide jaoks
        self.font_pisike = pygame.font.SysFont("Arial", 14)

        # Laeb helid ainult siis, kui heliefektid on saadaval
        if self.heliefektid_olemas:
            # Loob tavatoidu söömise heli
            self.heli_punkt  = loo_heli_punkt()
            # Loob ussi surma heli
            self.heli_surm   = loo_heli_surm()
            # Loob boonustoidu söömise heli
            self.heli_boonus = loo_heli_boonus()
        else:
            # Kui heli pole saadaval, määrab kõik helimuutujad väärtusele None
            self.heli_punkt = self.heli_surm = self.heli_boonus = None

        # Loob läbipaistva pinna ruudustiku eelrenderdamiseks
        self.ruudustik_surf = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)
        # Joonistab ruudustiku üks kord mällu (ei pea iga kaadrit uuesti joonistama)
        self._ehita_ruudustik()

        # Laeb eelmise mängu salvestatud parimad tulemused failist
        self.parimad_tulemused = laadi_tulemused()
        # Lähtestab kõik mängu muutujad uue mängu jaoks
        self.lahesta_mang()

    # --------------------------------------------------
    #  RUUDUSTIKU EELRENDERDAMINE
    # --------------------------------------------------

    def _ehita_ruudustik(self):
        # Täidab ruudustiku pinna läbipaistva värviga (tühjendab eelmise sisu)
        self.ruudustik_surf.fill((0, 0, 0, 0))
        # Käib läbi kõik vertikaalsete joonte x-positsioonid sammuga RUUT
        for x in range(0, LAIUS, RUUT):
            # Joonistab ühe vertikaalse ruudustikujoone ülevalt alla
            pygame.draw.line(self.ruudustik_surf, RUUDUSTIK, (x, VALI_Y_ALGUS), (x, KORGUS))
        # Käib läbi kõik horisontaalsete joonte y-positsioonid sammuga RUUT
        for y in range(VALI_Y_ALGUS, KORGUS, RUUT):
            # Joonistab ühe horisontaalse ruudustikujoone vasakult paremale
            pygame.draw.line(self.ruudustik_surf, RUUDUSTIK, (0, y), (LAIUS, y))

    # --------------------------------------------------
    #  MÄNGU LÄHTESTAMINE
    # --------------------------------------------------

    def lahesta_mang(self):
        # Arvutab väljakut horisontaalse keskpunkti ruutudes
        kesk_x = VALI_LAIUS  // 2
        # Arvutab väljakut vertikaalse keskpunkti ruutudes
        kesk_y = VALI_KORGUS // 2
        # Loob ussi algoleku kolme lüliga: pea, keha, saba
        self.uss = [
            (kesk_x,     kesk_y),   # Ussi pea asub väljakut keskel
            (kesk_x - 1, kesk_y),   # Esimene kehalüli on peast ühe ruudu võrra vasakul
            (kesk_x - 2, kesk_y),   # Saba on peast kahe ruudu võrra vasakul
        ]
        # Määrab algseks liikumissuunaks paremale (x kasvab, y ei muutu)
        self.suund     = (1, 0)
        # Järgmine suund on algul sama mis praegune suund
        self.uus_suund = (1, 0)

        # Nullib mängija punktiskoori
        self.skoor  = 0
        # Seab algtasemeks 1
        self.tase   = 1
        # Seab algkiiruseks 8 sammu sekundis
        self.kiirus = 8

        # Mäng ei ole veel alanud (ootab menüüs)
        self.mang_kaib = False
        # Mäng ei ole veel lõppenud
        self.mang_labi = False
        # Paus ei ole aktiveeritud
        self.paus      = False
        # Peamenüü on nähtav mängu alguses
        self.menuu     = True

        # Nullib söödud toiduosakeste loenduri tasemetõusu jaoks
        self.toidud_soodud      = 0
        # Määrab mitu toiduosakest on vaja ühe tasemetõusu jaoks
        self.TOITU_TASEME_KOHTA = 5

        # Boonustoit ei ole algul väljakul (None tähendab puudub)
        self.boonus_toit      = None
        # Boonustoidu taimer on algul null
        self.boonus_taimer    = 0
        # Boonustoit püsib väljakul 150 tikki enne kadumist
        self.BOONUS_KESTUS    = 150
        # Boonustoit ilmub iga 300 tikki tagant
        self.BOONUS_INTERVALL = 300
        # Koguarv tikke mängu algusest, kasutatakse boonuse ajastamiseks
        self.tiki_loendur     = 0

        # Loob tühja hulga kivide positsioonide hoidmiseks
        self.takistused = set()
        # Genereerib kivid praegusele tasemele vastavalt
        self.loo_takistused()

        # Paigutab esimese toiduosakese juhuslikku vabasse kohta
        self.toit = self.loo_toit_positsioon()
        # Loob tühja nimekirja ujuvate punktitekstide animatsioonide jaoks
        self.animatsioonid = []

        # Nullib liikumise akumulaatori delta-time süsteemi jaoks
        self.liikumise_akumulaator = 0.0

    # --------------------------------------------------
    #  TAKISTUSTE GENEREERIMINE
    # --------------------------------------------------

    def loo_takistused(self):
        # Tühjendab eelmised kivid (uue taseme jaoks)
        self.takistused = set()
        # Arvutab kivide arvu: igal tasemel 3 kivi rohkem
        kivide_arv = self.tase * 3

        # Võtab ussi alguspositsiooni x-koordinaadi
        kesk_x = VALI_LAIUS  // 2
        # Võtab ussi alguspositsiooni y-koordinaadi
        kesk_y = VALI_KORGUS // 2
        # Loob tühja hulga kaitstud positsioonide jaoks (kive ei paigutata sinna)
        kaitstud = set()
        # Käib läbi 7×7 ala ussi ümber (3 ruutu igas suunas)
        for dx in range(-3, 4):
            # Käib läbi y-suunalised naabrid
            for dy in range(-3, 4):
                # Lisab positsiooni kaitstud alasse, et uss ei satuks kohe kivi otsa
                kaitstud.add((kesk_x + dx, kesk_y + dy))

        # Loendur lõputu tsükli vältimiseks
        katsed = 0
        # Kordab kuni vajalik arv kive on paigutatud või katsed on otsas
        while len(self.takistused) < kivide_arv and katsed < 1000:
            # Suurendab katseloendur
            katsed += 1
            # Genereerib juhusliku x-koordinaadi (servadest 1 ruut eemale)
            x = random.randint(1, VALI_LAIUS  - 2)
            # Genereerib juhusliku y-koordinaadi (servadest 1 ruut eemale)
            y = random.randint(1, VALI_KORGUS - 2)
            # Moodustab koordinaatide paari
            pos = (x, y)
            # Kontrollib et koht pole kaitstud alal ega juba kivi peal
            if pos not in kaitstud and pos not in self.takistused:
                # Lisab kivi positsiooni takistuste hulka
                self.takistused.add(pos)

    # --------------------------------------------------
    #  TOIDU POSITSIONEERIMINE
    # --------------------------------------------------

    def loo_toit_positsioon(self):
        # Teisendab ussi nimekirja hulgaks kiiremaks otsinguks (O(1) vs O(n))
        uss_set = set(self.uss)
        # Kordab kuni sobiv positsioon leitud
        while True:
            # Genereerib juhusliku positsiooni mänguväljaku piirides
            pos = (random.randint(0, VALI_LAIUS - 1), random.randint(0, VALI_KORGUS - 1))
            # Kontrollib et toit ei ilmu ussi, kivi ega boonustoidu peale
            if pos not in uss_set and pos not in self.takistused and pos != self.boonus_toit:
                # Tagastab leitud sobiva positsiooni
                return pos

    def loo_boonus_toit_positsioon(self):
        # Teisendab ussi nimekirja hulgaks kiiremaks otsinguks
        uss_set = set(self.uss)
        # Kordab kuni sobiv positsioon leitud
        while True:
            # Genereerib juhusliku positsiooni mänguväljaku piirides
            pos = (random.randint(0, VALI_LAIUS - 1), random.randint(0, VALI_KORGUS - 1))
            # Kontrollib et boonustoit ei ilmu ussi, kivi ega tavatoidu peale
            if pos not in uss_set and pos not in self.takistused and pos != self.toit:
                # Tagastab leitud sobiva positsiooni
                return pos

    # --------------------------------------------------
    #  SISENDI TÖÖTLEMINE
    # --------------------------------------------------

    def tootle_sundmused(self):
        # Käib läbi kõik ootel olevad sündmused sündmuste järjekorrast
        for sundmus in pygame.event.get():
            # Kontrollib kas kasutaja sulges akna ristiga
            if sundmus.type == pygame.QUIT:
                # Lõpetab pygame töö korrektselt
                pygame.quit()
                # Väljub programmist täielikult
                sys.exit()

            # Kontrollib kas vajutati mõnda klahvi
            if sundmus.type == pygame.KEYDOWN:
                # Kui peamenüü on nähtav, töödeldakse ainult tühikuklahvi
                if self.menuu:
                    # Kontrollib kas vajutati tühikuklahvi
                    if sundmus.key == pygame.K_SPACE:
                        # Peidab peamenüü
                        self.menuu = False
                        # Aktiveerib mänguloogika käivitamise
                        self.mang_kaib = True
                    # Lõpetab sündmuse töötlemise, teisi klahve menüüs ei käsitleta
                    return

                # Kui mäng on läbi, töödeldakse ainult R ja Q klahve
                if self.mang_labi:
                    # R-klahv alustab uut mängu
                    if sundmus.key == pygame.K_r:
                        # Lähtestab kõik mängumuutujad algväärtustele
                        self.lahesta_mang()
                        # Näitab peamenüüd uuesti
                        self.menuu = True
                    # Q-klahv lõpetab programmi
                    elif sundmus.key == pygame.K_q:
                        # Lõpetab pygame töö korrektselt
                        pygame.quit()
                        # Väljub programmist
                        sys.exit()
                    # Lõpetab sündmuse töötlemise
                    return

                # P-klahv lülitab pausi sisse või välja
                if sundmus.key == pygame.K_p:
                    # Pöörab pausi oleku ümber (True→False või False→True)
                    self.paus = not self.paus

                # Liikumisklahve töödeldakse ainult pausi väliselt
                if not self.paus:
                    # Üles nool või W — liigub üles
                    if sundmus.key in (pygame.K_UP, pygame.K_w):
                        # Ei luba pöörduda otse vastassuunda (alla liikudes ei saa üles minna)
                        if self.suund != (0, 1):
                            # Seab järgmise suunana üles (y väheneb)
                            self.uus_suund = (0, -1)
                    # Alla nool või S — liigub alla
                    elif sundmus.key in (pygame.K_DOWN, pygame.K_s):
                        # Ei luba pöörduda otse vastassuunda
                        if self.suund != (0, -1):
                            # Seab järgmise suunana alla (y kasvab)
                            self.uus_suund = (0, 1)
                    # Vasak nool või A — liigub vasakule
                    elif sundmus.key in (pygame.K_LEFT, pygame.K_a):
                        # Ei luba pöörduda otse vastassuunda
                        if self.suund != (1, 0):
                            # Seab järgmise suunana vasakule (x väheneb)
                            self.uus_suund = (-1, 0)
                    # Parem nool või D — liigub paremale
                    elif sundmus.key in (pygame.K_RIGHT, pygame.K_d):
                        # Ei luba pöörduda otse vastassuunda
                        if self.suund != (-1, 0):
                            # Seab järgmise suunana paremale (x kasvab)
                            self.uus_suund = (1, 0)

    # --------------------------------------------------
    #  MÄNGU LOOGIKA UUENDAMINE
    # --------------------------------------------------

    def uuenda(self, delta_ms):
        # Ei uuenda mängu kui mäng ei käi, paus on sees või mäng on läbi
        if not self.mang_kaib or self.paus or self.mang_labi:
            return

        # Arvutab millisekundides kui kaua üks ussi samm võtta peaks
        sammu_intervall = 1000.0 / self.kiirus

        # Lisab möödunud aja akumulaatorisse
        self.liikumise_akumulaator += delta_ms

        # Kontrollib kas on kogunenud piisavalt aega ühe sammu tegemiseks
        if self.liikumise_akumulaator < sammu_intervall:
            # Liiga vara järgmiseks sammuks — tagastab ilma ussit liigutamata
            return

        # Lahutab ühe sammu aja akumulaatorist (ei nulli, et järgmine samm oleks täpne)
        self.liikumise_akumulaator -= sammu_intervall

        # Suurendab tikke loenduri, kasutatakse boonuse ajastamiseks ja animatsioonideks
        self.tiki_loendur += 1
        # Rakendab kasutaja valitud suuna (vajutus registreeriti juba inputis)
        self.suund = self.uus_suund

        # Võtab ussi pea praeguse x-koordinaadi
        pea_x, pea_y = self.uss[0]
        # Arvutab uue pea positsiooni liigutades ühe sammu praeguses suunas
        uus_pea = (pea_x + self.suund[0], pea_y + self.suund[1])

        # Kontrollib kas pea läks mänguväljaku piiridest välja
        if not (0 <= uus_pea[0] < VALI_LAIUS and 0 <= uus_pea[1] < VALI_KORGUS):
            # Uss põrkas seinaga — käivitab surmaprotseduuri
            self.ussi_surm()
            return

        # Teisendab ussi keha hulgaks kiiremaks kokkupõrke kontrolliks
        uss_keha = set(self.uss[1:])
        # Kontrollib kas pea puutub oma kehaga (v.a pea ise)
        if uus_pea in uss_keha:
            # Uss põrkas oma kehaga — käivitab surmaprotseduuri
            self.ussi_surm()
            return

        # Kontrollib kas pea puutub kivitakistusega
        if uus_pea in self.takistused:
            # Uss põrkas kiviga — käivitab surmaprotseduuri
            self.ussi_surm()
            return

        # Lisab uue pea ussi nimekirja ette (uss on liikunud)
        self.uss.insert(0, uus_pea)

        # Lipp: kas sellel tikil söödi midagi (True = uss kasvab)
        soi = False

        # Kontrollib kas uss jõudis tavatoidu peale
        if uus_pea == self.toit:
            # Arvutab punktid: 10 korrutatuna praeguse tasemega
            punktid = 10 * self.tase
            # Lisab punktid mängija skoorile
            self.skoor += punktid
            # Suurendab söödud toiduosakeste loenduri tasemetõusu jaoks
            self.toidud_soodud += 1
            # Lisab ujuva punktiteksti animatsiooni söömiskohale
            self.lisa_animatsioon("+" + str(punktid), uus_pea, VALGE)
            # Tekitab uue toiduosakese juhuslikku vabasse kohta
            self.toit = self.loo_toit_positsioon()
            # Märgib et söödi, uss peab kasvama
            soi = True
            # Mängib toidusöömise heli kui heli on olemas
            if self.heli_punkt:
                self.heli_punkt.play()
            # Kontrollib kas söödud toiduosakeste arv käivitab tasemetõusu
            self.kontrolli_taseme_tousu()

        # Kontrollib kas uss jõudis boonustoidu peale
        elif uus_pea == self.boonus_toit:
            # Arvutab boonuspunktid: 50 korrutatuna praeguse tasemega
            punktid = 50 * self.tase
            # Lisab boonuspunktid skoorile
            self.skoor += punktid
            # Lisab suure kollase "BOONUS!" teksti animatsioonina
            self.lisa_animatsioon("BOONUS +" + str(punktid) + "!", uus_pea, KOLLANE)
            # Eemaldab boonustoidu väljakult
            self.boonus_toit = None
            # Nullib boonustaimer kuna boonustoit on kadunud
            self.boonus_taimer = 0
            # Märgib et söödi, uss peab kasvama
            soi = True
            # Mängib boonussöömise heli kui heli on olemas
            if self.heli_boonus:
                self.heli_boonus.play()

        # Kui midagi ei söödud, uss ei kasva
        if not soi:
            # Eemaldab ussi viimase lüli (saba), et uss liiguks edasi ilma kasvamata
            self.uss.pop()

        # Uuendab boonustaimerit kui boonustoit on väljakul
        if self.boonus_toit:
            # Vähendab taimerit ühe tikk
            self.boonus_taimer -= 1
            # Kontrollib kas taimer on nulli jõudnud
            if self.boonus_taimer <= 0:
                # Eemaldab boonustoidu väljakult kuna aeg sai täis
                self.boonus_toit = None

        # Kontrollib kas on aeg uus boonustoit ilmutada
        if (self.boonus_toit is None and                          # Boonustoit pole praegu väljakul
            self.tiki_loendur % self.BOONUS_INTERVALL == 0 and   # Tikke arv jagub intervalliga
            self.tiki_loendur > 0):                               # Mäng on juba alanud (ei ilmu kohe)
            # Paigutab boonustoidu uude juhuslikku vabasse kohta
            self.boonus_toit   = self.loo_boonus_toit_positsioon()
            # Seab boonustaimer täis väärtusele
            self.boonus_taimer = self.BOONUS_KESTUS

        # Uuendab kõiki aktiivseid animatsioone ühe tikiga
        self.animatsioonid = [
            [tekst, x, y - 0.5, eluiga - 1, varv]               # Liigutab teksti 0.5 pikslit üles ja vähendab eluiga
            for tekst, x, y, eluiga, varv in self.animatsioonid  # Käib läbi kõik animatsioonid
            if eluiga > 0                                         # Eemaldab animatsioonid mille eluiga on lõppenud
        ]

    def kontrolli_taseme_tousu(self):
        # Kontrollib kas söödud toiduosakeste arv on jõudnud tasemetõusu piirini
        if self.toidud_soodud >= self.TOITU_TASEME_KOHTA:
            # Nullib söödud toiduosakeste loenduri järgmise taseme jaoks
            self.toidud_soodud = 0
            # Tõstab taset ühe võrra
            self.tase += 1
            # Suurendab kiirust kuid mitte üle 25 sammu sekundis
            self.kiirus = min(8 + self.tase * 2, 25)
            # Nullib liikumise akumulaatori et tasemevahetusel ei juhtuks topeltsammu
            self.liikumise_akumulaator = 0
            # Kuvab keskel suure "TASE X!" animatsiooniteksiteksit
            self.lisa_animatsioon("TASE " + str(self.tase) + "!", (VALI_LAIUS//2, VALI_KORGUS//2), KOLLANE)
            # Genereerib uued kivid uuele tasemele (rohkem kive)
            self.loo_takistused()

    def ussi_surm(self):
        # Peatab mänguloogika uuendamise
        self.mang_kaib = False
        # Aktiveerib mäng-läbi oleku, mis kuvab tulemuste ekraani
        self.mang_labi = True
        # Mängib surmahelioleku kui heli on olemas
        if self.heli_surm:
            self.heli_surm.play()
        # Lisab praeguse skoori parimate tulemuste nimekirja
        self.parimad_tulemused.append(self.skoor)
        # Salvestab uuendatud top-5 tulemused faili
        self.parimad_tulemused = salvesta_tulemused(self.parimad_tulemused)

    def lisa_animatsioon(self, tekst, pos, varv=VALGE):
        # Teisendab ruudustiku positsiooni ekraani pikselkoordinaatideks
        px, py = ruut_pikseliks(pos[0], pos[1])
        # Lisab uue animatsiooni nimekirja: tekst, x, y (ujukomaarv), eluiga 40 tikki, värv
        self.animatsioonid.append([tekst, px, float(py), 40, varv])

    # --------------------------------------------------
    #  JOONISTAMINE
    # --------------------------------------------------

    def joonista(self):
        # Täidab kogu ekraani põhitaustavärviga (kustutab eelmise kaadri)
        self.ekraan.fill(TAUSTAVARV)
        # Joonistab info-paneeli alati, olenemata mängu olekust
        self.joonista_paneel()

        # Valib mida joonistada sõltuvalt mängu olekust
        if self.menuu:
            # Kuvab peamenüü ekraani
            self.joonista_menuu()
        elif self.mang_labi:
            # Kuvab mäng-läbi ekraani tulemustega
            self.joonista_mang_labi()
        else:
            # Joonistab eelrenderdatud ruudustiku ühe blit-operatsiooniga
            self.ekraan.blit(self.ruudustik_surf, (0, 0))
            # Joonistab kivitakistused väljakule
            self.joonista_takistused()
            # Joonistab ussi silmadega pea ja gradueeruva kehaga
            self.joonista_uss()
            # Joonistab tavatoidu ja boonustoidu (kui on väljakul)
            self.joonista_toit()
            # Joonistab ujuvad punktitekstide animatsioonid
            self.joonista_animatsioonid()
            # Kuvab pausiülekatte kui paus on aktiveeritud
            if self.paus:
                self.joonista_paus()

        # Kuvab valmis kaadri ekraanile (topeltpuhverdamine)
        pygame.display.flip()

    def joonista_paneel(self):
        # Joonistab info-paneeli tumeda taustaga ristküliku
        pygame.draw.rect(self.ekraan, PANEEL_VARV, (0, 0, LAIUS, PANEEL_KORGUS))
        # Joonistab rohelise eraldusjoone paneeli ja mänguväljaku vahele
        pygame.draw.line(self.ekraan, ROHELINE, (0, PANEEL_KORGUS), (LAIUS, PANEEL_KORGUS), 2)

        # Renderdab skoori teksti valgeks
        skoor_tekst = self.font_kesk.render("Skoor: " + str(self.skoor), True, VALGE)
        # Kuvab skoori paneeli vasakus servas
        self.ekraan.blit(skoor_tekst, (20, 25))

        # Renderdab taseme teksti kollaseks
        tase_tekst = self.font_kesk.render("Tase: " + str(self.tase), True, KOLLANE)
        # Kuvab taseme paneeli horisontaalses keskel
        self.ekraan.blit(tase_tekst, (LAIUS//2 - tase_tekst.get_width()//2, 25))

        # Võtab parima tulemuse nimekirjast, või 0 kui nimekiri on tühi
        parim = max(self.parimad_tulemused) if self.parimad_tulemused else 0
        # Renderdab rekordi teksti helesinine värviga
        parim_tekst = self.font_vaike.render("Rekord: " + str(parim), True, HELESININE)
        # Kuvab rekordi paneeli paremas servas
        self.ekraan.blit(parim_tekst, (LAIUS - parim_tekst.get_width() - 20, 15))

        # Renderdab kiiruse teksti halliks
        kiirus_tekst = self.font_pisike.render("Kiirus: " + str(self.kiirus) + " FPS", True, HALL)
        # Kuvab kiiruse rekordi all paneeli paremas servas
        self.ekraan.blit(kiirus_tekst, (LAIUS - kiirus_tekst.get_width() - 20, 45))

        # Kuvab boonustaimer riba ainult kui boonustoit on väljakul ja mäng käib
        if self.boonus_toit and self.mang_kaib:
            # Arvutab järelejäänud aja protsendina (1.0 = täis, 0.0 = tühi)
            protsent = self.boonus_taimer / self.BOONUS_KESTUS
            # Määrab taimeririba laiuseks 120 pikslit
            riba_laius = 120
            # Joonistab musta taustariba taimeri all
            pygame.draw.rect(self.ekraan, MUST,  (LAIUS//2 - riba_laius//2, 48, riba_laius, 10), border_radius=5)
            # Joonistab roosa täitumisriba vastavalt järelejäänud ajale
            pygame.draw.rect(self.ekraan, ROOSA, (LAIUS//2 - riba_laius//2, 48, int(riba_laius * protsent), 10), border_radius=5)
            # Renderdab "Boonus!" teksti roosas
            b_tekst = self.font_pisike.render("Boonus!", True, ROOSA)
            # Kuvab boonusteksti taimeririba all keskel
            self.ekraan.blit(b_tekst, (LAIUS//2 - b_tekst.get_width()//2, 60))

    def joonista_takistused(self):
        # Käib läbi kõik kivide positsioonid takistuste hulgast
        for (kx, ky) in self.takistused:
            # Teisendab ruudustiku koordinaadid ekraanipikseliteks
            px, py = ruut_pikseliks(kx, ky)
            # Joonistab kivi halli täidetud ristküliku (1px servadest eemale)
            pygame.draw.rect(self.ekraan, HALL,    (px+1, py+1, RUUT-2, RUUT-2), border_radius=3)
            # Joonistab kivi tumeda piirjoone
            pygame.draw.rect(self.ekraan, TUM_HALL,(px+1, py+1, RUUT-2, RUUT-2), 2, border_radius=3)
            # Joonistab kivi ühe diagonaaljoone tekstuuri efektiks
            pygame.draw.line(self.ekraan, TUM_HALL, (px+4, py+4), (px+RUUT-5, py+RUUT-5), 2)
            # Joonistab kivi teise diagonaaljoone vastassuunas
            pygame.draw.line(self.ekraan, TUM_HALL, (px+RUUT-5, py+4), (px+4, py+RUUT-5), 2)

    def joonista_uss(self):
        # Käib läbi kõik ussi lülid, i=0 on pea
        for i, (ux, uy) in enumerate(self.uss):
            # Teisendab ruudustiku koordinaadid ekraanipikseliteks
            px, py = ruut_pikseliks(ux, uy)
            # Esimene lüli (i==0) on pea, kõik ülejäänud on keha
            if i == 0:
                # Joonistab pea tumerohelise ümara ristküliku
                pygame.draw.rect(self.ekraan, TUM_ROHELINE, (px+1, py+1, RUUT-2, RUUT-2), border_radius=6)
                # Võtab praeguse liikumissuuna silmade positsiooni arvutamiseks
                suund = self.suund
                # Arvutab silmade pikselkoordinaadid vastavalt liikumissuunale
                if suund == (1, 0):    silm1 = (px+14, py+5);  silm2 = (px+14, py+13)   # Paremale liikudes silmad paremas servas
                elif suund == (-1, 0): silm1 = (px+5,  py+5);  silm2 = (px+5,  py+13)   # Vasakule liikudes silmad vasakus servas
                elif suund == (0, -1): silm1 = (px+5,  py+5);  silm2 = (px+13, py+5)    # Üles liikudes silmad ülemises servas
                else:                  silm1 = (px+5,  py+14); silm2 = (px+13, py+14)   # Alla liikudes silmad alumises servas
                # Joonistab vasaku silma valge osa (raadius 3)
                pygame.draw.circle(self.ekraan, VALGE, silm1, 3)
                # Joonistab parema silma valge osa (raadius 3)
                pygame.draw.circle(self.ekraan, VALGE, silm2, 3)
                # Joonistab vasaku silma musta pupilli peale (raadius 1)
                pygame.draw.circle(self.ekraan, MUST,  silm1, 1)
                # Joonistab parema silma musta pupilli peale (raadius 1)
                pygame.draw.circle(self.ekraan, MUST,  silm2, 1)
            else:
                # Arvutab kehalüli heleduse: saba poole muutub üha tumedamaks (min 100)
                heledus = max(100, 255 - i * 5)
                # Loob rohelise värvi, mille heledus sõltub lüli asukohast
                varv = (0, heledus, 0)
                # Joonistab kehalüli rohelise ümara ristküliku (2px servadest eemale)
                pygame.draw.rect(self.ekraan, varv, (px+2, py+2, RUUT-4, RUUT-4), border_radius=4)

    def joonista_toit(self):
        # Teisendab tavatoidu ruudustiku koordinaadid pikseliteks
        px, py = ruut_pikseliks(*self.toit)
        # Arvutab toidu suuruse siinuslaine abil (pulssiv efekt)
        suurus = RUUT//2 - 2 + int(math.sin(self.tiki_loendur * 0.2) * 2)
        # Joonistab punase tavatoidu ringi väljakule
        pygame.draw.circle(self.ekraan, PUNANE, (px + RUUT//2, py + RUUT//2), suurus)

        # Joonistab boonustoidu ainult kui see on väljakul
        if self.boonus_toit:
            # Teisendab boonustoidu koordinaadid pikseliteks
            bx, by = ruut_pikseliks(*self.boonus_toit)
            # Arvutab boonustoidu suuruse kiiremalt pulseeriva siinuslainega
            suurus_b = RUUT//2 - 1 + int(math.sin(self.tiki_loendur * 0.5) * 3)
            # Joonistab heleSinise boonustoidu ringi
            pygame.draw.circle(self.ekraan, HELESININE, (bx + RUUT//2, by + RUUT//2), suurus_b)
            # Joonistab valge piirjoone ringi boonustoidu ümber (2px paksune)
            pygame.draw.circle(self.ekraan, VALGE,      (bx + RUUT//2, by + RUUT//2), suurus_b + 2, 2)

    def joonista_animatsioonid(self):
        # Käib läbi kõik aktiivsed ujuvad punktitekstid
        for andmed in self.animatsioonid:
            # Lahutab animatsiooni andmed eraldi muutujatesse
            tekst, x, y, eluiga, varv = andmed
            # Arvutab läbipaistvuse: animatsioon tuhmub lõpus (max 255)
            alpha = min(255, eluiga * 6)
            # Renderdab teksti pinnale määratud värviga
            surf = self.font_vaike.render(tekst, True, varv)
            # Seab pinna läbipaistvuse väärtuse
            surf.set_alpha(alpha)
            # Kuvab teksti ekraanile horisontaalselt tsentreeritud
            self.ekraan.blit(surf, (int(x) - surf.get_width()//2, int(y)))

    def joonista_paus(self):
        # Loob poolläbipaistva musta pinna kogu ekraani katmiseks
        kate = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)
        # Täidab katte musta värviga, alfa 160 (poolläbipaistev)
        kate.fill((0, 0, 0, 160))
        # Kuvab katte kogu ekraani peale
        self.ekraan.blit(kate, (0, 0))
        # Renderdab "PAUS" teksti kollasega suure fondiga
        tekst = self.font_suur.render("PAUS", True, KOLLANE)
        # Kuvab "PAUS" teksti ekraani horisontaalses ja vertikaalses keskel
        self.ekraan.blit(tekst, (LAIUS//2 - tekst.get_width()//2, KORGUS//2 - 30))
        # Renderdab juhisteksti "Vajuta P jatkamiseks" valgega
        alitekst = self.font_vaike.render("Vajuta P jatkamiseks", True, VALGE)
        # Kuvab juhisteksti peateksti all tsentreeritud
        self.ekraan.blit(alitekst, (LAIUS//2 - alitekst.get_width()//2, KORGUS//2 + 30))

    def joonista_menuu(self):
        # Renderdab mängu pealkirja rohelisega suure fondiga
        pealkiri = self.font_suur.render("SINU-MOODI USSIMANG", True, ROHELINE)
        # Kuvab pealkirja ekraani ülaosas horisontaalselt keskel
        self.ekraan.blit(pealkiri, (LAIUS//2 - pealkiri.get_width()//2, 100))

        # Renderdab alapealkirja halliga väikese fondiga
        ali = self.font_vaike.render("Viie taiustusega PyGame ussimang!", True, HALL)
        # Kuvab alapealkirja pealkirja all tsentreeritud
        self.ekraan.blit(ali, (LAIUS//2 - ali.get_width()//2, 160))

        # Loob nimekirja klahv-kirjeldus paaridest
        juhised = [
            ("Nooled / WASD", "- liikumine"),   # Liikumisklahvide kirjeldus
            ("P",             "- paus"),          # Pausiklahvi kirjeldus
            ("R",             "- restart"),       # Restartklahvi kirjeldus
            ("Q",             "- lopeta"),        # Lõpetamisklahvi kirjeldus
        ]
        # Määrab juhiste bloki alguse y-koordinaadi
        y = 210
        # Käib läbi kõik klahv-kirjeldus paarid
        for klahv, kirjeldus in juhised:
            # Renderdab klahvi nimetuse kollasega
            k_surf = self.font_vaike.render(klahv, True, KOLLANE)
            # Renderdab kirjelduse teksti valgega
            k_kirj = self.font_vaike.render(kirjeldus, True, VALGE)
            # Kuvab klahvi nimetuse vasakule keskmest
            self.ekraan.blit(k_surf, (LAIUS//2 - 120, y))
            # Kuvab kirjelduse veidi paremale klahvist
            self.ekraan.blit(k_kirj, (LAIUS//2 - 20,  y))
            # Liigub järgmise juhise reale
            y += 30

        # Loob nimekirja kõigi viie täiustuse kirjeldustest
        taiustused = [
            "1. Tasemesusteem - kiirus touseb iga 5 toiduosakese jarela",
            "2. Takistused - kivid muutuvad ohtlikumaks korgematele tasemetes",
            "3. Boonustoit - ajapiiranguga sinine toit (x5 punktid!)",
            "4. Heliefektid - helid soomisel ja surmisel",
            "5. Korgeimate tulemuste tabel - top 5 salvestatakse",
        ]
        # Määrab täiustuste sektsiooni alguse y-koordinaadi
        y = 370
        # Renderdab "Taiustused:" sektsiooni pealkirja helesinine värviga
        t_pealk = self.font_vaike.render("Taiustused:", True, HELESININE)
        # Kuvab täiustuste pealkirja tsentreeritud, 25px kõrgemal nimekirjast
        self.ekraan.blit(t_pealk, (LAIUS//2 - t_pealk.get_width()//2, y - 25))
        # Käib läbi kõik täiustuste kirjeldused
        for t in taiustused:
            # Renderdab täiustuse teksti halliga pisikese fondiga
            surf = self.font_pisike.render(t, True, HALL)
            # Kuvab teksti horisontaalselt tsentreeritud
            self.ekraan.blit(surf, (LAIUS//2 - surf.get_width()//2, y))
            # Liigub järgmise rea juurde
            y += 22

        # Kuvab top-5 tulemused ainult kui nimekirjas on vähemalt üks tulemus
        if self.parimad_tulemused:
            # Lisab väikese vahe täiustuste ja tulemuste vahele
            y += 10
            # Renderdab "TOP 5 TULEMUSED:" pealkirja kollasega
            top_p = self.font_vaike.render("TOP 5 TULEMUSED:", True, KOLLANE)
            # Kuvab tulemuste pealkirja tsentreeritud
            self.ekraan.blit(top_p, (LAIUS//2 - top_p.get_width()//2, y))
            # Liigub tulemuste loendi algusesse
            y += 28
            # Käib läbi kuni 5 parimat tulemust
            for i, tulemus in enumerate(self.parimad_tulemused[:5]):
                # Esimene koht on kollane, ülejäänud vahelduvad valge ja hallina
                varv = [KOLLANE, VALGE, HALL, HALL, HALL][i]
                # Renderdab tulemuse rea koha numbri ja punktidega
                t_surf = self.font_pisike.render("#" + str(i+1) + "  " + str(tulemus) + " punkti", True, varv)
                # Kuvab tulemuse rea tsentreeritud
                self.ekraan.blit(t_surf, (LAIUS//2 - t_surf.get_width()//2, y))
                # Liigub järgmise tulemuse reale
                y += 22

        # Võtab praeguse aja millisekundites vilkumise efekti jaoks
        aeg = pygame.time.get_ticks()
        # Kuvab teksti ainult paarilistel 500ms intervallidel (vilgub)
        if (aeg // 500) % 2 == 0:
            # Renderdab "Vajuta SPACE alustamiseks" rohelisega
            alusta = self.font_kesk.render("Vajuta SPACE alustamiseks", True, ROHELINE)
            # Kuvab vilkuva teksti ekraani allosas tsentreeritud
            self.ekraan.blit(alusta, (LAIUS//2 - alusta.get_width()//2, KORGUS - 55))

    def joonista_mang_labi(self):
        # Loob poolläbipaistva musta pinna kogu ekraani katmiseks
        kate = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)
        # Täidab katte musta värviga, alfa 200 (tumedam kui pausi kate)
        kate.fill((0, 0, 0, 200))
        # Kuvab katte kogu ekraani peale
        self.ekraan.blit(kate, (0, 0))

        # Renderdab "MANG LABI" pealkirja punasega suure fondiga
        pealkiri = self.font_suur.render("MANG LABI", True, PUNANE)
        # Kuvab pealkirja ekraani ülaosas horisontaalselt keskel
        self.ekraan.blit(pealkiri, (LAIUS//2 - pealkiri.get_width()//2, 120))

        # Renderdab lõppskoori kollasega keskmise fondiga
        skoor_t = self.font_kesk.render("Sinu skoor: " + str(self.skoor), True, KOLLANE)
        # Kuvab lõppskoori pealkirja all tsentreeritud
        self.ekraan.blit(skoor_t, (LAIUS//2 - skoor_t.get_width()//2, 200))

        # Renderdab saavutatud taseme teksti valgega
        tase_t = self.font_vaike.render("Joudsid tasemeni: " + str(self.tase), True, VALGE)
        # Kuvab tasemeteksti skoori all tsentreeritud
        self.ekraan.blit(tase_t, (LAIUS//2 - tase_t.get_width()//2, 245))

        # Määrab kõrgeimate tulemuste sektsiooni alguse y-koordinaadi
        y = 300
        # Renderdab "KORGEIMAD TULEMUSED" pealkirja helesinine värviga
        top_p = self.font_kesk.render("KORGEIMAD TULEMUSED", True, HELESININE)
        # Kuvab tulemuste pealkirja tsentreeritud
        self.ekraan.blit(top_p, (LAIUS//2 - top_p.get_width()//2, y))
        # Liigub tulemuste loendi algusesse
        y += 45
        # Käib läbi kuni 5 parimat tulemust
        for i, tulemus in enumerate(self.parimad_tulemused[:5]):
            # Esimene koht on kollane, ülejäänud valged
            varv = KOLLANE if i == 0 else VALGE
            # Renderdab tulemuse rea järjestuse ja punktidega
            t_surf = self.font_vaike.render("#" + str(i+1) + "  " + str(tulemus) + " punkti", True, varv)
            # Kuvab tulemuse rea tsentreeritud
            self.ekraan.blit(t_surf, (LAIUS//2 - t_surf.get_width()//2, y))
            # Liigub järgmise tulemuse reale
            y += 30

        # Renderdab "R - uus mang" nupu rohelisega
        r_surf = self.font_vaike.render("R - uus mang", True, ROHELINE)
        # Renderdab "Q - lopeta" nupu punasega
        q_surf = self.font_vaike.render("Q - lopeta",   True, PUNANE)
        # Kuvab R-nupu vasakule keskmest
        self.ekraan.blit(r_surf, (LAIUS//2 - 120, y + 20))
        # Kuvab Q-nupu paremale keskmest
        self.ekraan.blit(q_surf, (LAIUS//2 + 20,  y + 20))

    # --------------------------------------------------
    #  PÕHITSÜKKEL
    # --------------------------------------------------

    def kaivita(self):
        # Kordab lõputult kuni programmist väljutakse
        while True:
            # Piirab mängu 60 kaadriga sekundis ja tagastab möödunud aja millisekundites
            delta_ms = self.kell.tick(LOOP_FPS)
            # Loeb ja töötleb kõik kasutaja sisendid (alati 60x sekundis)
            self.tootle_sundmused()
            # Uuendab mängu loogikat delta-time põhjal (uss liigub omas tempos)
            self.uuenda(delta_ms)
            # Joonistab uue kaadri ekraanile
            self.joonista()


# -------------------------------------------------------
#  PROGRAMMI KÄIVITAMINE
# -------------------------------------------------------

if __name__ == "__main__":
    # Loob mänguobjekti ja initsialiseeriib kõik komponendid
    mang = SnakeMang()
    # Käivitab põhitsükli ja alustab mängu
    mang.kaivita()