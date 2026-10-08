"""Fit ellipse + 4 bands (each: centre line through two points, half-width) to EdinburghTramsGeneric.png."""
import sys, json, itertools
import numpy as np
from PIL import Image
sys.path.insert(0,'tools'); from render_svg import render
P='data_lake/downloads/edinburgh-trams-generic/EdinburghTramsGeneric.png'
A=np.array(Image.open(P).convert('RGBA')).astype(int)
op=A[...,3]>127
grey=op&(np.abs(A[...,:3]-[148,147,147]).sum(2)<20); red=op&(np.abs(A[...,:3]-[138,13,4]).sum(2)<40); white=op&(A[...,:3].min(2)>240)
ys,xs=np.nonzero(op); print('disc bbox',xs.min(),xs.max(),ys.min(),ys.max())
def line_fit(mask):
    ys,xs=np.nonzero(mask); X=np.stack([xs,ys],1).astype(float); c=X.mean(0); u,s,vt=np.linalg.svd(X-c,full_matrices=False); d=vt[0]; n=np.array([-d[1],d[0]])
    off=(X-c)@n; return c,d,np.percentile(np.abs(off),97)
# split red / white into two bands each by direction sign (NW-SE has positive slope in image coords)
out={}
for name,m in (('red',red),('white',white)):
    ys,xs=np.nonzero(m); X=np.stack([xs,ys],1).astype(float)
    # assign pixels to the band whose line is closer, iterate (2-line k-means)
    a=np.array([[0.6,-0.8]]); b=np.array([[0.8,0.6]])  # init directions: SW-NE, NW-SE
    lab=np.zeros(len(X),int)
    lines=[None,None]
    # init: split by local orientation using initial guesses through mask centre
    c=X.mean(0)
    for it in range(10):
        for k,init in enumerate(((0.83,-0.56),(0.83,0.56))):
            sel=X[lab==k] if it>0 else X
            if it==0:
                d=np.array(init); nrm=np.array([-d[1],d[0]]); cc=c
            else:
                cc=sel.mean(0); u,s,vt=np.linalg.svd(sel-cc,full_matrices=False); d=vt[0]; nrm=np.array([-d[1],d[0]])
            lines[k]=(cc,d,nrm)
        dist=np.stack([np.abs((X-l[0])@l[2]) for l in lines],1); lab=dist.argmin(1)
        if it==0:
            # second pass: separate by actual distance to two parallel-offset guesses is unreliable; rely on k-means
            pass
    for k in range(2):
        sel=X[lab==k]; cc=sel.mean(0); u,s,vt=np.linalg.svd(sel-cc,full_matrices=False); d=vt[0]; nrm=np.array([-d[1],d[0]])
        off=(sel-cc)@nrm; hw=np.percentile(np.abs(off),98)
        out[f'{name}{k}']=dict(c=cc.round(2).tolist(),d=d.round(5).tolist(),hw=round(float(hw),2),n=int(len(sel)))
print(json.dumps(out,indent=1))
json.dump(out,open('scratch/edinburgh_bands.json','w'))
