import numpy as np, itertools
from PIL import Image
exec(open('scratch/register.py').read().split('idx=np.load')[0])  # reuse tgt
S=4
idx=np.load('scratch/idx.npy'); land4=idx>0
vv,uu=np.mgrid[0:1400:3,0:1400:3]; t=tgt[vv,uu]; m=t!=0; vv,uu,t=vv[m],uu[m],t[m]
def score(s,ox,oy):
    x=((ox+s*uu)*S).astype(int); y=((oy+s*vv)*S).astype(int)
    ok=(x>=0)&(y>=0)&(x<land4.shape[1])&(y<land4.shape[0])
    v=np.where(land4[y.clip(0,land4.shape[0]-1),x.clip(0,land4.shape[1]-1)]&ok,1,-1)
    return (v==t).mean()
best=(0,)
s0,ox0,oy0=0.2325,39,433
for it in range(3):
    rs=np.linspace(-0.004,0.004,17)/(3**it); ro=np.linspace(-2,2,21)/(3**it)
    for ds,dx,dy in itertools.product(rs,ro,ro):
        sc=score(s0+ds,ox0+dx,oy0+dy)
        if sc>best[0]: best=(sc,s0+ds,ox0+dx,oy0+dy)
    _,s0,ox0,oy0=best; print(best)
np.save('scratch/xform.npy',np.array([s0,ox0,oy0]))
