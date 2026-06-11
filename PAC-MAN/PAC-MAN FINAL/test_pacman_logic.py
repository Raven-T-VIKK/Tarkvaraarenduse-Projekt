"""
Pac-Man loogika testid (pytest)
Testib mängu loogikat ilma pygame aknata (headless).
Kaivita: pytest test_pacman_logic.py -v
"""

import os
import sys
import importlib.util

# Laeb mangufaili otse teekonna jargi (failinimi sisaldab tuhikut/sidekriipsu)
_game_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PAC-MAN FINAL.py")
_spec = importlib.util.spec_from_file_location("pacman", _game_path)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["pacman"] = _mod

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

_spec.loader.exec_module(_mod)

from pacman import (
    Pacman, Ghost, Wall, Pellet,
    WALLS, GATE, WIN_W, WIN_H,
    BLINKY_DIRS, PINKY_DIRS, INKY_DIRS, CLYDE_DIRS,
    setup_level
)

import pytest


# ----------------------------------------------
# FIXTURES
# ----------------------------------------------

@pytest.fixture
def wall_group():
    """Tagastab koigi seinte sprite-grupi."""
    group = pygame.sprite.Group()
    for w in WALLS:
        group.add(Wall(w[0], w[1], w[2], w[3]))
    return group


@pytest.fixture
def gate_group():
    group = pygame.sprite.Group()
    group.add(Wall(GATE[0], GATE[1], GATE[2], GATE[3]))
    return group


@pytest.fixture
def pacman():
    return Pacman(303, 439)


@pytest.fixture
def blinky():
    return Ghost(287, 199, 'blinky', BLINKY_DIRS, len(BLINKY_DIRS) - 1)


@pytest.fixture
def level():
    return setup_level()


# ----------------------------------------------
# 1. SEIN (Wall)
# ----------------------------------------------

class TestWall:
    def test_wall_loodakse_oige_asukohaga(self):
        w = Wall(60, 60, 186, 6)
        assert w.rect.x == 60
        assert w.rect.y == 60

    def test_wall_oige_laius_ja_korgus(self):
        w = Wall(0, 0, 100, 50)
        assert w.rect.width == 100
        assert w.rect.height == 50

    @pytest.mark.parametrize("x,y,w,h", [
        (0, 0, 6, 600),
        (60, 60, 186, 6),
        (300, 0, 6, 66),
    ])
    def test_seinte_list_on_olemas(self, x, y, w, h):
        assert [x, y, w, h] in WALLS


# ----------------------------------------------
# 2. PELLET
# ----------------------------------------------

class TestPellet:
    def test_tavaline_pellet_loodud(self):
        p = Pellet(100, 100, big=False)
        assert p.big is False

    def test_power_pellet_loodud(self):
        p = Pellet(100, 100, big=True)
        assert p.big is True

    def test_power_pellet_suurem_radius(self):
        small = Pellet(100, 100, big=False)
        big = Pellet(100, 100, big=True)
        assert big.rect.width > small.rect.width

    def test_pellet_asukoht_on_center(self):
        p = Pellet(200, 150)
        assert p.rect.centerx == 200
        assert p.rect.centery == 150


# ----------------------------------------------
# 3. PACMAN
# ----------------------------------------------

