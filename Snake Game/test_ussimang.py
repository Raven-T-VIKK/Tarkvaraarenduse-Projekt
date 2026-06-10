# -*- coding: utf-8 -*-
# test_ussimang.py — Ussimängu loogika pytest testid

# Pytest tutorial: https://realpython.com/pytest-python-testing/

import pytest
import json
import os
import sys
import tempfile

# --- PYGAME MOCK ---
# Pygame vajab ekraani ja helikaart — testikeskkonnas neid pole.
# Loome lihtsa "mock" (võltsitud) pygame mooduli, et saaksime
# mängu loogika funktsioone testida ilma päris pygame'i käivitamata.

import types

# Loome tühja pygame mock-mooduli
pygame_mock = types.ModuleType("pygame")
pygame_mock.init = lambda: None
pygame_mock.quit = lambda: None

# Värvikonstantide mock
pygame_mock.SRCALPHA = 0

# display mock
display_mock = types.ModuleType("pygame.display")
display_mock.set_mode = lambda size: None
display_mock.set_caption = lambda title: None
pygame_mock.display = display_mock

# mixer mock
mixer_mock = types.ModuleType("pygame.mixer")
mixer_mock.init = lambda **kwargs: None
mixer_mock.get_init = lambda: (44100, -16, 2)
pygame_mock.mixer = mixer_mock

# font mock
font_mock = types.ModuleType("pygame.font")
font_mock.SysFont = lambda name, size, bold=False: None
pygame_mock.font = font_mock

# time mock
class ClockMock:
    def tick(self, fps): return 16
class TimeMock:
    Clock = ClockMock
    get_ticks = staticmethod(lambda: 0)
pygame_mock.time = TimeMock()

# Surface mock
class SurfaceMock:
    def fill(self, color): pass
    def blit(self, surf, pos): pass
    def get_width(self): return 100
    def get_height(self): return 100
pygame_mock.Surface = lambda size, flags=0: SurfaceMock()

# draw mock
draw_mock = types.ModuleType("pygame.draw")
draw_mock.rect = lambda *args, **kwargs: None
draw_mock.line = lambda *args, **kwargs: None
draw_mock.circle = lambda *args, **kwargs: None
pygame_mock.draw = draw_mock

# sndarray mock
sndarray_mock = types.ModuleType("pygame.sndarray")
sndarray_mock.make_sound = lambda arr: None
pygame_mock.sndarray = sndarray_mock

# event mock
pygame_mock.QUIT = 256
pygame_mock.KEYDOWN = 768
pygame_mock.K_SPACE = 32
pygame_mock.K_UP = 273
pygame_mock.K_DOWN = 274
pygame_mock.K_LEFT = 276
pygame_mock.K_RIGHT = 275
pygame_mock.K_w = 119
pygame_mock.K_s = 115
pygame_mock.K_a = 97
pygame_mock.K_d = 100
pygame_mock.K_p = 112
pygame_mock.K_r = 114
pygame_mock.K_q = 113

event_mock = types.ModuleType("pygame.event")
event_mock.get = lambda: []
pygame_mock.event = event_mock

sys.modules["pygame"] = pygame_mock
sys.modules["pygame.display"] = display_mock
sys.modules["pygame.mixer"] = mixer_mock
sys.modules["pygame.font"] = font_mock
sys.modules["pygame.draw"] = draw_mock
sys.modules["pygame.sndarray"] = sndarray_mock
sys.modules["pygame.event"] = event_mock

# --- IMPORDI MÄNGU FUNKTSIOONID ---
# sys.exit() kutsumine testis lõpetaks kogu pytest-i — asendame selle
sys.exit = lambda *args: (_ for _ in ()).throw(SystemExit(*args))

# Lisame uploads-kausta Pythoni otsinguteele
import pathlib

# Impordime mängu mooduli (failinimi sisaldab erimärke, kasutame importlib)
import importlib.util
MANG_FAIL = pathlib.Path(__file__).parent / "Ussimäng ( EDASI ARENDATUD ).py"
spec = importlib.util.spec_from_file_location("ussimang", MANG_FAIL)
ussimang = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ussimang)

# Toome testides kasutatavad funktsioonid otse kätte
salvesta_tulemused = ussimang.salvesta_tulemused
laadi_tulemused    = ussimang.laadi_tulemused
ruut_pikseliks     = ussimang.ruut_pikseliks
SnakeMang          = ussimang.SnakeMang

