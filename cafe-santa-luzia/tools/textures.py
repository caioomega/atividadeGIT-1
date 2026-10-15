"""Texturas rústicas do vídeo Café Santa Luzia (geradas uma vez, PNG).

- paper_dark.png  : papel envelhecido escuro (fundo principal), 1080x1920
- paper_light.png : pergaminho claro (molduras/rótulos), 1080x1920
- ink_noise.png   : ruído no canal alfa, usado na revelação "tinta se espalhando"
- crops do logo   : cena dos colhedores, faixa "Tradição e Qualidade", grãos, ornamento do topo
"""
import sys

import numpy as np
from PIL import Image, ImageFilter

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets"
W, H = 1080, 1920
rng = np.random.default_rng(42)


def value_noise(h, w, cell, r):
    gh, gw = h // cell + 3, w // cell + 3
    g = r.random((gh, gw)).astype(np.float32)
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((gw * cell, gh * cell), Image.BICUBIC)
    return np.asarray(im).astype(np.float32)[:h, :w] / 255


def fbm(h, w, base, octaves, r, gain=0.55):
    out = np.zeros((h, w), np.float32)
    amp, tot, cell = 1.0, 0.0, base
    for _ in range(octaves):
        out += amp * value_noise(h, w, max(2, int(cell)), r)
        tot += amp
        amp *= gain
        cell /= 2
    return out / tot


def fibers(h, w, n, r):
    """Fibras longas e finas do papel (traços quase horizontais)."""
    img = Image.new("L", (w, h), 0)
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    for _ in range(n):
        x, y = r.uniform(0, w), r.uniform(0, h)
        ang = r.normal(0, 0.35)
        L = r.uniform(20, 140)
        x2, y2 = x + np.cos(ang) * L, y + np.sin(ang) * L
        d.line([(x, y), (x2, y2)], fill=int(r.uniform(40, 120)), width=1)
    return np.asarray(img.filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32) / 255


def vignette(h, w, strength, power=2.2):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / np.sqrt(2)
    return 1 - strength * np.clip(d, 0, 1) ** power


def paper(base, dark, light, stain_col, seed, grain=0.06, vig=0.55):
    r = np.random.default_rng(seed)
    n1 = fbm(H, W, 420, 6, r)
    n2 = fbm(H, W, 90, 4, r)
    st = fbm(H, W, 260, 5, r)
    fib = fibers(H, W, 9000, r)
    t = np.clip(0.5 + (n1 - 0.5) * 1.6 + (n2 - 0.5) * 0.5, 0, 1)
    col = dark[None, None, :] * (1 - t[..., None]) + light[None, None, :] * t[..., None]
    col = col * 0.55 + base[None, None, :] * 0.45
    # manchas (água/café) com bordas um pouco mais escuras
    stain = np.clip((st - 0.62) * 6, 0, 1)
    edge = np.clip(1 - np.abs(st - 0.64) * 30, 0, 1) * 0.5
    col = col * (1 - 0.18 * stain[..., None]) + stain_col[None, None, :] * (0.12 * stain[..., None])
    col = col * (1 - 0.12 * edge[..., None])
    col = col * (1 + 0.10 * fib[..., None])
    col = col + (r.standard_normal((H, W, 1)) * 255 * grain * 0.25)
    col = col * vignette(H, W, vig)[..., None]
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB")


def logo_alpha(src, dst):
    """Remove o fundo preto do logo (alfa pela luminância, sem escurecer as bordas)."""
    a = np.asarray(Image.open(src).convert("RGB")).astype(np.float32) / 255
    alpha = np.clip((a.max(axis=2) - 0.06) / 0.12, 0, 1)
    rgb = np.where(alpha[..., None] > 0.01, np.clip(a / np.maximum(alpha[..., None], 1e-3), 0, 1), 0)
    Image.fromarray((np.dstack([rgb, alpha]) * 255).astype(np.uint8), "RGBA").save(dst)


if __name__ == "__main__":
    logo_alpha(f"{OUT}/logo_src.jpg", f"{OUT}/logo.png")
    paper(np.array([30, 22, 15.]), np.array([14, 10, 7.]), np.array([52, 38, 24.]), np.array([70, 45, 20.]), 1).save(f"{OUT}/paper_dark.png")
    paper(np.array([226, 205, 165.]), np.array([196, 168, 120.]), np.array([240, 226, 196.]), np.array([150, 110, 60.]), 2,
          grain=0.05, vig=0.35).save(f"{OUT}/paper_light.png")
    # ruído p/ revelação orgânica (alfa = fbm com borda "de tinta")
    n = fbm(H // 2, W // 2, 160, 7, np.random.default_rng(9), gain=0.6)
    n = (n - n.min()) / (n.max() - n.min())
    a = Image.fromarray((n * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    rgba = Image.merge("RGBA", (a, a, a, a))
    rgba.save(f"{OUT}/ink_noise.png")
    # variações com direção: a tinta nasce no centro / sobe de baixo
    yy, xx = np.mgrid[0:H // 2, 0:W // 2].astype(np.float32)
    d = np.sqrt(((xx - W / 4) / (W / 4)) ** 2 + ((yy - H / 4) / (W / 4)) ** 2)
    for name, bias in (("ink_center", d / d.max()), ("ink_bottom", 1 - yy / yy.max())):
        m = 0.45 * n + 0.55 * bias
        m = (m - m.min()) / (m.max() - m.min())
        a = Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
        Image.merge("RGBA", (a, a, a, a)).save(f"{OUT}/{name}.png")
    # recortes do logo (já com alfa)
    logo = Image.open(f"{OUT}/logo.png")
    logo.crop((60, 150, 1110, 592)).save(f"{OUT}/logo_scene.png")     # colhedores + paisagem
    logo.crop((240, 826, 930, 905)).save(f"{OUT}/logo_ribbon.png")    # faixa "Tradição e Qualidade"
    logo.crop((380, 890, 800, 1100)).save(f"{OUT}/logo_beans.png")    # grãos de café da base
    logo.crop((470, 20, 700, 190)).save(f"{OUT}/logo_ornament.png")   # ornamento com grão (topo)
    print("textures ok")
