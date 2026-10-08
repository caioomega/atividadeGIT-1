"""Gera texturas de nuvem (PNG RGBA): cúmulos feitos de esferas sombreadas
com bordas quebradas por ruído fractal.

Saída em assets/: clouds_front.png, clouds_back.png, clouds_top.png, steam.png
"""
import sys
import numpy as np
from PIL import Image, ImageFilter


def value_noise(h, w, cell, rng):
    gh, gw = h // cell + 3, w // cell + 3
    g = rng.random((gh, gw)).astype(np.float32)
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((gw * cell, gh * cell), Image.BICUBIC)
    return np.asarray(im).astype(np.float32)[:h, :w] / 255


def fbm(h, w, base, octaves, rng, gain=0.5):
    out = np.zeros((h, w), np.float32)
    amp, tot, cell = 1.0, 0.0, base
    for _ in range(octaves):
        out += amp * value_noise(h, w, max(2, int(cell)), rng)
        tot += amp
        amp *= gain
        cell /= 2
    return out / tot


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


LIGHT = np.array([-0.35, -0.75, 0.55])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def render_spheres(w, h, spheres, warm, rng, warp=10, soft=1.2, alpha_mul=1.0, tex=0.12):
    """Compõe esferas (cx, cy, r) de trás pra frente com sombreamento difuso."""
    rgb = np.zeros((h, w, 3), np.float32)
    A = np.zeros((h, w), np.float32)
    # deslocamento de domínio para quebrar o contorno perfeito das esferas
    wx = (fbm(h, w, 60, 4, rng) - .5) * 2 * warp
    wy = (fbm(h, w, 60, 4, rng) - .5) * 2 * warp
    detail = fbm(h, w, 40, 4, rng)
    white = np.array([255, 255, 255], np.float32)
    shadow = np.array(warm, np.float32)
    for (cx, cy, r) in sorted(spheres, key=lambda s: s[1] + s[2] * .3):
        x0, x1 = int(max(0, cx - r - warp)), int(min(w, cx + r + warp + 1))
        y0, y1 = int(max(0, cy - r - warp)), int(min(h, cy + r + warp + 1))
        if x0 >= x1 or y0 >= y1:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        dx = (xx + wx[y0:y1, x0:x1] - cx) / r
        dy = (yy + wy[y0:y1, x0:x1] - cy) / r
        d2 = dx * dx + dy * dy
        a = smoothstep(1.0, 0.86, np.sqrt(d2)) * alpha_mul
        nz = np.sqrt(np.clip(1 - d2, 0, 1))
        lam = np.clip(dx * LIGHT[0] + dy * LIGHT[1] + nz * LIGHT[2], 0, 1)
        shade = np.clip(0.30 + 0.85 * lam + tex * (detail[y0:y1, x0:x1] - .5), 0, 1)
        col = shadow * (1 - shade[..., None]) + white * shade[..., None]
        ra = a[..., None]
        rgb[y0:y1, x0:x1] = col * ra + rgb[y0:y1, x0:x1] * (1 - ra)
        A[y0:y1, x0:x1] = a + A[y0:y1, x0:x1] * (1 - a)
    # rgb está pré-multiplicado pelo alpha acumulado → desfaz
    out = np.where(A[..., None] > 1e-4, rgb / np.maximum(A[..., None], 1e-4), 255)
    img = Image.fromarray(np.dstack([np.clip(out, 0, 255).astype(np.uint8), (A * 255).astype(np.uint8)]), "RGBA")
    return img.filter(ImageFilter.GaussianBlur(soft)) if soft else img


def cumulus_bank(w, h, base_y, n_base, rmin, rmax, seed, levels=3):
    rng = np.random.default_rng(seed)
    spheres = []
    xs = np.linspace(-0.05 * w, 1.05 * w, n_base) + rng.uniform(-40, 40, n_base)
    level = []
    for x in xs:
        r = rng.uniform(rmin, rmax)
        level.append((x, base_y + rng.uniform(-.15, .35) * r, r))
    spheres += level
    # corpo inferior cheio
    for x in np.linspace(-.1 * w, 1.1 * w, n_base * 2):
        r = rmax * 1.3
        spheres.append((x + rng.uniform(-30, 30), base_y + r * .9 + rng.uniform(0, 60), r))
    for lv in range(levels):
        nxt = []
        for (cx, cy, r) in level:
            k = rng.integers(2, 4)
            for _ in range(k):
                ang = np.radians(rng.uniform(-160, -20))
                cr = r * rng.uniform(.42, .62)
                d = r * rng.uniform(.55, .8)
                nxt.append((cx + np.cos(ang) * d, cy + np.sin(ang) * d, cr))
        spheres += nxt
        level = [s for s in nxt if s[2] > 18]
    return spheres, rng


def plume_spheres(w, h, seed):
    rng = np.random.default_rng(seed)
    sp = []
    for i in range(16):
        t = i / 15
        r = (14 + 62 * t ** 0.8) * rng.uniform(.75, 1.25)
        sp.append((w * .4 + 70 * t * t + rng.uniform(-1, 1) * 26 * t, h - 24 - t * (h - 150), r))
    return sp, rng


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "assets"
    W = 1600
    sp, rng = cumulus_bank(W, 640, 300, 9, 120, 190, 11)
    render_spheres(W, 640, sp, (247, 196, 160), rng, warp=12).save(f"{out}/clouds_front.png")
    sp, rng = cumulus_bank(W, 560, 260, 11, 80, 140, 23)
    render_spheres(W, 560, sp, (250, 176, 128), rng, warp=10, soft=2.5).save(f"{out}/clouds_back.png")
    # faixas finas no alto: esferas achatadas espalhadas
    rng = np.random.default_rng(31)
    sp = [(rng.uniform(0, W), rng.uniform(140, 260), rng.uniform(40, 95)) for _ in range(40)]
    render_spheres(W, 420, sp, (255, 205, 170), rng, warp=22, soft=6, alpha_mul=.55).save(f"{out}/clouds_top.png")
    sp, rng = plume_spheres(320, 560, 41)
    render_spheres(320, 560, sp, (250, 200, 165), rng, warp=10, soft=3, alpha_mul=.5).save(f"{out}/steam.png")
    print("clouds ok")