RUUT         = ussimang.RUUT
VALI_Y_ALGUS = ussimang.VALI_Y_ALGUS
VALI_LAIUS   = ussimang.VALI_LAIUS
VALI_KORGUS  = ussimang.VALI_KORGUS


# ===================================================================
#  FIXTURE — loob igale testile puhta mänguobjekti
# ===================================================================

@pytest.fixture
def mang():
    """Loob SnakeMang objekti enne iga testi ja tagastab selle."""
    m = SnakeMang.__new__(SnakeMang)   # ei kutsu __init__ (pygame vajab ekraani)
    m.heliefektid_olemas = False
    m.heli_punkt = m.heli_surm = m.heli_boonus = None
    m.font_suur = m.font_kesk = m.font_vaike = m.font_pisike = None
    m.ekraan = SurfaceMock()
    m.ruudustik_surf = SurfaceMock()
    m.parimad_tulemused = []
    m.animatsioonid = []
    m.lahesta_mang(m) if False else None   # ei kasuta (kutsume allpool)
    # Käsitsi lähtestamine (mirrors lahesta_mang):
    kesk_x = VALI_LAIUS  // 2
    kesk_y = VALI_KORGUS // 2
    m.uss = [(kesk_x, kesk_y), (kesk_x - 1, kesk_y), (kesk_x - 2, kesk_y)]
    m.suund      = (1, 0)
    m.uus_suund  = (1, 0)
    m.skoor      = 0
    m.tase       = 1
    m.kiirus     = 8
    m.mang_kaib  = True
    m.mang_labi  = False
    m.paus       = False
    m.menuu      = False
    m.toidud_soodud      = 0
    m.TOITU_TASEME_KOHTA = 5
    m.boonus_toit        = None
    m.boonus_taimer      = 0
    m.BOONUS_KESTUS      = 150
    m.BOONUS_INTERVALL   = 300
    m.tiki_loendur       = 0
    m.takistused         = set()
    m.toit               = (0, 0)   # algselt nurgas, testides muudetakse
    m.animatsioonid      = []
    m.liikumise_akumulaator = 0.0
    return m


# ===================================================================
#  1. KOORDINAATIDE TEISENDAMINE
# ===================================================================

class TestRuutPikseliks:
    """Testid ruut_pikseliks() funktsioonile."""

    def test_alguspunkt(self):
        """Ruudustiku (0, 0) peab vastama pikslitele (0, VALI_Y_ALGUS)."""
        px, py = ruut_pikseliks(0, 0)
        assert px == 0
        assert py == VALI_Y_ALGUS

    def test_esimene_ruut(self):
        """Ruudustiku (1, 1) peab olema nihutatud täpselt RUUT pikslite võrra."""
        px, py = ruut_pikseliks(1, 1)
        assert px == RUUT
        assert py == VALI_Y_ALGUS + RUUT

    def test_suurem_koordinaat(self):
        """Kontrollib suvalise koordinaadi arvutust."""
        px, py = ruut_pikseliks(5, 3)
        assert px == 5 * RUUT
        assert py == VALI_Y_ALGUS + 3 * RUUT


# ===================================================================
#  2. TULEMUSTE SALVESTAMINE JA LAADIMINE
# ===================================================================

class TestTulemused:
    """Testid salvesta_tulemused() ja laadi_tulemused() funktsioonidele."""

    def test_salvesta_sorteerib_kahanevas(self, tmp_path, monkeypatch):
        """Salvestatud tulemused peavad olema suurimast väikseimani."""
        monkeypatch.chdir(tmp_path)
        tulemus = salvesta_tulemused([30, 10, 50, 20, 40])
        assert tulemus == [50, 40, 30, 20, 10]

    def test_salvesta_jatab_top5(self, tmp_path, monkeypatch):
        """Salvestablist tohib olla maksimaalselt 5 tulemust."""
        monkeypatch.chdir(tmp_path)
        tulemus = salvesta_tulemused([10, 90, 30, 70, 50, 80, 20, 60, 40, 100])
        assert len(tulemus) == 5
        assert tulemus[0] == 100

    def test_laadi_tagastab_tuhja_kui_faili_pole(self, tmp_path, monkeypatch):
        """laadi_tulemused() peab tagastama [] kui faili pole olemas."""
        monkeypatch.chdir(tmp_path)
        tulemus = laadi_tulemused()
        assert tulemus == []

    def test_salvesta_ja_laadi_ring(self, tmp_path, monkeypatch):
        """Salvestatud tulemused peavad failist samana tagasi tulema."""
        monkeypatch.chdir(tmp_path)
        algne = [100, 80, 60]
        salvesta_tulemused(algne)
        laetud = laadi_tulemused()
        assert laetud == [100, 80, 60]

    def test_salvesta_uuendab_eelnevat(self, tmp_path, monkeypatch):
        """Teine salvestamine peab esimest üle kirjutama."""
        monkeypatch.chdir(tmp_path)
        salvesta_tulemused([50, 30])
        salvesta_tulemused([200, 150])
        laetud = laadi_tulemused()
        assert laetud[0] == 200


