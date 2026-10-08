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
    wa = re.search(r'\swidth="([^"]+)"', head).group(1)
    ha = re.search(r'\sheight="([^"]+)"', head).group(1)
    vb = re.search(r'\sviewBox="([^"]+)"', head)
    if vb and re.search(r'[a-z%]', wa + ha):  # mm, cm, % ...: size by the viewBox instead
        w, h = [float(v) for v in re.split(r'[\s,]+', vb.group(1).strip())[2:4]]
    else:
        w, h = float(re.sub(r'[^\d.]', '', wa)), float(re.sub(r'[^\d.]', '', ha))
    W, H = round(w * scale), round(h * scale)
    html = src.with_name(src.stem + '.render.html')
    html.write_text(f'<html><body style="margin:0;background:#000"><img src="{src.name}" '
                    f'style="width:{W}px;height:{H}px;display:block"></body></html>', encoding='utf8')
    try:
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--screenshot={out}',
                        f'--window-size={W},{H}', '--force-device-scale-factor=1', html.as_uri()],
                       check=True, capture_output=True)
    finally:
        html.unlink(missing_ok=True)
    return W, H


if __name__ == '__main__':
    print(render(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 1.0))
