"""Render an SVG to PNG with headless Chrome (used to compare a rebuild with its PNG).

usage: python tools/render_svg.py in.svg out.png [scale]
"""
import re
import subprocess
import sys
from pathlib import Path

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'


def render(src, out, scale=1.0):
    src, out = Path(src).resolve(), Path(out).resolve()
    s = src.read_text(encoding='utf8')
    head = re.search(r'<svg\b[^>]*>', s, re.S).group(0)
    wm = re.search(r'\swidth="([^"]+)"', head)
    hm = re.search(r'\sheight="([^"]+)"', head)
    vb = re.search(r'\sviewBox="([^"]+)"', head)
    wa, ha = (wm.group(1) if wm else '%'), (hm.group(1) if hm else '%')
    if not vb and not (wm and hm):
        wa, ha = '300', '150'  # the browser default for an unsized SVG
    per_px = {'px': 1, '': 1, 'mm': 96 / 25.4, 'cm': 96 / 2.54, 'in': 96, 'pt': 96 / 72, 'pc': 16}

    def length(v):
        m = re.fullmatch(r'\s*([\d.eE+-]+)\s*([a-z]*)\s*', v)
        return float(m.group(1)) * per_px[m.group(2)] if m and m.group(2) in per_px else None
    w, h = length(wa), length(ha)
    if (w is None or h is None) and vb:  # missing or %: size by the viewBox
        w, h = [float(v) for v in re.split(r'[\s,]+', vb.group(1).strip())[2:4]]
    W, H = round(w * scale), round(h * scale)
    html = src.with_name(src.stem + '.render.html')
    html.write_text(f'<html><body style="margin:0;background:transparent"><img src="{src.name}" '
                    f'style="width:{W}px;height:{H}px;display:block"></body></html>', encoding='utf8')
    try:
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--screenshot={out}',
                        f'--window-size={W},{H}', '--force-device-scale-factor=1', '--default-background-color=00000000', html.as_uri()],
                       check=True, capture_output=True)
    finally:
        html.unlink(missing_ok=True)
    return W, H


if __name__ == '__main__':
    print(render(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 1.0))
