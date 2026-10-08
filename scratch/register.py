"""Find scale/offset mapping target PNG pixels -> SVG user units (render at 1px/unit)."""
import numpy as np
from PIL import Image
from numpy.fft import rfft2, irfft2
T=np.array(Image.open('data_lake/downloads/kinai-hyuga/Kinai-and-Hyuga-Province-in-Japan-RA.png').convert('RGB')).astype(int)
def near(c,tol=12): return (np.abs(T-np.array(c)).sum(2)<tol)
sea=near((213,225,254))|near((234,240,255))
land=near((251,251,251),10)|near((255,233,184))|near((139,227,178))|((T.min(2)>245))
tgt=np.zeros(T.shape[:2]); tgt[land]=1; tgt[sea]=-1
idx=np.load('scratch/idx.npy'); src=np.where(idx>0,1.0,-1.0)
H,W=src.shape
best=None
for s in np.arange(0.15,0.30,0.0025):  # svg units per target px
    n=round(1400*s)
    t=np.array(Image.fromarray(((tgt+1)*127.5).astype(np.uint8)).resize((n,n),Image.BILINEAR)).astype(float)/127.5-1
    P=(1024,1024)
    F=irfft2(rfft2(src,P)*np.conj(rfft2(t,P)),P)
    i=np.unravel_index(np.argmax(F),F.shape); sc=F[i]/(n*n)
    if best is None or sc>best[0]: best=(sc,s,i)
print(best)
sc,s,(oy,ox)=best
print(f'svg_x = {ox} + {s}*u ; svg_y = {oy} + {s}*v')
