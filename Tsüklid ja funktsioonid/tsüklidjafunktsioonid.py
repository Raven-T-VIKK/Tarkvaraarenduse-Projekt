import pygame
import sys

# ── Värvid ──────────────────────────────────────────────────────────────────
BG         = (15, 15, 25)
PANEL      = (25, 25, 40)
ACCENT     = (100, 220, 140)
TEXT       = (230, 230, 240)
TEXT_DIM   = (130, 130, 150)
BORDER     = (50, 55, 80)

LINE_COLORS = {
    "Punane":    (220, 60,  60),
    "Roheline":  (60,  200, 100),
    "Sinine":    (60,  120, 220),
    "Kollane":   (230, 200, 50),
    "Oranž":     (230, 130, 40),
    "Lilla":     (160, 80,  210),
    "Türkiis":   (50,  200, 200),
    "Valge":     (240, 240, 240),
    "Must":      (20,  20,  20),
    "Roosa":     (230, 100, 170),
}

TAUST_VARV = (144, 238, 144)


def draw_rounded_rect(surf, color, rect, radius=10, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Slider:
    def __init__(self, x, y, w, min_val, max_val, default, label):
        self.rect     = pygame.Rect(x, y, w, 6)
        self.min      = min_val
        self.max      = max_val
        self.value    = default
        self.label    = label
        self.dragging = False
        self.hr       = 11

    def _val_to_x(self):
        t = (self.value - self.min) / (self.max - self.min)
        return self.rect.x + int(t * self.rect.w)

    def handle(self):
        return pygame.Rect(self._val_to_x() - self.hr,
                           self.rect.centery - self.hr,
                           self.hr * 2, self.hr * 2)

    def event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and self.handle().collidepoint(e.pos):
            self.dragging = True
        if e.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        if e.type == pygame.MOUSEMOTION and self.dragging:
            t = max(0.0, min(1.0, (e.pos[0] - self.rect.x) / self.rect.w))
            self.value = round(self.min + t * (self.max - self.min))

    def draw(self, surf, font_sm, font_label):
        draw_rounded_rect(surf, BORDER, self.rect.inflate(0, 4), radius=4)
        filled = self.rect.copy()
        filled.w = max(0, self._val_to_x() - self.rect.x)
        if filled.w > 0:
            draw_rounded_rect(surf, ACCENT, filled.inflate(0, 4), radius=4)
        hx, hy = self._val_to_x(), self.rect.centery
        pygame.draw.circle(surf, BG,    (hx, hy), self.hr + 2)
        pygame.draw.circle(surf, ACCENT,(hx, hy), self.hr)
        pygame.draw.circle(surf, (200, 255, 220), (hx, hy), 4)
        lbl = font_label.render(self.label, True, TEXT_DIM)
        surf.blit(lbl, (self.rect.x, self.rect.y - 26))
        val_s = font_sm.render(str(int(self.value)), True, ACCENT)
        surf.blit(val_s, (self.rect.right - val_s.get_width(), self.rect.y - 26))


class ColorPicker:
    def __init__(self, x, y, label):
        self.label    = label
        self.selected = "Punane"
        self.names    = list(LINE_COLORS.keys())
        self.x, self.y = x, y
        self.sw, self.sh = 44, 30
        self.gap = 7
        self.rects = {}
        self._build()

    def _build(self):
        cols = 5
        for i, name in enumerate(self.names):
            col = i % cols
            row = i // cols
            self.rects[name] = pygame.Rect(
                self.x + col * (self.sw + self.gap),
                self.y + row * (self.sh + self.gap),
                self.sw, self.sh)

    def event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            for name, r in self.rects.items():
                if r.collidepoint(e.pos):
                    self.selected = name

    def draw(self, surf, font_label, font_tiny):
        lbl = font_label.render(self.label, True, TEXT_DIM)
        surf.blit(lbl, (self.x, self.y - 28))
        for name, r in self.rects.items():
            color = LINE_COLORS[name]
            draw_rounded_rect(surf, color, r, radius=7)
            if name == self.selected:
                draw_rounded_rect(surf, (255,255,255), r, radius=7,
                                  border=3, border_color=(255,255,255))
            lum = 0.299*color[0] + 0.587*color[1] + 0.114*color[2]
            tc  = (10,10,10) if lum > 160 else (240,240,240)
            t   = font_tiny.render(name, True, tc)
            surf.blit(t, t.get_rect(center=r.center))

    def get_color(self):
        return LINE_COLORS[self.selected]

    def height(self):
        rows = (len(self.names) + 4) // 5
        return rows * (self.sh + self.gap)


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect    = pygame.Rect(x, y, w, h)
        self.text    = text
        self.hover   = False
        self.clicked = False
        self._anim   = 0.0

    def event(self, e):
        self.clicked = False
        if e.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(e.pos)
        if e.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(e.pos):
            self.clicked = True

    def draw(self, surf, font):
        target = 1.0 if self.hover else 0.0
        self._anim += (target - self._anim) * 0.18
        base = lerp_color(ACCENT, (180, 255, 200), self._anim)
        shadow = pygame.Rect(self.rect.x+2, self.rect.y+4, self.rect.w, self.rect.h)
        draw_rounded_rect(surf, (0, 40, 20), shadow, radius=14)
        draw_rounded_rect(surf, base, self.rect, radius=14)
        lbl = font.render(self.text, True, (5, 25, 10))
        surf.blit(lbl, lbl.get_rect(center=self.rect.center))


def draw_grid(surf, ridu, veerge, ruudu_suurus, joone_varv):
    surf.fill(TAUST_VARV)
    for r in range(ridu + 1):
        pygame.draw.line(surf, joone_varv,
                         (0, r * ruudu_suurus),
                         (veerge * ruudu_suurus, r * ruudu_suurus), 1)
    for c in range(veerge + 1):
        pygame.draw.line(surf, joone_varv,
                         (c * ruudu_suurus, 0),
                         (c * ruudu_suurus, ridu * ruudu_suurus), 1)


def show_grid(ridu, veerge, ruudu_suurus, joone_varv):
    laius  = veerge * ruudu_suurus
    korgus = ridu   * ruudu_suurus
    info   = pygame.display.Info()
    laius  = min(laius,  info.current_w  - 20)
    korgus = min(korgus, info.current_h  - 60)

    win = pygame.display.set_mode((laius, korgus))
    pygame.display.set_caption(f"Ruudustik  {veerge}×{ridu}  |  ESC = tagasi menüüsse")
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        draw_grid(win, ridu, veerge, ruudu_suurus, joone_varv)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.display.set_mode((600, 700))
                pygame.display.set_caption("Ruudustiku Generaator")
                return


def main():
    pygame.init()
    W, H = 600, 700
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Ruudustiku Generaator")
    clock  = pygame.time.Clock()

    try:
        f_title = pygame.font.SysFont("segoeui", 26, bold=True)
        f_label = pygame.font.SysFont("segoeui", 15)
        f_sm    = pygame.font.SysFont("segoeui", 15, bold=True)
        f_tiny  = pygame.font.SysFont("segoeui", 11)
        f_btn   = pygame.font.SysFont("segoeui", 17, bold=True)
    except Exception:
        f_title = f_label = f_sm = f_tiny = f_btn = pygame.font.SysFont(None, 18)

    pad      = 48
    slider_w = W - pad * 2

    sl_size = Slider(pad, 140, slider_w, 10, 80, 20, "Ruudu suurus (px)")
    sl_rows = Slider(pad, 235, slider_w,  1, 50, 24, "Ridade arv")
    sl_cols = Slider(pad, 330, slider_w,  1, 60, 32, "Veergude arv")

    cp   = ColorPicker(pad, 420, "Joone värv")
    cp_h = cp.height()

    btn_y = 420 + cp_h + 30
    btn   = Button(W // 2 - 130, btn_y, 260, 52, "Loo ruudustik!")

    while True:
        clock.tick(60)
        screen.fill(BG)

        draw_rounded_rect(screen, PANEL,
                          pygame.Rect(18, 18, W - 36, H - 36),
                          radius=20, border=1, border_color=BORDER)

        title = f_title.render("Ruudustiku Generaator", True, TEXT)
        screen.blit(title, title.get_rect(centerx=W//2, y=40))
        sub = f_label.render("Vali seaded ja klõpsa nupule!", True, TEXT_DIM)
        screen.blit(sub, sub.get_rect(centerx=W//2, y=76))
        pygame.draw.line(screen, BORDER, (pad, 106), (W - pad, 106), 1)

        sl_size.draw(screen, f_sm, f_label)
        sl_rows.draw(screen, f_sm, f_label)
        sl_cols.draw(screen, f_sm, f_label)
        cp.draw(screen, f_label, f_tiny)
        btn.draw(screen, f_btn)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            sl_size.event(e)
            sl_rows.event(e)
            sl_cols.event(e)
            cp.event(e)
            btn.event(e)
            if btn.clicked:
                show_grid(int(sl_rows.value), int(sl_cols.value),
                          int(sl_size.value), cp.get_color())


if __name__ == "__main__":
    main()