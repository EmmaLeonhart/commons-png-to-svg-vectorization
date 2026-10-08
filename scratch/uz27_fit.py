"""Fit size/position of the 1927 flag's Arabic lines to the PNG ink boxes (2 rounds)."""
import re, subprocess, sys
import numpy as np
from PIL import Image
from scipy import ndimage as nd
B='files/uzbek-ssr-flag-1927/build.py'; SVG='files/uzbek-ssr-flag-1927/Flag of the Uzbek Soviet Socialist Republic (1927-1929).svg'
P='data_lake/downloads/uzbek-ssr-flag-1927/Flag of the Uzbek Soviet Socialist Republic(1927-1929).png'
def box(p, y0, y1):
    T=np.array(Image.open(p).convert('RGB')).astype(int)[y0:y1]; g=(T[...,1]>150)&(T[...,0]>200)
    ys,xs=np.nonzero(g); return xs.min(), xs.max()+1, ys.min()+y0, ys.max()+1+y0
target={'line-arabic-1':box(P,0,62),'line-arabic-2':box(P,112,180)}
for it in range(3):
    subprocess.run([sys.executable,B],check=True,capture_output=True)
    subprocess.run([sys.executable,'tools/render_svg.py',SVG,'scratch/uz27_out.png'],check=True,capture_output=True)
    s=open(B,encoding='utf8').read()
    for lid,(y0,y1) in {'line-arabic-1':(0,64),'line-arabic-2':(110,185)}.items():
        x0,x1,t0,t1=box('scratch/uz27_out.png',y0,y1); X0,X1,T0,T1=target[lid]
        m=re.search(rf"\('{lid}', ([\d.]+), ([\d.]+), ([\d.]+),",s); x,y,fs=map(float,m.groups())
        k=(T1-T0)/(t1-t0); nfs=fs*k
        # after scaling about the anchor (right edge x, baseline y): new edges
        nx=x+(X1-(x+(x1-x)*k)); ny=y+(T1-(y+(t1-y)*k))
        s=s.replace(m.group(0),f"('{lid}', {nx:.1f}, {ny:.1f}, {nfs:.1f},")
        print(it,lid,'svg',(x0,x1,t0,t1),'png',target[lid],'->',round(nx,1),round(ny,1),round(nfs,1))
    open(B,'w',encoding='utf8').write(s)
