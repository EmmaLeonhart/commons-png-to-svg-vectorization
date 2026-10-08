"""Render an SVG to PNG with headless Chrome. usage: render.py in.svg out.png scale"""
import sys, subprocess, pathlib, re, tempfile, os
src, out, scale = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]).resolve(), float(sys.argv[3])
s = src.read_text(encoding='utf8')
w = float(re.search(r'<svg[^>]*?\swidth="([\d.]+)', s).group(1)); h = float(re.search(r'<svg[^>]*?\sheight="([\d.]+)', s).group(1))
W, H = round(w*scale), round(h*scale)
html = src.with_suffix('.render.html')
html.write_text(f'<html><body style="margin:0;background:#000"><img src="{src.name}" style="width:{W}px;height:{H}px;display:block"></body></html>', encoding='utf8')
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
subprocess.run([chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--screenshot={out}', f'--window-size={W},{H}', '--force-device-scale-factor=1', html.as_uri()], check=True, capture_output=True)
html.unlink()
print(out, W, H)
