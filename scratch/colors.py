import numpy as np, json
from PIL import Image
from collections import Counter
T=np.array(Image.open('data_lake/downloads/kinai-hyuga/Kinai-and-Hyuga-Province-in-Japan-RA.png').convert('RGB'))
idx=np.load('scratch/idx.npy'); units=json.load(open('scratch/units.json')); S=4
s,ox,oy=np.load('scratch/xform.npy')
vv,uu=np.mgrid[0:1400,0:1400]
x=((ox+s*uu)*S).astype(int); y=((oy+s*vv)*S).astype(int)
k=idx[y,x]
for i in sorted(set(k.ravel())-{0}):
    m=k==i; c=Counter(map(tuple,T[m].tolist())).most_common(2)
    ys,xs=np.nonzero(m)
    print(i,units[i-1],m.sum(),'centroid px',int(xs.mean()),int(ys.mean()),c)
