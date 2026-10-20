import sys, io, numpy as np, resvg_py
from PIL import Image
def r(p, w=543):
    return np.array(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=open(p, encoding='utf8').read(), width=w)))).convert('RGB')).astype(float)
A = r(sys.argv[1]); B = r(sys.argv[2])
d = np.abs(A - B).max(2)
mse = ((A - B) ** 2).mean()
print(f'PSNR {10 * np.log10(255 ** 2 / max(mse, 1e-9)):.1f} dB, pixels off by >24: {100 * (d > 24).mean():.2f}%, >48: {100 * (d > 48).mean():.2f}%')
if len(sys.argv) > 3:
    W = Image.new('RGB', (A.shape[1] * 2 + 10, A.shape[0]), '#888')
    W.paste(Image.fromarray(A.astype('uint8')), (0, 0)); W.paste(Image.fromarray(B.astype('uint8')), (A.shape[1] + 10, 0)); W.save(sys.argv[3])