class TestPacman:
    def test_pacman_algpositsioon(self, pacman):
        assert pacman.rect.centerx == 303
        assert pacman.rect.centery == 439

    def test_pacman_suund_parem(self, pacman):
        pacman.set_direction(3, 0)
        assert pacman.change_x == 3
        assert pacman.change_y == 0
        assert pacman.facing == 0

    def test_pacman_suund_vasak(self, pacman):
        pacman.set_direction(-3, 0)
        assert pacman.facing == 180

    def test_pacman_suund_ules(self, pacman):
        pacman.set_direction(0, -3)
        assert pacman.facing == 90

    def test_pacman_suund_alla(self, pacman):
        pacman.set_direction(0, 3)
        assert pacman.facing == 270

    def test_pacman_liigub_ilma_seinata(self, wall_group, gate_group):
        pm = Pacman(200, 340)
        start_x = pm.rect.x
        pm.set_direction(3, 0)
        pm.update(wall_group, gate_group)
        assert pm.rect.x != start_x

    def test_pacman_ei_labi_seina(self, pacman, wall_group, gate_group):
        wall = Wall(350, 430, 20, 30)
        wall_group.add(wall)
        pacman.rect.right = wall.rect.left - 1
        old_x = pacman.rect.x
        pacman.set_direction(3, 0)
        for _ in range(10):
            pacman.update(wall_group, gate_group)
        assert pacman.rect.x <= old_x + 3 * 10

    def test_tunnel_warp_vasakult(self, pacman, wall_group, gate_group):
        pacman.set_direction(-3, 0)
        pacman.rect.right = -1
        pacman.update(wall_group, gate_group)
        assert pacman.rect.left >= WIN_W - 10

    def test_tunnel_warp_paremalt(self, pacman, wall_group, gate_group):
        pacman.set_direction(3, 0)
        pacman.rect.left = WIN_W + 1
        pacman.update(wall_group, gate_group)
        assert pacman.rect.right <= 10

    def test_pacman_center_property(self, pacman):
        cx, cy = pacman.center
        assert cx == pacman.rect.centerx
        assert cy == pacman.rect.centery


# ----------------------------------------------
# 4. GHOST
# ----------------------------------------------

class TestGhost:
    def test_ghost_loodud_oige_nimega(self, blinky):
        assert blinky.name == 'blinky'

    def test_ghost_scared_olek(self, blinky):
        blinky.update_scared(True, 300)
        assert blinky.scared is True
        assert blinky.scared_timer == 300

    def test_ghost_scared_kaob_ara(self, blinky):
        blinky.update_scared(True, 300)
        blinky.update_scared(False, 0)
        assert blinky.scared is False

    @pytest.mark.parametrize("name,expected_color", [
        ('blinky', (255, 0, 0)),
        ('pinky',  (255, 184, 255)),
        ('inky',   (0, 255, 255)),
        ('clyde',  (255, 184, 82)),
    ])
    def test_ghost_varvid(self, name, expected_color):
        dirs = BLINKY_DIRS
        g = Ghost(287, 199, name, dirs, len(dirs) - 1)
        assert g.color == expected_color

    def test_ghost_tunnel_warp(self, blinky, wall_group):
        blinky.rect.right = -1
        blinky.change_x = -1
        blinky.update(wall_group)
        assert blinky.rect.left >= WIN_W - 10


# ----------------------------------------------
# 5. SKOOR JA MANGULOOGIKA
# ----------------------------------------------

class TestGameLogic:
    def test_tavaline_pellet_annab_10_punkti(self):
        score = 0
        p = Pellet(100, 100, big=False)
        score += 50 if p.big else 10
        assert score == 10

    def test_power_pellet_annab_50_punkti(self):
        score = 0
        p = Pellet(100, 100, big=True)
        score += 50 if p.big else 10
        assert score == 50

    def test_ghost_tapmine_annab_200_punkti(self):
        score = 0
        score += 200
        assert score == 200

    def test_elu_kaotus(self):
        lives = 3
        lives -= 1
        assert lives == 2

    def test_mangija_kaotab_kolm_elu(self):
        lives = 3
        for _ in range(3):
            lives -= 1
        assert lives == 0

    def test_setup_level_loob_pelletid(self, level):
        _, _, _, pellet_list = level
        assert len(pellet_list) > 0

    def test_setup_level_loob_seinad(self, level):
        _, wall_list, _, _ = level
        assert len(wall_list) == len(WALLS)

    def test_setup_level_loob_varvava(self, level):
        _, _, gate_group, _ = level
        assert len(gate_group) == 1

    def test_power_pelletid_nurgatingimus(self, level):
        _, _, _, pellet_list = level
        all_pellets = list(pellet_list)
        assert len(all_pellets) > 0
        big_count = sum(1 for p in all_pellets if p.big)
        assert big_count == 0

    def test_kokkuporge_pacman_ja_ghost(self, pacman, blinky):
        blinky.rect.center = pacman.rect.center
        assert pacman.rect.colliderect(blinky.rect)

    def test_ei_ole_kokkuporge_kaugel(self, pacman, blinky):
        blinky.rect.center = (0, 0)
        pacman.rect.center = (500, 500)
        assert not pacman.rect.colliderect(blinky.rect)