import sys, numpy as np
from PIL import Image, ImageFilter
import potrace
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
W = im.size[0]*4
im = im.resize((W, W), Image.LANCZOS)
a = np.asarray(im).astype(int)
r,g,b = a[...,0],a[...,1],a[...,2]
masks = {
 'orange': (r-b > 80),
 'dark':   (r < 90) & (g < 90) & (b < 90),
 'gray':   (r > 100) & (r < 185) & (abs(r-b) < 20) & (abs(r-g) < 20),
}
def trace(m, blur=3):
    mi = Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
    m2 = np.asarray(mi) > 127
    bm = potrace.Bitmap(~m2)
    path = bm.trace(turdsize=200, alphamax=1.0, opticurve=True, opttolerance=0.4)
    d = []
    for c in path:
        s = c.start_point; d.append(f"M{s.x:.1f},{s.y:.1f}")
        for seg in c.segments:
            if seg.is_corner:
                d.append(f"L{seg.c.x:.1f},{seg.c.y:.1f}L{seg.end_point.x:.1f},{seg.end_point.y:.1f}")
            else:
                d.append(f"C{seg.c1.x:.1f},{seg.c1.y:.1f} {seg.c2.x:.1f},{seg.c2.y:.1f} {seg.end_point.x:.1f},{seg.end_point.y:.1f}")
        d.append("Z")
    return "".join(d)
cols = {'orange':'#F58634','gray':'#858688','dark':'#363435'}
parts = {k: trace(m, 6 if k=='orange' else 3) for k,m in masks.items()}
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {W}">' + \
  ''.join(f'<path id="logo-{k}" fill="{cols[k]}" fill-rule="evenodd" d="{parts[k]}"/>' for k in ['orange','gray','dark']) + '</svg>'
open(out,'w').write(svg)
import json; json.dump({'W':W, **parts}, open(out.replace('.svg','.json'),'w'))
print('ok', W, {k:len(v) for k,v in parts.items()})
