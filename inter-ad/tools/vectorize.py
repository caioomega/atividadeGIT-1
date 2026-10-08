"""Vectoriza os logos do Inter (JPG) em paths SVG usando potracer."""
import sys, json
import numpy as np
from PIL import Image, ImageFilter
import potrace

def trace(path, invert, crop=None, scale=2):
    im = Image.open(path).convert("RGB")
    if crop:
        im = im.crop(crop)
    w, h = im.size
    im = im.resize((w * scale, h * scale), Image.LANCZOS).filter(ImageFilter.GaussianBlur(scale * 1.2))
    # canal mínimo: laranja (B=0) e preto ficam escuros, branco fica claro
    a = np.asarray(im).astype(np.float32).min(axis=2) / 255.0
    ink = (a < 0.5) if invert else (a > 0.5)
    # potracer trata valores "escuros" (False) como tinta
    bm = potrace.Bitmap(~ink)
    plist = bm.trace(turdsize=20, alphamax=1.0, opticurve=True, opttolerance=0.6)
    d = []
    for curve in plist:
        sx, sy = curve.start_point.x, curve.start_point.y
        parts = [f"M{sx/scale:.2f},{sy/scale:.2f}"]
        for seg in curve:
            if seg.is_corner:
                parts.append(f"L{seg.c.x/scale:.2f},{seg.c.y/scale:.2f}L{seg.end_point.x/scale:.2f},{seg.end_point.y/scale:.2f}")
            else:
                parts.append(f"C{seg.c1.x/scale:.2f},{seg.c1.y/scale:.2f} {seg.c2.x/scale:.2f},{seg.c2.y/scale:.2f} {seg.end_point.x/scale:.2f},{seg.end_point.y/scale:.2f}")
        parts.append("Z")
        d.append("".join(parts))
    ys, xs = np.nonzero(ink)
    bbox = [xs.min() / scale, ys.min() / scale, xs.max() / scale, ys.max() / scale]
    return d, bbox, (w, h)

if __name__ == "__main__":
    word, sym, out = sys.argv[1], sys.argv[2], sys.argv[3]
    wd, wb, ws = trace(word, invert=True)
    sd, sb, ss = trace(sym, invert=False)
    json.dump({"word": {"paths": wd, "bbox": wb, "size": ws},
               "symbol": {"paths": sd, "bbox": sb, "size": ss}}, open(out, "w"))
    print("word paths", len(wd), wb, "symbol paths", len(sd), sb)