# ===================================================================
#  3. TASEMETÕUS
# ===================================================================

class TestTasemeTous:
    """Testid kontrolli_taseme_tousu() meetodile."""

    def test_tase_touseb_5_toidu_jarele(self, mang):
        """Tase peab tõusma pärast 5 toiduosakese söömist."""
        mang.toidud_soodud = 5
        mang.kontrolli_taseme_tousu()
        assert mang.tase == 2

    def test_kiirus_touseb_koos_tasemega(self, mang):
        """Kiirus peab tasemega kasvama."""
        algne_kiirus = mang.kiirus
        mang.toidud_soodud = 5
        mang.kontrolli_taseme_tousu()
        assert mang.kiirus > algne_kiirus

    def test_kiirus_ei_ule_25(self, mang):
        """Kiirus ei tohi ületada 25 sammu sekundis."""
        mang.tase = 100
        mang.toidud_soodud = 5
        mang.kontrolli_taseme_tousu()
        assert mang.kiirus <= 25

    def test_loendur_nullib_tasemevahetusel(self, mang):
        """toidud_soodud peab nulli minema pärast tasemetõusu."""
        mang.toidud_soodud = 5
        mang.kontrolli_taseme_tousu()
        assert mang.toidud_soodud == 0

    def test_tase_ei_touse_enne_piiri(self, mang):
        """Tase ei tohi tõusta kui söödud on vähem kui 5."""
        mang.toidud_soodud = 4
        mang.kontrolli_taseme_tousu()
        assert mang.tase == 1


# ===================================================================
#  4. USSI SURM
# ===================================================================

class TestUssiSurm:
    """Testid ussi_surm() meetodile."""

    def test_mang_labi_aktiveerub(self, mang, tmp_path, monkeypatch):
        """ussi_surm() peab seadma mang_labi = True."""
        monkeypatch.chdir(tmp_path)
        mang.ussi_surm()
        assert mang.mang_labi is True

    def test_mang_kaib_peatub(self, mang, tmp_path, monkeypatch):
        """ussi_surm() peab seadma mang_kaib = False."""
        monkeypatch.chdir(tmp_path)
        mang.ussi_surm()
        assert mang.mang_kaib is False

    def test_skoor_lisatakse_tulemustesse(self, mang, tmp_path, monkeypatch):
        """Hetke skoor peab surma korral tulemuste nimekirja lisatuma."""
        monkeypatch.chdir(tmp_path)
        mang.skoor = 42
        mang.ussi_surm()
        assert 42 in mang.parimad_tulemused


# ===================================================================
#  5. TOIDU POSITSIOON
# ===================================================================

class TestToiduPositsioon:
    """Testid loo_toit_positsioon() meetodile."""

    def test_toit_ei_ilmu_ussi_peale(self, mang):
        """Toit ei tohi tekkida samale positsioonile kus uss asub."""
        for _ in range(50):
            pos = mang.loo_toit_positsioon()
            assert pos not in set(mang.uss)

    def test_toit_ei_ilmu_kivi_peale(self, mang):
        """Toit ei tohi tekkida kivi positsioonile."""
        mang.takistused = {(5, 5), (6, 6), (7, 7)}
        for _ in range(50):
            pos = mang.loo_toit_positsioon()
            assert pos not in mang.takistused

    def test_toit_on_valjakul(self, mang):
        """Toidu positsioon peab olema mänguväljaku piirides."""
        for _ in range(50):
            x, y = mang.loo_toit_positsioon()
            assert 0 <= x < VALI_LAIUS
            assert 0 <= y < VALI_KORGUS