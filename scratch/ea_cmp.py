import resvg_py, io
from PIL import Image
D = 'data_lake/downloads/east-asia-cutout/'
print('start', flush=True)
a = Image.open(D + 'East Asia Cutout Projection.png').convert('RGB')
s = open(D + 'East Asia (orthographic projection) 2009-10-04.svg', encoding='utf8').read()
b = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=s, width=541)))).convert('RGB')
c = Image.new('RGB', (801, 541), 'white'); c.paste(a, (0, 0)); c.paste(b, (260, 0)); c.save('scratch/arms/ea.png')
print('ok')
